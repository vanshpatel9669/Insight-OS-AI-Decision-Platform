"""Pydantic request/response schemas for both subsystems: rule-based
triage decisions and case retrieval.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EnterpriseRecord(BaseModel):
    record_id: str
    customer_tier: str = "standard"
    risk_score: float = Field(ge=0, le=1)
    revenue_impact: float = Field(ge=0)
    open_issues: int = Field(ge=0)
    sla_hours_remaining: float = Field(ge=0)


class DecisionResponse(BaseModel):
    record_id: str
    decision: str
    priority_score: float
    guardrail_status: str
    recommended_workflow: str
    explanation: list[str]
    context_summary: str | None = Field(
        default=None,
        description="RAG-generated summary of similar historical cases. Only "
        "populated when include_context=true is requested and RAG "
        "generation is enabled and reachable; otherwise null.",
    )


class Case(BaseModel):
    """A historical support/ops case in the retrieval corpus."""

    case_id: str
    customer_tier: str
    issue_type: str
    summary: str
    resolution: str
    outcome: str  # "resolved" | "escalated" | "sla_breach"

    def to_document_text(self) -> str:
        return (
            f"[{self.customer_tier} | {self.issue_type} | {self.outcome}] "
            f"{self.summary} Resolution: {self.resolution}"
        )


class CaseSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class RankedCase(BaseModel):
    case: Case
    embedding_score: float
    rerank_score: float


class CaseSearchResponse(BaseModel):
    results: list[RankedCase]
    timing_ms: dict[str, float] = Field(
        description="Real per-stage latency for this request: embed_query, "
        "vector_retrieve, rerank, total. Not a benchmark claim — the "
        "actual measured cost of this specific call."
    )
