"""Environment-based configuration. Single source of truth for all settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INSIGHT_", env_file=".env", extra="ignore")

    # MongoDB — source of truth for case records and the decision log.
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "insight_os"

    # Retrieval
    embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    rerank_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    retrieval_top_k: int = 20  # candidates pulled by embedding search before reranking
    rerank_top_k: int = 5  # final results returned after reranking

    # Optional RAG context generation. Off by default: it depends on a
    # locally running Ollama server, which is not assumed to be present in
    # every deployment (and is never available in CI). See
    # docs/architecture.md for why this is opt-in rather than core.
    enable_rag_generation: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_request_timeout_s: float = 60.0

    # Observability
    log_level: str = "INFO"
    service_name: str = "insight-os"


def get_settings() -> Settings:
    return Settings()
