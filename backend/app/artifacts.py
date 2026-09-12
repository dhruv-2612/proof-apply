"""Deterministic rendering, PDF inspection and release checks (never model agents)."""
import re, json
from pathlib import Path
import pymupdf
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .config import settings
from .models import digest, now, uid, Writing
from .extraction import normalized

ORDER=['Summary','Education','Skills','Experience','Projects','Coursework']
def draft_hash(draft):
    return digest({k:draft[k] for k in ('version','header','statements','page_limit')})
def ordered(statements): return sorted(statements,key=lambda s:ORDER.index(s['section']))
def compact(text): return re.sub(r'\s+','',text.replace('\u00ad',''))
def expected_text(draft):
    pieces=[draft['header']['name']]
    if draft['header']['contact']: pieces.append(draft['header']['contact'])
    for section in ORDER:
        group=[s for s in draft['statements'] if s['section']==section]
        if group: pieces.extend([section.upper(),*[s['text'] for s in group]])
    return '\n'.join(pieces)

def render(draft,folder):
    from weasyprint import HTML
    environment=Environment(loader=FileSystemLoader(Path(__file__).parent/'templates'),autoescape=select_autoescape(['html']))
    html=environment.get_template('resume.html').render(header=draft['header'],sections=[{'title':section,'statements':[s for s in draft['statements'] if s['section']==section]} for section in ORDER])
    def blocked_fetcher(url,*args,**kwargs): raise ValueError('External/local resource loading is disabled.')
    pdf=folder/(draft['id']+'.pdf')
    HTML(string=html,url_fetcher=blocked_fetcher).write_pdf(pdf)
    preview=folder/(draft['id']+'.png')
    with pymupdf.open(pdf) as document: document[0].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(preview)
    return pdf,preview

def inspect_pdf(path,draft):
    issues=[]
    try:
        with pymupdf.open(path) as pdf:
            if len(pdf)>draft['page_limit'] or len(pdf)<1: issues.append('page_limit')
            text='\n'.join(page.get_text(sort=False) for page in pdf)
            if not text.strip(): issues.append('empty_pdf')
            if compact(text)!=compact(expected_text(draft)): issues.append('pdf_content_mismatch')
            for page in pdf:
                if abs(page.rect.width-595.276)>2 or abs(page.rect.height-841.89)>2: issues.append('not_a4')
                for word in page.get_text('words'):
                    if word[0]<34 or word[1]<34 or word[2]>page.rect.width-34 or word[3]>page.rect.height-34: issues.append('text_outside_safe_bounds')
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines',[]):
                        for span in line['spans']:
                            if span['text'].strip() and span['size']<10.49: issues.append('tiny_text')
            return {'passed':not issues,'issues':sorted(set(issues)),'page_count':len(pdf),'selectable_text':bool(text.strip()),'sha256':digest(path.read_bytes())}
    except Exception: return {'passed':False,'issues':['invalid_pdf'],'page_count':0,'selectable_text':False,'sha256':None}

