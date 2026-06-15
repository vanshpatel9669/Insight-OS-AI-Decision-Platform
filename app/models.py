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
