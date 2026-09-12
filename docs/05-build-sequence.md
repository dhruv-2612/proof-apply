# Ordered two-day build sequence

## Working assumptions

There are 48 elapsed hours and a team of roughly 2–4 people using Codex. These are planning allocations, not promises of build duration or a requirement for anyone to remain awake continuously. Assign an integration owner. If people work in parallel, agree on docs/03 contracts first and avoid simultaneous edits to the same files. Backend/agent, frontend/design, and test/demo responsibilities can proceed independently after the first milestone.

The coding agent should implement stages in order, verify each gate and continue. Update BUILD_STATUS.md after every milestone with passed checks, real output, open issues and the next action. A missing live API key blocks live tests, not schemas, mock integration, UI or PDF work. A missing Stitch connection blocks final visual matching, not backend progress.

## Repository target

```text
AGENTS.md
README.md
BUILD_STATUS.md
docs/                         this implementation brief
design/
  STITCH-MANIFEST.md           actual project/screen IDs and retrieved assets
  tokens.json
  references/                 exported screen images and design assets
backend/
  pyproject.toml
  uv.lock                     or a reproducible lock for the selected installer
  app/
    main.py
    config.py
    api/                      sessions, sources, runs, artifacts
    models/                   Pydantic schemas and SQLModel tables
    services/                 jobs, storage, source extraction, events
    agents/                   graph, coordinator, evidence, research, fit, writer, reviewer
    providers/                Gemini adapter, mock adapter, capability probe
    tools/                    evidence lookup, research, render, validate
    prompts/                  versioned instruction templates
    templates/                resume.html, resume.css, bundled font if needed
  tests/                      unit, contract, integration, controlled failure cases
  scripts/                    capability check, fixture conversion, evaluation runner
frontend/
  package.json
  package-lock.json
  next.config.ts
  src/app/                    static page, layout, global styles
  src/components/             workspace views and shared controls
  src/lib/                    API types/client, event polling, view state
sample-data/                  supplied fictional fixtures; never production defaults
Dockerfile
render.yaml
.env.example
.gitignore
```

Do not create empty modules merely to match the tree. Group small functions sensibly. Use exact filenames that fit the selected stable framework version and document variations.

## M0 — Capability and deployment skeleton — hours 0–3

- Inspect repository, requirements and official current docs. Confirm Python/Node versions, model API compatibility and licenses. Pin tested packages and frontend lockfiles.
- Create a FastAPI health endpoint, static Next.js shell, environment parsing and mock provider interface.
- Produce a minimal Linux container with WeasyPrint dependencies and confirm it can generate a small valid PDF before building other features. Do not leave PDF installation until the final hours.
- Implement the Gemini capability probe with fictional text: structured output, one custom tool round trip, selected model access, URL Context, and optional search grounding tested separately. Do not enable billing. Capture access results without logging the API key.
- Retrieve Stitch references if available; record actual IDs/screens. Backend work continues without them.

Gate: `/api/health` works; frontend static export builds; a minimal PDF renders in the target environment; capability report identifies live features, unavailable features and mock mode honestly.

## M1 — Inputs, evidence and contracts — hours 3–8

- Implement ephemeral sessions, secure file paths, upload/text slots, limits and parsing for supported formats.
- Parse supplied fictional Markdown immediately; create PDF/DOCX variants from that same content for parser tests. Preserve page/paragraph locators and reject image-only/encrypted files clearly.
- Implement Sources, Evidence, Requirements, Matches, ResumeDraft and Evaluation schemas. Validate excerpts against actual extracted text.
- Add exclusions/clarifications as separate records and version inputs. Implement evidence-review UI against real endpoints.
- Keep contact fields outside model input. Label fictional fixtures, self-report and source support correctly.

Gate: fixtures produce traceable candidate facts and JD requirements; invalid input receives a useful error; cross-session access is blocked; the user can inspect a claim and source excerpt.

## M2 — Coordinator and specialist graph — hours 8–14

- Implement the coordinator action schema and code-owned prerequisite/budget policy.
- Add scoped evidence, researcher, fit, writer and quality-review tasks using docs/04.
- Implement `read_evidence` and `inspect_company_kb` first. Add URL Context through the adapter and optional free search only when its probe passes.
- Integrate one focused clarification pause and resume path with version/idempotency checks.
- Store concise decisions and tool outcomes as events; expose run status and incremental polling.
- Use seeded model responses only in explicitly labeled mock tests. Build actual conditional graph edges now, not a list of prompts that always executes identically.

Gate: two fixture scenarios take different routes; an unavailable URL chooses supplied KB; an unsupported metric leads to targeted revision or rejection; invalid supervisor finalization is refused.

## M3 — Resume and verification — hours 14–20

