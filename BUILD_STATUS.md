# Build status

Updated: 2026-09-13. Local implementation and offline acceptance checks pass. The app is **not marked fully complete**: an inspected real-Gemini package and Linux container validation remain unresolved. Stitch retrieval and functional design adaptation are now verified.

## Working locally

FastAPI serves the Next.js static export at http://127.0.0.1:8000. Final health and page requests returned 200. Restart with `start-local.cmd`; see README.md for clean setup.

The full Prepare -> Evidence -> Build -> Results journey works with real extraction, immutable source excerpts, inclusion/exclusion, conditional LangGraph planning, company-KB research/fallback, human clarification/resume, bounded revision, a truthful activity log, actual PDF rendering and downloadable PDF/JSON/Markdown artifacts. Final checks bind the exact draft, evaluation and artifact hashes. Unresolved checks and cancellation prevent verified downloads. Sessions are isolated and expire after two hours.

The requested layout is one A4 page, one column, 11-point body text and conventional headings. Both fictional examples were rendered and inspected. Frontend role coverage is 92.307% with Docker explicitly missing; platform coverage is 11.111% with four required gaps and an additional evidence-lookup branch. These are documented-requirement heuristics, not hiring predictions.

The supplied real resume DOCX and Amazon JD PDF were also parsed and rendered locally with zero model calls. Their private one-page parser/layout rehearsal is in ignored `output/private/local-sample/`. This extractive offline result is not a live AI-tailored application and requires content review.

## Milestones in docs/05 order

| Milestone | Actual status |
|---|---|
| M0 capability/skeleton | Health, static export, Python 3.11 dependencies and native Windows PDF rendering passed. Metadata-only Gemini model listing passed. Linux PDF/container gate and generation/tool probes remain unverified. Continued independent local work rather than treating those as passes. |
| M1 inputs/contracts | Passed locally: immutable locators, role separation, evidence decisions, file limits, malformed/scanned/encrypted errors and session boundaries. |
| M2 conditional graph | Passed offline and under controlled faults: different fixture routes, actual KB fallback, clarification/resume, illegal-action prevention, bounded schema repair/retry and cancellation. |
| M3 artifacts/release | Passed with real PDFs: one rewrite maximum; exact values, source roles, separate reviewer verdicts, page/text/geometry and final hash checks. |
| M4 interface | Six actual desktop screenshots and HTML exports retrieved, inspected and adapted. Desktop/mobile UI passes; deliberate differences and missing mobile reference are documented. |
| M5 live integration | BLOCKED pending confirmation that the key's Google AI Studio project is Free tier with billing disabled, then actual capability probes and end-to-end runs. No Gemini generation calls were made. |
| M6 evaluation | Local deterministic checks for T01-T20 pass. Real semantic validation remains part of M5. Secret/private-file audit and PDF/UI visual review performed. |
| M7 deployment | Dockerfile, one Render Free service configuration and instructions prepared. Docker is not installed, so image build/run and Linux resource behavior are unverified. No publication requested or attempted. |
| M8 handoff | README, evaluation mapping, fictional packages/traces, screenshots, actual offline silent demo recording and presentation summary prepared. Team naming and final live/submission rehearsal remain team inputs. |

## Verification actually run

- `backend/.venv/Scripts/python.exe -m pytest backend/tests -q`: **50 passed**, 84.40 seconds. One upstream Starlette/AnyIO deprecation warning. Includes actual PDF rendering during integration tests.
- `npm.cmd --prefix frontend run typecheck`: passed with strict TypeScript enabled.
- `npm.cmd --prefix frontend run build`: passed; Next.js static export. Repeated after correcting visible punctuation encoding.
- `npx.cmd playwright test` from frontend, with the workspace browser path: **7 passed**, 24.0 seconds on 2026-09-13. Real FastAPI/static UI at 1440px and 390px; keyboard/source drawer, full download flow, refresh, input errors, mobile pasted resume and long filename, actual clarification resume, explicitly controlled needs_review download lockout, and delayed-session initialization before source submission.
- `backend/scripts/run_example.py --mode mock --scenario frontend` and `--scenario platform`: checked one-page PDF and reports; preserved under `output/examples/` with actual traces.
- `backend/scripts/run_local_sample.py`: supplied private documents, local-only extraction/render rehearsal, one page, no model attempts.
- Visual review: actual fictional and private PDF pages; desktop/mobile Prepare, Evidence, Build, Results and source comparison; controlled attention screen labeled as such.
- Local process sample: approximately 194.3 MiB RSS / 202.5 MiB peak working set after fixture runs. This Windows observation is not a Render/Linux capacity certification. See `output/qa/runtime-measurement.json`.
- Staged files and exported browser bundle scanned for the actual environment key without printing it. Private sample documents, private outputs, .env, runtime data and installed tools are ignored by Git.

Controlled fault tests cover a fabricated 40% claim with a valid ID, 18 changed to 80, inflated ownership/certification, company/JD role confusion, genuine missing qualifications, hostile source instructions, provider failure, malformed JSON, real overflow and PDF text loss, stale artifacts, duplicate requests, cancelled/expired/cross-session access, uncertain review and no silent live-to-mock fallback. See `docs/EVALUATION.md` for the mapping.

