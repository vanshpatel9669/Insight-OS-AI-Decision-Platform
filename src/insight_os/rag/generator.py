"""Retrieval-augmented context generation: takes the reranked cases a search
already retrieved and asks a local LLM (via Ollama) to summarize what they
imply for the current decision. This is genuinely retrieval-augmented — the
LLM only ever sees the retrieved case text, not the whole corpus — but it is
opt-in (`INSIGHT_ENABLE_RAG_GENERATION=true`), not part of the default
request path.

Why opt-in rather than always-on: local LLM inference on CPU is measured at
tens of seconds per call on the development machine (see
docs/architecture.md), which is fine as a documented, manually-verified
capability but not something CI can exercise (no LLM runtime available in
CI) or something a demo API should block its primary endpoint on by
default.
"""

from __future__ import annotations

from llama_index.llms.ollama import Ollama

from insight_os.models import RankedCase

_PROMPT_TEMPLATE = """You are assisting an operations analyst. Given the following \
similar historical cases, write a 2-3 sentence summary of the pattern they suggest \
for the current situation. Be concise and concrete. Do not invent case details \
beyond what's given.

Similar cases:
{cases_block}

Summary:"""


def build_generator(base_url: str, model: str, request_timeout_s: float) -> Ollama:
    return Ollama(model=model, base_url=base_url, request_timeout=request_timeout_s)


def generate_context_summary(llm: Ollama, ranked_cases: list[RankedCase]) -> str:
    cases_block = "\n".join(
        f"- [{rc.case.outcome}] {rc.case.summary} Resolution: {rc.case.resolution}"
        for rc in ranked_cases
    )
    prompt = _PROMPT_TEMPLATE.format(cases_block=cases_block)
    response = llm.complete(prompt)
    return str(response).strip()
