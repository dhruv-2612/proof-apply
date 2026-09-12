# Fictional sample pack

All people, institutions, companies, projects and results in this folder are invented for development and demonstration. They are not anyone's actual qualifications. Keep this folder labeled as sample data. Do not insert its facts into a real candidate's resume.

## Main journey

Upload [candidate-base.md](candidate-base.md), [project-evidence.md](project-evidence.md), and optionally [course-evidence.md](course-evidence.md) as candidate sources. Paste [job-frontend.md](job-frontend.md) as the JD and use [company-knowledge.md](company-knowledge.md) as company knowledge. Use the fictional header Mira Rao and `mira@example.com`; do not attempt to contact that address.

Expected selection: React, TypeScript, REST API integration, unit tests, Git, and accessible interface work. Docker remains a preferred-skill gap. The course on cloud foundations does not prove AWS certification. The writer can improve clarity and specificity but must not invent a performance metric or leadership role.

The fixture company uses a reserved `.example` domain and should never be researched as a real company. Research it through the supplied KB. A separate non-personal live-source test can use an actual employer's official website supplied by the team.

## Other tests

Use [job-platform.md](job-platform.md) to test a large genuine role gap. Use [adversarial-input.txt](adversarial-input.txt) only in a labeled adversarial test. [expected-cases.json](expected-cases.json) defines assertions and controlled draft mutations; it contains test oracles, not model responses or instructions for real runs.

In M1, create binary parser fixtures from the same fictional Markdown: one text-based PDF and one DOCX. Check extracted text against the Markdown and maintain location mappings. A separate long synthetic resume can exercise two-page overflow. These binary samples are intentionally generated during implementation so the team's actual parser/render environment is exercised. No real personal resume is required.

## Source distinctions

Candidate sources may support candidate statements. Company knowledge and JDs may guide research/matching only. The test oracle must never enter a live model's candidate context. Explicit expected IDs are stable test labels; the running app can create its own IDs and map them in the test harness.
