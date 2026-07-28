"""FastAPI dependency-injection wiring. Every dependency here is a plain
function referenced via `Depends(...)`, which is what makes them
overridable in tests (`app.dependency_overrides[get_x] = fake_x`)
regardless of the `lru_cache` used for process-wide singleton caching in
production.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from llama_index.llms.ollama import Ollama
from pymongo.database import Database

from insight_os.config import Settings, get_settings
from insight_os.db.mongo import get_database
from insight_os.decision_engine import DecisionEngine
from insight_os.rag.generator import build_generator
from insight_os.retrieval.embeddings import get_embed_model
from insight_os.retrieval.index_store import get_database_cases, load_index
from insight_os.retrieval.reranker import get_reranker
from insight_os.retrieval.search_service import SearchService

INDEX_PERSIST_DIR = Path("storage")


@lru_cache
def get_cached_settings() -> Settings:
    return get_settings()


def get_db() -> Database:
    return get_database()


@lru_cache
def get_decision_engine() -> DecisionEngine:
    return DecisionEngine()


@lru_cache
def get_search_service() -> SearchService:
    settings = get_cached_settings()
    db = get_database()
    embed_model = get_embed_model(settings.embed_model_name)
    index = load_index(settings.mongo_uri, settings.mongo_db, INDEX_PERSIST_DIR, embed_model)
    reranker = get_reranker(settings.rerank_model_name)
    cases_by_id = {c.case_id: c for c in get_database_cases(db)}
    return SearchService(index=index, reranker=reranker, cases_by_id=cases_by_id)


@lru_cache
def get_generator() -> Ollama | None:
    settings = get_cached_settings()
    if not settings.enable_rag_generation:
        return None
    return build_generator(
        settings.ollama_base_url, settings.ollama_model, settings.ollama_request_timeout_s
    )
