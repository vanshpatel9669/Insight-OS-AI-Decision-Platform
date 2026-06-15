class DecisionEngine:
    def score(self, record):
        tier_bonus = 0.15 if record.customer_tier.lower() == "enterprise" else 0.05
        revenue_factor = min(record.revenue_impact / 100000, 1) * 0.25
        issue_factor = min(record.open_issues / 10, 1) * 0.20
        sla_factor = (1 - min(record.sla_hours_remaining / 48, 1)) * 0.25
        score = record.risk_score * 0.35 + revenue_factor + issue_factor + sla_factor + tier_bonus
        return round(min(score, 1.0), 3)

    def decide(self, record):
        score = self.score(record)
        explanation = [
            f"Risk contribution from model score: {record.risk_score:.2f}",
            f"Revenue impact considered: ${record.revenue_impact:,.0f}",
            f"Open operational issues: {record.open_issues}",
            f"SLA remaining: {record.sla_hours_remaining} hours",
        ]
        if score >= 0.80:
            decision, workflow = "escalate", "executive-ops-war-room"
        elif score >= 0.55:
            decision, workflow = "prioritize", "customer-success-technical-review"
        else:
            decision, workflow = "monitor", "standard-ops-queue"
        guardrail = "requires_human_approval" if record.risk_score > 0.85 or record.revenue_impact > 250000 else "passed"
        return {
            "record_id": record.record_id,
            "decision": decision,
            "priority_score": score,
            "guardrail_status": guardrail,
            "recommended_workflow": workflow,
            "explanation": explanation,
        }
