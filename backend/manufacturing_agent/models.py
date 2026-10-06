from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MachineState(StrEnum):
    PRINTING = "printing"
    IDLE = "idle"
    ATTENTION = "attention"
    OFFLINE = "offline"


class HealthState(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class Temperature(BaseModel):
    current: float | None = None
    target: float | None = None


class MachineJob(BaseModel):
    reference: str
    part: str
    material: str
    progress_percent: float = Field(ge=0, le=100)
    remaining_minutes: int = Field(ge=0)


class Machine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    process: Literal["FDM", "SLA"]
    workspace_mm: str
    state: MachineState
    health: HealthState
    status_message: str
    nozzle: Temperature
    bed: Temperature
    job: MachineJob | None = None
    last_seen: str


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    domain: str
    machine_id: str | None = None
    material: str | None = None
    file: str


class KnowledgeChunk(BaseModel):
    id: str
    document_id: str
    title: str
    section: str
    page: int
    domain: str
    machine_id: str | None = None
    material: str | None = None
    text: str


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    section: str
    page: int
    domain: str
    excerpt: str
    score: float = Field(ge=0, le=1)


class SearchResponse(BaseModel):
    query: str
    strategy: str
    results: list[SearchResult]


class ToolTrace(BaseModel):
    id: str
    tool: str
    input_summary: str
    result: Literal["success", "fallback", "blocked"]
    duration_ms: int = Field(ge=0)
    created_at: datetime


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    machine_id: str | None = None


class Citation(BaseModel):
    document_id: str
    title: str
    page: int
    excerpt: str
    score: float


class AskResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    provider: str
    citations: list[Citation]
    tools: list[ToolTrace]


class QuoteRequest(BaseModel):
    material: str = "PETG"
    part_weight_g: float = Field(default=72, gt=0, le=20_000)
    print_hours: float = Field(default=3.5, gt=0, le=500)
    labor_minutes: float = Field(default=18, ge=0, le=1_000)
    quantity: int = Field(default=1, ge=1, le=1_000)
    failure_rate_percent: float = Field(default=8, ge=0, lt=100)
    margin_percent: float = Field(default=35, ge=0, le=500)


class QuoteBreakdown(BaseModel):
    material: str
    quantity: int
    material_cost: float
    energy_cost: float
    machine_cost: float
    labor_cost: float
    packaging_cost: float
    risk_buffer: float
    unit_cost: float
    unit_price: float
    total_price: float
    currency: Literal["USD"] = "USD"


class EvaluationCase(BaseModel):
    id: str
    question: str
    expected_document_ids: list[str]
    category: str


class EvaluationResult(BaseModel):
    id: str
    question: str
    category: str
    expected_document_ids: list[str]
    retrieved_document_ids: list[str]
    hit_at_3: bool
    reciprocal_rank: float


class EvaluationSummary(BaseModel):
    cases: int
    recall_at_3: float
    mean_reciprocal_rank: float
    citation_precision_target: float = 0.9
    results: list[EvaluationResult]