- Implement escaped structured resume data to a single A4 HTML/CSS template to PDF.
- Implement exact-value/role checks, per-claim semantic review, relevance coverage, writing notes, PDF text/geometry checks and final artifact hashing.
- Implement the one-revision loop. Every new draft invalidates previous evaluation and PDF release status.
- Generate evidence/change reports from stored records, including base-to-final and draft-to-draft edits.
- Preserve passing draft versions; unresolved blockers yield needs_review. An honest optional Docker gap may coexist with completion.

Gate: a complete mock-backed journey creates real PDF and reports; seeded unsupported claims fail; repaired claims pass after actual rerender/recheck; inspected pages look clean.

## M4 — Stitch UI implementation — hours 20–26

- Adapt retrieved Stitch screens into shared components/tokens, following docs/08. Use actual data contracts, no fixed metrics.
- Wire Prepare, Evidence, Build, Results, source drawer and attention variants.
- Use accessible file input, inline validation, consistent status badges, human-readable events, polling/reconnect and genuine downloads.
- Use static page/query-based view state compatible with one hosted service. Restore active run IDs within the current session only; avoid persisting personal source text in localStorage.
- Handle mobile resume preview with a fit-to-width view/download alternative.

Gate: one user can operate the full journey using only the UI at desktop and mobile widths; every visible action works or is explicitly disabled for a stated reason; static export succeeds.

## M5 — Live integration and relevance — hours 26–32

- Run the selected Gemini model on fictional candidate data and supplied company KB.
- Verify actual tool calls, SDK response parsing, schemas and bounded adaptation. Fix observed errors rather than prompt-bloating.
- If available, test one real official company URL with non-personal research input and record provenance. Never search for the fictional employer as if it were real.
- Check that model attempts, revisions and source counts in the UI match the trace.
- Run the normal fixture and a case with insufficient skills. The second must disclose gaps, not create expertise.

Gate: at least one real Gemini end-to-end run produces a checked package; controlled failure cases behave honestly. If quota prevents this, report the live gate as blocked and continue offline tests without claiming a live pass.

## M6 — Evaluation and hardening — hours 32–38

- Run all required tests in docs/06 with deterministic fixtures; rerun representative semantic checks live when quota permits.
- Test source-role confusion, valid citation with unsupported wording, date/ownership conflict, 429/timeout, expired session, malformed uploads and version mismatch.
- Inspect both PDF versions and browser views; measure approximate memory/runtime under a single job.
- Review logs, bundle and repository for secrets and accidental personal data. Verify source files are not publicly served.

Gate: no known failure of the release gate; no stale downloadable artifacts; errors and limitations are visible; frontend build and backend suite pass.

## M7 — Free deployment readiness — hours 38–43

- Complete the multi-stage container and Render Free configuration in docs/07. Test one-origin routes locally through the container.
- Package a local startup path for the team and a checked fictional example package. Explain temporary storage and how to download results before expiry.
- Prepare the deployment; when the team explicitly requests publication and account access exists, deploy and check the actual URL. If access is missing, provide reproducible steps and mark live hosting unverified.
- On a deployed instance, check cold-start behavior, health, upload, model run, download, session isolation and restart/expiry behavior.

Gate: container works; either live deployment verified or deployment steps and exact blocker documented. Do not quietly upgrade plans to fix resource issues.

## M8 — Demonstration and handoff — hours 43–48

- Freeze features. Fix blockers only.
- Rehearse a short goal-to-result live demonstration and a clearly labeled controlled failure/recovery demonstration.
- Record demo video, preserve downloaded example artifacts and write the README covering architecture, setup, model access, limits, eval results and local fallback.
- Prepare a presentation summary and repository submission naming following the organizers' requirements; the team supplies its actual team name.
- Record final BUILD_STATUS.md with tested commands, deployment URL if verified, which evaluations were live versus mocked, and remaining limitations.

Gate: another teammate can start the app from the README, reproduce the main fictional case, and explain how the agent adapts. Demo claims match measured behavior.

## If the schedule slips

At hour 20 there must be an end-to-end path to a real PDF. If not, simplify the visual shell and focus on M3 before adding extras. At hour 32 stop new features. A supplied-KB researcher with live Gemini reasoning and good failure recovery is acceptable under the brief; paid search is not a required dependency. Maintain a real model path even when a separate offline demonstration exists.

## BUILD_STATUS template

```markdown
# Build status
Current milestone:
Working end-to-end behavior:
Last successful backend checks:
Last successful frontend build:
Last inspected PDF/UI:
Live Gemini capability/results (or blocker):
Stitch references actually inspected:
Hosting status (local/prepared/live verified):
Known limitations and failing tests:
Next concrete step:
Decisions changed from brief, with reason:
```
