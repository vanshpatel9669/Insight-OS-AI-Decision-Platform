from app.decision_engine import DecisionEngine
from app.models import EnterpriseRecord

def test_high_risk_escalates():
    record = EnterpriseRecord(record_id="R1", customer_tier="enterprise", risk_score=0.9, revenue_impact=100000, open_issues=6, sla_hours_remaining=2)
    result = DecisionEngine().decide(record)
    assert result["decision"] == "escalate"
