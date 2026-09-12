# Demo and presentation handoff

## What is available now

- Actual silent recording: `output/demo/mock-workflow.webm`. The visible mode badge says offline/mock. It is not a live Gemini run or a simulated live replay.
- Fictional checked outputs and traces: `output/examples/mock-frontend/` and `output/examples/mock-platform/`.
- Desktop/mobile screenshots: `output/qa/`.
- Private local sample rehearsal: `output/private/local-sample/`, excluded from Git. Never use personal documents in the free Gemini demo.

## Four-minute rehearsal

1. **0:00–0:30, goal:** Explain that ProofApply prepares one truthful resume and an evidence report. Choose the fictional frontend sample. State the processing mode before starting.
2. **0:30–1:00, evidence:** Open the project contribution excerpt. Show original location and self-reported status. Approve supported excerpts, excluding unclear context.
3. **1:00–2:00, work:** Start the run. Show actual research provenance, requirement matching, rendering and review events. The offline demo makes zero model calls; a future live demo must pass the separate Gemini gate first.
4. **2:00–3:00, adaptation:** Show the platform fixture's extra evidence lookup and four missing requirements. For unsupported-claim recovery, run the clearly labeled fault-injection test below. Do not claim the injected error occurred spontaneously in Gemini.
5. **3:00–4:00, result:** Show the real one-page PDF, a claim/source link, Docker as a genuine gap, and both report downloads. Explain that source coverage is not a hiring prediction.

Controlled recovery command:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/test_failure_gates.py -k metric40 -v
```

The test injects an invented 40% saving attached to a real evidence ID. It verifies first-draft rejection, one revision, a different rendered PDF, and successful checks of the final exact draft.

## Presentation summary

**1. Problem and scope.** Students and early-career candidates need role-specific resumes without invented qualifications. Output is an A4 single-column PDF and an auditable evidence/change report. No application submission or account system.

**2. Evidence design.** Immutable original excerpts, locators, hashes and source roles. Inclusion decisions are separate from evidence. A real source ID is traceability, not proof that arbitrary rewritten wording is supported.

**3. Decisions and tools.** A LangGraph coordinator chooses from legal actions based on research, gaps and review results. Specialists have scoped contexts. Deterministic code parses files, enforces limits, renders PDFs and owns final release.

**4. Adaptation and verification.** The platform fixture takes an extra source lookup. Missing company research can pause and resume from SQLite. Controlled bad claims fail; at most one rewrite is allowed. The PDF, evaluation and reports must share the exact checked hashes.

**5. Measured local results.** Normal fixture: 92.31% source coverage with Docker missing. Platform fixture: 11.11% with four required qualifications missing. Both produce actual checked PDFs in explicit offline mode. Show the test results in BUILD_STATUS.md, including any remaining blockers.

**6. Honest limitations and next gate.** No live Gemini package yet; billing-disabled free-tier confirmation and capability probes remain necessary. All six Stitch desktop references are retrieved and adapted; Linux/Docker execution remains unverified. Deployment files are prepared, not published. Same-model review can share errors and self-reported sources are not independently verified.

The team must supply its real team name and organizer-required submission naming. Do not substitute ProofApply for the team's identity. A finished presentation deck and narrated competition video can build on this summary after the live validation gate is resolved.
