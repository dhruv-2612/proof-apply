# ProofApply

Truthful resume preparation for Tech Zephyr 4.0, Problem Statement 11. One FastAPI service serves a Next.js static export and runs a bounded LangGraph workflow. The result is an A4, single-column resume PDF plus source-linked Markdown and JSON reports.

**Local offline flow works. The six Stitch desktop designs are retrieved and adapted. Live Gemini generation and Linux container execution remain unverified. This is not marked acceptance-complete or deployed.** See [BUILD_STATUS.md](BUILD_STATUS.md) for the latest measured results.

## Start on this Windows workspace

Double-click `start-local.cmd`, or run it from a terminal. Open **http://127.0.0.1:8000**. The Python 3.11 environment, native PDF libraries and exported frontend have been installed here. If the service is already running, open the URL directly instead of starting a second copy.

1. Choose **Load fictional sample**.
2. Inspect the original excerpts in **Evidence**. **Approve supported excerpts** includes the extracted positive statements and excludes unclear/context excerpts; individual decisions are also available.
3. Select the explicitly labeled **Offline · mock provider** mode and choose **Build my resume**.
4. Inspect the actual activity, checks, role gaps and original claim sources. Download the PDF and both reports.
5. Use **Clear temporary session** to start again. No accounts or permanent history are provided.

The fictional frontend case has six direct required matches and a missing preferred Docker qualification: `12 / 13 = 92.31%`. The platform case has four genuine required gaps and a direct preferred Git match: `1 / 9 = 11.11%`. These are transparent source-coverage heuristics, not commercial ATS scores or hiring predictions.

## Reproduce the environment

