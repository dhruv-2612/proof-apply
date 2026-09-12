"""One Gemini boundary; mock is always explicit. No implicit model or mode fallback."""
import json, re, time
from pathlib import Path
from pydantic import ValidationError
from google import genai
from google.genai import types, errors
from .config import settings
from .models import *
from .extraction import normalized

PROMPTS=Path(__file__).parent/'prompts'
class ProviderError(RuntimeError):
    def __init__(self,code='provider_unavailable',retryable=False):
        self.code=code; self.retryable=retryable
        super().__init__('Model request unavailable. Check free quota/model access; no fallback was used.')

class GeminiProvider:
    mode='gemini'
    def __init__(self,run,save,event,config=settings):
        self.run=run;self.save=save;self.event=event;self.config=config
        self.client=genai.Client(api_key=config.gemini_api_key,http_options=types.HttpOptions(timeout=45000,retry_options=types.HttpRetryOptions(attempts=1)))
    def close(self): self.client.close()
    def _attempt(self):
        if self.run['model_attempts']>=min(18,self.config.max_model_calls): raise ProviderError('model_budget_exhausted')
        if time.monotonic()>self.run.get('_deadline',float('inf')): raise ProviderError('deadline_exceeded')
        self.run['model_attempts']+=1;self.save()
    def _request(self,contents,config):
        for attempt in range(2):
            self._attempt()
            try: return self.client.models.generate_content(model=self.config.gemini_model,contents=contents,config=config)
            except Exception as exc:
                code=getattr(exc,'code',None)
                transient=code in (429,500,502,503,504) or isinstance(exc,(TimeoutError,)) or 'timeout' in type(exc).__name__.lower()
                self.event('provider','request_failed',f'Model attempt failed ({code or "transport"}); '+('one bounded retry available.' if transient and attempt==0 else 'no more retries.'),status='error')
                if not transient or attempt==1: raise ProviderError('quota_exhausted' if code==429 else 'provider_unavailable',transient) from None
                retry_after=2
                response=getattr(exc,'response',None)
                if response is not None:
                    try: retry_after=max(2,float(response.headers.get('Retry-After','2')))
                    except (ValueError,AttributeError): pass
                if retry_after>60 or time.monotonic()+retry_after>self.run.get('_deadline',float('inf')): raise ProviderError('retry_after_exceeds_deadline',True)
                time.sleep(retry_after)
    def call(self,task,schema,payload):
        body=json.dumps(payload,ensure_ascii=False)
        if len(body)>90000: raise ProviderError('context_limit')
        prompt=(PROMPTS/'shared-v1.txt').read_text()+'\n'+(PROMPTS/(task+'-v1.txt')).read_text()
        for repair in range(2):
            response=self._request(body,types.GenerateContentConfig(system_instruction=prompt,response_mime_type='application/json',response_json_schema=schema.model_json_schema(),temperature=0.1,max_output_tokens=10000,automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)))
            try: result=schema.model_validate_json(response.text or '')
            except (ValueError,ValidationError):
                self.event('provider','schema_rejected',f'{task} response failed strict schema validation.',status='error')
                if repair: raise ProviderError('invalid_model_output') from None
                prompt+='\nThe last response failed schema validation. Return a complete schema-valid JSON object.'
                continue
            self.event(task,'model_result',f'{task.replace("_"," ").capitalize()} returned validated structured output.')
            return result
    def research_url(self,url,question):
        response=self._request(f'{question}\nApproved public company URL: {url}\nUse only this URL. Report uncertainty.',types.GenerateContentConfig(tools=[types.Tool(url_context=types.UrlContext())],temperature=0.1,max_output_tokens=2000))
        metadata=[]
        for candidate in response.candidates or []:
            context=getattr(candidate,'url_context_metadata',None)
            for item in getattr(context,'url_metadata',[]) or []:
                metadata.append(item.model_dump(mode='json'))
        succeeded=any('SUCCESS' in str(x.get('url_retrieval_status','')) and x.get('retrieved_url')==url for x in metadata)
        return ToolResult(status='ok' if succeeded else 'error',data={'summary':response.text or '', 'retrieval_metadata':metadata},source_refs=[url] if succeeded else [],error_code=None if succeeded else 'url_not_retrieved')

