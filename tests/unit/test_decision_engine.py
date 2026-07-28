from insight_os.decision_engine import DecisionEngine
from insight_os.models import EnterpriseRecord


def _record(**overrides: object) -> EnterpriseRecord:
    defaults: dict[str, object] = {
        "record_id": "R1",
        "customer_tier": "standard",
        "risk_score": 0.5,
        "revenue_impact": 10_000,
        "open_issues": 1,
        "sla_hours_remaining": 40,
    }
    defaults.update(overrides)
    return EnterpriseRecord.model_validate(defaults)


def test_high_risk_enterprise_escalates():
    record = _record(
        customer_tier="enterprise",
        risk_score=0.9,
        revenue_impact=100_000,
        open_issues=6,
        sla_hours_remaining=2,
    )
    result = DecisionEngine().decide(record)
    assert result.decision == "escalate"
    assert result.recommended_workflow == "executive-ops-war-room"


def test_low_risk_monitors():
    record = _record(risk_score=0.1, revenue_impact=1_000, open_issues=0, sla_hours_remaining=48)
    result = DecisionEngine().decide(record)
    assert result.decision == "monitor"
    assert result.recommended_workflow == "standard-ops-queue"


def test_guardrail_triggers_on_high_risk_score():
    record = _record(risk_score=0.9, revenue_impact=1_000)
    result = DecisionEngine().decide(record)
    assert result.guardrail_status == "requires_human_approval"


def test_guardrail_triggers_on_high_revenue_impact():
    record = _record(risk_score=0.1, revenue_impact=300_000)
    result = DecisionEngine().decide(record)
    assert result.guardrail_status == "requires_human_approval"


def test_guardrail_passes_below_thresholds():
    record = _record(risk_score=0.5, revenue_impact=10_000)
    result = DecisionEngine().decide(record)
    assert result.guardrail_status == "passed"


def test_score_is_bounded_at_one():
    record = _record(
        customer_tier="enterprise",
        risk_score=1.0,
        revenue_impact=1_000_000,
        open_issues=100,
        sla_hours_remaining=0,
    )
    result = DecisionEngine().decide(record)
    assert result.priority_score <= 1.0


def test_context_summary_defaults_to_none():
    result = DecisionEngine().decide(_record())
    assert result.context_summary is None


def test_context_summary_passed_through():
    result = DecisionEngine().decide(_record(), context_summary="similar cases suggest X")
    assert result.context_summary == "similar cases suggest X"
