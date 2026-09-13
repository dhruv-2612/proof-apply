# Build status

> **Muse branch deviations (2026-09-13, user-requested, NOT on main):**
> live Gemini accepts user-supplied real documents (synthetic-only gate lifted in
> `backend/app/main.py`; header contact fields still stripped from model calls);
> offline matcher uses a ~600-skill literal vocabulary (`backend/app/skills.py`);
> fit payload withholds `claim_id` to stop evidence/claim ID confusion;
> resume template restyled within PDF gates. First real-data live package:
> `output/private/live-pm-amazon-04/` (PM @ Amazon, 9 attempts, 0 revisions,
> 87.5% honest coverage, manually inspected). Backend suite 57 passed;
> frontend typecheck + static export rebuilt. Restart the local server to pick
> up backend changes. Private outputs stay git-ignored.
>
> Main-line status below is unchanged.
>
> **Muse update 2 (2026-09-13):** JD auto-detect (`POST /api/sources/{id}/detect-target`,
> auto-applied in UI after JD save); explicit **Enhance with Gemini** evidence action
> (`POST /api/evidence/enhance`, verbatim-validated, static merge for the rest,
> decisions reset for re-review); automatic model-knowledge company brief when no
> company source exists, with code-enforced substance threshold and manual
> clarification fallback; fit payload withholds `claim_id` (fixes evidence/claim ID
> confusion on large sets). Verified live, no company KB supplied: detect returned
> Product Manager @ Amazon exactly; enhance fixed categories (Projects 18→15,
> Coursework 1→4, +Summary); run completed, 9 attempts, 0 revisions, honest 75%
> coverage (`output/private/live-pm-amazon-06/`, inspected). Suite: 61 passed
> (57 + 4 new); typecheck + static export rebuilt.
>
> **Muse update 5 (2026-09-13):** prepare-screen parity from the user-supplied 01
> HTML: files-attached chip, per-file excerpt counts, full-width excerpt-spectrum
> strip (real per-source counts), careers-URL input (`official_url` slot, feeds
> URL-Context research), collapsible company notes, readiness checklist in the
> footer, blocker list under the Evidence build button, Help & Docs dialog.
> Fictional strip, fake counts/anchors, candidate IDs and the 1/2-page selector
> deliberately not copied. Fixed a flex-specificity bug stretching file icons.
> Verified 1440px screenshots. Suite: 64 backend + 7 UI (journey converted to
> manual entry, still asserts 92%).
>
> **Muse update 6 (2026-09-13):** step-2 Evidence view rebuilt from the 02 HTML:
> stage pill + file count, Review-Index donut (real decided ratio, never called
> verification), status tabs with live counts, search + category chips, per-card
> Clarify-claim inline form, amber unclear treatment, excluded strikethrough with
> re-include, target panel with included chip + review-progress bar + unclear
> guardrail, Back-to-inputs button, transparency card; build button renamed
> "Build my application". Fabricated items not copied (78% index, 0.94
> confidence, invented claim texts). Verified 1440px screenshot. Suite: 64
> backend + 7 UI.
>
> **Muse update 3 (2026-09-13):** cross-format parity verified (txt/md/docx/pdf give
> identical resume evidence and normalized-identical JD text). Fixed DOCX heading
> detection: heading styles, any-case section labels and Summary mapping
> (`is_heading`/`section_for`); static splitter remains verbatim-first, the LLM
> enhance only recategorizes/adds validated excerpts. Confirmed division of labor:
> scripts do text extraction + keyword spotting (`terms()`), Gemini does
> requirements/fit/writing/review (5 clean requirements from unnumbered JD bullets
> in 1 live call). Suite: 63 passed.
>
> **Muse update 4 (2026-09-13):** Stitch access reconfirmed; all 6 screens + HTML
> exports retrieved fresh and byte-identical to morning copies (screens unchanged;
> screenshot CDN refused direct download, local PNGs retained). UI rework on muse:
> Inter bundled locally (OFL, offline @font-face), phase pills, session chip,
> drag-drop resume zone, per-file remove (`DELETE /api/sources/{id}` with evidence
> cascade), How-it-works card, value cards, design footer. All fictional/sample/
> mock-facing UI removed (sample loader, mode selector → auto engine, fictional
> labels); backend mock + fixtures stay for tests/offline only. Verified with
> 1440px + 390px screenshots. Suite: 64 passed; typecheck + export rebuilt.

