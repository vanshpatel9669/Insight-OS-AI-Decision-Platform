#!/usr/bin/env python3
"""Reads all cases from MongoDB, embeds them, and builds/persists the
retrieval index. Run this once after generate_synthetic_cases.py (or after
any change to the cases collection) — the API loads the persisted index at
startup rather than re-embedding the whole corpus on every process start.

Usage: python scripts/build_index.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pymongo import MongoClient  # noqa: E402

from insight_os.config import get_settings  # noqa: E402
from insight_os.db.mongo import CASES_COLLECTION  # noqa: E402
from insight_os.logging_config import configure_logging, get_logger  # noqa: E402
from insight_os.retrieval.embeddings import get_embed_model  # noqa: E402
from insight_os.retrieval.index_store import build_index, get_database_cases  # noqa: E402

INDEX_PERSIST_DIR = Path(__file__).resolve().parent.parent / "storage"


def main() -> None:
    configure_logging()
    logger = get_logger(__name__)
    settings = get_settings()

    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    case_count = db[CASES_COLLECTION].count_documents({})
    if case_count == 0:
        raise SystemExit("No cases in MongoDB. Run scripts/generate_synthetic_cases.py first.")

    logger.info("index_build_started", case_count=case_count)
    cases = get_database_cases(db)
    embed_model = get_embed_model(settings.embed_model_name)

    t0 = time.monotonic()
    build_index(cases, embed_model, settings.mongo_uri, settings.mongo_db, INDEX_PERSIST_DIR)
    elapsed_s = time.monotonic() - t0

    logger.info(
        "index_build_completed",
        case_count=case_count,
        elapsed_s=round(elapsed_s, 1),
        docs_per_sec=round(case_count / elapsed_s, 1) if elapsed_s > 0 else None,
    )
    print(f"Built index for {case_count} cases in {elapsed_s:.1f}s -> {INDEX_PERSIST_DIR}")


if __name__ == "__main__":
    main()
