"""No key output. List is metadata-only; probes require explicit free-tier attestation."""
import argparse, json, sys, importlib.metadata
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.config import settings, ROOT
from app.models import Requirements, now
from app.providers import gemini_schema
from google import genai
from google.genai import types
p=argparse.ArgumentParser();p.add_argument('--list',action='store_true');p.add_argument('--model');p.add_argument('--confirm-free-tier',action='store_true');args=p.parse_args()
client=genai.Client(api_key=settings.gemini_api_key,http_options=types.HttpOptions(timeout=30000,retry_options=types.HttpRetryOptions(attempts=1)))
if args.list:
    try:
        models=[m.name.removeprefix('models/') for m in client.models.list() if 'generateContent' in (m.supported_actions or [])]
        print(json.dumps({'available_model_ids':models},indent=2))
    except Exception as exc: print(json.dumps({'status':'unavailable','code':getattr(exc,'code',type(exc).__name__)}));sys.exit(1)
    finally: client.close()
    sys.exit()
# Pricing-inspected configurations, never auto-fallback. Re-check pricing before expanding.
allowed={'gemini-3.8-flash','gemini-3.7-flash','gemini-3.6-flash','gemini-3.5-flash','gemini-3.1-flash-lite'}
if not args.confirm_free_tier or args.model not in allowed or settings.allow_paid_services:
    p.error('Confirm the project is Free with billing disabled and select a pricing-inspected model. No generation request sent.')
report={'model':args.model,'sdk_version':importlib.metadata.version('google-genai'),'checked_at':now(),'free_tier_attested':True,'structured_output':'not_tested','custom_function':'not_tested','url_context':'not_tested','search_grounding':'disabled: inspected model pricing does not list free API search','known_quota_restrictions':'Account quotas apply; no paid fallback. Capability is not a billing guarantee.'}
try:
    response=client.models.generate_content(model=args.model,contents='Extract exactly one required requirement from this fictional source JSON. Preserve source id and original text verbatim: {"id":"fixture-jd","text":"Experience with React."}' ,config=types.GenerateContentConfig(response_mime_type='application/json',response_json_schema=gemini_schema(Requirements),max_output_tokens=1500,automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)))
    result=Requirements.model_validate_json(response.text)
    report['structured_output']='passed' if len(result.requirements)==1 and result.requirements[0].jd_source_id=='fixture-jd' and result.requirements[0].original_excerpt=='Experience with React.' else 'failed'
    report['schema_validation']='Actual nested Requirements schema; all local Pydantic bounds enforced.'
    report['structured_sample']=result.model_dump()
except Exception as exc: report['structured_output']='failed: '+str(getattr(exc,'code',type(exc).__name__))
if report['structured_output']=='passed':
    try:
        function=types.FunctionDeclaration(name='read_fixture',description='Read the fictional test count.',parameters_json_schema={'type':'object','properties':{'id':{'type':'string'}},'required':['id']})
        config=types.GenerateContentConfig(tools=[types.Tool(function_declarations=[function])],tool_config=types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode='ANY')),automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),max_output_tokens=500)
        prompt='Call read_fixture with id fixture-18. Then state the returned count.'
        response=client.models.generate_content(model=args.model,contents=prompt,config=config)
        calls=response.function_calls or []
        if len(calls)!=1 or calls[0].name!='read_fixture' or calls[0].args!={'id':'fixture-18'}: raise ValueError('Unexpected tool call')
        contents=[types.Content(role='user',parts=[types.Part.from_text(text=prompt)]),response.candidates[0].content,types.Content(role='user',parts=[types.Part.from_function_response(name='read_fixture',response={'count':18})])]
        follow=client.models.generate_content(model=args.model,contents=contents,config=types.GenerateContentConfig(tools=[types.Tool(function_declarations=[function])],automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),max_output_tokens=1000))
        report['custom_function']='passed' if '18' in (follow.text or '') else 'failed'
    except Exception as exc:
        report['custom_function']='failed: '+str(getattr(exc,'code',type(exc).__name__))
        report['custom_function_error']=str(exc).replace(settings.gemini_api_key,'[redacted]')[:1600]
    try:
        response=client.models.generate_content(model=args.model,contents='Use URL Context to read https://ai.google.dev/gemini-api/docs and state one product fact. No personal information.',config=types.GenerateContentConfig(tools=[types.Tool(url_context=types.UrlContext())],max_output_tokens=1000,automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)))
        metadata=[c.url_context_metadata.model_dump(mode='json') for c in response.candidates or [] if c.url_context_metadata]
        report['url_context']='passed' if 'URL_RETRIEVAL_STATUS_SUCCESS' in json.dumps(metadata) else 'unverified: no successful retrieval metadata'
        report['url_metadata']=metadata
    except Exception as exc: report['url_context']='failed: '+str(getattr(exc,'code',type(exc).__name__))
client.close()
(ROOT/'capabilities.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
