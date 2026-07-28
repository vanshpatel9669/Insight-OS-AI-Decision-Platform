"""API tests. `get_db` is overridden with a mongomock database (fast,
deterministic, no real MongoDB needed) and `get_search_service` is
overridden with a small real (embedding + reranker, real models) in-memory
search service — see tests/unit/test_search_service.py for why that's
sufficient to exercise real ranking logic without a running MongoDB.
`get_generator` is left at its default (disabled), matching the
production default of INSIGHT_ENABLE_RAG_GENERATION=false.
"""

from __future__ import annotations

import mongomock
import pytest
from fastapi.testclient import TestClient
from llama_index.core import Document, VectorStoreIndex

from insight_os.api.dependencies import get_db, get_search_service
from insight_os.api.main import app
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
        summary="Customer reported a billing discrepancy on their invoice.",
        resolution="Root cause identified; fix deployed.",
        outcome="resolved",
    ),
    Case(
        case_id="C2",
        customer_tier="standard",
        issue_type="sla_breach",
        summary="SLA breach: downtime exceeded contractual uptime commitment.",
        resolution="SLA credit issued.",
        outcome="sla_breach",
    ),
]


@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    return client["insight_os_test"]


@pytest.fixture
def search_service():
    settings = get_settings()
    embed_model = get_embed_model(settings.embed_model_name)
    documents = [
        Document(text=c.to_document_text(), doc_id=c.case_id, metadata={"case_id": c.case_id})
        for c in _CASES
    ]
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    reranker = get_reranker(settings.rerank_model_name)
    return SearchService(index=index, reranker=reranker, cases_by_id={c.case_id: c for c in _CASES})


@pytest.fixture
def client(mock_db, search_service):
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_search_service] = lambda: search_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_reports_case_count(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["case_count"] == 2


def test_decide_without_context(client):
    response = client.post(
        "/v1/decide",
        json={
            "record_id": "R1",
            "customer_tier": "enterprise",
            "risk_score": 0.9,
            "revenue_impact": 100_000,
            "open_issues": 6,
            "sla_hours_remaining": 2,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "escalate"
    assert body["context_summary"] is None


def test_decide_with_context_fails_when_rag_disabled(client):
    response = client.post(
        "/v1/decide?include_context=true",
        json={
            "record_id": "R2",
            "risk_score": 0.5,
            "revenue_impact": 10_000,
            "open_issues": 1,
            "sla_hours_remaining": 20,
        },
    )
    assert response.status_code == 400


def test_decide_persists_to_db(client, mock_db):
    client.post(
        "/v1/decide",
        json={
            "record_id": "R3",
            "risk_score": 0.2,
            "revenue_impact": 5_000,
            "open_issues": 0,
            "sla_hours_remaining": 40,
        },
    )
    response = client.get("/v1/decisions")
    assert response.status_code == 200
    ids = [item["record_id"] for item in response.json()["items"]]
    assert "R3" in ids


def test_decide_rejects_invalid_risk_score(client):
    response = client.post(
        "/v1/decide",
        json={
            "record_id": "R4",
            "risk_score": 1.5,
            "revenue_impact": 5_000,
            "open_issues": 0,
            "sla_hours_remaining": 40,
        },
    )
    assert response.status_code == 422


def test_case_search(client):
    response = client.post("/v1/cases/search", json={"query": "billing invoice issue", "top_k": 2})
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 2
    assert body["results"][0]["case"]["case_id"] == "C1"
    assert "total_ms" in body["timing_ms"]


def test_case_search_rejects_empty_query(client):
    response = client.post("/v1/cases/search", json={"query": ""})
    assert response.status_code == 422


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
