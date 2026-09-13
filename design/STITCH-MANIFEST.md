# Stitch reference manifest

Status: **all six desktop screens retrieved and inspected, 2026-09-13**.
Project: [ProofApply Design Workspace](https://stitch.withgoogle.com/projects/11030537791420483270).
Project ID: `11030537791420483270`. MCP server name: `stitch`; endpoint: `https://stitch.googleapis.com/mcp`.

## Actual access

A fresh MCP HTTP connection successfully initialized and listed 16 tools. Invoked `get_project`, `list_screens` and `get_screen` using their actual discovered schemas. Downloaded every returned screenshot and HTML export successfully. No Stitch generation, editing or project mutations were performed; no Gemini SDK was used for design access. No billing changes or purchase occurred.

The conversation's built-in MCP registry still retained an earlier startup error; retrieval used a fresh local MCP protocol client with the existing configured Stitch credential. Credentials remain outside the repository and were not sent to asset-download hosts. This is actual MCP retrieval, not browser scraping or guessed screenshots.

## Retrieved references

The screenshot downloads are smaller previews than the logical frame dimensions; both are recorded accurately. `references/screens.json` records file hashes, byte counts and retrieval timestamps without credential-bearing links.

| Frame | Screen ID | Logical desktop frame | Downloaded PNG pixels | Local assets |
|---|---|---|---|---|
| 01 - Prepare Application | `bfed38206ead4c6793320614a552d9a7` | 2560 x 3646 | 359 x 512 | [PNG](references/01.png), [HTML](references/01.html) |
| 02 - Review Evidence | `c2ca20efbba54fc29c7e60d1e591966a` | 2560 x 2900 | 452 x 512 | [PNG](references/02.png), [HTML](references/02.html) |
| 03 - Building Application | `0b2f9475162745b4ae7bd8fb7e1fe88d` | 2560 x 2620 | 500 x 512 | [PNG](references/03.png), [HTML](references/03.html) |
| 04 - Results Workspace | `4602bbc2da594aa39e0d42f8b6e00865` | 2560 x 3018 | 434 x 512 | [PNG](references/04.png), [HTML](references/04.html) |
| 05 - Source Comparison | `a7c67cd9cae84557adcf4bdea0209d34` | 2560 x 2884 | 454 x 512 | [PNG](references/05.png), [HTML](references/05.html) |
| 06 - Attention & Recovery States | `8459d6aa0eda466f94832be42688f654` | 2560 x 3856 | 340 x 512 | [PNG](references/06.png), [HTML](references/06.html) |

No desktop frame is missing. No separate mobile frame was returned by `list_screens`; mobile styling is an implementation adaptation checked at 390px, not a pixel match to an unseen mobile design.

## Export inspection and implementation

All six screenshots were visually inspected. All HTML exports were read for layout, tokens, control behavior and embedded code before adaptation. Their shared Tailwind configuration establishes mint `#f1fcf7`, green `#00513b`, white card surfaces, 12px card corners, 24px gutters and Inter typography. `tokens.json` derives the color palette from the actual export and records the system-font fallback.

Exports contain CDN Tailwind/Google Fonts scripts or styles, Material Symbols, static candidate/score/progress examples, tab/accordion/zoom handlers, and attention-state mock controls. These exports are retained only as design references and are not served or executed by the application. React handlers and the compiled local Tailwind stack implement actual interactions; no runtime CDN scripts, font requests or fictional avatar assets were copied into the app.

| Frame | Working implementation |
|---|---|
| 01 Prepare | Horizontal workflow header, mint canvas, paired experience/target cards, supporting sample/format panels, actual uploads/paste and source saves. |
| 02 Evidence | Single-column evidence cards with filters and decisions; target/context panel and actual processing/start controls. Coverage is calculated during a run rather than copying a design score before analysis. |
| 03 Build | Actual event timeline beside a document panel. A real PDF preview appears when a result exists; otherwise a clear waiting state is shown. No fabricated progress percentage or intermediate draft. |
| 04 Results | Real PDF beside checks, requirement support and source/change tabs; actual backend metrics and eligible downloads. |
| 05 Comparison | Two-column final-claim/original-excerpt dialog, exact source locator/context and evidence principle panel; native keyboard focus/ESC and real exclusion/clarification controls. Before writing, a source statement is explicitly labeled rather than presented as a rewritten claim. |
| 06 Attention | Shared amber attention styling for actual errors, clarification and needs_review; no forced quota fault or fabricated recovery ledger. Existing bounded failure behavior remains enforced by the backend. |

Deliberate differences: one-page output only per user; no invented semantic-confidence percentages, candidate IDs, verification progress, external credentials or imaginary audit stages; system Arial/Helvetica fallback rather than remote Inter; source comparison is an accessible modal in the static workspace rather than a separate route; no unsupported Help/history/publishing actions. The design's absolute no-hallucination promise is not repeated. Contact processing and offline/live labels retain the application's truthful limitations.

Visual comparison: actual 1440px and 390px application captures are under `output/qa/`. Layout, colors, typography hierarchy, source comparison and attention states were compared with the retrieved screenshots. This is a functional adaptation, not a pixel-perfect claim. Final browser/build results are recorded in BUILD_STATUS.md.

## Access history

Muse branch, 2026-09-13 ~11:35 UTC: project, all six screens and all six HTML
exports retrieved fresh via the Stitch tools. Every HTML export is
byte-identical to the morning copies, so the screens are unchanged and the UI
gap is purely adaptation. Screenshot CDN URLs returned HTTP 400 to direct
download (likely session-bound); the retained local PNGs plus fresh HTML were
used instead. No project edits, no billing changes.

On 2026-09-12 and the initial 2026-09-13 inventory checks, no callable Stitch tools were exposed. Naming the server revealed a startup failure: a credential value had been supplied as `bearer_token_env_var`. That duplicate invalid entry was removed while retaining the existing `X-Goog-Api-Key` header. A handshake then succeeded; a concurrent external config change removed the server before project retrieval. After the user reconnected it and requested another attempt, the fresh MCP client retrieved the project and all six screens listed above. The previous missing-design blocker is resolved.
