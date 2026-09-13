# Evaluation record

Fault injections are explicitly controlled application tests, not measured spontaneous Gemini mistakes. The live feedback harness uses real Gemini responses around one deliberately injected bad claim. The real PDF renderer runs during integration tests.

| Brief case | Implemented evidence |
|---|---|
| T01 normal frontend | `test_normal_real_pdf_offline_provider` plus checked fictional example |
| T02 40% with valid citation | injected `metric40`; initial gate fails, one rewrite rerenders/rechecks |
| T03 18 becomes 80 | injected `test80`; exact quantity and offline semantic checks reject |
| T04 inflated ownership | injected `ownership`; leadership/backend inflation rejected |
| T05 company/JD role confusion | injected `company_role`; no candidate evidence relation exists |
| T06 actual missing qualifications | platform journey; four gaps, 11.11% coverage, no invented skills |
| T07 course becomes certification | injected `certification`; unsupported credential blocked |
| T08 embedded instructions | malicious context classified unclear; no score or tool override |
| T09 URL fails with KB | `test_url_failure_really_uses_kb`; unavailable URL then actual supplied-KB inspection |
| T10 URL/no research | pause and new-source resume; safe stop without research |
| T11 429/timeout behavior | actual adapter fake transport: one Retry-After-respecting retry, recovery and exhaustion |
| T12 malformed structured output | schema repair bounded to one retry; invalid writer blocks |
| T13 overflow/content loss | real multipage rendering; one cut/re-render or needs_review; actual PDF text removal detected |
| T14 draft/PDF mutation | stale draft hash and modified PDF prevent download |
| T15 cancelled/expired | pending writer cancellation cannot release; expiry deletes own session only |
| T16 duplicate start/reply | idempotency returns same run/reply, no additional work |
| T17 other session | 404 for another session's run, evidence and artifacts |
| T18 bad files | malformed, unsupported, oversized, scanned and encrypted input errors |
| T19 missing/uncertain reviewer | no release; at most one rewrite; explicit needs_review |
| T20 live failure vs mock | unavailable live request creates no mock run; adapter mode never switches |

Additional checks cover conflicting dates/quantities, immutable source updates, protected origin/cookie behavior, original JD excerpts, degree abbreviations, PDF/DOCX fixture variants, and a genuine local SQLite pause/resume across application restart.

The mock reviewer verifies only exact approved excerpts. Live validation now includes manually accepted normal, missing-skills and controlled-feedback packages. Earlier automatic successes rejected during manual inspection remain labeled not accepted under `output/validation/`.

Frontend checks use real FastAPI endpoints and the actual static export, at 1440px and 390px. They test keyboard activation, source drawer dismissal, evidence review, build, real PDF/report responses, source comparison, changes, event log, refresh recovery, invalid files and session clearing.

PDF visual inspections cover the fictional example and the private single-page local rehearsal. The latter is not an AI-tailored live result; its selected excerpts require user review before application use. All six Stitch desktop screenshots and HTML exports were retrieved on 2026-09-13. Adapted desktop/mobile captures were inspected against them; system fonts and mobile layout differ intentionally, and no separate mobile reference was returned. The latest browser suite also checks actual final-claim/source comparison and scroll restoration.

## Final local result (2026-09-12)

Backend: 50 passed in 84.40 seconds; one upstream deprecation warning. Strict frontend typecheck and static export passed. Browser acceptance: six tests passed, including real clarification resume and pasted-resume/mobile validation; one attention-state test uses an explicitly controlled result fixture. Actual one-page PDF renderings were inspected. No real Gemini generation or Linux container execution occurred; neither is counted as a pass.


## Stitch adaptation validation (2026-09-13)

Strict TypeScript and static export passed. The final browser suite passed seven scenarios in 24.0 seconds against the actual local service. Added assertions for final claim/original source comparison and view scroll restoration, plus a delayed-session regression that verifies source submission is unavailable until the cookie exists. A bootstrap race discovered during visual adaptation was fixed; no backend or PDF-template code changed. All six retrieved desktop references and the 1440px/390px application captures were inspected.

## Final live and container acceptance (2026-09-13)

- Backend: **57 passed in 74.57s**, one upstream deprecation warning. Includes course-provider citation and actual PDF contact-header regressions.
- Browser: **7 passed in 24.9s** with the worker idle. Typecheck and final Docker Next static export passed. Live result/activity counters and source-linked claims inspected against the real trace.
- Free-tier Gemini 3.1 Flash-Lite: actual nested schema, custom function and URL Context probes passed. Normal: 9 attempts/0 rewrites; missing-skills: 10/0; controlled feedback: 12/1. All used 5 sources, one KB action, zero mock calls, and passed manual final source/PDF review. `output/qa/live-validation.json` records the values.
- The platform trace actually reads original evidence after finding four required gaps. The gaps remain missing. The controlled 40% claim fails both exact and real semantic checks, then disappears from the checked revision. Both PDFs were inspected.
- Manual rejection of earlier summaries/coursework revealed incomplete citations despite live reviewer approval. Per-claim named facts and expected qualification status now have additional code checks. This limited sample does not establish general model accuracy.
- Container: actual Linux image build, one-page rendering, health/static routes, PDF upload (12 evidence excerpts), downloads, isolation, restart integrity, clearing and replacement session loss passed. 512 MiB limit; 149.4 MiB observed after a run, not peak. Runtime image has no pytest; no Linux full-suite claim. `output/qa/container-checks.json` records the checks.

Normal live coverage is 14/15 (93.33%) versus fixed-fixture 12/13 (92.31%): the model separately extracted REST integration and API error handling. Platform coverage remains 1/9 (11.11%). Scores reflect requirement granularity and are not candidate improvement or a hiring prediction. Deployment/cold-start validation is separate and deferred by the user.
