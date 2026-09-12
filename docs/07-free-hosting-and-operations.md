# Free hosting and operating constraints

## First check Gemini access

Use a Google AI Studio API key supplied through `GEMINI_API_KEY` on the backend. A chat subscription is not evidence of model/API billing entitlement. Do not enable billing. Make the exact model ID configurable, with a Pro preference when confirmed available at zero cost. If Pro is unavailable or its quota is unusable, document and use a verified free Gemini Flash alternative consistent with the team's zero-cost constraint; do not silently upgrade services.

Read current official pricing and the account's available quota before selecting IDs. At preparation time Google's pricing page lists some Flash free grounding allowances and free URL Context, while other model rows differ. This corrects the earlier blanket statement that search grounding is unavailable for every free API model. Availability still requires an account-level check. [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)

Create a capability record with selected model/SDK version, structured-output result, custom-function test result, URL Context status, search-grounding status, checked timestamp and known quota restrictions. Test built-in tools separately from custom functions/strict output to avoid model-specific combination failures. On an unavailable tool, use the supplied KB path without changing the truthfulness rules.

## Configuration contract

Create `.env.example` with placeholders and comments. Values below are recommended app defaults, not provider quotas.

```dotenv
APP_ENV=development
LLM_MODE=mock
GEMINI_API_KEY=
GEMINI_MODEL=
GEMINI_RESEARCH_MODEL=
ALLOW_PAID_SERVICES=false
RESEARCH_MODE=provided_kb
ENABLE_SEARCH_GROUNDING=false
CHECKPOINT_BACKEND=sqlite
DATABASE_URL=sqlite:///./data/proofapply.db
SESSION_TTL_MINUTES=120
MAX_FILES=5
MAX_FILE_MB=5
MAX_TOTAL_UPLOAD_MB=15
MAX_TOTAL_EXTRACTED_CHARS=100000
MAX_CONCURRENT_RUNS=1
MAX_MODEL_CALLS=18
MAX_RESEARCH_CALLS=2
MAX_COMPANY_URLS=3
MAX_REVISIONS=1
MAX_CLARIFICATIONS=2
MAX_ACTIVE_RUN_SECONDS=600
FREE_DEMO_SYNTHETIC_ONLY=true
PUBLIC_LIVE_RUNS=false
DEMO_ACCESS_CODE=
PORT=8000
```

The app-level `ALLOW_PAID_SERVICES=false` flag is a guardrail, not a guarantee of Google billing behavior. The actual protection is using a verified free-tier project without paid billing and not enabling paid features. Keep an explicit allowlist of tested model/tool configurations. Never reuse a paid project accidentally. Do not print secrets or include them in capability results.

On Render set `APP_ENV=production`, `CHECKPOINT_BACKEND=memory` and the environment's bound port. `LLM_MODE=gemini` only when the live capability checks pass. Store the database and per-session files in a writable temporary app directory. Avoid committing `.env`, generated private data or logs. Mock mode remains a separate deliberate mode with a visible label.

## One Render Free service

Use a multi-stage Dockerfile. Build the Next.js export in the Node build stage. Install Python runtime packages, required WeasyPrint system libraries and fonts in a slim Debian-based Python stage, then copy backend and `frontend/out/` into it. Run one Uvicorn worker bound to `0.0.0.0:$PORT`. Mount API routes before static routes. Serve `/` with the export's index file and static assets with appropriate content types.

Install WeasyPrint/Pango/font dependencies from its current official Linux instructions; exact package names must be validated in the container. Keep browser binaries and frontend build tooling out of the runtime image. Test memory with a single render and small inputs. [WeasyPrint installation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

Create `render.yaml` selecting the Free web-service compute plan explicitly, Docker runtime and `/api/health`. Do not provision a paid disk, worker, cron job, database or custom domain. Prefer the provided host URL.

Render Free sleeps after idle periods, can restart, and loses local files/SQLite data. The documentation lists a 512 MB free instance and temporary filesystem. Without a payment method, limit exhaustion can suspend service instead of charging it. Confirm the current plan during deployment. Keep the demo single-job and download artifacts promptly. [Render free-service limits](https://render.com/docs/free), [Render billing behavior](https://render.com/docs/faq)

On restart, old client run IDs must return an expired/missing-session response, not show a permanently spinning job. Memory checkpoints do not survive. SQLite on this host is also temporary; do not advertise history or durable recovery. Delete expired session data lazily on requests and periodically within the app process; no paid scheduler is needed.

## Quota and endpoint protection

No full account system is needed. Use opaque per-session cookies and ownership checks for runs/files. Prevent a public demo from exhausting the team's small free quota: default hosted public interaction to the labeled sample/offline flow, or enable live generation only after entering a shared demonstration access code. That code is checked server-side, never bundled into the frontend. The team can enable public live runs deliberately with a small per-session/global rate limit.

Use process-managed bounded tasks for the MVP: return 202 quickly, then poll status. Keep task references, catch exceptions, and reflect failures in run state. Offload blocking parser/PDF work from the event loop. In-process jobs may be interrupted by host restarts; do not imply a durable worker queue.

## Candidate data and sources

Google's unpaid-service terms restrict submitting personal, sensitive or confidential information and describe product-improvement processing. The free demo therefore uses the fictional sources in this kit. Real resumes may be used for local parser/visual tests without sending them to the model. A user's checkbox or removal of an email address does not make the rest of a real employment history non-personal. [Gemini API terms](https://ai.google.dev/gemini-api/terms)

Render contact headers from local/application data without including them in model prompts. In the hosted app those fields temporarily reside on the server; UI wording must say “excluded from model requests,” not falsely promise “never leaves your computer.” Do not log source bodies. For a production personal-data mode, the team would need a suitable processing arrangement and its own privacy design; that is outside the free hackathon scope.

Allow only relevant public HTTPS company URLs. Reject local/private-network addresses and credentials in URLs. If implementing any direct HTTP source fetch later, also validate DNS/redirect destinations, response size and content type. Use safe HTML escaping, controlled resource paths and a restricted WeasyPrint resource fetcher; resumes must not load arbitrary remote images or local files.

## Deployment checklist

1. Build and run the container locally; test upload, source review, run, PDF and both report downloads.
2. Verify no Gemini secret is in frontend assets or git history and source/artifact directories are not public static directories.
3. Prepare free-service config and model capability snapshot. Only publish after the team requests deployment to its account.
4. Test live URL after deployment, including a cold start, and keep its limits in the README.
5. Keep the local app, a real recorded demonstration and downloaded fictional example outputs ready for judging.
