from __future__ import annotations

import json
import re
from pathlib import Path

from .config import settings
from .models import EvaluationCase, KnowledgeChunk, KnowledgeDocument, Machine

HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_machines() -> list[Machine]:
    raw = _read_json(settings.data_dir / "fixtures" / "machines.json")
    return [Machine.model_validate(item) for item in raw]


def load_documents() -> list[KnowledgeDocument]:
    raw = _read_json(settings.data_dir / "knowledge" / "catalog.json")
    return [KnowledgeDocument.model_validate(item) for item in raw]


def load_chunks() -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for document in load_documents():
        body = (settings.data_dir / "knowledge" / document.file).read_text(encoding="utf-8").strip()
        matches = list(HEADING.finditer(body))
        for index, match in enumerate(matches, start=1):
            start = match.end()
            end = matches[index].start() if index < len(matches) else len(body)
            text = " ".join(body[start:end].strip().split())
            chunks.append(
                KnowledgeChunk(
                    id=f"{document.id}-p{index}",
                    document_id=document.id,
                    title=document.title,
                    section=match.group(1),
                    page=index,
                    domain=document.domain,
                    machine_id=document.machine_id,
                    material=document.material,
                    text=text,
                )
            )
    return chunks


def load_evaluation_cases() -> list[EvaluationCase]:
    cases: list[EvaluationCase] = []
    path = settings.evals_dir / "dataset.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(EvaluationCase.model_validate_json(line))
    return cases
