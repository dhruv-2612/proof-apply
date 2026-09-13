# Demo and presentation handoff

> Muse branch: the UI no longer preloads any sample. All flows below use data
> entered manually through the Prepare inputs (paste or upload); the backend
> `/api/demo` fixture endpoint and mock provider remain for tests and offline
> use only. The UI suite (`frontend/tests/journey.spec.ts`) now drives the full
> journey with fixture files entered manually and still asserts the 92% normal
> coverage, proving parity with the old preloaded path.

## What is available now

## What is available now

- Actual silent recording: `output/demo/mock-workflow.webm`. The visible mode badge says offline/mock. It is not a live Gemini run or a simulated live replay.
- Fictional checked outputs and traces: `output/examples/mock-frontend/` and `output/examples/mock-platform/`.
- Desktop/mobile screenshots: `output/qa/`.
- Private local sample rehearsal: `output/private/local-sample/`, excluded from Git. Never use personal documents in the free Gemini demo.

## Four-minute rehearsal

1. **0:00–0:30, goal:** Explain that ProofApply prepares one truthful resume and an evidence report. Enter the resume, job description and company context manually through Prepare. State the processing engine before starting.
2. **0:30–1:00, evidence:** Open the project contribution excerpt. Show original location and self-reported status. Approve supported excerpts, excluding unclear context.
3. **1:00–2:00, work:** Start the run. Show actual research provenance, requirement matching, rendering and review events. The offline recording makes zero model calls. The accepted live normal run made 9 actual model attempts; select live mode explicitly for a new live rehearsal.
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

**6. Honest limitations and next gate.** Three live Gemini packages and Linux/Docker execution now pass local acceptance. All six Stitch desktop references are retrieved and adapted. Deployment files are prepared, not published. Same-model review can share errors and self-reported sources are not independently verified.

The team must supply its real team name and organizer-required submission naming. Do not substitute ProofApply for the team's identity. A finished presentation deck and narrated competition video can build on this summary after the live validation gate is resolved.

## Accepted live examples

`output/examples/gemini-frontend/`, `gemini-platform/` and `gemini-feedback/` preserve real PDFs, source-linked reports, traces, evaluations and manual review records. Counts: 9/10/12 model attempts, 0/0/1 rewrites, zero mock calls. The controlled feedback case deliberately injects 40%; identify this before showing its first draft. The live normal ratio is 93.33%, due to separately extracted REST/error-handling requirements; the offline recording remains 92.31%. Neither ratio predicts hiring.

The existing video is an actual silent offline recording. It remains useful as an explicitly labeled fallback, not as a recording of live Gemini execution. Team naming and a final narrated competition video/presentation remain team work; public Render publication was deferred.