Updated: 2026-09-13. **Local implementation acceptance passes.** The real Gemini, Stitch design and Linux container gates are verified. Public hosting is prepared, not deployed; the user deferred Render setup. No billing, paid fallback or purchase was enabled.

## Working locally

Open http://127.0.0.1:8000 or use `start-local.cmd`. FastAPI serves the Next.js static export. Prepare -> Evidence -> Build -> Results works with immutable source excerpts, candidate decisions, conditional LangGraph planning, supplied-KB research, clarification/resume, one revision maximum, final PDF/content/hash checks and actual activity records. A4, one page, one column, 11-point body text is the selected resume format.

Live mode uses **gemini-3.1-flash-lite** through **google-genai 2.23.0**. Offline remains an explicitly selected mock mode, with zero model attempts. Personal sample documents remain local/offline only; unpaid live processing accepts server-verified fictional fixtures. The supplied private resume/JD were parsed and rendered locally under ignored `output/private/local-sample/`.

## Milestones in docs/05 order

| Milestone | Verified outcome |
|---|---|
| M0 capability/skeleton | Health/static export/PDF passed. Actual nested structured output, custom function round trip and URL Context passed. Initially unavailable Linux gate is now verified in Docker. |
| M1 inputs/contracts | Immutable page/paragraph/line locators, role separation, decisions, upload limits and session boundaries pass. Fixed PDF email headers discarding the whole page during evidence proposal. |
| M2 conditional graph | Normal/platform routes differ; platform performs an actual evidence lookup for its four required gaps. KB fallback, clarification/resume, budgets and illegal-action prevention pass. |
| M3 artifacts/release | Real one-page PDFs, exact quantities, named-fact citations, qualification status, separate semantic review and exact final artifact checks pass. At most one rewrite. |
| M4 interface | Six actual Stitch screenshots and HTML exports retrieved and inspected; working desktop/mobile adaptation and browser acceptance pass. |
| M5 live integration | Three accepted real-Gemini packages: normal, missing qualifications, and explicitly controlled reviewer feedback. All final claims/citations and PDF pages manually inspected. |
| M6 evaluation | T01-T20 deterministic checks and representative live cases pass. Latest backend suite: 57 passed. Secret/private-data audit and PDF/browser inspections completed. |
| M7 deployment readiness | Linux image builds and serves a checked PDF with a 512 MiB memory cap. Health, upload, downloads, isolation, restart and container replacement checked. Render publication deferred by user. |
| M8 handoff | README, evaluation mapping, fictional packages/traces, screenshots, actual offline demo recording and presentation summary available. Team identity and final narrated competition materials remain team inputs. |

## Verification actually run

- `backend/.venv/Scripts/python.exe -m pytest backend/tests -q`: **57 passed in 74.57s**, one upstream Starlette/AnyIO deprecation warning. Includes real PDF rendering and the PDF contact-header regression.
- `npm.cmd --prefix frontend run typecheck`: passed. Next.js static export also built successfully in the final Docker image using `npm ci` and the lockfile.
- `npx.cmd playwright test`: **7 passed in 24.9s**, desktop 1440px/mobile 390px, keyboard/source comparison, downloads, refresh, input errors, clarification, controlled attention and delayed session cookie. An earlier desktop test collided with a live run occupying the single worker; all seven passed with the worker idle.
- Actual live UI inspection: fictional/live badge, 9 model attempts, 0 revisions, 7 source-linked final statements and PDF preview agree with the stored normal-case trace. Screenshots in `output/qa/live-*.png`.
- Final local Docker image `proofapply:local`: Linux amd64, Python 3.11, static UI and real WeasyPrint rendering. The mock HTTP fixture completed under 512 MiB / 1 CPU; observed memory after a run was 149.4 MiB (not peak), no OOM. Final package: `output/examples/linux-final-frontend/`.
- Container checks: health/page 200, checked PDF/JSON/Markdown downloads and same PDF hash after restart, cross-session 404s, private paths 404, PDF upload yielding 12 evidence excerpts, session clearing, old session unavailable after container replacement. See `output/qa/container-checks.json`. Runtime image excludes pytest; the full suite was run on Windows, not claimed as a Linux pytest pass.
- Visual review: final PDFs for all three live packages, both controlled-feedback drafts, Linux PDF, adapted desktop/mobile UI and live result/activity screens. All final resumes are one page with selectable text and no clipping.

