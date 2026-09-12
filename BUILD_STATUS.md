# Build status

Updated: 2026-09-12. Local implementation and offline acceptance checks pass. The app is **not marked fully complete**: an inspected real-Gemini package, Stitch comparison and Linux container validation remain unresolved.

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
| M4 interface | Functional temporary desktop/mobile UI passed. Stitch fidelity remains unverified. |
| M5 live integration | BLOCKED pending confirmation that the key's Google AI Studio project is Free tier with billing disabled, then actual capability probes and end-to-end runs. No Gemini generation calls were made. |
| M6 evaluation | Local deterministic checks for T01-T20 pass. Real semantic validation remains part of M5. Secret/private-file audit and PDF/UI visual review performed. |
| M7 deployment | Dockerfile, one Render Free service configuration and instructions prepared. Docker is not installed, so image build/run and Linux resource behavior are unverified. No publication requested or attempted. |
| M8 handoff | README, evaluation mapping, fictional packages/traces, screenshots, actual offline silent demo recording and presentation summary prepared. Team naming and final live/submission rehearsal remain team inputs. |

## Verification actually run

- `backend/.venv/Scripts/python.exe -m pytest backend/tests -q`: **50 passed**, 84.40 seconds. One upstream Starlette/AnyIO deprecation warning. Includes actual PDF rendering during integration tests.
- `npm.cmd --prefix frontend run typecheck`: passed with strict TypeScript enabled.
- `npm.cmd --prefix frontend run build`: passed; Next.js static export. Repeated after correcting visible punctuation encoding.
- `npx.cmd playwright test` from frontend, with the workspace browser path: **6 passed**. Real FastAPI/static UI at 1440px and 390px; keyboard/source drawer, full download flow, refresh, input errors, mobile pasted resume and long filename, actual clarification resume, and explicitly controlled needs_review download lockout.
- `backend/scripts/run_example.py --mode mock --scenario frontend` and `--scenario platform`: checked one-page PDF and reports; preserved under `output/examples/` with actual traces.
- `backend/scripts/run_local_sample.py`: supplied private documents, local-only extraction/render rehearsal, one page, no model attempts.
- Visual review: actual fictional and private PDF pages; desktop/mobile Prepare, Evidence, Build, Results and source comparison; controlled attention screen labeled as such.
- Local process sample: approximately 194.3 MiB RSS / 202.5 MiB peak working set after fixture runs. This Windows observation is not a Render/Linux capacity certification. See `output/qa/runtime-measurement.json`.
- Staged files and exported browser bundle scanned for the actual environment key without printing it. Private sample documents, private outputs, .env, runtime data and installed tools are ignored by Git.

Controlled fault tests cover a fabricated 40% claim with a valid ID, 18 changed to 80, inflated ownership/certification, company/JD role confusion, genuine missing qualifications, hostile source instructions, provider failure, malformed JSON, real overflow and PDF text loss, stale artifacts, duplicate requests, cancelled/expired/cross-session access, uncertain review and no silent live-to-mock fallback. See `docs/EVALUATION.md` for the mapping.

## Live, design and cost record

`capabilities.json` records successful metadata listing with google-genai 2.23.0. Structured output, custom function round trip and URL Context remain not_tested. Model listing does not verify generation quota or billing entitlement. Search is disabled. The runtime requires explicit free-tier confirmation and passed capability checks before live mode; no paid fallback, billing change or purchase was made. Real personal resumes are restricted to local/offline processing; live demonstrations accept only server-verified fictional fixtures.

No callable Stitch MCP tools or screen exports were available. The supplied project ID is 11030537791420483270; project web retrieval failed. `design/STITCH-MANIFEST.md` lists all six missing screen IDs, dimensions, screenshots and export code. Current CSS/tokens are temporary, with no pixel-match claim.

## Preservation, packaging and known limits

Original brief, fictional fixtures and private sample documents were preserved. The directory had no Git repository; a local repository was initialized, with tested Python/frontend lockfiles included. There is no remote push or public deployment.

Backend modules are grouped by responsibility rather than creating empty directories from the suggested tree. Windows WeasyPrint uses workspace-local MSYS2 native libraries installed from hash-checked package metadata; tested runtime details are in `scripts/windows-pdf-runtime-tested.json`. Docker preparation uses Linux system packages but remains unexecuted here.

The mock matcher/reviewer is conservative and extractive, with limited vocabulary; it cannot establish arbitrary semantic paraphrase quality. Deterministic date/conflict rules are narrow. A same-model live reviewer can share model errors. The temporary UI uses supplied company KB; separately probed URL Context is accessible through the source API. No OCR or repository crawling. Content cuts can omit relevant details and are recorded in reports. PyMuPDF has AGPL/commercial licensing; no project license or paid license was invented.

## Next concrete steps

1. Confirm that the Google AI Studio project associated with the existing key is Free tier with billing disabled. Then run the documented fictional capability probe, select only a successfully verified free model, and inspect normal, missing-qualification and reviewer-feedback live packages when quota permits. Keep live acceptance unresolved until these succeed.
2. Reconnect Stitch or supply the six reference exports/IDs; adapt and compare the temporary UI against actual references.
3. When Docker is available, build/run the prepared image and repeat health, PDF, session and restart checks locally. Render publication still requires the team's destination/account and an explicit deployment request.
