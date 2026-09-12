# What the team should give Codex

## Essential inputs

| Input | How to provide it | Why it matters |
| --- | --- | --- |
| This entire build kit | Copy into the application repository as described in 00-START-HERE.md | Complete behavior, architecture, contracts, tests and implementation order |
| Stitch design reference | Project URL/ID, selected screen IDs, connected MCP; exported screenshots/code/assets as fallback | Prevents Codex from guessing the intended UI |
| Gemini API setup | Set GEMINI_API_KEY in backend environment; give the selected model ID and free-tier status as text | Enables actual model calls and determines available research tools |
| Repository and team details | Target repository/folder, actual team name, deadline/timezone, skills/team size | Sets implementation location, ownership and submission naming |
| Fictional test documents | Included sample-data folder | A reproducible source of truth without personal-data exposure |

The original hackathon DOCX is helpful to retain in a reference folder. Its relevant workflow and rubric are already captured in docs/01. Do not paste secrets into Markdown, chat, frontend code or Stitch. Having a Gemini chat subscription alone does not finish API setup.

## Useful extra material

- A genuine target JD from an employer's official listing, with URL and capture date. It can be used with a fictional candidate for a live demo.
- The company's About/Careers/engineering page URLs, or a short supplied company KB with source URLs and capture dates. The latter enables a research path without search access.
- A fictional or fully non-personal base resume as both text-based PDF and DOCX to exercise both parsers. During the build, Codex can generate these from the supplied Markdown and compare extraction against the original text.
- A project README or report naming individual contributions, technology actually used, test counts and any legitimately measured result. Keep scope and ownership clear.
- One example of an intentionally missing qualification and one conflicting claim/date for testing. Included test cases already cover these patterns.
- A screenshot of a preferred professional resume layout if you want to change the single-column default. Keep the application's visual design and the resume's printable layout distinct.

For real personal resumes, restrict initial use to local parsing/visual checks unless the processing service and data arrangement permit that use. Do not assume superficial redaction makes an entire resume suitable for the unpaid Gemini API.

## Images and assets

No image generation, stock photos or paid assets are needed. The app can use the ProofApply wordmark, line icons and CSS. If the team has an existing logo, supply SVG or transparent PNG plus permission to use it. Stitch screenshots and the fictional resume preview provide much more useful build context than decorative images.

## Fill this short handoff note

```text
Team name:
Deadline and timezone:
Team size and familiar languages:
Repository/folder:
Stitch project URL/ID:
Selected screen IDs or exported reference folder:
Gemini API key configured in backend environment: yes/no
Gemini model ID with confirmed free access, if known:
Search grounding / URL Context probe results, if known:
Use included fictional samples initially: yes
Render account available for later deployment: yes/no
Other required hackathon rules:
```

Unknown optional fields should not block the initial build. Codex should use the kit defaults, record assumptions and continue with work that is independent of missing inputs.
