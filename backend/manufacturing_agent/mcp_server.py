from __future__ import annotations

import json
import os
from time import perf_counter

from mcp.server.mcpserver import MCPServer

from .application import services
from .config import settings
from .fixtures import load_documents
from .models import AskResponse, Machine, QuoteBreakdown, QuoteRequest, SearchResponse
from .pricing import MATERIALS, estimate_quote

mcp = MCPServer(
    "Manufacturing Knowledge Agent",
    instructions=(
        "Use the knowledge and machine tools to answer questions about the synthetic manufacturing demo. "
        "All tools are read-only or deterministic calculations. Cite returned document ids and pages."
    ),
)


@mcp.tool()
def search_knowledge(query: str, top_k: int = 5, domain: str | None = None) -> SearchResponse:
    """Search synthetic manufacturing manuals and playbooks with grounded citations."""
    started = perf_counter()
    response = services.retriever.search(query, top_k=top_k, domain=domain)
    services.activity.record("search_knowledge", json.dumps(query), started)
    return response


@mcp.tool()
def get_machine_status(machine_id: str) -> Machine:
    """Return the normalized status of one synthetic machine. This tool never contacts real hardware."""
    started = perf_counter()
    machine = services.machines.get(machine_id)
    services.activity.record(
        "get_machine_status", json.dumps({"machine_id": machine.id}, separators=(",", ":")), started
    )
    return machine


@mcp.tool()
def estimate_print_job(
    material: str,
    part_weight_g: float,
    print_hours: float,
    labor_minutes: float = 18,
    quantity: int = 1,
    failure_rate_percent: float = 8,
    margin_percent: float = 35,
) -> QuoteBreakdown:
    """Calculate a transparent synthetic 3D-printing quote without model-generated arithmetic."""
    started = perf_counter()
    quote = estimate_quote(
        QuoteRequest(
            material=material,
            part_weight_g=part_weight_g,
            print_hours=print_hours,
            labor_minutes=labor_minutes,
            quantity=quantity,
            failure_rate_percent=failure_rate_percent,
            margin_percent=margin_percent,
        )
    )
    services.activity.record(
        "estimate_print_job",
        json.dumps({"material": material, "part_weight_g": part_weight_g}, separators=(",", ":")),
        started,
    )
    return quote


@mcp.tool()
async def diagnose_incident(question: str, machine_id: str | None = None) -> AskResponse:
    """Combine read-only machine context with retrieved evidence to diagnose a synthetic incident."""
    response = await services.agent.ask(question, machine_id)
    return response


@mcp.resource("manufacturing://machines")
def machines_resource() -> str:
    """Synthetic machine inventory in JSON."""
    return json.dumps([machine.model_dump(mode="json") for machine in services.machines.list()], indent=2)


@mcp.resource("manufacturing://materials")
def materials_resource() -> str:
    """Synthetic material costing profiles in JSON."""
    public_profiles = {
        name: {key: str(value) for key, value in profile.items()} for name, profile in MATERIALS.items()
    }
    return json.dumps(public_profiles, indent=2)


@mcp.resource("manufacturing://knowledge/{document_id}")
def knowledge_resource(document_id: str) -> str:
    """Read one synthetic manufacturing knowledge document."""
    document = next((item for item in load_documents() if item.id == document_id), None)
    if document is None:
        raise ValueError(f"Unknown document: {document_id}")
    return (settings.data_dir / "knowledge" / document.file).read_text(encoding="utf-8")


@mcp.prompt()
def incident_triage(machine_id: str, symptom: str) -> str:
    """Create a grounded incident-triage request for a synthetic machine."""
    return (
        f"Investigate symptom '{symptom}' on synthetic machine '{machine_id}'. "
        "First call get_machine_status, then search_knowledge. Separate observations from recommendations, "
        "cite every recommendation, and do not claim that any physical action was performed."
    )


def main() -> None:
    transport = os.getenv("MKA_MCP_TRANSPORT", "stdio").lower()
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8001, json_response=True)
        return
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
