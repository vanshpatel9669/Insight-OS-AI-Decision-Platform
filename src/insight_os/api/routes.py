"""HTTP routes — thin; retrieval/generation/decision logic all live in
their own modules, this file only wires requests to them.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from llama_index.llms.ollama import Ollama
from pymongo.database import Database

from insight_os.api.dependencies import (
    get_db,
    get_decision_engine,
    get_generator,
    get_search_service,
)
from insight_os.db.mongo import DECISIONS_COLLECTION
from insight_os.decision_engine import DecisionEngine
from insight_os.logging_config import get_logger
from insight_os.models import (
    CaseSearchRequest,
    CaseSearchResponse,
    DecisionResponse,
    EnterpriseRecord,
)
from insight_os.rag.generator import generate_context_summary
from insight_os.retrieval.search_service import SearchService

router = APIRouter()
logger = get_logger(__name__)

DbDep = Annotated[Database, Depends(get_db)]
EngineDep = Annotated[DecisionEngine, Depends(get_decision_engine)]
SearchDep = Annotated[SearchService, Depends(get_search_service)]
GeneratorDep = Annotated[Ollama | None, Depends(get_generator)]


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(db: DbDep, search: SearchDep) -> dict:
    db.command("ping")
    return {"status": "ready", "case_count": search.case_count}


def _record_query_text(record: EnterpriseRecord) -> str:
    return (
        f"{record.customer_tier} tier customer, risk score {record.risk_score:.2f}, "
        f"{record.open_issues} open issues, revenue impact ${record.revenue_impact:,.0f}, "
        f"SLA remaining {record.sla_hours_remaining} hours"
    )


@router.post("/v1/decide", response_model=DecisionResponse)
async def decide(
    record: EnterpriseRecord,
    db: DbDep,
    engine: EngineDep,
    search: SearchDep,
    generator: GeneratorDep,
    include_context: bool = False,
) -> DecisionResponse:
    context_summary = None
    if include_context:
        if generator is None:
            raise HTTPException(
                status_code=400,
                detail="include_context=true requires INSIGHT_ENABLE_RAG_GENERATION=true "
                "and a reachable Ollama server.",
            )
        try:
            search_result = search.search(
                _record_query_text(record), retrieval_top_k=20, final_top_k=3
            )
            context_summary = generate_context_summary(generator, search_result.results)
        except Exception as exc:  # noqa: BLE001 — degrade gracefully, don't fail the decision
            logger.error("context_generation_failed", error=str(exc))
            context_summary = None

    decision = engine.decide(record, context_summary=context_summary)
    db[DECISIONS_COLLECTION].insert_one(decision.model_dump())
    logger.info("decision_served", record_id=record.record_id, decision=decision.decision)
    return decision


@router.get("/v1/decisions")
async def decisions(db: DbDep) -> dict:
    items = list(db[DECISIONS_COLLECTION].find({}, {"_id": 0}))
    return {"items": items}


@router.post("/v1/cases/search", response_model=CaseSearchResponse)
async def search_cases(payload: CaseSearchRequest, search: SearchDep) -> CaseSearchResponse:
    return search.search(payload.query, retrieval_top_k=20, final_top_k=payload.top_k)
