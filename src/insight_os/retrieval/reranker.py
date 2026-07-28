"""Cross-encoder reranking — a second, more expensive but more accurate
scoring pass over the embedding retriever's candidate set. Embedding
similarity (bi-encoder) is fast but only approximates relevance; a
cross-encoder that attends over the (query, candidate) pair jointly is
slower per-pair but measurably more accurate, which is the entire reason a
two-stage retrieve-then-rerank pipeline exists instead of returning raw
embedding-similarity order.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import CrossEncoder


@lru_cache
def get_reranker(model_name: str) -> CrossEncoder:
    return CrossEncoder(model_name)


def rerank(reranker: CrossEncoder, query: str, candidates: list[str]) -> list[float]:
    if not candidates:
        return []
    pairs = [(query, candidate) for candidate in candidates]
    # CrossEncoder.predict's stub type covers its general multi-modal input
    # shape (text/image/audio/video dicts); a list[tuple[str, str]] is a
    # valid runtime input (verified directly) but narrower than the stub
    # admits under invariant List typing.
    scores = reranker.predict(pairs)  # type: ignore[arg-type]
    return [float(s) for s in scores]