def check_statements(draft,evidence,sources,requirements):
    issues=[];emap={e['id']:e for e in evidence};smap={s['id']:s for s in sources};rids={r['id'] for r in requirements}
    # Conflicting exact values for the same explicitly named fact remain blockers.
    anchored_values={}
    for e in evidence:
        for match in re.finditer(r'(\d+)\s+(Vitest unit tests|unit tests)',e['exact_excerpt'],re.I):
            anchor=match.group(2).lower()
            anchored_values.setdefault(anchor,set()).add(match.group(1))
    if any(len(values)>1 for values in anchored_values.values()):
        issues.append(issue('conflicting_values','Included sources give conflicting quantities for the same test-count fact. Exclude or clarify the conflicting source.'))
    project_periods=set()
    for e in evidence:
        if 'Campus Room Booker' in e['context_excerpt']:
            years=tuple(re.findall(r'\b20\d{2}\b',e['context_excerpt']))
            if years: project_periods.add(years)
    if len(project_periods)>1:
        issues.append(issue('conflicting_dates','Included evidence gives conflicting dates for Campus Room Booker. Resolve or exclude the conflict.'))
    ids=[s['id'] for s in draft['statements']]
    if len(ids)!=len(set(ids)): issues.append(issue('duplicate_statement_ids','Duplicate statement identifiers.'))
    for s in draft['statements']:
        cited=[emap.get(id) for id in s['evidence_ids']]
        if not cited or any(e is None for e in cited):
            issues.append(issue('invalid_evidence','Claim cites missing/excluded evidence.',s));continue
        if set(s['claim_ids'])!={e['claim_id'] for e in cited}: issues.append(issue('claim_id_mismatch','Claim IDs must match cited evidence exactly.',s))
        if not set(s['requirement_ids'])<=rids: issues.append(issue('invalid_requirement','Unknown requirement relation.',s))
        for e in cited:
            source=smap.get(e['source_id'])
            if not source or source['role']!='candidate': issues.append(issue('source_role','Only candidate sources may support claims.',s));continue
            chunks={c['locator']:c['text'] for c in source['locator_map']}
            if normalized(e['exact_excerpt']) not in normalized(chunks.get(e['locator'],'')): issues.append(issue('invalid_excerpt','Evidence excerpt/locator does not match original source.',s))
        excerpts=' '.join(e['exact_excerpt'] for e in cited)
        numbers=set(re.findall(r'\d+(?:\.\d+)?%?',s['text']))
        if not numbers<=set(re.findall(r'\d+(?:\.\d+)?%?',excerpts)): issues.append(issue('exact_quantity','A number, date or percentage is absent from its cited excerpt.',s))
        # Conservative high-risk expansions also fail in deterministic code. Reviewer checks other semantics.
        for pattern in (r'\bled\b',r'\bteam leader\b',r'\bexpert\b',r'\bcertified\b',r'\bcertification\b',r'\bproduction users\b'):
            if re.search(pattern,s['text'],re.I) and not any(re.search(pattern,e['exact_excerpt'],re.I) and not re.search(r'\bnot\b|\bno\b|never',e['context_excerpt'],re.I) for e in cited):
                issues.append(issue('unsupported_expansion','Ownership, seniority, credential or outcome is not established by the cited excerpt.',s))
    return issues

def issue(category,explanation,statement=None):
    return dict(id=uid(),category=category,severity='blocker',statement_ids=[statement['id']] if statement else [],evidence_ids=statement['evidence_ids'] if statement else [],explanation=explanation,suggested_action='Remove or correct using eligible original evidence, then rerender and recheck.')

def coverage(requirements,matches):
    weights={r['id']:2 if r['importance']=='required' else 1 for r in requirements}
    denominator=sum(weights.values())
    numerator=sum(weights.get(m['requirement_id'],0)*{'direct':1,'partial':.5,'missing':0,'unclear':0}[m['status']] for m in matches)
    return {'numerator':numerator,'denominator':denominator,'percent':100*numerator/denominator if denominator else None,'meaning':'Documented source coverage; not hiring likelihood or a commercial ATS score.'}

def build_report(run,draft,evaluation,evidence,sources):
    emap={e['id']:e for e in evidence};included={id for s in draft['statements'] for id in s['evidence_ids']}
    claims=[dict(statement_id=s['id'],text=s['text'],section=s['section'],evidence=[{k:emap[id][k] for k in ('id','source_id','exact_excerpt','locator','support_status')} for id in s['evidence_ids'] if id in emap]) for s in draft['statements']]
    base_ids={s['id'] for s in sources if s['slot']=='resume'}
    changes=[{'before':' | '.join(emap[id]['exact_excerpt'] for id in s['evidence_ids'] if id in emap),'after':s['text'],'reason':'Retained/reordered exact evidence' if any(s['text']==emap[id]['exact_excerpt'] for id in s['evidence_ids'] if id in emap) else 'Supported paraphrase for role relevance','evidence_ids':s['evidence_ids']} for s in draft['statements']]
    omissions=[{'text':e['exact_excerpt'],'evidence_id':e['id'],'reason':'Omitted from final selection; original source remains unchanged.'} for e in evidence if e['source_id'] in base_ids and e['id'] not in included]
    return {'run_id':run['id'],'mode':run['mode'],'target':{'role':run['role_title'],'company':run['company_name']},'draft_id':draft['id'],'draft_hash':draft['sha256'],'pdf_hash':evaluation['pdf_hash'],'generated_at':now(),'revision_count':run['revision_count'],'model_attempts':run['model_attempts'],'mock_calls':run.get('mock_calls',0),'research':run['research_findings'],'sources':[{'id':s['id'],'display_name':s['display_name'],'role':s['role'],'sha256':s['sha256'],'retrieval_status':s['retrieval_status']} for s in sources],'claims':claims,'requirements':run['requirements'],'matches':run['matches'],'coverage':coverage(run['requirements'],run['matches']),'changes':changes,'base_omissions':omissions,'draft_versions':run['draft_ids'],'dropped_claims':run.get('dropped_claims',[]),'evaluations':evaluation,'uncertainty':['Source support is not independent verification of self-reported experience.','Same-model semantic review may share writer errors.'] if run['mode']=='gemini' else ['Explicit offline run. Extractive rules only; no live semantic assessment.','Source support is not independent verification.']}

