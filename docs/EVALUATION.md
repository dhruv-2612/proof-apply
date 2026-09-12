# Evaluation record

All fault injections are deterministic application tests, not measured spontaneous Gemini mistakes. The real PDF renderer runs during integration tests.

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

The mock reviewer verifies only exact approved excerpts. The live reviewer adapter exists but has not been called on a generation run. At least one inspected real Gemini package is still an unresolved acceptance gate; the requested normal/missing-skill/feedback live comparison is not available.

Frontend checks use real FastAPI endpoints and the actual static export, at 1440px and 390px. They test keyboard activation, source drawer dismissal, evidence review, build, real PDF/report responses, source comparison, changes, event log, refresh recovery, invalid files and session clearing.

PDF visual inspections cover the fictional example and the private single-page local rehearsal. The latter is not an AI-tailored live result; its selected excerpts require user review before application use. Desktop and mobile UI captures are inspected, but no Stitch fidelity comparison is possible without the missing references.

## Final local result (2026-09-12)

Backend: 50 passed in 84.40 seconds; one upstream deprecation warning. Strict frontend typecheck and static export passed. Browser acceptance: six tests passed, including real clarification resume and pasted-resume/mobile validation; one attention-state test uses an explicitly controlled result fixture. Actual one-page PDF renderings were inspected. No real Gemini generation or Linux container execution occurred; neither is counted as a pass.
