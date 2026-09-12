# Data and API contracts

## Types and storage

Implement these as Pydantic v2 models with unknown fields rejected at model/API boundaries. IDs are backend-assigned opaque values. Datetimes use UTC ISO 8601. A provider's valid JSON is still validated by application code. Store records in SQLModel tables, with structured JSON fields where that keeps the MVP smaller. Do not create a complex relational ontology.

| Record | Required fields and rules |
| --- | --- |
| Session | id, created_at, expires_at, demo flag; opaque HttpOnly cookie, no signup |
| Source | id, session_id, kind, role, display_name, sha256, extracted_text, locator_map, created_at; optional canonical URL and retrieval status |
| Evidence | id, source_id, category, subject, atomic_claim, exact_excerpt, locator, support_status, support_basis; optional exact quantities/dates/ownership |
| EvidenceDecision | evidence_id, include/exclude/clarify, reason, optional new_source_id; never edits original evidence |
| Requirement | id, jd_source_id, text, original_excerpt, importance=required/preferred, normalized_terms; split compound clauses into atomic requirements |
| ResearchFinding | id, statement, source refs, provenance, retrieval_status, observed_at, uncertainty |
| Match | requirement_id, evidence_ids, status=direct/partial/missing/unclear, explanation, included_in_draft; partial is not full proficiency |
| ResumeDraft | id, version, sha256, header_ref, summary statements, skills, education, experience, projects, page_limit |
| ResumeStatement | id, text, claim_ids, evidence_ids, requirement_ids; candidate factual content always has support |
| EvaluationIssue | id, category, severity=blocker/warning/info, statement_ids, evidence_ids, explanation, suggested_action |
| Evaluation | draft_id, draft_hash, pdf_hash, checks, issues, coverage details, semantic_review_status, evaluated_at |
| Artifact | id, session_id, run_id, kind, path, sha256, draft_hash, media_type, size_bytes, release_status |
| Activity | seq, run_id, time, actor, action, summary, source_ids, result_ids, status, mode; append-only |
| Run | id, session_id, status, graph_stage, mode, capability_snapshot, version, counters, latest result IDs, pending_question, error, timestamps |

Header name/contact fields remain outside model context and are copied by the renderer. For fictional fixtures the name is also fictional, but keep the architecture consistent. User input can supply role/location preferences separately from factual achievements. A summary sentence is not exempt from support requirements.

## Graph state

```text
run_id, session_id, input_version
source_ids, evidence_ids, evidence_decisions
requirements, research_findings, matches
drafts, current_draft_id, artifact_ids, evaluations
pending_question, latest_decision, unresolved_issues
model_attempts, research_calls, revision_count, clarification_count
execution_elapsed_seconds, cancelled, next_action
```

Large original files and full source bodies are referenced, not recopied into every graph checkpoint. The event store is the source of truth for timeline rendering. Do not stream raw graph state to the browser.

## Run lifecycle

Allowed statuses: `queued`, `running`, `awaiting_input`, `completed`, `needs_review`, `blocked`, `failed`, `cancelled`, `expired`.

- Initial ingestion and evidence review happen before generation. A run captures the current source/evidence version when started.
- Only one generation run executes at a time. If occupied, return busy with a retry hint; no unbounded queue.
- `awaiting_input` contains a pending question ID and allowed replies. Resume with a version check and an idempotency key. A repeated reply cannot start a second job.
- `completed` requires an exact passing draft/PDF/report package. It may contain honestly disclosed role gaps.
- `needs_review` means a draft exists but factual or layout uncertainty remains; disable verified downloads. Expose only a visibly unverified draft preview plus issue report.
- `blocked` means missing necessary evidence/research or unavailable quota prevents completion. `failed` is an unhandled/permanent technical failure with an actionable error.
- A cancelled job stops scheduling new nodes, and any late external response must not release artifacts. Session expiry deletes only that session's temporary files/records.

Persist source files under generated session directories. Never construct a path from the original upload filename. All record and artifact access requires the matching session cookie. Cross-session access returns 404.

## HTTP endpoints

