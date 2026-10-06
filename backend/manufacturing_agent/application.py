from __future__ import annotations

from dataclasses import dataclass

from .agent import ManufacturingAgent
from .config import settings
from .fixtures import load_chunks
from .retrieval import HybridRetriever, OpenAIEmbeddingProvider
from .services import ActivityStore, EvaluationService, MachineRepository


@dataclass(slots=True)
class ApplicationServices:
    retriever: HybridRetriever
    machines: MachineRepository
    activity: ActivityStore
    evaluations: EvaluationService
    agent: ManufacturingAgent


def build_services() -> ApplicationServices:
    embedding_provider = None
    if settings.openai_enabled and settings.openai_api_key:
        embedding_provider = OpenAIEmbeddingProvider(settings.openai_api_key)
    retriever = HybridRetriever(load_chunks(), embedding_provider=embedding_provider)
    machines = MachineRepository()
    activity = ActivityStore()
    evaluations = EvaluationService(retriever)
    agent = ManufacturingAgent(settings, retriever, machines, activity)
    return ApplicationServices(retriever, machines, activity, evaluations, agent)


services = build_services()
