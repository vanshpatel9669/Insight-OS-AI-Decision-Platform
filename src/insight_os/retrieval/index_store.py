"""Builds and loads the case-retrieval vector index.

Document content and index metadata are backed by MongoDB (`MongoDocumentStore`
/ `MongoIndexStore`) — genuinely persisted there, not just read from Mongo
once and discarded. The vector data itself is NOT Mongo-backed: native
`$vectorSearch` requires MongoDB Atlas Search, which a self-hosted/local
MongoDB does not provide. LlamaIndex's storage backends are pluggable
independently per component, so the vector store persists to local disk
(`SimpleVectorStore`, an in-memory cosine-similarity index serialized to
JSON) while docstore/index metadata remain genuinely in Mongo. This is a
deliberate, documented split, not an oversight — see docs/architecture.md.
"""

from __future__ import annotations

from pathlib import Path

from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.indices.base import BaseIndex
from llama_index.core.schema import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from pymongo.database import Database

from insight_os.models import Case

VECTOR_STORE_SUBDIR = "vector_store"


def _mongo_storage_context(mongo_uri: str, mongo_db: str, persist_dir: Path) -> StorageContext:
    docstore = MongoDocumentStore.from_uri(uri=mongo_uri, db_name=mongo_db)
    index_store = MongoIndexStore.from_uri(uri=mongo_uri, db_name=mongo_db)
    if (persist_dir / VECTOR_STORE_SUBDIR).exists():
        return StorageContext.from_defaults(
            docstore=docstore,
            index_store=index_store,
            persist_dir=str(persist_dir / VECTOR_STORE_SUBDIR),
        )
    return StorageContext.from_defaults(docstore=docstore, index_store=index_store)


def build_index(
    cases: list[Case],
    embed_model: HuggingFaceEmbedding,
    mongo_uri: str,
    mongo_db: str,
    persist_dir: Path,
) -> VectorStoreIndex:
    documents = [
        Document(
            text=case.to_document_text(),
            doc_id=case.case_id,
            metadata={"case_id": case.case_id},
        )
        for case in cases
    ]
    storage_context = _mongo_storage_context(mongo_uri, mongo_db, persist_dir)
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=embed_model, show_progress=True
    )
    persist_dir.mkdir(parents=True, exist_ok=True)
    storage_context.persist(persist_dir=str(persist_dir / VECTOR_STORE_SUBDIR))
    return index


def load_index(
    mongo_uri: str, mongo_db: str, persist_dir: Path, embed_model: HuggingFaceEmbedding
) -> BaseIndex:
    if not (persist_dir / VECTOR_STORE_SUBDIR).exists():
        raise FileNotFoundError(
            f"No persisted index at {persist_dir}. Run `python scripts/build_index.py` first."
        )
    storage_context = _mongo_storage_context(mongo_uri, mongo_db, persist_dir)
    return load_index_from_storage(storage_context, embed_model=embed_model)


def get_database_cases(db: Database) -> list[Case]:
    return [
        Case.model_validate(doc, from_attributes=False) for doc in db["cases"].find({}, {"_id": 0})
    ]
