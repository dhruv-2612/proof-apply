"""Bounded sequential worker and conditional LangGraph with durable local pauses."""
from concurrent.futures import ThreadPoolExecutor
from typing import TypedDict
from pathlib import Path
import sqlite3, time, json, threading
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from .models import *
from .providers import MockProvider, GeminiProvider, ProviderError
from .extraction import eligible_evidence, normalized, add_source
from .artifacts import *

class GraphState(TypedDict):
    run_id: str
    next_action: str
class StopRun(Exception): pass

class Jobs:
    def __init__(self,store,config,provider_factory=None):
        self.store=store;self.config=config;self.provider_factory=provider_factory
        self.pool=ThreadPoolExecutor(max_workers=1,thread_name_prefix='proofapply')
        self.busy=False;self.futures=set()
        self.connection=None
        if config.checkpoint_backend=='sqlite':
            self.connection=sqlite3.connect(store.directory/'checkpoints.db',check_same_thread=False)
            self.checkpointer=SqliteSaver(self.connection)
        else: self.checkpointer=InMemorySaver()
    def shutdown(self):
        self.pool.shutdown(wait=True,cancel_futures=True)
        if self.connection: self.connection.close()
    def expire(self,sid):
        for r in self.store.list('run',sid):
            if r['status'] not in ('completed','failed','blocked','needs_review','cancelled','expired'):
                r['status']='expired';self.store.update(r['id'],r)
            try: self.checkpointer.delete_thread(r['id'])
            except Exception: pass
    def submit(self,id,reply=None):
        if self.busy: raise RuntimeError('Server busy')
        self.busy=True
        future=self.pool.submit(self.execute,id,reply);self.futures.add(future)
        def finished(f):
            with self.store.lock: self.futures.discard(f);self.busy=False
        future.add_done_callback(finished)
    def execute(self,id,reply=None):
        run=self.store.get(id,kind='run')
        started=time.monotonic();previous_elapsed=run.get('execution_elapsed_seconds',0)
        run['_deadline']=started+min(600,self.config.max_active_run_seconds)-previous_elapsed
        def guard():
            latest=self.store.get(id,run['session_id'],'run');s=self.store.get(run['session_id'],kind='session')
            if not s or not latest or latest['status'] in ('cancelled','expired'): raise StopRun()
            if time.monotonic()>run['_deadline']: raise ProviderError('deadline_exceeded')
        def save():
            with self.store.lock:
                guard();run['updated_at']=now();run['execution_elapsed_seconds']=round(previous_elapsed+time.monotonic()-started,2)
                self.store.update(id,{k:v for k,v in run.items() if not k.startswith('_')})
        def event(actor,action,summary,source_ids=None,status='ok',result_ids=None):
            guard();self.store.event(run,actor,action,summary,source_ids,status,result_ids)
        factory=self.provider_factory or (GeminiProvider if run['mode']=='gemini' else MockProvider)
        provider=factory(run,save,event,self.config)
        def sources(): return [self.store.get(i,run['session_id'],'source') for i in run['source_ids']]
        def evidence(): return eligible_evidence(self.store,run['session_id'],run['source_ids'])
        def source_context(source):
            # Header/contact fields are not part of any provider request.
            import re
            text=source['extracted_text']
            text='\n'.join(line for line in text.splitlines() if not re.search(r'@|contact placeholder|^# Mira Rao$',line,re.I))
            return {'id':source['id'],'slot':source['slot'],'role':source['role'],'text':text}
        def stage(name):
            guard();run['transitions']+=1
            if run['transitions']>40: raise ProviderError('graph_budget_exhausted')
            run['graph_stage']=name;save()
        def parse(state):
            stage('requirements');source=next(s for s in sources() if s['slot']=='job')
            output=provider.call('requirements',Requirements,{'source':source_context(source)})
            items=[]
            for req in output.requirements:
                if req.jd_source_id!=source['id'] or normalized(req.original_excerpt) not in normalized(source['extracted_text']): raise ProviderError('invalid_requirement_excerpt')
                items.append({**req.model_dump(),'id':uid()})
            run['requirements']=items;save();return {'next_action':'coordinator'}
        def allowed_actions():
            remaining_sources=[s for s in sources() if s['role']=='company' and s['id'] not in run.get('attempted_research_sources',[])]
            if not run['research_ok']:
                if remaining_sources and run['research_calls']<min(2,self.config.max_research_calls): return ['research']
                if run['clarification_count']<min(2,self.config.max_clarifications): return ['ask_user','blocked']
                return ['blocked']
            if not run['matches']: return ['assess_fit']
            if not run['draft_ids']:
                required={r['id'] for r in run['requirements'] if r['importance']=='required'}
                if not run['inspected'] and any(m['requirement_id'] in required and m['status'] in ('partial','missing','unclear') for m in run['matches']): return ['inspect_evidence','draft']
                return ['draft']
            if not run['evaluation_ids']: return ['blocked']
            evaluation=self.store.get(run['evaluation_ids'][-1],run['session_id'],'evaluation')
            if not evaluation['checks']['passed']:
                if run['revision_count']<min(1,self.config.max_revisions): return ['revise','needs_review']
                return ['needs_review']
            return ['finalize']
        def coordinator(state):
            stage('coordinator');allowed=allowed_actions()
            decision=provider.call('coordinator',Decision,{'allowed_actions':allowed,'requirements':run['requirements'],'matches':run['matches'],'research_ok':run['research_ok'],'research_results':run['research_findings'],'evaluation_issues':self.store.get(run['evaluation_ids'][-1],run['session_id'],'evaluation')['issues'] if run['evaluation_ids'] else [],'remaining_revisions':1-run['revision_count'],'remaining_model_attempts':18-run['model_attempts']})
            if decision.action not in allowed: raise ProviderError('illegal_coordinator_action')
            run['latest_decision']=decision.model_dump();save();event('coordinator',decision.action,decision.reason)
            return {'next_action':decision.action}
        def research(state):
            stage('research');available=[s for s in sources() if s['role']=='company' and s['id'] not in run.get('attempted_research_sources',[])]
            choice=provider.call('research',ResearchChoice,{'sources':[{'id':s['id'],'slot':s['slot'],'display_name':s['display_name']} for s in available],'available_tools':['inspect_company_kb','research_official_urls'],'target_role':run['role_title']})
            chosen=[s for s in available if s['id'] in choice.source_ids]
            if not chosen or len(chosen)!=len(set(choice.source_ids)): raise ProviderError('invalid_research_source')
            if run['research_calls']>=2: raise ProviderError('research_budget_exhausted')
            run['research_calls']+=1;run.setdefault('attempted_research_sources',[]).extend(choice.source_ids)
            if choice.tool=='inspect_company_kb':
                if any(s['slot']!='company' for s in chosen): raise ProviderError('research_source_role')
                tool=ToolResult(status='ok',data=[{'source_id':s['id'],'excerpt':s['extracted_text'],'locators':s['locator_map']} for s in chosen],source_refs=choice.source_ids)
                for s in chosen:
                    run['research_findings'].append({'id':uid(),'statement':s['extracted_text'],'source_refs':[s['id']],'provenance':'supplied_kb','retrieval_status':'ok','observed_at':now(),'uncertainty':'Supplied knowledge; no live site verification.'})
                run['research_ok']=True
            else:
                if any(s['slot']!='official_url' for s in chosen): raise ProviderError('research_source_role')
                url=chosen[0]['canonical_url']
                cap=run['capability_snapshot']
                tool=provider.research_url(url,choice.question) if run['mode']=='mock' or cap.get('url_context_enabled') else ToolResult(status='error',error_code='url_context_not_verified')
                run['research_findings'].append({'id':uid(),'statement':tool.data.get('summary','') if tool.data else 'Official URL could not be inspected.','source_refs':choice.source_ids,'provenance':'live_url' if tool.status=='ok' else 'unavailable_url','retrieval_status':tool.status,'observed_at':now(),'uncertainty':'User-supplied public URL; site ownership not independently established.' if tool.status=='ok' else tool.error_code,'retrieval_metadata':tool.data.get('retrieval_metadata',[]) if tool.data else []})
                if tool.status=='ok': run['research_ok']=True
            save();event('researcher',choice.tool,'Inspected supplied company knowledge.' if choice.tool=='inspect_company_kb' else ('Retrieved approved URL with provider metadata.' if tool.status=='ok' else 'URL unavailable; supplied knowledge or clarification is needed.'),choice.source_ids,tool.status)
            return {}
        def fit(state):
            stage('assess_fit');es=evidence()
            result=provider.call('fit',Fit,{'requirements':run['requirements'],'evidence':es,'research':run['research_findings']})
            reqids={r['id'] for r in run['requirements']};eids={e['id'] for e in es}
            if len(result.matches)!=len(reqids) or {m.requirement_id for m in result.matches}!=reqids: raise ProviderError('incomplete_fit')
            for m in result.matches:
                if not set(m.evidence_ids)<=eids or (m.status=='direct' and not m.evidence_ids) or (m.status=='missing' and m.evidence_ids): raise ProviderError('invalid_fit_evidence')
            if not set(result.relevant_evidence_ids)<=eids: raise ProviderError('invalid_selected_evidence')
            run['matches']=[m.model_dump() for m in result.matches];run['fit']=result.model_dump();save()
            event('fit_analyst','coverage',f"Mapped {len(result.matches)} requirements; {sum(m.status=='missing' for m in result.matches)} have no supporting evidence.")
            return {}
        def inspect(state):
            stage('inspect_evidence');run['inspected']=True
            missing={m['requirement_id'] for m in run['matches'] if m['status'] in ('missing','partial','unclear')}
            # Deliberate exact-source lookup for gaps; negative/context statements are never promoted.
            from .providers import terms
            sought=set(t for r in run['requirements'] if r['id'] in missing for t in terms(r['text']))
            found=[e for e in self.store.list('evidence',run['session_id']) if e['source_id'] in run['source_ids'] and sought.intersection(terms(e['exact_excerpt']))]
            event('evidence_specialist','read_evidence',f'Read {len(found)} original excerpts relevant to observed gaps. Excluded, negated or unclear material cannot establish proficiency.',list({e['source_id'] for e in found}))
            save();return {}
        def ask(state):
            stage('awaiting_input')
            if not run.get('pending_question'):
                run['clarification_count']+=1
                run['pending_question']={'id':uid(),'question':'No usable company research is available. Supply a short company knowledge excerpt and its source, or stop this run.','allowed_replies':['answer','exclude'],'kind':'company_knowledge'}
                run['version']+=1
            save()
            answer=interrupt(run['pending_question'])
            if answer.get('exclude'):
                run['status']='blocked';run['error']={'code':'research_missing','message':'Required company research was not supplied.'}
            else:
                s=self.store.get(run['session_id'],kind='session');source=add_source(self.store,s,'company',answer['answer'].encode(),'company-clarification.txt');run['source_ids'].append(source['id']);run['status']='running'
            run['pending_question']=None;save();event('user','clarification','Recorded clarification as a new immutable source.' if not answer.get('exclude') else 'Stopped because research is missing.')
            return {'next_action':'blocked' if answer.get('exclude') else 'coordinator'}
        def write(state):
            revision=state['next_action']=='revise';stage('revision' if revision else 'draft')
            if revision:
                if run['revision_count']>=1: raise ProviderError('revision_budget_exhausted')
                run['revision_count']+=1
            es=evidence();issues=self.store.get(run['evaluation_ids'][-1],run['session_id'],'evaluation')['issues'] if run['evaluation_ids'] else []
            writing=provider.call('writer',Writing,{'evidence':es,'fit':run['fit'],'requirements':run['requirements'],'research':run['research_findings'],'page_limit':run['page_limit'],'revision':revision,'issues':issues})
            draft={'version':len(run['draft_ids'])+1,'header':run['header'],'statements':writing.model_dump()['statements'],'page_limit':run['page_limit'],'edit_reason':writing.edit_reason,'created_at':now()}
            draft['statements']=ordered(draft['statements']);draft['sha256']=draft_hash(draft)
            if run['draft_ids']:
                previous=self.store.get(run['draft_ids'][-1],run['session_id'],'draft')
                newtexts={s['text'] for s in draft['statements']}
                run['dropped_claims']=[{'text':s['text'],'reason':'Removed during bounded revision after evaluation feedback.'} for s in previous['statements'] if s['text'] not in newtexts]
            for aid in run['artifact_ids']:
                a=self.store.get(aid,run['session_id'],'artifact');a['release_status']='superseded';self.store.update(aid,a)
            run['artifact_ids']=[]
            draft=self.store.add('draft',run['session_id'],draft);run['draft_ids'].append(draft['id']);save();return {}
        def render_review(state):
            stage('render_and_review');draft=self.store.get(run['draft_ids'][-1],run['session_id'],'draft')
            pdf,preview=render(draft,self.store.folder(run['session_id']));run['preview_path']=str(preview)
            pdf_check=inspect_pdf(pdf,draft);es=evidence();issues=check_statements(draft,es,sources(),run['requirements'])
            for error in pdf_check['issues']: issues.append(issue(error,'PDF failed '+error.replace('_',' ')+'.'))
            event('renderer','render_resume',f'Rendered draft {draft["version"]}; {pdf_check["page_count"]} A4 page(s).',result_ids=[draft['id']])
            semantic='failed';verdicts=[];notes=[]
            try:
                review=provider.call('reviewer',Review,{'statements':draft['statements'],'evidence':es,'original_candidate_context':[source_context(s) for s in sources() if s['role']=='candidate'],'requirements':run['requirements'],'deterministic_issues':issues,'pdf_checks':pdf_check})
                verdicts=[v.model_dump() for v in review.verdicts];notes=review.writing_notes
                if len(verdicts)!=len(draft['statements']) or {v['statement_id'] for v in verdicts}!={s['id'] for s in draft['statements']}: issues.append(issue('incomplete_semantic_review','Reviewer did not assess every statement exactly once.'))
                else:
                    semantic='passed'
                    for verdict in verdicts:
                        if verdict['status']!='supported':
                            semantic='failed';s=next(s for s in draft['statements'] if s['id']==verdict['statement_id']);issues.append(issue('semantic_support',verdict['reason'],s))
            except ProviderError as exc:
                issues.append(issue('reviewer_unavailable','Independent review failed: '+exc.code))
            passed=not issues and semantic=='passed' and pdf_check['passed']
            evaluation=self.store.add('evaluation',run['session_id'],{'draft_id':draft['id'],'draft_hash':draft['sha256'],'pdf_hash':pdf_check['sha256'],'checks':{'passed':passed,'source_rules':not any(i['category'] not in pdf_check['issues'] for i in issues),'pdf':pdf_check},'issues':issues,'coverage':coverage(run['requirements'],run['matches']),'semantic_review_status':semantic,'semantic_review_mode':'gemini' if run['mode']=='gemini' else 'offline_exact_excerpt','verdicts':verdicts,'writing_notes':notes,'evaluated_at':now()})
            run['evaluation_ids'].append(evaluation['id']);run['pdf_path']=str(pdf);save();event('reviewer','evaluation','Source and PDF checks passed.' if passed else f'{len(issues)} blocker(s) require revision or review.',status='ok' if passed else 'error',result_ids=[evaluation['id']])
            return {}
        def package(state):
            stage('release_gate');draft=self.store.get(run['draft_ids'][-1],run['session_id'],'draft');evaluation=self.store.get(run['evaluation_ids'][-1],run['session_id'],'evaluation')
            es=evidence();included={i for s in draft['statements'] for i in s['evidence_ids']}
            for m in run['matches']: m['included_in_draft']=bool(set(m['evidence_ids'])&included)
            report=build_report(run,draft,evaluation,es,sources());folder=self.store.folder(run['session_id'])
            paths={'pdf':Path(run['pdf_path']),'json':folder/(draft['id']+'.json'),'markdown':folder/(draft['id']+'.md')}
            paths['json'].write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');paths['markdown'].write_text(report_markdown(report),encoding='utf-8')
            artifacts=[]
            for kind,path in paths.items():
                artifacts.append(self.store.add('artifact',run['session_id'],{'session_id':run['session_id'],'run_id':id,'kind':kind,'path':str(path),'sha256':digest(path.read_bytes()),'draft_hash':draft['sha256'],'media_type':{'pdf':'application/pdf','json':'application/json','markdown':'text/markdown'}[kind],'size_bytes':path.stat().st_size,'release_status':'pending'}))
            run['artifact_ids']=[a['id'] for a in artifacts]
            failures=release_gate(run,draft,evaluation,artifacts,self.store)
            with self.store.lock:
                guard()
                if failures: run['status']='needs_review';run['error']={'code':'release_gate','message':', '.join(failures)}
                else:
                    for artifact in artifacts: artifact['release_status']='released';self.store.update(artifact['id'],artifact)
                    run['status']='completed'
                run['result']=report;save()
            event('release_gate','finalize','Released the checked PDF and matching reports.' if not failures else 'Release refused: '+', '.join(failures),status='ok' if not failures else 'error')
            return {}
        def stop(state):
            action=state['next_action'];stage(action);run['status']=action if action in ('needs_review','blocked') else 'blocked'
            if run['draft_ids'] and run['evaluation_ids']:
                d=self.store.get(run['draft_ids'][-1],run['session_id'],'draft');e=self.store.get(run['evaluation_ids'][-1],run['session_id'],'evaluation');run['result']=build_report(run,d,e,evidence(),sources())
            else: run['error']=run.get('error') or {'code':'prerequisites_missing','message':'Required evidence or company research is unavailable.'}
            save();return {}
        graph=StateGraph(GraphState)
        for name,node in [('parse',parse),('coordinator',coordinator),('research',research),('assess_fit',fit),('inspect_evidence',inspect),('ask_user',ask),('draft',write),('revise',write),('render_review',render_review),('finalize',package),('needs_review',stop),('blocked',stop)]: graph.add_node(name,node)
        graph.add_edge(START,'parse');graph.add_edge('parse','coordinator')
        graph.add_conditional_edges('coordinator',lambda s:s['next_action'],{a:a for a in ['research','assess_fit','inspect_evidence','ask_user','draft','revise','finalize','needs_review','blocked']})
        for node in ['research','assess_fit','inspect_evidence','render_review']: graph.add_edge(node,'coordinator')
        graph.add_conditional_edges('ask_user',lambda s:s['next_action'],{'coordinator':'coordinator','blocked':'blocked'})
        graph.add_edge('draft','render_review');graph.add_edge('revise','render_review')
        for node in ['finalize','needs_review','blocked']: graph.add_edge(node,END)
        compiled=graph.compile(checkpointer=self.checkpointer)
        try:
            guard();run['status']='running';save()
            event('system','resume' if reply else 'start','Resumed the same graph checkpoint.' if reply else f'Started an explicit {run["mode"]} run.')
            outcome=compiled.invoke(Command(resume=reply) if reply else {'run_id':id,'next_action':'parse'},config={'configurable':{'thread_id':id},'recursion_limit':45})
            if outcome.get('__interrupt__'):
                run['status']='awaiting_input';save()
        except StopRun: pass
        except Exception as exc:
            latest=self.store.get(id,run['session_id'],'run')
            if latest and latest['status'] not in ('cancelled','expired'):
                code=exc.code if isinstance(exc,ProviderError) else 'internal_error'
                run['status']='blocked' if isinstance(exc,ProviderError) else 'failed';run['error']={'code':code,'message':str(exc) if isinstance(exc,ProviderError) else 'The run failed safely. Check local diagnostics and start a new run.'}
                # Diagnostics contain exception class only, never provider response or candidate text.
                run['diagnostic_type']=type(exc).__name__
                try: save();event('system','stopped',f'Run stopped: {code}. No verified artifacts released.',status='error')
                except StopRun: pass
        finally: provider.close()
