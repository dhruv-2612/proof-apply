import io, re, zipfile, ipaddress
from pathlib import Path
from urllib.parse import urlsplit
import pymupdf
from docx import Document
from docx.table import Table
from .models import digest, now, uid
from .config import ROOT

class InputError(ValueError):
    def __init__(self, message, status=422, code='invalid_input'):
        super().__init__(message); self.status=status; self.code=code

def normalized(text): return ' '.join(text.split())
def extract(data: bytes, filename: str):
    if len(data)>5*1024*1024: raise InputError('File exceeds 5 MB. Supply a smaller file or paste text.',413,'too_large')
    suffix=Path(filename).suffix.lower()
    chunks=[]
    try:
        if suffix=='.pdf':
            with pymupdf.open(stream=data,filetype='pdf') as pdf:
                if pdf.is_encrypted: raise InputError('Encrypted PDF. Export an unlocked text PDF or paste text.')
                if len(pdf)>30: raise InputError('PDF exceeds 30 pages. Supply relevant excerpts.')
                for i,page in enumerate(pdf):
                    text=page.get_text(sort=True).strip()
                    if not text: raise InputError('Scanned or empty PDF page. OCR is not supported; paste text or upload DOCX.')
                    chunks.append({'locator':f'page {i+1}','text':text})
        elif suffix=='.docx':
            with zipfile.ZipFile(io.BytesIO(data)) as zipped:
                if sum(x.file_size for x in zipped.infolist())>30*1024*1024: raise InputError('Expanded DOCX exceeds safe size.',413,'too_large')
            doc=Document(io.BytesIO(data))
            def walk(container, prefix):
                for i,item in enumerate(container.iter_inner_content()):
                    loc=f'{prefix} {i+1}'
                    if isinstance(item,Table):
                        for ri,row in enumerate(item.rows):
                            for ci,cell in enumerate(row.cells): walk(cell, f'{loc}, row {ri+1}, cell {ci+1}, paragraph')
                    elif item.text.strip(): chunks.append({'locator':loc,'text':item.text.strip()})
            walk(doc,'paragraph')
        elif suffix in ('.txt','.md'):
            text=data.decode('utf-8-sig')
            chunks=[{'locator':f'line {i+1}','text':line.strip()} for i,line in enumerate(text.splitlines()) if line.strip()]
        else: raise InputError('Supported formats: text-based PDF, DOCX, Markdown and UTF-8 text.',415,'unsupported_type')
    except InputError: raise
    except Exception: raise InputError('This document could not be parsed. Export a valid PDF/DOCX or paste plain text.') from None
    if not chunks: raise InputError('No readable text found. Paste the document text.')
    if sum(len(x['text']) for x in chunks)>100000: raise InputError('Extracted text exceeds 100,000 characters.',413,'too_large')
    return chunks

def validate_url(value):
    try:
        p=urlsplit(value)
        if p.scheme!='https' or not p.hostname or p.username or p.password or p.port not in (None,443): raise ValueError()
        host=p.hostname.lower()
        if host=='localhost' or '.' not in host or host.endswith(('.local','.internal','.localhost')): raise ValueError()
        try:
            ip=ipaddress.ip_address(host)
            if not ip.is_global: raise ValueError()
        except ValueError:
            # IP-looking hosts are never accepted; domains are sent only to the provider URL tool.
            if re.fullmatch(r'[\d.:]+',host) or ':' in host: raise InputError('Only public HTTPS company domains are supported.')
        return value
    except (ValueError, TypeError): raise InputError('Use a public HTTPS company URL without credentials or a custom port.') from None

SLOTS={'resume':'candidate','evidence':'candidate','job':'job','company':'company','official_url':'company','style':'style'}

