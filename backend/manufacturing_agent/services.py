from __future__ import annotations

import json
from collections import deque
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from .fixtures import load_evaluation_cases, load_machines
from .models import EvaluationResult, EvaluationSummary, Machine, ToolTrace
from .retrieval import HybridRetriever


class MachineRepository:
    def __init__(self, machines: list[Machine] | None = None) -> None:
        self.machines = machines or load_machines()

    def list(self) -> list[Machine]:
        return self.machines

    def get(self, machine_id: str) -> Machine:
        normalized = machine_id.strip().lower()
        for machine in self.machines:
            if machine.id.lower() == normalized or machine.name.lower() == normalized:
                return machine
        raise KeyError(f"Unknown machine: {machine_id}")


class ActivityStore:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self._items: deque[ToolTrace] = deque(
            [
                ToolTrace(
                    id="seed-search",
                    tool="search_knowledge",
                    input_summary='"PETG temperature and moisture"',
                    result="success",
                    duration_ms=84,
                    created_at=now - timedelta(minutes=4),
                ),
                ToolTrace(
                    id="seed-status",
                    tool="get_machine_status",
                    input_summary='{"machine_id":"northstar-cell"}',
                    result="success",
                    duration_ms=32,
                    created_at=now - timedelta(minutes=7),
                ),
                ToolTrace(
                    id="seed-quote",
                    tool="estimate_print_job",
                    input_summary='{"material":"PETG","part_weight_g":72}',
                    result="success",
                    duration_ms=17,
                    created_at=now - timedelta(minutes=11),
                ),
            ],
            maxlen=50,
        )

    def record(self, tool: str, input_summary: str, started_at: float, result: str = "success") -> ToolTrace:
        trace = ToolTrace(
            id=str(uuid4()),
            tool=tool,
            input_summary=input_summary[:180],
            result=result,
            duration_ms=max(1, round((perf_counter() - started_at) * 1000)),
            created_at=datetime.now(UTC),
        )
        self._items.appendleft(trace)
        return trace

    def list(self, limit: int = 12) -> list[ToolTrace]:
        return list(self._items)[:limit]


class EvaluationService:
    def __init__(self, retriever: HybridRetriever) -> None:
        self.retriever = retriever

    def run(self) -> EvaluationSummary:
        results: list[EvaluationResult] = []
        for case in load_evaluation_cases():
            response = self.retriever.search(case.question, top_k=3)
            retrieved = [item.document_id for item in response.results]
            expected = set(case.expected_document_ids)
            rank = next(
                (
                    index
                    for index, document_id in enumerate(retrieved, start=1)
                    if document_id in expected
                ),
                0,
            )
            results.append(
                EvaluationResult(
                    id=case.id,
                    question=case.question,
                    category=case.category,
                    expected_document_ids=case.expected_document_ids,
                    retrieved_document_ids=retrieved,
                    hit_at_3=bool(rank),
                    reciprocal_rank=round(1 / rank, 3) if rank else 0,
                )
            )
        cases = len(results)
        return EvaluationSummary(
            cases=cases,
            recall_at_3=round(sum(item.hit_at_3 for item in results) / cases, 3) if cases else 0,
            mean_reciprocal_rank=(
                round(sum(item.reciprocal_rank for item in results) / cases, 3) if cases else 0
            ),
            results=results,
        )


def load_json_resource(path: Path) -> str:
    return json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2)
