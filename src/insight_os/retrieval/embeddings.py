"""Embedding model singleton — loaded once per process, not once per request."""

from __future__ import annotations

from functools import lru_cache

from llama_index.embeddings.huggingface import HuggingFaceEmbedding


@lru_cache
def get_embed_model(model_name: str) -> HuggingFaceEmbedding:
    return HuggingFaceEmbedding(model_name=model_name)
