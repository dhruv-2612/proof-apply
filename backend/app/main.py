from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import secrets, time
from fastapi import FastAPI, Request, Response, UploadFile, File, Form, Header as HttpHeader
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from .config import ROOT, settings
from .models import *
from .storage import Store
from .extraction import *

TERMINAL={'completed','needs_review','blocked','failed','cancelled','expired'}
class ApiError(Exception):
    def __init__(self,status,code,message,retryable=False): self.status=status;self.code=code;self.message=message;self.retryable=retryable

def create_app(config=settings, directory=None, provider_factory=None):
    store=Store(directory or config.data_dir)
    from .jobs import Jobs
    jobs=Jobs(store,config,provider_factory)
    @asynccontextmanager
    async def lifespan(app):
        import asyncio
        # Restarted worker tasks are not durable. Human pauses retain their SQLite checkpoint.
        for r in store.list('run'):
            if r['status'] in ('queued','running'):
                r.update(status='blocked',error={'code':'server_restarted','message':'Server restarted during generation. Start a new run.'});store.update(r['id'],r)
        async def cleanup_loop():
            while True:
                await asyncio.sleep(30)
                cleanup()
        task=asyncio.create_task(cleanup_loop())
        yield
        task.cancel();jobs.shutdown();store.engine.dispose()
    app=FastAPI(title='ProofApply',version='0.1.0',lifespan=lifespan)
    app.state.store=store;app.state.jobs=jobs
    def cleanup():
        for s in store.list('session'):
            if datetime.fromisoformat(s['expires_at'])<=datetime.now(timezone.utc): jobs.expire(s['id']);store.delete_session(s['id'])
    def session(request):
        cleanup()
        s=store.get(request.cookies.get('proofapply_session',''),kind='session')
        if not s: raise ApiError(410,'session_expired','Session missing or expired. Start a new temporary session.')
        return s
    def owned_run(request,id):
        s=session(request);r=store.get(id,s['id'],'run')
        if not r: raise ApiError(404,'not_found','Run not found in this session.')
        return r
    def editable(s):
        if any(r['status'] not in TERMINAL for r in store.list('run',s['id'])): raise ApiError(409,'input_locked','Finish or cancel the active run before changing evidence.')
    def key(value):
        if not value or not 8<=len(value)<=128: raise ApiError(422,'idempotency_key_required','Supply an Idempotency-Key of 8?128 characters.')
    @app.middleware('http')
    async def boundaries(request,call_next):
        if request.method not in ('GET','HEAD','OPTIONS'):
            origin=request.headers.get('origin')
            from urllib.parse import urlsplit
            origin_parts=urlsplit(origin) if origin else None
            if origin_parts and (origin_parts.netloc!=request.url.netloc or origin_parts.scheme not in (('https',) if config.app_env=='production' else ('http','https'))):
                return JSONResponse({'error':{'code':'origin_rejected','message':'Cross-origin writes are not allowed.','retryable':False}},403)
            try:
                if int(request.headers.get('content-length','0'))>16*1024*1024: return JSONResponse({'error':{'code':'too_large','message':'Request exceeds 16 MB.','retryable':False}},413)
            except ValueError: return JSONResponse({'error':{'code':'invalid_length','message':'Invalid content length.','retryable':False}},400)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='same-origin'
        response.headers['X-Frame-Options']='SAMEORIGIN'
        if request.url.path.startswith('/api'): response.headers['Cache-Control']='no-store'
        return response
    @app.exception_handler(ApiError)
    async def api_error(request,exc):
        return JSONResponse({'error':{'code':exc.code,'message':exc.message,'retryable':exc.retryable}},exc.status)
    @app.exception_handler(InputError)
    async def input_error(request,exc): return JSONResponse({'error':{'code':exc.code,'message':str(exc),'retryable':False}},exc.status)
    @app.exception_handler(RequestValidationError)
    async def validation_error(request,exc):
        # Never reflect raw input (it may contain contacts/access code).
        errors=[{'field':'.'.join(map(str,e['loc'])),'message':e['msg']} for e in exc.errors()]
        return JSONResponse({'error':{'code':'validation','message':'Check the highlighted fields.','retryable':False,'fields':errors}},422)
    @app.get('/api/health')
    def health(): return {'status':'ok'}
    @app.get('/api/capabilities')
    def capabilities():
        return {'mode':config.llm_mode,'model':config.gemini_model or None,'live_processing_enabled':bool(config.live_ready()),'research_options':['provided_kb'],'temporary_storage':True,'synthetic_only_live':False,'prompt_version':'v1; writer/reviewer v2','sdk_version':__import__('importlib.metadata',fromlist=['version']).version('google-genai'),'url_context_enabled':config.feature_ready('url_context'),'limitations':['Stitch desktop references adapted; mobile layout uses the same design system.','Muse branch: live processing accepts user-supplied documents at the user request; header contact fields stay local.']}
    @app.post('/api/sessions',status_code=201)
    def create_session(body:SessionInput,request:Request,response:Response):
        cleanup()
        existing=store.get(request.cookies.get('proofapply_session',''),kind='session')
        if existing: return {k:existing[k] for k in ('id','expires_at','demo','input_version')}
        if len(store.list('session'))>=30: raise ApiError(429,'session_limit','Server session limit reached; retry after expiry.',True)
        id=uid();s=store.add('session',id,{'created_at':now(),'expires_at':(datetime.now(timezone.utc)+timedelta(minutes=config.session_ttl_minutes)).isoformat(),'demo':body.demo,'input_version':0,'ingestion_model_attempts':0},id)
        response.set_cookie('proofapply_session',id,httponly=True,samesite='strict',secure=config.app_env=='production',max_age=config.session_ttl_minutes*60)
        return {k:s[k] for k in ('id','expires_at','demo','input_version')}
    @app.post('/api/sources',status_code=201)
    async def source(request:Request,slot:str=Form(...),text:str|None=Form(None),file:UploadFile|None=File(None)):
        import asyncio
        s=session(request);editable(s)
        if (file is None)==(text is None): raise ApiError(422,'one_input_required','Supply exactly one file or text value.')
        data=await file.read(5*1024*1024+1) if file else text.encode()
        filename=file.filename if file else slot+'.txt'
        def ingest():
            with store.lock:
                current=store.get(s['id'],kind='session');editable(current)
                return add_source(store,current,slot,data,filename or 'input.txt')
        created=await asyncio.to_thread(ingest)
        return {'source_id':created['id'],'display_name':created['display_name'],'parse_status':'ready','role':created['role']}
    @app.delete('/api/sources/{id}')
    def delete_source(id:str,request:Request):
        with store.lock:
            s=session(request);editable(s)
            source=store.get(id,s['id'],'source')
            if not source: raise ApiError(404,'not_found','Source not found in this session.')
            for e in store.list('evidence',s['id']):
                if e['source_id']==id: store.delete(e['id'])
            for d in store.list('decision',s['id']):
                if store.get(d['evidence_id'],s['id'],'evidence') is None: store.delete(d['id'])
            store.delete(id)
            try: (store.folder(s['id'])/(id+'.source')).unlink(missing_ok=True)
            except OSError: pass
            s['input_version']+=1;store.update(s['id'],s)
            return {'deleted':True}
    @app.post('/api/demo',status_code=201)
    def demo(body:DemoInput,request:Request):
        s=session(request);editable(s)
        if store.list('source',s['id']): raise ApiError(409,'not_empty','Clear this session before loading the fictional fixture.')
        s['demo']=True;store.update(s['id'],s)
        for slot,name in [('resume','candidate-base.md'),('evidence','project-evidence.md'),('evidence','course-evidence.md'),('job','job-'+body.scenario+'.md'),('company','company-knowledge.md')]:
            add_source(store,s,slot,(ROOT/'sample-data'/name).read_bytes(),name)
        return {'header':{'name':'Mira Rao','contact':'mira@example.com'},'role_title':'Junior Frontend Developer' if body.scenario=='frontend' else 'Junior Platform Engineer','company_name':'CedarWorks Labs','source_ids':[x['id'] for x in store.list('source',s['id'])]}
    @app.get('/api/evidence')
    def evidence(request:Request):
        s=session(request)
        return {'session':{k:s[k] for k in ('id','demo','expires_at','input_version')},'sources':store.list('source',s['id']),'evidence':store.list('evidence',s['id']),'decisions':list(decision_map(store,s['id']).values())}
    @app.post('/api/evidence/decisions')
    def decide(body:EvidenceDecision,request:Request):
        with store.lock:
            s=session(request);editable(s);e=store.get(body.evidence_id,s['id'],'evidence')
            if not e: raise ApiError(404,'not_found','Evidence not found.')
            if body.decision=='include' and e['support_status']!='self_reported': raise ApiError(422,'unclear_evidence','Unclear/context evidence must be excluded or clarified with a new statement.')
            new_source=None
            if body.decision=='clarify':
                if not body.clarification_text: raise ApiError(422,'clarification_required','Write the specific corrected fact; the original excerpt will remain unchanged.')
                new_source=add_source(store,s,'evidence',body.clarification_text.encode(),'clarification.txt')['id']
            record=store.add('decision',s['id'],{**body.model_dump(exclude={'clarification_text'}),'new_source_id':new_source,'created_at':now()})
            s['input_version']+=1;store.update(s['id'],s)
            return record
    @app.post('/api/evidence/enhance')
    def enhance(request:Request):
        from .live_ingest import gemini_ingest
        from .providers import ProviderError
        if not config.live_ready(): raise ApiError(503,'live_unavailable','Live enhancement requires confirmed free-tier access and a passing capability probe.')
        with store.lock:
            s=session(request);editable(s)
            candidates=[x for x in store.list('source',s['id']) if x['role']=='candidate']
            if not candidates: raise ApiError(422,'no_evidence','Upload a resume first.')
            report=[]
            for source in candidates:
                chunks=[{'locator':c['locator'],'text':c['text']} for c in source['locator_map']]
                if sum(len(c['text']) for c in chunks)>80000:
                    report.append({'source_id':source['id'],'status':'static_kept','warning':'Source too large for a bounded enhancement call.'});continue
                try:
                    proposal=gemini_ingest(store,s,config,'extract',EvidenceProposal,{'chunks':chunks})
                except ProviderError as exc:
                    report.append({'source_id':source['id'],'status':'static_kept','warning':'Enhancement unavailable ('+exc.code+'); static excerpts kept.'});continue
                for e in store.list('evidence',s['id']):
                    if e['source_id']==source['id']: store.delete(e['id'])
                for d in store.list('decision',s['id']):
                    if store.get(d['evidence_id'],s['id'],'evidence') is None: store.delete(d['id'])
                accepted,dropped=apply_proposal(store,s,source,proposal.items)
                blob=normalized(' '.join(e['exact_excerpt'] for e in store.list('evidence',s['id']) if e['source_id']==source['id']))
                propose_evidence(store,s,source,skip_covered=blob)
                total=len([e for e in store.list('evidence',s['id']) if e['source_id']==source['id']])
                report.append({'source_id':source['id'],'status':'enhanced','accepted':accepted,'dropped_nonverbatim':dropped,'evidence':total})
            s['input_version']+=1;store.update(s['id'],s)
            return {'report':report,'input_version':s['input_version'],'notice':'Evidence was re-extracted. Review every excerpt again before building.'}
    @app.post('/api/sources/{id}/detect-target')
    def detect_target(id:str,request:Request):
        from .live_ingest import gemini_ingest
        from .providers import ProviderError
        if not config.live_ready(): raise ApiError(503,'live_unavailable','Live detection requires confirmed free-tier access and a passing capability probe.')
        with store.lock:
            s=session(request)
            source=store.get(id,s['id'],'source')
            if not source or source['role']!='job': raise ApiError(404,'not_found','Job description not found in this session.')
            try:
                found=gemini_ingest(store,s,config,'detect-target',TargetDetect,{'text':source['extracted_text'][:20000]})
            except ProviderError:
                raise ApiError(503,'detect_failed','Automatic detection is unavailable right now. Enter the role and company manually.',True)
            return {'source_id':id,'role_title':found.role_title,'company_name':found.company_name}
    @app.post('/api/sources/{id}/detect-header')
    def detect_header(id:str,request:Request):
        # Script-only header detection: no model call, so contact details never
        # leave the server for this. Name is the first name-like line; contact
        # is the email and/or long digit string found near the top of the file.
        s=session(request)
        source=store.get(id,s['id'],'source')
        if not source or source['role']!='candidate': raise ApiError(404,'not_found','Candidate source not found in this session.')
        import re
        lines=[line.strip() for chunk in source['locator_map'] for line in chunk['text'].splitlines() if line.strip()]
        labels={'summary','objective','profile','education','skills','experience','coursework','projects','project','work experience','employment'}
        name=''
        for line in lines[:6]:
            words=line.split()
            if len(line)>60 or len(words)>5 or len(words)<1: continue
            if '@' in line or 'http' in line or '|' in line: continue
            if re.search(r'\d|,|;',line): continue
            if line.lstrip('# ').strip().lower() in labels: continue
            name=line.lstrip('# ').strip()
            break
        head='\n'.join(lines[:12])
        email=re.search(r'[\w.+-]+@[\w-]+\.[\w.]+',head)
        phone=''
        for match in re.finditer(r'\+?[\d][\d\s().-]{6,}[\d]',head):
            if len(re.sub(r'\D','',match.group(0)))>=10:
                phone=match.group(0).strip()
                break
        contact=' | '.join(part for part in (email.group(0) if email else '',phone) if part)
        return {'source_id':id,'name':name,'contact':contact[:240]}
    @app.post('/api/runs',status_code=202)
    def start(body:RunInput,request:Request,idempotency_key:str|None=HttpHeader(None)):
        key(idempotency_key)
        with store.lock:
            s=session(request);payload_hash=digest(body.model_dump(exclude={'demo_access_code'}))
            existing=next((r for r in store.list('run',s['id']) if r['idempotency_key']==idempotency_key),None)
            if existing:
                if existing['request_hash']!=payload_hash: raise ApiError(409,'idempotency_conflict','This key was already used for different input.')
                return public_run(existing)
            if jobs.busy: raise ApiError(409,'server_busy','One run is already executing. Retry shortly.',True)
            editable(s)
            if body.expected_input_version!=s['input_version']: raise ApiError(409,'version_mismatch','Evidence changed. Refresh and review it before building.')
            if len(set(body.source_ids))!=len(body.source_ids): raise ApiError(422,'duplicate_sources','Source IDs must be unique.')
            sources=[store.get(id,s['id'],'source') for id in body.source_ids]
            if any(x is None for x in sources): raise ApiError(404,'not_found','Source not found in this session.')
            if not any(x['slot']=='resume' for x in sources) or sum(x['slot']=='job' for x in sources)!=1: raise ApiError(422,'missing_input','A base resume and one job description are required.')
            decisions=decision_map(store,s['id'])
            evidence=[e for e in store.list('evidence',s['id']) if e['source_id'] in body.source_ids]
            if any(e['id'] not in decisions for e in evidence): raise ApiError(422,'review_required','Review each evidence item before building.')
            if not eligible_evidence(store,s['id'],body.source_ids): raise ApiError(422,'no_evidence','Include at least one supported candidate excerpt.')
            if len(store.list('run',s['id']))>=6: raise ApiError(429,'run_limit','Maximum six runs per temporary session.')
            if body.mode=='gemini':
                if not config.live_ready(): raise ApiError(503,'live_unavailable','Live generation requires confirmed free-tier access and a passing capability probe.')
                # Muse branch: the user explicitly requested live Gemini processing of
                # their own supplied documents. Header name/contact fields are still
                # stripped from every model request; resume body text is sent at the
                # user's request and consumes their free-tier quota (no paid fallback).
                if config.app_env=='production' and not config.public_live_runs and (not config.demo_access_code or not secrets.compare_digest(body.demo_access_code,config.demo_access_code)): raise ApiError(403,'demo_access_required','The team demonstration access code is required for hosted live runs.')
                recent=[r for r in store.list('run') if r['mode']=='gemini' and (datetime.now(timezone.utc)-datetime.fromisoformat(r['created_at'])).total_seconds()<3600]
                if len(recent)>=12: raise ApiError(429,'live_hourly_limit','Hourly live demonstration limit reached.',True)
            run=store.add('run',s['id'],{**body.model_dump(exclude={'demo_access_code','expected_input_version'}),'session_id':s['id'],'input_version':s['input_version'],'idempotency_key':idempotency_key,'request_hash':payload_hash,'status':'queued','graph_stage':'queued','version':1,'created_at':now(),'updated_at':now(),'model_attempts':0,'mock_calls':0,'research_calls':0,'revision_count':0,'clarification_count':0,'transitions':0,'requirements':[],'matches':[],'research_findings':[],'research_ok':False,'inspected':False,'draft_ids':[],'evaluation_ids':[],'artifact_ids':[],'pending_question':None,'error':None,'capability_snapshot':{**capabilities(),'mode':body.mode},'execution_elapsed_seconds':0})
            jobs.submit(run['id']);return public_run(run)
    @app.get('/api/runs/{id}')
    def run_status(id:str,request:Request): return public_run(owned_run(request,id))
    @app.get('/api/runs/{id}/events')
    def events(id:str,request:Request,after:int=0):
        r=owned_run(request,id);items=sorted([e for e in store.list('event',r['session_id']) if e['run_id']==id and e['seq']>after],key=lambda x:x['seq'])
        return {'events':items,'next_cursor':items[-1]['seq'] if items else after}
    @app.post('/api/runs/{id}/resume',status_code=202)
    def resume(id:str,body:ResumeInput,request:Request,idempotency_key:str|None=HttpHeader(None)):
        key(idempotency_key)
        with store.lock:
            r=owned_run(request,id)
            previous=next((a for a in store.list('reply',r['session_id']) if a['run_id']==id and a['key']==idempotency_key),None)
            if previous:
                if previous['hash']!=digest(body.model_dump()): raise ApiError(409,'idempotency_conflict','Reply key already used for another answer.')
                return public_run(r)
            if r['status']!='awaiting_input' or r['version']!=body.expected_version or not r['pending_question'] or r['pending_question']['id']!=body.question_id: raise ApiError(409,'version_mismatch','This clarification is no longer current.')
            if jobs.busy: raise ApiError(409,'server_busy','Another run is active. Retry shortly.',True)
            if not body.exclude and not body.answer.strip(): raise ApiError(422,'answer_required','Supply a company knowledge statement or choose stop.')
            # Muse branch: clarification answers are accepted in gemini mode too, since
            # live processing of user-supplied documents was explicitly requested.
            store.add('reply',r['session_id'],{'run_id':id,'key':idempotency_key,'hash':digest(body.model_dump())})
            r['version']+=1;r['status']='queued';store.update(id,r);jobs.submit(id,body.model_dump());return public_run(r)
    @app.post('/api/runs/{id}/cancel',status_code=202)
    def cancel(id:str,body:CancelInput,request:Request):
        with store.lock:
            r=owned_run(request,id)
            if r['status']=='cancelled': return public_run(r)
            if r['version']!=body.expected_version or r['status'] in TERMINAL: raise ApiError(409,'version_mismatch','Run has already changed or finished.')
            r['status']='cancelled';r['version']+=1;r['updated_at']=now();store.update(id,r)
            store.event(r,'user','cancel','Cancelled; no further artifacts may be released.')
            return public_run(r)
    @app.get('/api/runs/{id}/result')
    def result(id:str,request:Request):
        r=owned_run(request,id)
        result=r.get('result')
        if not result: return {'status':r['status'],'issues':[],'artifacts':[]}
        # Never expose internal filesystem paths.
        return {**result,'status':r['status'],'artifacts':[{'id':a['id'],'kind':a['kind'],'href':'/api/artifacts/'+a['id']} for a in [store.get(a,r['session_id'],'artifact') for a in r['artifact_ids']] if a and a['release_status']=='released' and r['status']=='completed'],'preview_url':'/api/runs/'+id+'/preview' if r.get('preview_path') else None}
    @app.get('/api/runs/{id}/preview')
    def preview(id:str,request:Request):
        r=owned_run(request,id)
        path=r.get('preview_path')
        if not path or not Path(path).is_file(): raise ApiError(404,'not_found','Preview is not available yet.')
        return FileResponse(path,media_type='image/png')
    @app.get('/api/artifacts/{id}')
    def artifact(id:str,request:Request):
        s=session(request);a=store.get(id,s['id'],'artifact')
        if not a: raise ApiError(404,'not_found','Artifact not found.')
        r=store.get(a['run_id'],s['id'],'run')
        if not r or r['status']!='completed' or a['release_status']!='released': raise ApiError(409,'not_released','Verified downloads are disabled until every final check passes.')
        from .artifacts import release_gate
        draft=store.get(r['draft_ids'][-1],s['id'],'draft');evaluation=store.get(r['evaluation_ids'][-1],s['id'],'evaluation')
        artifacts=[store.get(aid,s['id'],'artifact') for aid in r['artifact_ids']]
        if release_gate(r,draft,evaluation,artifacts,store): raise ApiError(409,'integrity_failed','Artifact integrity check failed. Start a new checked run.')
        ext={'pdf':'pdf','json':'json','markdown':'md'}[a['kind']]
        return FileResponse(a['path'],media_type=a['media_type'],filename='ProofApply-'+a['kind']+'.'+ext)
    @app.delete('/api/sessions/current')
    def clear(request:Request,response:Response):
        s=session(request);jobs.expire(s['id']);store.delete_session(s['id']);response.delete_cookie('proofapply_session');return {'cleared':True}
    if (ROOT/'frontend/out').exists(): app.mount('/',StaticFiles(directory=ROOT/'frontend/out',html=True),name='frontend')
    return app

def public_run(r):
    return {k:r.get(k) for k in ('id','status','graph_stage','mode','version','pending_question','error','created_at','updated_at','model_attempts','mock_calls','revision_count','research_calls','clarification_count','execution_elapsed_seconds','capability_snapshot','role_title','company_name','header')}

app=create_app()