# Explicit deterministic fixture provider. The reviewer permits only verbatim excerpts.
class MockProvider:
    mode='mock'
    def __init__(self,run,save,event,config=settings): self.run=run;self.save=save;self.event=event
    def close(self): pass
    def call(self,task,schema,payload):
        self.run['mock_calls']=self.run.get('mock_calls',0)+1;self.save()
        if task=='coordinator':
            allowed=payload['allowed_actions']
            action=next(a for a in ['research','assess_fit','inspect_evidence','ask_user','draft','revise','finalize','needs_review','blocked'] if a in allowed)
            result=Decision(action=action,reason={'inspect_evidence':'Check original evidence for the observed role gaps before writing.','revise':'Address the factual/layout blockers once, then rerender and recheck.','finalize':'Evaluated draft is ready for the independent release gate.','ask_user':'A company source or safe evidence decision is required.'}.get(action,f'Prerequisites permit {action.replace("_"," ")}.'))
        elif task=='requirements':
            source=payload['source'];preferred=False;items=[]
            for line in source['text'].splitlines():
                if 'preferred' in line.lower(): preferred=True
                if re.match(r'^\d+\.',line.strip()):
                    items.append(Requirement(id=uid(),jd_source_id=source['id'],text=re.sub(r'^\d+\.\s*','',line),original_excerpt=line,importance='preferred' if preferred else 'required',normalized_terms=terms(line)))
            if not items:
                for line in source['text'].splitlines():
                    if len(line)>20 and re.search(r'experience|ability|knowledge|degree|skill|qualification',line,re.I):
                        items.append(Requirement(id=uid(),jd_source_id=source['id'],text=line[:500],original_excerpt=line[:2000],importance='required',normalized_terms=terms(line)))
            if not items: raise ProviderError('no_requirements_detected')
            result=Requirements(requirements=items[:50])
        elif task=='research':
            sources=payload['sources']; source=next((s for s in sources if s['slot']=='company'),sources[0])
            result=ResearchChoice(tool='inspect_company_kb' if source['slot']=='company' else 'research_official_urls',question='Which documented product and team priorities align with the target role?',source_ids=[source['id']])
        elif task=='fit':
            matches=[];selected=set()
            for req in payload['requirements']:
                req_terms=terms(req['text']);ids=[]
                for e in payload['evidence']:
                    if req_terms and all(term in terms(e['exact_excerpt']) for term in req_terms): ids.append(e['id'])
                selected.update(ids)
                matches.append(Match(requirement_id=req['id'],evidence_ids=ids,status='direct' if ids else 'missing',explanation='Original candidate excerpt documents this requirement.' if ids else 'No eligible candidate evidence establishes this qualification.'))
            result=Fit(matches=matches,relevant_evidence_ids=sorted(selected))
        elif task=='writer':
            evidence=payload['evidence'];fit=payload['fit'];selected=set(fit['relevant_evidence_ids'])
            chosen=[e for e in evidence if e['id'] in selected or e['category'] in ('Education','Skills','Experience') or 'Campus Room Booker' in e['exact_excerpt']]
            if any('Mira built' in e['exact_excerpt'] for e in chosen):
                chosen=[e for e in chosen if not e['exact_excerpt'].startswith(('Worked on the frontend','She manually checked'))]
            # Preserve job title/date/contribution together in offline output. Select a
            # concise first contribution from each role rather than orphaning headings.
            grouped={}
            for e in chosen:
                if e.get('entry_title'): grouped.setdefault(e['entry_title'],[]).append(e)
            keep={e['id'] for group in grouped.values() for e in group[:3]}
            chosen=[e for e in chosen if not e.get('entry_title') or e['id'] in keep]
            if len(chosen)<3: chosen=evidence[:8]
            # Content selection, never shrinking below the template's 11-point body.
            cap=295 if payload.get('revision') else 420
            statements=[];words=0
            for e in sorted(chosen,key=lambda x: {'Education':0,'Skills':1}.get(x['category'],2)):
                if words+len(e['exact_excerpt'].split())>cap: continue
                words+=len(e['exact_excerpt'].split())
                statements.append(Statement(id=uid(),text=e['exact_excerpt'],section=e['category'],claim_ids=[e['claim_id']],evidence_ids=[e['id']],requirement_ids=[m['requirement_id'] for m in fit['matches'] if e['id'] in m['evidence_ids']]))
            result=Writing(statements=statements,edit_reason='Selected and reordered exact source excerpts by role relevance; omitted unsupported or lower-priority material.')
        elif task=='reviewer':
            evidence={e['id']:e for e in payload['evidence']};verdicts=[]
            for statement in payload['statements']:
                supported=any(normalized(statement['text'])==normalized(evidence[id]['exact_excerpt']) for id in statement['evidence_ids'] if id in evidence)
                verdicts.append(Verdict(statement_id=statement['id'],status='supported' if supported else 'uncertain',reason='Exact approved candidate excerpt preserved.' if supported else 'Offline review cannot validate this paraphrase against the original excerpt.'))
            result=Review(verdicts=verdicts,writing_notes=['Offline extractive reviewer; no live semantic assessment was performed.'])
        else: raise ValueError('Unknown mock task')
        self.event(task,'mock_result',f'Explicit offline {task} result generated. No model request.')
        return schema.model_validate(result.model_dump())
    def research_url(self,url,question):
        return ToolResult(status='error',error_code='offline_url_unavailable',warnings=['Offline provider does not retrieve URLs.'])

def terms(text):
    value=text.lower();out=[]
    mapping={'react':r'\breact\b','typescript':r'\btypescript\b','rest':r'\brest\b','tests':r'unit tests|automated.*tests|vitest','git':r'\bgit\b','accessible':r'accessible|keyboard|accessibility','docker':r'\bdocker\b','kubernetes':r'\bkubernetes\b','ci/cd':r'ci/cd|pipelines','linux':r'linux'}
    for term,pattern in mapping.items():
        if re.search(pattern,value): out.append(term)
    return out
