from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .application import services
from .config import settings
from .fixtures import load_documents
from .models import (
    AskRequest,
    AskResponse,
    EvaluationSummary,
    Machine,
    QuoteBreakdown,
    QuoteRequest,
    SearchResponse,
    ToolTrace,
)
from .pricing import MATERIALS, estimate_quote

app = FastAPI(
    title="Manufacturing Knowledge Agent",
    version="0.1.0",
    description="Portfolio-safe MCP and RAG workspace backed by synthetic manufacturing data.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "mode": "synthetic-demo",
        "ai_provider_configured": settings.openai_enabled,
        "knowledge_chunks": len(services.retriever.chunks),
    }


@app.get("/api/dashboard")
def dashboard() -> dict:
    machines = services.machines.list()
    evaluation = services.evaluations.run()
    return {
        "mode": "Synthetic demo",
        "machines": len(machines),
        "needs_attention": sum(machine.health != "healthy" for machine in machines),
        "knowledge_chunks": len(services.retriever.chunks),
        "citation_precision": evaluation.recall_at_3,
        "retrieval_mrr": evaluation.mean_reciprocal_rank,
    }


@app.get("/api/machines", response_model=list[Machine])
def machines() -> list[Machine]:
    return services.machines.list()


@app.get("/api/machines/{machine_id}", response_model=Machine)
def machine(machine_id: str) -> Machine:
    try:
        return services.machines.get(machine_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/knowledge")
def knowledge_documents() -> list[dict]:
    return [document.model_dump() for document in load_documents()]


@app.get("/api/knowledge/search", response_model=SearchResponse)
def search_knowledge(
    q: str = Query(min_length=2, max_length=500),
    top_k: int = Query(default=5, ge=1, le=10),
    domain: str | None = Query(default=None, max_length=80),
) -> SearchResponse:
    return services.retriever.search(q, top_k=top_k, domain=domain)


@app.post("/api/agent/ask", response_model=AskResponse)
async def ask_agent(request: AskRequest) -> AskResponse:
    return await services.agent.ask(request.question, request.machine_id)


@app.get("/api/materials")
def materials() -> list[str]:
    return [name.title() for name in MATERIALS]


@app.post("/api/quotes/estimate", response_model=QuoteBreakdown)
def quote(request: QuoteRequest) -> QuoteBreakdown:
    try:
        return estimate_quote(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/activity", response_model=list[ToolTrace])
def activity(limit: int = Query(default=12, ge=1, le=50)) -> list[ToolTrace]:
    return services.activity.list(limit)


@app.get("/api/evaluations", response_model=EvaluationSummary)
def evaluations() -> EvaluationSummary:
    return services.evaluations.run()


FRONTEND_DIST = settings.root_dir / "frontend" / "dist"
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        candidate = (FRONTEND_DIST / path).resolve()
        if candidate.is_file() and FRONTEND_DIST.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")


def run() -> None:
    uvicorn.run("manufacturing_agent.api:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    run()
