import io
import pytest
from app.extraction import extract, InputError, validate_url
from app.models import digest
from app.config import ROOT
from docx import Document
import pymupdf

def test_fixture_excerpts_are_traceable(client):
    client.post('/api/sessions',json={'demo':True})
    assert client.post('/api/demo',json={'scenario':'frontend'}).status_code==201
    data=client.get('/api/evidence').json()
    sources={s['id']:s for s in data['sources']}
    for e in data['evidence']:
        assert e['exact_excerpt'] in sources[e['source_id']]['extracted_text']
        assert e['locator'] in [c['locator'] for c in sources[e['source_id']]['locator_map']]
    assert all(s['role']=='candidate' for s in sources.values() if s['slot'] in ('resume','evidence'))
    assert any('18 Vitest' in e['exact_excerpt'] for e in data['evidence'])

def test_docx_and_pdf_variants():
    text='Fictional candidate wrote 18 unit tests.'
    doc=Document();doc.add_paragraph(text);out=io.BytesIO();doc.save(out)
    assert extract(out.getvalue(),'fixture.docx')[0]['text']==text
    pdf=pymupdf.open();page=pdf.new_page();page.insert_text((50,50),text)
    assert extract(pdf.tobytes(),'fixture.pdf')[0]['text']==text
    pdf.close()

@pytest.mark.parametrize('filename,data,status',[('bad.pdf',b'broken',422),('bad.docx',b'bad',422),('image.png',b'PNG',415),('large.txt',b'a'*(5*1024*1024+1),413)],ids=['malformed_pdf','malformed_docx','unsupported_type','oversize'])
def test_bad_documents(filename,data,status):
    with pytest.raises(InputError) as error: extract(data,filename)
    assert error.value.status==status

def test_scanned_and_encrypted_pdf():
    pdf=pymupdf.open();pdf.new_page()
    with pytest.raises(InputError,match='Scanned'): extract(pdf.tobytes(),'scanned.pdf')
    locked=pdf.tobytes(encryption=pymupdf.PDF_ENCRYPT_AES_256,user_pw='secret',owner_pw='owner')
    with pytest.raises(InputError,match='Encrypted'): extract(locked,'locked.pdf')

@pytest.mark.parametrize('url',['http://company.com','https://localhost/a','https://127.0.0.1','https://10.0.0.1','https://[::1]','https://user:pass@company.com','https://company.com:8080'])
def test_private_urls_rejected(url):
    with pytest.raises(InputError): validate_url(url)

def test_cross_session_evidence_and_strict_body(client):
    assert client.post('/api/sessions',json={'demo':True,'admin':True}).status_code==422
    client.post('/api/sessions',json={'demo':True});client.post('/api/demo',json={'scenario':'frontend'})
    first=client.get('/api/evidence').json()['evidence'][0]
    client.cookies.clear();client.post('/api/sessions',json={'demo':False})
    assert client.post('/api/evidence/decisions',json={'evidence_id':first['id'],'decision':'exclude'}).status_code==404

def test_sources_are_immutable(client):
    client.post('/api/sessions',json={'demo':True});client.post('/api/demo',json={'scenario':'frontend'})
    data=client.get('/api/evidence').json();e=data['evidence'][0]
    original=data['sources'][0]
    assert client.post('/api/evidence/decisions',json={'evidence_id':e['id'],'decision':'exclude'}).status_code==200
    assert client.get('/api/evidence').json()['sources'][0]==original
    with pytest.raises(ValueError): client.app.state.store.update(original['id'],{'text':'changed'})
