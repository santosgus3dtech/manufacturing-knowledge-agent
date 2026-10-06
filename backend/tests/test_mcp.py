import pytest
from mcp import Client

from manufacturing_agent.mcp_server import mcp


@pytest.mark.asyncio
async def test_mcp_exposes_typed_tools_resources_and_prompts() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

    tool_names = {tool.name for tool in tools.tools}
    assert tool_names == {
        "diagnose_incident",
        "estimate_print_job",
        "get_machine_status",
        "search_knowledge",
    }
    assert {resource.uri for resource in resources.resources} >= {
        "manufacturing://machines",
        "manufacturing://materials",
    }
    assert {prompt.name for prompt in prompts.prompts} == {"incident_triage"}


@pytest.mark.asyncio
async def test_mcp_quote_tool_returns_structured_content() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "estimate_print_job",
            {"material": "PETG", "part_weight_g": 72, "print_hours": 3.5},
        )

    assert not result.is_error
    assert result.structured_content["material"] == "Petg"
    assert result.structured_content["total_price"] > 0