| Method/path | Request | Success and behavior |
| --- | --- | --- |
| `GET /api/health` | none | Small process health response; no credentials, network model probe or source data |
| `GET /api/capabilities` | none | Sanitized current availability: mode, configured model label, research options, temporary_storage, live_processing_enabled |
| `POST /api/sessions` | `{demo: boolean}` | 201 session, HttpOnly SameSite cookie, expiry; no account |
| `POST /api/sources` | multipart file or text + declared input slot | 201 source ID and parse status; backend assigns source role from slot |
| `GET /api/evidence` | session cookie | Evidence and sources for review; paginate only if necessary |
| `POST /api/evidence/decisions` | evidence_id, decision, clarification_text? | Records exclusion or new self-reported source; increments input version |
| `POST /api/runs` | source_ids, role_title, company_name, page_limit, mode + Idempotency-Key | 202 run ID and status; capture input version; no duplicate generation |
| `GET /api/runs/{id}` | cookie | Latest status, stage, counters, result refs, pending question, public errors |
| `GET /api/runs/{id}/events?after=0` | cookie | Ordered events plus next_cursor; only events after supplied seq |
| `POST /api/runs/{id}/resume` | question_id, answer/exclude, expected_version + Idempotency-Key | 202; validate answer and current pause; continue same checkpoint |
| `POST /api/runs/{id}/cancel` | expected_version | 202/200; idempotent cancellation |
| `GET /api/runs/{id}/result` | cookie | Role matches, evidence map, changes, evaluations and artifact links for exact version |
| `GET /api/artifacts/{id}` | cookie | Stream eligible PDF/report, correct Content-Type and safe download filename |
| `DELETE /api/sessions/current` | cookie | Explicit clear-session UI action; deletes only current session data |

Represent official URLs, JD text and company KB as sources via their respective input slots. Extraction may occur as a bounded asynchronous ingestion task; expose parse status on evidence reads. Disable Build until ingestion and evidence review finish. Add an ingestion status endpoint only if needed; document it in generated OpenAPI.

Use 413 for oversized content, 415 for unsupported types, 422 for invalid inputs, 409 for version mismatch/busy, 429 for local limits, 503 for unavailable provider, and 404/410 for inaccessible/expired runs as appropriate. Return `{error: {code, message, retryable, retry_after_seconds?, field?}}`; never return provider credentials or raw stack traces.

Evidence extraction during ingestion can consume model calls before a generation run exists. Track those attempts at the session level too, cache extraction by source hash, and include their usage in the displayed total. Upload/reparse endpoints need the same live-access and rate-limit policy as run generation; they must not become an unmetered model endpoint.

## Example grounded statement

```json
{
  "id": "statement-1",
  "text": "Built React and TypeScript booking screens for a campus room-booking project.",
  "claim_ids": ["fact-2"],
  "evidence_ids": ["evidence-project-ui"],
  "requirement_ids": ["req-react", "req-typescript"]
}
```

The verifier must compare the statement with the original excerpt. Attaching `evidence-project-ui` to an invented 40% improvement still fails.

## Evaluation and score contracts

Three distinct layers:

1. Hard checks: IDs exist, proper source roles, exact credentials/quantities/dates preserved, no unsupported expansion detected, semantic review completed with no unresolved factual issue, rendered artifact matches checked draft, PDF readability passes.
2. Role-coverage heuristic: required weight=2, preferred weight=1; direct match=1, partial=0.5, missing/unclear=0. `100 * sum(weight * match_value) / sum(weight)`. Round only for display; denominator zero yields null, not 100. Store the mapping and reasons, not just a score. This is documented source coverage, not hiring likelihood.
3. Evidence utilization: how much available relevant evidence actually appears in the draft, plus qualitative writing comments. Missing candidate qualifications must not be counted as a fixable writing issue.

No weighted average can cancel a factual blocker. No universal threshold such as 80% can force the agent to fabricate a required skill. A score improvement is useful only when the added support is valid.

## PDF and report contracts

Generate PDF from escaped structured data and a controlled Jinja template. A4, single column, conventional headings, readable 10.5–11.5pt body, approximately 14–18mm margins, no photo or decorative icons in the resume. Prefer content cuts/reordering over shrinking type. Enforce the user's page cap. Metadata should not contain internal secrets or private source paths.

PDF checks: correct page count, nonempty selectable text, expected headings, all expected statements retained in correct broad order, no words outside page bounds, no text clipped at bottom, no unexpectedly tiny text, no missing name/contact values, and no unsupported text introduced by the renderer. Compare normalized extraction with the draft, accounting only for whitespace/hyphenation. Also rasterize and inspect pages in development; a text check does not prove attractive layout. A small Gemini visual check can flag suspicious layout but cannot waive deterministic checks.

Evidence/change report Markdown and JSON contain: run mode, target role, consulted sources and access outcomes, final claim-to-source links, requirement matches/gaps, before/after edits with reasons, dropped unsupported claims, evaluation outcomes, uncertainty, iteration count, final draft/PDF hashes and timestamp. Compare extracted base-resume content to final content as well as draft 1 to draft 2; mark additions and omissions. Generate report facts from stored records. Do not invent improvements, score gains or reviewer events.
