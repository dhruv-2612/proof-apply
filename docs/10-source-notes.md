# Source notes and corrections

Prepared 12 September 2026. The stack is a project recommendation; official references below support capability or deployment facts. Recheck version-sensitive details when implementation begins. No API key, Stitch project or deployment was accessed while creating this kit.

## Primary project source

The supplied `Tech_Zephyr_4.0_Agentic_AI_Final_Problem_Statements.docx`, Problem Statement 11 and its adjacent submission requirements/rubric. Relevant text was extracted from the document. Page layout could not be rendered in the available environment, so no page numbers are asserted. The project requirements are reproduced in substance in docs/01.

## Official technical references

| Topic | Reference | Implementation implication |
| --- | --- | --- |
| Gemini SDK | [Google API libraries](https://ai.google.dev/gemini-api/docs/libraries) | Use the official google-genai package and its current supported API |
| Gemini schemas | [Structured output](https://ai.google.dev/gemini-api/docs/structured-output) | Model response schemas plus independent Pydantic validation |
| Gemini tools | [Function calling](https://ai.google.dev/gemini-api/docs/function-calling) | Model selects named functions; the application executes validated calls |
| Research | [URL Context](https://ai.google.dev/gemini-api/docs/url-context), [Search grounding](https://ai.google.dev/gemini-api/docs/google-search) | Public-page research and returned provenance; check model/tool availability |
| Model cost | [Pricing](https://ai.google.dev/gemini-api/docs/pricing), [Billing](https://ai.google.dev/gemini-api/docs/billing) | Verify API tier, exact model and quota before live work |
| Data terms | [Gemini terms](https://ai.google.dev/gemini-api/terms) | Fictional/non-personal input for unpaid demonstration |
| Graph structure | [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) | Nodes can be ordinary code or model tasks; conditional edges control flow |
| State | [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) | Checkpoint by run and resume narrow human clarifications |
| Frontend hosting | [Next.js static export](https://nextjs.org/docs/app/guides/static-exports) | Prebuilt frontend, no required runtime Next.js server |
| PDF runtime | [WeasyPrint first steps](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) | Test native dependencies in the deployment container early |
| Free hosting | [Render Free](https://render.com/docs/free), [Render FAQ](https://render.com/docs/faq) | Ephemeral storage, idle wake-up and usage caps; no paid upgrades |
| Stitch design | [Google's Stitch introduction](https://developers.googleblog.com/en/stitch-a-new-way-to-design-uis/) | Natural-language/image input and available design/code handoff; use actual exports |
| Coding context | [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | Discover connected tools and keep persistent project instructions |

## Clarifications from the earlier discussion

1. Assigning work to specialists does not make them mistake-free. A reviewer has its own error rate. Evidence checks and measured tests remain necessary.
2. A rule that every claim has an evidence ID does not prove semantic truth. The exact wording must be supported by the source.
3. Search-grounding availability is model-specific; the earlier blanket free-tier restriction was too broad. The capability probe is the implementation authority.
4. A Render Free SQLite file is temporary. Local checkpoint persistence and hosted restart recovery are different capabilities.
5. Mocked failures are useful tests, but cannot be presented as measured live model behavior. Design metrics are illustrative until replaced by actual calculations.
6. Research through a supplied company knowledge source is within the problem statement. It is an appropriate fallback when live access is unavailable.
7. “ATS checks passed” means this app's documented checks passed, not that every commercial applicant-tracking system will accept or rank the resume highly.

This kit does not require paid training datasets or commercial ATS validation. Optional occupational taxonomies can be evaluated after the core build; they are not candidate evidence.