def add_source(store,session,slot,data,filename):
    if slot not in SLOTS: raise InputError('Unknown input slot.')
    existing=store.list('source',session['id'])
    if slot=='official_url': validate_url(data.decode().strip())
    if len([s for s in existing if s['slot'] in ('resume','evidence')])>=5 and slot in ('resume','evidence'): raise InputError('Maximum one resume and four evidence files.',413,'too_many_files')
    if slot in ('resume','job') and any(s['slot']==slot for s in existing): raise InputError('This slot is already filled. Clear the session to replace it.',409,'slot_filled')
    if slot=='official_url' and sum(s['slot']==slot for s in existing)>=3: raise InputError('Maximum three company URLs.')
    if sum(s['size_bytes'] for s in existing)+len(data)>15*1024*1024: raise InputError('Session upload limit is 15 MB.',413,'too_large')
    chunks=extract(data, filename)
    text='\n'.join(c['text'] for c in chunks)
    if sum(len(s['extracted_text']) for s in existing)+len(text)>100000: raise InputError('Session text limit is 100,000 characters.',413,'too_large')
    known={digest(p.read_bytes()) for p in (ROOT/'sample-data').glob('*.md')}
    source=store.add('source',session['id'],dict(session_id=session['id'],slot=slot,role=SLOTS[slot],kind=Path(filename).suffix.lstrip('.'),display_name=Path(filename.replace('\\','/')).name[:160],sha256=digest(data),extracted_text=text,locator_map=chunks,created_at=now(),size_bytes=len(data),synthetic=digest(data) in known,canonical_url=text if slot=='official_url' else None,retrieval_status='provided'))
    (store.folder(session['id'])/(source['id']+'.source')).write_bytes(data)
    if source['role']=='candidate': propose_evidence(store,session,source)
    session['input_version']+=1; store.update(session['id'],session)
    return source

def propose_evidence(store,session,source):
    section='Projects'
    current_entry=None
    # PDF locators cover whole pages. Filter contact/header lines individually
    # so one email address cannot discard every qualification on that page.
    segments=({'locator':chunk['locator'],'text':line,'context':chunk['text']}
              for chunk in source['locator_map'] for line in chunk['text'].splitlines() if line.strip())
    for chunk in segments:
        txt=chunk['text']
        if txt.startswith('#') or (txt.isupper() and len(txt)<55):
            heading=txt.lstrip('# ').lower()
            section=next((s for s in ('Education','Skills','Experience','Coursework') if s.lower() in heading),'Projects')
            continue
        if re.search(r'@|https?://|contact|fictional|evidence notes|unknowns',txt,re.I): continue
        if section=='Experience' and '|' in txt and len(txt)<180 and not re.match(r'^\d|^[\u2022\u2023-]',txt):
            current_entry=txt
        # Exact sentence spans, preserving original paragraph as context for negation/ownership.
        for sentence in re.split(r'(?<!\b[A-Z]\.)(?<=[.!?])\s+(?=[A-Z])|\n',txt):
            sentence=sentence.strip()
            if len(sentence)<10: continue
            suspicious=bool(re.search(r'ignore .*rules|system (prompt|instruction)|give full marks|perfect ATS score|skip verification|api.key|follow these instructions',chunk['context'],re.I))
            negative=bool(re.search(r'\b(no |not |never |does not|did not|do not|unknown|unavailable|different teammate)',sentence,re.I))
            category=section
            if 'B.Tech' in sentence or 'graduation' in sentence.lower(): category='Education'
            if 'course' in sentence.lower(): category='Coursework'
            claim=uid()
            store.add('evidence',session['id'],dict(source_id=source['id'],category=category,subject='candidate',entry_title=current_entry if category=='Experience' else None,atomic_claim=sentence,exact_excerpt=sentence,context_excerpt=chunk['context'],locator=chunk['locator'],support_status='unclear' if suspicious or negative else 'self_reported',support_basis='Exact local excerpt; candidate approval is not independent verification.',claim_id=claim,quantities=re.findall(r'\d+(?:\.\d+)?%?',sentence),created_at=now()))

def decision_map(store,sid):
    result={}
    for d in store.list('decision',sid): result[d['evidence_id']]=d
    return result

def eligible_evidence(store,sid,source_ids):
    decisions=decision_map(store,sid)
    return [e for e in store.list('evidence',sid) if e['source_id'] in source_ids and decisions.get(e['id'],{}).get('decision')=='include' and e['support_status']=='self_reported']
