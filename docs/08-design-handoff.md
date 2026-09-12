# Stitch design handoff and frontend contract

## Retrieve before implementing final styling

The team will generate designs using STITCH-PROMPT.md and connect Stitch through MCP. This kit does not establish that connection or assume particular Stitch tool names. Discover the actual available connector tools; retrieve the identified project/screens and use their supported export/read functions. Do not invent a project ID or claim to have inspected screens that are unavailable.

Record in `design/STITCH-MANIFEST.md`: project URL/ID, screen ID/name, desktop/mobile dimensions, retrieval time, local reference path, exported asset/code path where available, and implementation view. Screen screenshots are sufficient visual references when richer exports are unavailable. Verify generated export links actually work.

If MCP is not accessible, request the specific missing screenshot/export while continuing the backend and temporary UI. No need to upload candidate documents or API keys to Stitch. Use the fictional design content in the prompt.

Codex supports connecting MCP servers and reading project-level instructions. Follow current product documentation if setup help is needed; this plan does not prescribe an unverified Stitch endpoint or authentication command. [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), [AGENTS.md instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## Screen to implementation mapping

| Stitch frame | App view/component | Required backend connection |
| --- | --- | --- |
| 01-Prepare | PrepareView, EvidenceUpload, TargetRoleForm | Session/source creation and ingestion status |
| 02-Evidence | EvidenceReview, SourceDrawer, ClarificationForm | Evidence list, exclusions and new-source clarification |
| 03-Build | RunWorkspace, ActivityTimeline, DraftPreview | Run creation, status/events polling, cancel and resume |
| 04-Results | ResultsWorkspace, RoleMatches, ChecksPanel, ChangesList | Result data and eligible artifact downloads |
| 05-Source-Comparison | ClaimSourceDrawer | Original source excerpts and exact claim mapping |
| 06-Attention | AttentionPanel variants | Field errors, quota, source failure, needs_review, session expiry |

Use shared Button, Input, Textarea, Badge, Tabs, Drawer, Alert, FileRow and EmptyState components. Prefer lightweight local components to adding a UI framework that conflicts with Stitch exports. Icons may use lucide-react; text labels carry status meaning. Fonts should use system fallback or be self-hosted; do not require a runtime Google Fonts request.

## Design behavior constraints

- Resume preview uses the actual rendered PDF. If a browser cannot embed it, offer the permitted artifact download or a rendered page image, with text access where practical.
- Metrics are calculated by the backend; Stitch's 92% is a fixture example only.
- Source links open the original excerpt and location. Do not substitute another AI summary for the source.
- The default reviewer screen can exclude evidence and record a clarification. It must not silently edit immutable uploaded source text.
- A result with factual/format blockers uses needs_review. Hide/disable verified-download actions. A completed result with honest skills gaps remains downloadable.
- Live, mock and recorded demonstration modes are visible and are never interchanged invisibly.
- No fake progress percentage or fabricated timeline activity. Show the current stage and elapsed time with real events.
- Contact fields are excluded from model requests; do not promise browser-only storage when hosting uses the backend.
- The app has temporary sessions rather than permanent history. Refresh can recover a running session only while that server/session remains alive.

## Static export and routing

Implement the workspace as static `/` plus client-side view/run query state. Use relative `/api` URLs. In development either use a documented backend URL with limited localhost CORS or a development proxy; production has one origin. Never expose keys through NEXT_PUBLIC variables.

Use `output: 'export'` in Next.js configuration and avoid features requiring a Next server. This hosting design uses FastAPI for all runtime requests. [Next.js static exports](https://nextjs.org/docs/app/guides/static-exports)

## Visual acceptance

Compare actual screenshots at 1440px and 390px with the retrieved Stitch views. Check typography hierarchy, spacing, colors, page structure, drawers and disabled/loading states. Test a keyboard-only journey, mobile overflow, long filenames, long job titles, empty evidence, validation errors and quota exhaustion. Inspect the white resume document separately from the surrounding styled application.

If a Stitch screen introduces unsupported features, align its visible controls with the scoped product and document the difference. Missing design states can use the established component system; avoid blocking the whole build for minor variations. Mark design fidelity unverified if references could not be inspected.
