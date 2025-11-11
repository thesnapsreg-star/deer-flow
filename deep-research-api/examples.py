"""
Deep Research API Examples

Demonstrates how to use the Deep Research API in Python
"""
import asyncio
import httpx
import json
from typing import Optional


API_BASE_URL = "http://localhost:8080"


async def health_check():
    """Check API health"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/health")
        return response.json()


async def simple_research(query: str):
    """
    Perform simple research with default settings

    Args:
        query: Research question

    Returns:
        Research results dictionary
    """
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/research",
            json={"query": query}
        )
        return response.json()


async def advanced_research(
    query: str,
    max_steps: int = 5,
    report_style: str = "academic",
    enable_clarification: bool = False,
    enable_background: bool = True,
):
    """
    Perform advanced research with custom configuration

    Args:
        query: Research question
        max_steps: Maximum research steps
        report_style: Report style (academic, news, social, investment)
        enable_clarification: Enable query clarification
        enable_background: Enable background investigation

    Returns:
        Research results dictionary
    """
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/research",
            json={
                "query": query,
                "max_step_num": max_steps,
                "report_style": report_style,
                "enable_clarification": enable_clarification,
                "enable_background_investigation": enable_background,
                "auto_accept_plan": True,
            }
        )
        return response.json()


async def stream_research(query: str, max_steps: int = 3):
    """
    Stream research progress in real-time

    Args:
        query: Research question
        max_steps: Maximum research steps
    """
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{API_BASE_URL}/research/stream",
            json={
                "query": query,
                "max_step_num": max_steps,
            }
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    print(f"Stage: {data.get('stage')} - {data.get('message')}")
                    if data.get('observations'):
                        print(f"  Observations: {len(data['observations'])}")


async def example_1_quick_fact():
    """Example 1: Quick fact lookup"""
    print("=== Example 1: Quick Fact Lookup ===\n")

    result = await simple_research("What is the capital of France?")

    print(f"Query: {result['query']}")
    print(f"\nReport:\n{result['final_report']}")
    print(f"\nResearch ID: {result['research_id']}")


async def example_2_technical_research():
    """Example 2: Technical research with academic style"""
    print("\n=== Example 2: Technical Research ===\n")

    result = await advanced_research(
        query="Explain how transformer neural networks work",
        max_steps=5,
        report_style="academic",
        enable_background=True,
    )

    print(f"Query: {result['query']}")
    print(f"\nResearch Plan: {result['plan']['title']}")
    print(f"Steps executed: {len(result['plan']['steps'])}")
    print(f"\nObservations: {len(result['observations'])}")
    print(f"\nReport Preview:\n{result['final_report'][:500]}...")


async def example_3_market_analysis():
    """Example 3: Market analysis with investment style"""
    print("\n=== Example 3: Market Analysis ===\n")

    result = await advanced_research(
        query="Analyze the current state of the electric vehicle market",
        max_steps=6,
        report_style="investment",
        enable_background=True,
    )

    print(f"Query: {result['query']}")
    print(f"\nResearch Plan: {result['plan']['title']}")

    # Print research steps
    print("\nResearch Steps:")
    for i, step in enumerate(result['plan']['steps'], 1):
        print(f"{i}. {step['title']}")
        print(f"   Type: {step['step_type']}")

    print(f"\nSources: {len(result['resources'])}")
    print(f"\nReport:\n{result['final_report']}")


async def example_4_streaming():
    """Example 4: Streaming research progress"""
    print("\n=== Example 4: Streaming Research ===\n")

    print("Starting research with progress updates...\n")
    await stream_research(
        query="What are the latest developments in quantum computing?",
        max_steps=3
    )


async def example_5_multiple_styles():
    """Example 5: Same query with different report styles"""
    print("\n=== Example 5: Multiple Report Styles ===\n")

    query = "What is artificial general intelligence?"
    styles = ["academic", "news", "social"]

    for style in styles:
        print(f"\n--- {style.upper()} Style ---\n")
        result = await advanced_research(
            query=query,
            max_steps=2,
            report_style=style,
            enable_background=False,
        )
        print(result['final_report'][:300] + "...\n")


async def example_6_error_handling():
    """Example 6: Error handling"""
    print("\n=== Example 6: Error Handling ===\n")

    try:
        # Empty query should fail
        result = await simple_research("")
        print(result)
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Details: {e.response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")


async def example_7_comprehensive():
    """Example 7: Comprehensive research workflow"""
    print("\n=== Example 7: Comprehensive Workflow ===\n")

    # 1. Health check
    print("1. Checking API health...")
    health = await health_check()
    print(f"   Status: {health['status']}")
    print(f"   Models: {len(health['models_available'])}")

    # 2. Research
    print("\n2. Starting research...")
    query = "Compare Python and Rust for backend development"
    result = await advanced_research(
        query=query,
        max_steps=4,
        report_style="academic",
        enable_background=True,
    )

    # 3. Analysis
    print(f"\n3. Research completed!")
    print(f"   Research ID: {result['research_id']}")
    print(f"   Query: {result['query']}")
    print(f"   Plan: {result['plan']['title']}")
    print(f"   Steps: {len(result['plan']['steps'])}")
    print(f"   Observations: {len(result['observations'])}")
    print(f"   Sources: {len(result['resources'])}")

    # 4. Display key findings
    print("\n4. Key Findings:")
    for i, obs in enumerate(result['observations'][:3], 1):
        print(f"   {i}. {obs[:100]}...")

    # 5. Display sources
    print("\n5. Top Sources:")
    for i, resource in enumerate(result['resources'][:3], 1):
        print(f"   {i}. {resource.get('title', 'N/A')}")
        print(f"      {resource.get('url', 'N/A')}")

    # 6. Display report
    print("\n6. Final Report:")
    print(result['final_report'])


async def main():
    """Run all examples"""
    print("Deep Research API Examples")
    print("=" * 60)

    try:
        # Check if API is running
        await health_check()
        print("✓ API is running\n")
    except httpx.ConnectError:
        print("✗ API is not running!")
        print("\nPlease start the API server first:")
        print("  python -m api.main\n")
        return

    # Run examples
    examples = [
        ("Quick Fact", example_1_quick_fact),
        ("Technical Research", example_2_technical_research),
        ("Market Analysis", example_3_market_analysis),
        ("Streaming", example_4_streaming),
        ("Multiple Styles", example_5_multiple_styles),
        ("Error Handling", example_6_error_handling),
        ("Comprehensive", example_7_comprehensive),
    ]

    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...\n")
    print("=" * 60)

    for name, example_func in examples:
        try:
            await example_func()
        except KeyboardInterrupt:
            print("\n\nStopped by user")
            break
        except Exception as e:
            print(f"\nError in {name}: {str(e)}")
            continue

        print("\n" + "-" * 60)

    print("\nAll examples completed!")


if __name__ == "__main__":
    # Run specific example
    # asyncio.run(example_1_quick_fact())

    # Or run all examples
    asyncio.run(main())
