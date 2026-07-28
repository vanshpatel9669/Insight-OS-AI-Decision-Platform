"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from insight_os.api.routes import router
from insight_os.config import get_settings
from insight_os.logging_config import configure_logging
from insight_os.observability import configure_tracing, instrument_app


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    configure_tracing(settings.service_name)

    app = FastAPI(
        title="Insight-OS Decision Intelligence Platform",
        description=(
            "Rule-based operations triage scoring, plus a real embedding-search-"
            "and-reranking retrieval service over MongoDB-backed case records, "
            "with optional local-LLM RAG context generation."
        ),
        version="0.1.0",
    )
    app.include_router(router)
    instrument_app(app)
    return app


app = create_app()
