"""SearchService tests run against a real (small, in-memory) vector index
built with the real embedding model and the real cross-encoder reranker —
not mocks. SearchService itself only depends on a `BaseIndex`, so this
in-memory index (no Mongo docstore backing) is sufficient to exercise its
actual ranking logic without needing a running MongoDB.
"""

from __future__ import annotations

from llama_index.core import Document, VectorStoreIndex

from insight_os.config import get_settings
from insight_os.models import Case
from insight_os.retrieval.embeddings import get_embed_model
from insight_os.retrieval.reranker import get_reranker
from insight_os.retrieval.search_service import SearchService

_CASES = [
    Case(
        case_id="C1",
        customer_tier="enterprise",
        issue_type="billing_discrepancy",
        summary="Customer reported a $12,000 discrepancy on their invoice.",
        resolution="Root cause identified in billing-service; fix deployed.",
        outcome="resolved",
    ),
    Case(
        case_id="C2",
        customer_tier="standard",
        issue_type="sla_breach",
        summary="SLA breach: 8h downtime exceeded contractual uptime commitment.",
        resolution="SLA credit issued; runbook updated.",
        outcome="sla_breach",
    ),
    Case(
        case_id="C3",
        customer_tier="enterprise",
        issue_type="security_incident",
        summary="Anomalous access pattern flagged, requiring credential rotation.",
        resolution="Escalated to on-call; credentials rotated.",
        outcome="escalated",
    ),
]


def _build_service() -> SearchService:
    settings = get_settings()
    embed_model = get_embed_model(settings.embed_model_name)
    documents = [
        Document(text=c.to_document_text(), doc_id=c.case_id, metadata={"case_id": c.case_id})
        for c in _CASES
    ]
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    reranker = get_reranker(settings.rerank_model_name)
    cases_by_id = {c.case_id: c for c in _CASES}
    return SearchService(index=index, reranker=reranker, cases_by_id=cases_by_id)


def test_search_returns_ranked_results():
    service = _build_service()
    response = service.search("billing invoice discrepancy", retrieval_top_k=3, final_top_k=2)
    assert len(response.results) == 2
    assert response.results[0].case.case_id == "C1"


def test_search_reports_real_timing():
    service = _build_service()
    response = service.search("security credential issue", retrieval_top_k=3, final_top_k=2)
    assert set(response.timing_ms) == {"vector_retrieve_ms", "rerank_ms", "total_ms"}
    assert response.timing_ms["total_ms"] >= response.timing_ms["rerank_ms"]
    assert all(v >= 0 for v in response.timing_ms.values())


def test_search_respects_final_top_k():
    service = _build_service()
    response = service.search("customer issue", retrieval_top_k=3, final_top_k=1)
    assert len(response.results) == 1


def test_case_count_property():
    service = _build_service()
    assert service.case_count == 3
