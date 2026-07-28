"""Orchestrates the two-stage retrieval pipeline: embedding search over the
vector index (cheap, approximate) narrows the corpus to a candidate set,
then cross-encoder reranking (expensive, accurate) reorders that candidate
set for the final response. Every stage is timed for real — the response's
`timing_ms` is measured on this exact call, not a claim from a benchmark
run elsewhere.
"""

from __future__ import annotations

import time

from llama_index.core.indices.base import BaseIndex
from sentence_transformers import CrossEncoder

from insight_os.models import Case, CaseSearchResponse, RankedCase
from insight_os.retrieval.reranker import rerank


class SearchService:
    def __init__(self, index: BaseIndex, reranker: CrossEncoder, cases_by_id: dict[str, Case]):
        self._index = index
        self._reranker = reranker
        self._cases_by_id = cases_by_id

    @property
    def case_count(self) -> int:
        return len(self._cases_by_id)

    def search(self, query: str, retrieval_top_k: int, final_top_k: int) -> CaseSearchResponse:
        t_start = time.perf_counter()

        retriever = self._index.as_retriever(similarity_top_k=retrieval_top_k)
        t_retrieve_start = time.perf_counter()
        nodes = retriever.retrieve(query)
        t_retrieve_end = time.perf_counter()

        candidate_ids = [n.node.metadata.get("case_id", n.node.node_id) for n in nodes]
        candidate_texts = [n.node.get_content() for n in nodes]
        embedding_scores = {
            cid: float(n.score or 0.0) for cid, n in zip(candidate_ids, nodes, strict=True)
        }

        t_rerank_start = time.perf_counter()
        rerank_scores = rerank(self._reranker, query, candidate_texts)
        t_rerank_end = time.perf_counter()

        ranked = sorted(
            zip(candidate_ids, rerank_scores, strict=True),
            key=lambda pair: pair[1],
            reverse=True,
        )[:final_top_k]

        results = [
            RankedCase(
                case=self._cases_by_id[cid],
                embedding_score=embedding_scores[cid],
                rerank_score=score,
            )
            for cid, score in ranked
            if cid in self._cases_by_id
        ]

        t_end = time.perf_counter()
        timing_ms = {
            "vector_retrieve_ms": round((t_retrieve_end - t_retrieve_start) * 1000, 2),
            "rerank_ms": round((t_rerank_end - t_rerank_start) * 1000, 2),
            "total_ms": round((t_end - t_start) * 1000, 2),
        }
        return CaseSearchResponse(results=results, timing_ms=timing_ms)
