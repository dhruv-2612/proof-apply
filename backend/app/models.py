from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4
import hashlib, json
from pydantic import BaseModel, ConfigDict, Field

def uid(): return uuid4().hex
def now(): return datetime.now(timezone.utc).isoformat()
def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()
class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')
class Header(Strict):
    name: str = Field(min_length=1, max_length=100)
    contact: str = Field(default='', max_length=240)
class SessionInput(Strict):
    demo: bool = False
class EvidenceDecision(Strict):
    evidence_id: str
    decision: Literal['include','exclude','clarify']
    reason: str = Field(default='', max_length=500)
    clarification_text: str | None = Field(default=None, max_length=2000)
class Requirement(Strict):
    id: str
    jd_source_id: str
    text: str = Field(min_length=1, max_length=500)
    original_excerpt: str = Field(min_length=1, max_length=2000)
    importance: Literal['required','preferred']
    normalized_terms: list[str] = Field(max_length=15)
class Requirements(Strict):
    requirements: list[Requirement] = Field(min_length=1, max_length=50)
class Match(Strict):
    requirement_id: str
    evidence_ids: list[str] = Field(max_length=20)
    status: Literal['direct','partial','missing','unclear']
    explanation: str = Field(max_length=700)
    included_in_draft: bool = False
class Fit(Strict):
    matches: list[Match] = Field(max_length=50)
    relevant_evidence_ids: list[str] = Field(max_length=80)
class Statement(Strict):
    id: str
    text: str = Field(min_length=1, max_length=1200)
    section: Literal['Summary','Skills','Education','Experience','Projects','Coursework']
    claim_ids: list[str] = Field(min_length=1, max_length=8)
    evidence_ids: list[str] = Field(min_length=1, max_length=8)
    requirement_ids: list[str] = Field(max_length=30)
class Writing(Strict):
    statements: list[Statement] = Field(min_length=1, max_length=40)
    edit_reason: str = Field(max_length=1000)
class Verdict(Strict):
    statement_id: str
    status: Literal['supported','contradicted','uncertain']
    reason: str = Field(max_length=1000)
class Review(Strict):
    verdicts: list[Verdict] = Field(max_length=40)
    writing_notes: list[str] = Field(max_length=15)
class Decision(Strict):
    action: Literal['research','inspect_evidence','assess_fit','ask_user','draft','revise','finalize','needs_review','blocked']
    reason: str = Field(max_length=500)
    target_ids: list[str] = Field(default_factory=list, max_length=20)
    task_instruction: str = Field(default='', max_length=500)
    expected_observation: str = Field(default='', max_length=500)
class ResearchChoice(Strict):
    tool: Literal['inspect_company_kb','research_official_urls']
    question: str = Field(min_length=1, max_length=500)
    source_ids: list[str] = Field(min_length=1, max_length=3)
class RunInput(Strict):
    source_ids: list[str] = Field(min_length=2, max_length=12)
    role_title: str = Field(min_length=1, max_length=160)
    company_name: str = Field(min_length=1, max_length=160)
    page_limit: Literal[1,2] = 1
    mode: Literal['mock','gemini'] = 'mock'
    header: Header
    expected_input_version: int
    demo_access_code: str = Field(default='', max_length=200)
class ResumeInput(Strict):
    question_id: str
    answer: str = Field(default='', max_length=3000)
    exclude: bool = False
    expected_version: int
class CancelInput(Strict):
    expected_version: int
class DemoInput(Strict):
    scenario: Literal['frontend','platform'] = 'frontend'
class ToolResult(Strict):
    status: Literal['ok','partial','error']
    data: Any = None
    source_refs: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error_code: str | None = None
class EvidenceItem(Strict):
    locator: str = Field(min_length=1, max_length=200)
    exact_excerpt: str = Field(min_length=10, max_length=2000)
    category: Literal['Summary','Skills','Education','Experience','Projects','Coursework']
class EvidenceProposal(Strict):
    items: list[EvidenceItem] = Field(min_length=1, max_length=150)
class TargetDetect(Strict):
    role_title: str = Field(min_length=1, max_length=160)
    company_name: str = Field(min_length=1, max_length=160)
class CompanyBrief(Strict):
    summary: str = Field(min_length=1, max_length=2000)
    key_facts: list[str] = Field(max_length=10)