## Accepted live packages

| Package under output/examples/ | Model attempts | Revisions | Coverage | Manual result |
|---|---:|---:|---:|---|
| gemini-frontend | 9 | 0 | 93.33% | Passed; Docker missing |
| gemini-platform | 10 | 0 | 11.11% | Passed; Docker, Kubernetes, CI/CD and Linux administration missing |
| gemini-feedback | 12 | 1 | 93.33% | Passed; injected unsupported 40% rejected and removed |

Each used 5 supplied fictional sources, one actual supplied-KB research action, and **zero mock calls**. Each directory has the real PDF, reports, trace, evaluation history and manual review record. The controlled harness deliberately appended the 40% claim to a real Gemini draft; it is not represented as a spontaneous model error. Export of that completed run was recovered from its local evaluation database after the runner ended before export.

The live model split REST integration and API error handling into separate required requirements, so its frontend denominator is 15 (14 supported), while the deterministic fixture uses 13 (12 supported, 92.31%). This is extraction granularity, not improved qualifications or a hiring prediction. Small-sample live success is not a general hallucination guarantee.

## Observed failures and fixes

Actual live testing found a function-result role mismatch, rejection of nested constrained schemas, and an illegal coordinator action. Corrected the SDK role, converted only the wire schema while retaining all strict local Pydantic limits, and constrained the generated action enum to currently legal choices.

Manual review rejected earlier automated successes: summary statements borrowed facts from other citations; expected graduation was omitted; course provider names lacked their own citations. Historical packages remain under `output/validation/` with NOT ACCEPTED review records; their stored downloads were revoked. Added expected-status and per-statement technology/proper-name checks, stronger writer/reviewer instructions and a download-time source recheck. Only the three packages above count as accepted.

Container testing found that a contact email in a PDF page caused the evidence filter to skip the entire page. Filtering now operates on lines while preserving original page locators and context. The new regression and actual Linux upload passed.

## Access, cost and design

The user confirmed the key belongs to a Free tier account with no payment method or credits. `capabilities.json` records actual successful nested Requirements generation, an explicit function round trip and URL Context retrieval of Google's public documentation with success metadata. Search remains disabled; no paid model fallback. A model listing alone was never counted as generation validation. The supplied AI Studio get-started URL could not be fetched by the web tool; current official Gemini structured-output, SDK and pricing documentation were used instead.

Stitch access is resolved: ProofApply Design Workspace `11030537791420483270`, all six desktop screens, PNGs and HTML exports. `design/STITCH-MANIFEST.md` records IDs, local paths, hashes and visual comparisons. Reads used a fresh client against the configured Stitch MCP endpoint because the conversation registry retained an older connection error. No remote design was edited. System fonts/mobile adaptations are deliberate; no mobile frame was returned and no pixel-perfect match is claimed.

## Preservation and limits

Original brief/fixtures/private documents remain preserved. Local commit `818234f` appeared during this validation work and was preserved. No remote push or public deployment was performed. Environment credentials, private samples, installed tools and runtime data stay ignored; Docker context excludes them and generated outputs.

Evidence establishes source support, not independent verification. Same-model review can share writer errors; deterministic named-fact/conflict rules are narrow and conservative. No OCR, arbitrary repository crawling, paid search, accounts or application submission. Content cuts are reported. Two-hour sessions and temporary storage are intentional; active jobs do not survive service restarts. Local Docker observations do not certify Render cold starts or production load. Upstream library licenses, including PyMuPDF AGPL/commercial terms, remain applicable.

## Next step

The team can run the fictional live demonstration locally, review its package, and finalize team naming, presentation and narrated submission video. Use fresh output labels when reproducing examples to preserve accepted runs. When the team supplies a Render destination/account and explicitly requests publication, deploy the prepared single Free service and verify its actual live URL. No local acceptance blocker remains.
