"""MongoDB access. A single cached client per process; the database object
itself is what call sites depend on (via FastAPI DI), so tests can swap in
a mongomock database without touching connection logic.
"""

from __future__ import annotations

from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from insight_os.config import Settings, get_settings

CASES_COLLECTION = "cases"
DECISIONS_COLLECTION = "decisions"


@lru_cache
def get_mongo_client() -> MongoClient:
    settings = get_settings()
    return MongoClient(settings.mongo_uri)


def get_database() -> Database:
    settings: Settings = get_settings()
    return get_mongo_client()[settings.mongo_db]


def ensure_indexes(db: Database) -> None:
    db[CASES_COLLECTION].create_index("case_id", unique=True)
    db[DECISIONS_COLLECTION].create_index("record_id")