## Live, design and cost record

`capabilities.json` records successful metadata listing with google-genai 2.23.0. Structured output, custom function round trip and URL Context remain not_tested. Model listing does not verify generation quota or billing entitlement. Search is disabled. The runtime requires explicit free-tier confirmation and passed capability checks before live mode; no paid fallback, billing change or purchase was made. Real personal resumes are restricted to local/offline processing; live demonstrations accept only server-verified fictional fixtures.

Stitch access is resolved. A fresh MCP client retrieved ProofApply Design Workspace (`11030537791420483270`) and all six desktop screenshots/HTML exports. `design/STITCH-MANIFEST.md` records the real IDs, dimensions, local paths, hashes and adaptation decisions. The UI uses their structure and colors with system-font/mobile adaptations; no pixel-perfect claim. The built-in conversation registry retained an old startup error, so reads used the configured MCP endpoint through a fresh client. No remote design was generated or edited.

## Preservation, packaging and known limits

Original brief, fictional fixtures and private sample documents were preserved. The directory had no Git repository; a local repository was initialized, with tested Python/frontend lockfiles included. There is no remote push or public deployment.

Backend modules are grouped by responsibility rather than creating empty directories from the suggested tree. Windows WeasyPrint uses workspace-local MSYS2 native libraries installed from hash-checked package metadata; tested runtime details are in `scripts/windows-pdf-runtime-tested.json`. Docker preparation uses Linux system packages but remains unexecuted here.

The mock matcher/reviewer is conservative and extractive, with limited vocabulary; it cannot establish arbitrary semantic paraphrase quality. Deterministic date/conflict rules are narrow. A same-model live reviewer can share model errors. The UI uses supplied company KB; separately probed URL Context is accessible through the source API. No OCR or repository crawling. Content cuts can omit relevant details and are recorded in reports. PyMuPDF has AGPL/commercial licensing; no project license or paid license was invented.

## Next concrete steps

1. Confirm that the Google AI Studio project associated with the existing key is Free tier with billing disabled. Then run the documented fictional capability probe, select only a successfully verified free model, and inspect normal, missing-qualification and reviewer-feedback live packages when quota permits. Keep live acceptance unresolved until these succeed.
2. Review the adapted UI with the team. All six desktop references are present; a separate mobile reference is optional and was not returned by Stitch.
3. When Docker is available, build/run the prepared image and repeat health, PDF, session and restart checks locally. Render publication still requires the team's destination/account and an explicit deployment request.

## Earlier metadata/access recheck: 2026-09-13 (Stitch outcome superseded below)

The requested Gemini generateContent model listing succeeded using the existing .env key and installed google-genai SDK. Returned IDs include gemini-2.5-flash, gemini-2.5-pro, gemini-3.1-flash-lite, gemini-3.5-flash, gemini-3.6-flash, gemini-3.7-flash and gemini-3.8-flash. No generation or tool probe was invoked; free-tier/billing confirmation and live acceptance remain pending. Stitch tool discovery again found no callable connector; all six design reference gaps remain. No application code changed, so the existing test results above were not rerun.

## Earlier Stitch connection diagnosis: 2026-09-13 (resolved below)

The named `stitch` server was registered but failed startup because a credential value was placed in `bearer_token_env_var`. Removed that invalid duplicate setting while retaining the existing X-Goog-Api-Key header. A fresh read-only MCP handshake and 16-tool listing succeeded. Before project retrieval completed, the external config changed and removed the stitch entry; the newer config was preserved. No screen exports were retrieved and no UI changes were made. Reconnect/reload Stitch before continuing design retrieval. See design/STITCH-MANIFEST.md for the precise access history.

## Stitch retrieval and UI milestone: 2026-09-13

All six actual screens, downloaded PNGs and HTML exports are preserved under `design/references/`. Inspected layout, tokens and export scripts; adapted the horizontal workflow header, paired Prepare cards, Evidence target panel, Build preview panel, Results styling, two-column claim/source dialog and attention palette. Kept real backend values and events, native accessible controls and actual downloads. Did not import the exports' simulated countdowns, fixed confidence values, fake save/export notices or CDN scripts. Added scroll-to-top on view changes so the result opens at its heading.

Strict TypeScript check and Next static export passed. The final seven-scenario browser suite passed in 24.0 seconds, including actual final-claim/source comparison and delayed session initialization. An earlier rerun exposed a real startup race (source submission before the session cookie); actions now remain disabled until bootstrap finishes. Programmatic invalid-file injection was updated to wait for the enabled input. No backend code or PDF template changed, so the previously recorded 50-test backend run remains the latest backend result; it was not rerun merely for styling. UI captures were refreshed at 1440px and 390px and visually compared with the retrieved desktop references. The offline demo recording is refreshed to the new UI. Final secret/private-file audit covers repository files and the static bundle. Live Gemini and Linux/Docker gates remain unresolved.
