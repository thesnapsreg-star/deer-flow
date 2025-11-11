#!/usr/bin/env python3
"""
Deep Research MCP Server

Exposes deep research capabilities via Model Context Protocol (MCP)
"""
import asyncio
import json
import logging
from typing import Any, Sequence
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deep-research-mcp")

# MCP Server instance
app = Server("deep-research-mcp")

# Configuration
API_BASE_URL = "http://localhost:8080"


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available research tools"""
    return [
        Tool(
            name="deep_research",
            description="""
Perform deep research on any topic using a multi-agent AI research framework.

This tool orchestrates multiple specialized AI agents to:
1. Clarify vague research questions
2. Create comprehensive research plans
3. Conduct web searches and information gathering
4. Analyze data and perform computations
5. Generate detailed research reports

The framework uses:
- Coordinator: Handles initial query and clarification
- Planner: Creates structured research plans
- Researcher: Performs web searches and gathers information
- Coder: Analyzes data and performs calculations
- Reporter: Synthesizes findings into comprehensive reports

Best for: Complex research questions, market analysis, technical investigations,
academic research, competitive intelligence, and any task requiring systematic
information gathering and analysis.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The research question or topic to investigate",
                    },
                    "max_steps": {
                        "type": "integer",
                        "description": "Maximum number of research steps (default: 5)",
                        "default": 5,
                    },
                    "report_style": {
                        "type": "string",
                        "enum": ["academic", "news", "social", "investment"],
                        "description": "Style of the final report (default: academic)",
                        "default": "academic",
                    },
                    "enable_clarification": {
                        "type": "boolean",
                        "description": "Enable multi-turn clarification for vague queries (default: false)",
                        "default": False,
                    },
                    "enable_background_investigation": {
                        "type": "boolean",
                        "description": "Enable pre-planning background investigation (default: true)",
                        "default": True,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="quick_research",
            description="""
Quick research mode - faster, less comprehensive research with fewer steps.

Use this for:
- Quick fact-checking
- Simple questions with straightforward answers
- When you need rapid results
- Preliminary research before deep dive

This runs the same multi-agent framework but with reduced steps and
faster processing.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The research question or topic",
                    },
                    "report_style": {
                        "type": "string",
                        "enum": ["academic", "news", "social", "investment"],
                        "description": "Style of the final report",
                        "default": "academic",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Execute research tool"""
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        if name == "deep_research":
            return await execute_deep_research(arguments)
        elif name == "quick_research":
            return await execute_quick_research(arguments)
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error executing research: {str(e)}\n\nPlease ensure the Deep Research API server is running at {API_BASE_URL}",
            )
        ]


async def execute_deep_research(arguments: dict) -> Sequence[TextContent]:
    """Execute deep research via API"""
    query = arguments.get("query")
    max_steps = arguments.get("max_steps", 5)
    report_style = arguments.get("report_style", "academic")
    enable_clarification = arguments.get("enable_clarification", False)
    enable_background_investigation = arguments.get("enable_background_investigation", True)

    if not query:
        return [TextContent(type="text", text="Error: 'query' parameter is required")]

    logger.info(f"Starting deep research: {query}")

    # Call research API
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/research",
            json={
                "query": query,
                "max_step_num": max_steps,
                "report_style": report_style,
                "enable_clarification": enable_clarification,
                "enable_background_investigation": enable_background_investigation,
                "auto_accept_plan": True,
            },
        )

        if response.status_code != 200:
            error_detail = response.text
            return [
                TextContent(
                    type="text",
                    text=f"Research API error (status {response.status_code}): {error_detail}",
                )
            ]

        result = response.json()

    # Format response
    report_text = format_research_response(result, detailed=True)
    return [TextContent(type="text", text=report_text)]


async def execute_quick_research(arguments: dict) -> Sequence[TextContent]:
    """Execute quick research with minimal steps"""
    query = arguments.get("query")
    report_style = arguments.get("report_style", "academic")

    if not query:
        return [TextContent(type="text", text="Error: 'query' parameter is required")]

    logger.info(f"Starting quick research: {query}")

    # Call research API with reduced steps
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/research",
            json={
                "query": query,
                "max_step_num": 2,  # Reduced steps for quick research
                "report_style": report_style,
                "enable_clarification": False,
                "enable_background_investigation": False,
                "auto_accept_plan": True,
            },
        )

        if response.status_code != 200:
            error_detail = response.text
            return [
                TextContent(
                    type="text",
                    text=f"Research API error (status {response.status_code}): {error_detail}",
                )
            ]

        result = response.json()

    # Format response (less detailed for quick research)
    report_text = format_research_response(result, detailed=False)
    return [TextContent(type="text", text=report_text)]


def format_research_response(result: dict, detailed: bool = True) -> str:
    """Format research API response into readable text"""
    output = []

    # Header
    output.append("# Deep Research Report\n")
    output.append(f"**Query:** {result.get('query', 'N/A')}\n")
    output.append(f"**Research ID:** {result.get('research_id', 'N/A')}\n")
    output.append("")

    # Research plan (if detailed)
    if detailed:
        plan = result.get("plan", {})
        if plan:
            output.append("## Research Plan\n")
            output.append(f"**Title:** {plan.get('title', 'N/A')}\n")
            output.append(f"**Thought:** {plan.get('thought', 'N/A')}\n")
            output.append("")

            steps = plan.get("steps", [])
            if steps:
                output.append("### Research Steps\n")
                for i, step in enumerate(steps, 1):
                    output.append(f"{i}. **{step.get('title', 'N/A')}**")
                    output.append(f"   - Type: {step.get('step_type', 'N/A')}")
                    output.append(f"   - Description: {step.get('description', 'N/A')}")
                    if step.get("execution_result"):
                        output.append(f"   - Result: {step['execution_result'][:200]}...")
                    output.append("")

    # Key observations (if detailed)
    if detailed:
        observations = result.get("observations", [])
        if observations:
            output.append("## Key Observations\n")
            for i, obs in enumerate(observations, 1):
                output.append(f"{i}. {obs}\n")
            output.append("")

    # Final report
    output.append("## Final Report\n")
    final_report = result.get("final_report", "No report generated")
    output.append(final_report)
    output.append("")

    # Resources
    resources = result.get("resources", [])
    if resources and detailed:
        output.append("## Sources\n")
        for i, resource in enumerate(resources, 1):
            url = resource.get("url", "N/A")
            title = resource.get("title", "N/A")
            output.append(f"{i}. [{title}]({url})")
        output.append("")

    return "\n".join(output)


async def main():
    """Run the MCP server"""
    logger.info("Starting Deep Research MCP Server")
    logger.info(f"API Base URL: {API_BASE_URL}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
