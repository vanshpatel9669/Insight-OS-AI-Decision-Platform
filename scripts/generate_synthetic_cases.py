#!/usr/bin/env python3
"""Generates a reproducible synthetic corpus of enterprise-ops case records
and writes them to MongoDB.

This is synthetic data, generated from templates with randomized details —
not real customer records, and documented as such everywhere it's
referenced. The corpus size is a real, tested number (see --count and
docs/architecture.md), not the "1M+" figure in other materials — see
README.md's "What this repo does not claim" section for why that number
isn't reproduced here.

Usage: python scripts/generate_synthetic_cases.py --count 50000 --seed 0
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pymongo import MongoClient  # noqa: E402

from insight_os.config import get_settings  # noqa: E402
from insight_os.db.mongo import CASES_COLLECTION, ensure_indexes  # noqa: E402

TIERS = ["enterprise", "standard", "smb"]
ISSUE_TYPES = [
    "billing_discrepancy",
    "sla_breach",
    "data_export_failure",
    "integration_failure",
    "security_incident",
    "performance_degradation",
    "access_management",
    "contract_dispute",
]
OUTCOMES = ["resolved", "escalated", "sla_breach"]
SYSTEMS = ["billing-service", "auth-gateway", "data-pipeline", "reporting-api", "sso-provider"]

_SUMMARY_TEMPLATES = {
    "billing_discrepancy": (
        "Customer reported a ${amount} discrepancy on their invoice, traced to {system}."
    ),
    "sla_breach": (
        "SLA breach on {system}: {hours}h downtime exceeded contractual uptime commitment."
    ),
    "data_export_failure": (
        "Data export via {system} failed for {records} records, blocking a compliance deadline."
    ),
    "integration_failure": (
        "Third-party integration through {system} began silently dropping webhook events."
    ),
    "security_incident": (
        "Anomalous access pattern flagged on {system}, requiring credential rotation review."
    ),
    "performance_degradation": (
        "{system} p95 latency degraded to {hours}x baseline during peak hours."
    ),
    "access_management": (
        "Customer requested an urgent permissions change on {system} blocking their team."
    ),
    "contract_dispute": "Customer disputed contract terms related to {system} usage overages.",
}

_RESOLUTION_TEMPLATES = {
    "resolved": (
        "Root cause identified in {system}; fix deployed and customer confirmed resolution."
    ),
    "escalated": (
        "Escalated to engineering on-call for {system}; resolution required a hotfix release."
    ),
    "sla_breach": "SLA credit issued; {system} runbook updated to prevent recurrence.",
}


def generate_case(rng: random.Random, index: int) -> dict:
    tier = rng.choice(TIERS)
    issue_type = rng.choice(ISSUE_TYPES)
    outcome = rng.choice(OUTCOMES)
    system = rng.choice(SYSTEMS)
    summary = _SUMMARY_TEMPLATES[issue_type].format(
        amount=rng.randint(500, 50_000),
        system=system,
        hours=rng.randint(1, 12),
        records=rng.randint(100, 50_000),
    )
    resolution = _RESOLUTION_TEMPLATES[outcome].format(system=system)
    return {
        "case_id": f"CASE-{index:07d}",
        "customer_tier": tier,
        "issue_type": issue_type,
        "summary": summary,
        "resolution": resolution,
        "outcome": outcome,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=5_000)
    args = parser.parse_args()

    settings = get_settings()
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    ensure_indexes(db)
    db[CASES_COLLECTION].delete_many({})

    rng = random.Random(args.seed)
    batch: list[dict] = []
    written = 0
    for i in range(args.count):
        batch.append(generate_case(rng, i))
        if len(batch) >= args.batch_size:
            db[CASES_COLLECTION].insert_many(batch)
            written += len(batch)
            print(f"  wrote {written}/{args.count} cases", flush=True)
            batch = []
    if batch:
        db[CASES_COLLECTION].insert_many(batch)
        written += len(batch)

    print(f"Done: {written} synthetic cases in {settings.mongo_db}.{CASES_COLLECTION}")


if __name__ == "__main__":
    main()
