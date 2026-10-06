from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI

from .models import KnowledgeChunk, SearchResponse, SearchResult

TOKEN = re.compile(r"[a-z0-9][a-z0-9.+-]*")
SYNONYMS: dict[str, set[str]] = {
    "blocked": {"clog", "clogged", "jam", "flow", "underextrusion"},
    "clog": {"blocked", "jam", "flow", "underextrusion"},
    "disconnect": {"offline", "unreachable", "network", "timeout"},
    "offline": {"disconnect", "unreachable", "network", "timeout"},
    "lifting": {"warp", "warping", "adhesion", "corners"},
    "warp": {"lifting", "adhesion", "corners"},
    "vibration": {"belt", "motion", "resonance", "loose"},
    "cost": {"quote", "price", "material", "labor", "energy"},
    "quote": {"cost", "price", "margin", "risk"},
    "petg": {"stringing", "moisture", "temperature", "adhesion"},
    "resin": {"vat", "exposure", "flow", "support"},
}


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def expand(tokens: Sequence[str]) -> set[str]:
    expanded = set(tokens)
    for token in tokens:
        expanded.update(SYNONYMS.get(token, set()))
    return expanded


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIEmbeddingProvider:
    name = "openai-embeddings+bm25"

    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


def cosine(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


@dataclass(slots=True)
class IndexedChunk:
    chunk: KnowledgeChunk
    tokens: list[str]
    counts: Counter[str]


class HybridRetriever:
    def __init__(
        self,
        chunks: list[KnowledgeChunk],
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        if not chunks:
            raise ValueError("At least one knowledge chunk is required")
        self.chunks = chunks
        self.embedding_provider = embedding_provider
        self.index = [
            IndexedChunk(chunk, tokenize(chunk.text), Counter(tokenize(chunk.text)))
            for chunk in chunks
        ]
        self.average_length = sum(len(item.tokens) for item in self.index) / len(self.index)
        self.document_frequency = Counter[str]()
        for item in self.index:
            self.document_frequency.update(set(item.tokens))
        self._chunk_embeddings: list[list[float]] | None = None
        self.last_strategy = "bm25+manufacturing-vocabulary"

    def _bm25(self, query_tokens: set[str], item: IndexedChunk) -> float:
        score = 0.0
        k1 = 1.5
        b = 0.75
        total = len(self.index)
        length_ratio = len(item.tokens) / self.average_length
        for token in query_tokens:
            frequency = item.counts.get(token, 0)
            if not frequency:
                continue
            document_frequency = self.document_frequency[token]
            inverse_frequency = math.log(1 + (total - document_frequency + 0.5) / (document_frequency + 0.5))
            score += inverse_frequency * (
                frequency * (k1 + 1) / (frequency + k1 * (1 - b + b * length_ratio))
            )
        return score

    def _local_semantic_score(self, query_tokens: set[str], item: IndexedChunk) -> float:
        document_tokens = expand(item.tokens)
        overlap = len(query_tokens & document_tokens)
        union = len(query_tokens | document_tokens)
        score = overlap / union if union else 0.0
        metadata = " ".join(
            filter(
                None,
                (
                    item.chunk.title,
                    item.chunk.section,
                    item.chunk.domain,
                    item.chunk.machine_id,
                    item.chunk.material,
                ),
            )
        ).lower()
        direct_matches = sum(1 for token in query_tokens if token in metadata)
        return min(1.0, score * 3.5 + direct_matches * 0.12)

    def _embedding_scores(self, query: str) -> list[float] | None:
        if self.embedding_provider is None:
            return None
        try:
            if self._chunk_embeddings is None:
                self._chunk_embeddings = self.embedding_provider.embed(
                    [f"{chunk.title}\n{chunk.section}\n{chunk.text}" for chunk in self.chunks]
                )
            query_embedding = self.embedding_provider.embed([query])[0]
            self.last_strategy = self.embedding_provider.name
            return [max(0.0, cosine(query_embedding, vector)) for vector in self._chunk_embeddings]
        except Exception:
            self.last_strategy = "bm25+manufacturing-vocabulary (provider fallback)"
            return None

    def search(self, query: str, top_k: int = 5, domain: str | None = None) -> SearchResponse:
        clean_query = " ".join(query.split())[:500]
        query_tokens = expand(tokenize(clean_query))
        if not query_tokens:
            return SearchResponse(query=clean_query, strategy=self.last_strategy, results=[])

        candidates = [item for item in self.index if domain is None or item.chunk.domain == domain]
        raw_bm25 = [self._bm25(query_tokens, item) for item in candidates]
        highest_bm25 = max(raw_bm25, default=1.0) or 1.0
        embedding_scores = self._embedding_scores(clean_query)

        scored: list[tuple[float, IndexedChunk]] = []
        for item, lexical_score in zip(candidates, raw_bm25, strict=True):
            lexical = lexical_score / highest_bm25
            if embedding_scores is not None:
                original_index = self.index.index(item)
                semantic = embedding_scores[original_index]
            else:
                semantic = self._local_semantic_score(query_tokens, item)
            combined = min(1.0, lexical * 0.66 + semantic * 0.34)
            scored.append((combined, item))

        scored.sort(key=lambda pair: (-pair[0], pair[1].chunk.document_id, pair[1].chunk.page))
        results = [
            SearchResult(
                chunk_id=item.chunk.id,
                document_id=item.chunk.document_id,
                title=item.chunk.title,
                section=item.chunk.section,
                page=item.chunk.page,
                domain=item.chunk.domain,
                excerpt=item.chunk.text[:280] + ("..." if len(item.chunk.text) > 280 else ""),
                score=round(score, 3),
            )
            for score, item in scored[: max(1, min(top_k, 10))]
            if score > 0
        ]
        return SearchResponse(query=clean_query, strategy=self.last_strategy, results=results)