Requires Python 3.11, Node 22, npm and [uv](https://docs.astral.sh/uv/). `backend/uv.lock`, the hash-pinned `backend/requirements.lock`, and `frontend/package-lock.json` are checked in. Use the locks; do not re-resolve dependencies for the demo.

```powershell
uv sync --project backend --frozen
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
```

On Windows, WeasyPrint needs Pango. This repo includes a workspace-only installer that reads the official MSYS2 package index, verifies package SHA-256 checksums, and extracts runtime libraries without changing your system:

```powershell
backend/.venv/Scripts/python.exe scripts/install_windows_pdf.py
./start-local.cmd
```

Alternatively use the official [WeasyPrint Windows installation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows). The app discovers this repository's `.tools/msys/ucrt64/bin` automatically. On Linux, install the system packages listed in `Dockerfile`, then:

```sh
uv sync --project backend --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run --directory backend uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Use the exported UI through FastAPI for one-origin operation. `next dev` alone has no API proxy. After frontend edits, rebuild the static export; after backend edits, restart FastAPI. API documentation is at `/docs`.

## Gemini and zero-cost policy

The existing `.env` is preserved and ignored by Git. Secrets never enter the frontend bundle. [Google's pricing](https://ai.google.dev/gemini-api/docs/pricing), [official SDK](https://googleapis.github.io/python-genai/), and model metadata were inspected. The configured key successfully listed models. **A metadata listing does not prove free generation quota, tool access, or billing status.** No generation calls have been made in the recorded build so far.

Before any generation probe, confirm in Google AI Studio that the project associated with the key is on the **Free tier with billing disabled**. No code flag can guarantee Google's billing state. Never enable billing or try a paid fallback.

After that confirmation, select a currently free, available model from the probe's inspected allowlist and run:

```powershell
backend/.venv/Scripts/python.exe backend/scripts/capability_probe.py --list
backend/.venv/Scripts/python.exe backend/scripts/capability_probe.py --model gemini-3.8-flash --confirm-free-tier
```

The second command performs fictional structured-output and explicit function-call round-trip checks and a separate public URL Context probe. It saves a sanitized `capabilities.json`. A failed probe stays failed. Search grounding is disabled; no zero-cost search configuration has been verified. The current unprobed configuration uses supplied company knowledge. URL Context is enabled only for a model whose separate probe passed. The UI uses the KB path; approved URLs can also be added through the source API.

Only after structured output and the custom function probe pass, configure these values without changing the key:

```dotenv
GEMINI_MODEL=gemini-3.8-flash
FREE_TIER_CONFIRMED=true
LLM_MODE=gemini
ALLOW_PAID_SERVICES=false
```

Restart the service, explicitly select live mode in the UI, and run the server-verified fictional fixtures. Prove at least a normal and a missing-qualification journey, then inspect the resulting claim/source pairs and PDF. The official SDK supports the `models.generate_content` response-schema interface used here; built-in tools are probed separately. No automatic mode or model fallback exists.

**Real personal resumes are local/offline only.** The unpaid Gemini processing restrictions apply to the whole personal history, not merely email removal. The live API refuses non-fixture candidate/company sources even if the browser claims they are fictional. Header name/contact fields are copied locally by the renderer and excluded from model requests. On a hosted service, those fields temporarily reside on that server.

## Architecture and checks

- Immutable source records retain raw extracted text, hashes and page/paragraph/line locators. Candidate, job, company and style roles are assigned by the upload slot. Original files use generated paths.
- Inclusion, exclusion and clarification are separate append-only records. A clarification creates a new source. Evidence review is required before generation.
- A conditional LangGraph coordinator receives code-owned legal actions. Successful research and fit are prerequisites to writing. The platform fixture performs an additional exact-source lookup. Research failure can fall back to a supplied KB or pause for clarification.
- Local checkpoints use SQLite; Render uses memory. Human replies check question ID, run version and idempotency key. One worker executes one run at a time; there is no durable queue.
- Gemini tasks use separate prompts for coordination, requirements, research choice, fit, writing and independent semantic review. Tools, rendering, storage and release checks are ordinary Python code. The mock provider is an explicit extractive demonstration, not a semantic substitute for live AI.
- Hard gates validate evidence/claim/requirement relations, source roles, quantities, high-risk wording, detected conflicts, reviewer completeness, page count, selectable PDF text, bounds, font size and exact content/order. Same-model review can still share errors; source support is not external fact verification.
- At most 18 model attempts, two research actions, two human pauses, one rewrite and 600 active seconds. Every rewrite gets a new hash, PDF and evaluation. Factual/layout uncertainty produces `needs_review` with downloads disabled.
- Reports record research provenance, matches/gaps, final claim links, edits, base omissions, dropped draft claims, counters and final hashes. The download route rechecks artifact integrity. A cancelled or expired run cannot release late results.
- Cookies are opaque, HttpOnly and SameSite Strict. Source/run/artifact access is session-scoped. Cross-origin writes are rejected. Sessions expire after two hours; a periodic in-process cleanup deletes temporary files/records. Hosting restarts can interrupt runs.

## Test and inspect

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests -q
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
$env:PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/browsers"
npx.cmd --prefix frontend playwright install chromium
npm.cmd --prefix frontend run test:ui
backend/.venv/Scripts/python.exe backend/scripts/run_example.py --mode mock --scenario frontend
backend/.venv/Scripts/python.exe backend/scripts/run_example.py --mode mock --scenario platform
```

Start FastAPI before browser/example checks. UI tests cover 1440px and 390px, keyboard entry and drawer dismissal, source review, real generation/downloads, refresh recovery and invalid upload errors. `output/qa/` contains captured screenshots; `output/examples/` contains explicitly labeled fictional outputs and traces. Failure-injection tests demonstrate application behavior, not spontaneous Gemini hallucinations.

The supplied real DOCX and Amazon JD also parse locally. To reproduce their local-only parser/layout rehearsal:

```powershell
backend/.venv/Scripts/python.exe backend/scripts/run_local_sample.py
```

Its private outputs are excluded from Git under `output/private/`. It never calls Gemini. Review the selected content before using it as an actual application: the offline writer preserves excerpts and has limited role understanding.

## Design and deployment readiness

All six screens from Stitch project `11030537791420483270` were retrieved through its MCP connection, including screenshots and HTML exports. The UI adapts their horizontal navigation, mint palette, paired workspace panels and source comparison. [design/STITCH-MANIFEST.md](design/STITCH-MANIFEST.md) records actual screen IDs, assets, inspection and deliberate differences. Desktop and mobile browser captures were compared with the references. No separate mobile frame was returned; the app uses a system-font fallback and makes no pixel-perfect claim. Raw design exports remain reference files and are not served by the app.

`Dockerfile` builds the static frontend in a Node stage and serves it with FastAPI/one Uvicorn worker in Python 3.11. `render.yaml` explicitly selects one Free web service and provisions no disk, worker, paid database or domain. **Docker is absent on the build machine, so this Linux image has not been built or executed.**

When Docker is available, first test locally:

```sh
docker build -t proofapply .
docker run --rm -p 8000:8000 -e APP_ENV=development -e CHECKPOINT_BACKEND=memory proofapply
```

Repeat health, fixture, download and restart checks. Only publish after the team supplies its Render account/destination and explicitly requests deployment. Verify the then-current free plan and actual URL; a YAML file is not deployment evidence. Render Free storage is temporary and idle services sleep. Keep the local app and downloaded outputs ready. Hosted live runs default to disabled; a server-side `DEMO_ACCESS_CODE` or deliberate `PUBLIC_LIVE_RUNS` configuration is required in addition to the free-tier/probe gates.

## License and remaining limits

PyMuPDF uses AGPL/commercial licensing; it is **not MIT**. Review upstream and project distribution obligations before publication. Other key libraries include WeasyPrint (BSD), python-docx (MIT), FastAPI (MIT), LangGraph (MIT) and google-genai (Apache-2.0); transitive dependencies retain their own licenses. No project-wide license is invented for the team's submission.

No OCR, arbitrary repository crawling, paid search, accounts, application submission or cover letters. The offline matcher recognizes the fictional technology vocabulary and conservatively reports other requirements as missing; it is not a general natural-language fit model. Deterministic conflict rules are conservative and narrow; live review remains essential for arbitrary paraphrases. One-page content cuts may omit relevant source details, all visible in the report. The UI intentionally exposes only the user-requested one-page layout, although the backend accepts a two-page cap.