def report_markdown(report):
    lines=['# ProofApply evidence and change report',f"Mode: **{report['mode']}**",f"Target: {report['target']['role']} at {report['target']['company']}",f"Draft hash: `{report['draft_hash']}`",f"PDF hash: `{report['pdf_hash']}`",f"Revisions: {report['revision_count']} ? Model attempts: {report['model_attempts']}",'## Research']
    for finding in report['research']: lines.append(f"- {finding['provenance']}: {finding['statement']} (status: {finding['retrieval_status']})")
    lines+=['## Requirements and gaps']
    reqs={r['id']:r for r in report['requirements']}
    for match in report['matches']: lines.append(f"- {reqs[match['requirement_id']]['text']}: **{match['status']}** ? {match['explanation']}")
    lines+=['## Final claims and original evidence']
    for claim in report['claims']:
        lines.append(f"\n### {claim['text']}")
        for e in claim['evidence']: lines.append(f"- Source `{e['source_id']}`, {e['locator']}; evidence `{e['id']}` ({e['support_status']})\n\n> {e['exact_excerpt']}")
    lines+=['## Changes']
    for change in report['changes']: lines.append(f"- Before: {change['before']}\n  After: {change['after']}\n  Reason: {change['reason']}")
    lines+=['## Base resume omissions']+[f"- {o['text']} ? {o['reason']}" for o in report['base_omissions']]
    lines+=['## Dropped draft claims']+[f"- {o['text']} ? {o['reason']}" for o in report['dropped_claims']]
    lines+=['## Checks',json.dumps(report['evaluations']['checks'],indent=2),'## Limits']+['- '+u for u in report['uncertainty']]
    return '\n\n'.join(lines)

def release_gate(run,draft,evaluation,artifacts,store):
    errors=[]
    if run['status'] in ('cancelled','expired') or not store.get(run['session_id']): errors.append('inactive_session_or_run')
    if not run.get('research_ok') or not run.get('matches'): errors.append('prerequisites_missing')
    if run['revision_count']>1 or run['model_attempts']>18: errors.append('budget_exceeded')
    current=draft_hash(draft)
    if draft['sha256']!=current or evaluation['draft_hash']!=current or evaluation['draft_id']!=draft['id']: errors.append('draft_hash_mismatch')
    if not evaluation['checks'].get('passed') or evaluation['semantic_review_status']!='passed' or any(i['severity']=='blocker' for i in evaluation['issues']): errors.append('evaluation_blocked')
    required={'pdf','json','markdown'}
    if {a['kind'] for a in artifacts}!=required: errors.append('artifact_set_incomplete')
    for a in artifacts:
        path=Path(a['path'])
        if not path.is_file() or digest(path.read_bytes())!=a['sha256'] or a['draft_hash']!=current: errors.append('artifact_hash_mismatch');continue
        if a['kind']=='pdf':
            if a['sha256']!=evaluation['pdf_hash'] or not inspect_pdf(path,draft)['passed']: errors.append('pdf_not_current')
        if a['kind']=='json':
            report=json.loads(path.read_text(encoding='utf-8'))
            if report['draft_hash']!=current or report['pdf_hash']!=evaluation['pdf_hash']: errors.append('report_mismatch')
    return sorted(set(errors))
