# Product requirements and scope

## Objective

Build ProofApply for Tech Zephyr 4.0 Problem Statement 11, Autonomous Resume & Application Agent. A candidate supplies base information and a target role; the system independently chooses useful actions to prepare a truthful, relevant application package. The required final package is a tailored resume PDF plus an evidence/change report. Cover letters and application submission are outside this MVP.

The source problem statement requires job-description parsing, role/company research through search or knowledge tools, candidate-evidence inspection, relevant evidence selection, PDF drafting/rendering, ATS/relevance/format/factual evaluation, replanning and revision, final verification, and an explanation of important edits. This brief paraphrases that source; its instructions are project requirements, not permission to access accounts or send applications.

## Who and what to support

- Students and early-career candidates targeting one role per run; English only in the MVP.
- One base resume plus up to four additional project/profile documents, or equivalent text input.
- PDF, DOCX, Markdown and text inputs. Text-based PDFs only; provide a clear scanned/encrypted-file alternative. Images/OCR and arbitrary repository crawling are deferred.
- A pasted JD is required. Company name, role title and official URL support research. A supplied company knowledge document/text is a first-class research source.
- One A4 single-column resume template, one-page student default, selectable two-page cap.
- One automatic revision at most. Sources are immutable; all draft versions remain identifiable within the temporary session.

## Completion conditions

1. A run has a parsed requirements list with original JD excerpts and required/preferred distinctions.
2. The researcher records sources consulted, access results and remaining uncertainty. Successful inspection of a supplied company KB qualifies; failed live access alone does not count as completed research.
3. Every substantive candidate statement in the final resume links to source evidence. Personal header fields are copied directly from local user-confirmed fields and are also checked for exact preservation.
4. Evaluations distinguish source support, role coverage, writing quality and PDF readability. No commercial ATS or hiring-success claim is made.
5. A feedback-based decision can trigger evidence retrieval, clarification, source exclusion or a rewritten draft. An unchanged happy path need not revise artificially.
6. Final PDF and reports reference the same draft version/hash and pass the release gate. Failed or uncertain factual checks prevent the completed status.
7. The user can inspect sources, decisions, role gaps, before/after changes and download passed artifacts.

## Competition alignment

| Criterion from supplied rubric | Weight | Demonstration evidence |
| --- | --- | --- |
| Agentic workflow and autonomy | 25% | Coordinator selects actions from observed gaps; different inputs produce different routes |
| Tool/environment interaction | 15% | Actual document parsing, knowledge/URL inspection, rendering and checking |
| Adaptation and failure recovery | 15% | Failed research fallback, unsupported claim removal, one targeted revision |
| Technical implementation | 15% | Typed contracts, bounded graph, real backend/frontend integration |
| Problem relevance and innovation | 10% | Claim-to-source comparison and evidence-driven tailoring |
| Prototype functionality and UX | 10% | Working input-to-download flow matching Stitch screens |
| Evaluation, verification and robustness | 10% | Counterexample tests, final artifact checks and truthful limits |

The source explicitly states that agent count and framework choice do not themselves earn points. Explain why each specialist has a useful responsibility and show what it did.

## Scope boundaries

Do not build accounts, payment screens, permanent candidate history, job applications, email sending, cover letters, recruiter ranking, interview scheduling, a template gallery, model training or a large RAG service. A small evidence lookup over the supplied documents is sufficient. ESCO/O*NET normalization is optional after the core passes, not a dependency.

If behind schedule, cut animated agent graphics, extra template styles, optional external datasets and optional live search. Preserve the evidence ledger, actual model calls, supplied-KB research, PDF checks, adaptive revision, report and tests.

## Important accuracy distinctions

“Supported by source” does not mean independently verified in the real world. A self-reported resume remains self-reported. A code repository can support what it contains but not necessarily who authored every part, the candidate's mastery, or a business outcome. Dates, metrics, credentials and ownership need appropriate source support.

Code can reject nonexistent source IDs, changed numbers, bad schemas and unapproved tools. It cannot prove that any arbitrary natural-language paraphrase is true. Add a separate semantic review and conservative abstention. A fresh reviewer context helps separation but does not eliminate correlated model errors.

Use “No unsupported claims detected in the checked draft” only when that evaluation ran. Prefer “Source checks passed” on the UI. Do not promise zero hallucinations.
