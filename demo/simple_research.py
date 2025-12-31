#!/usr/bin/env python3
"""
Demo: Simple research query
Shows basic flow: user -> research_manager -> research_agent -> result
"""

import asyncio
import sys
from pathlib import Path

# Add paths for local packages
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ai-orchestration"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_orchestration import Orchestrator
from vibe_docs.agents import build_research_manager_config, build_research_agent_config


async def main():
    print("=" * 60)
    print("  Simple Research Demo")
    print("  Basic flow: user -> research_manager -> research_agent -> result")
    print("=" * 60)
    print()

    # Create orchestrator
    logs_dir = Path("./demo_runs")
    orch = Orchestrator(logs_dir=logs_dir, default_model="claude-sonnet-4-20250514")

    # Register agents
    print("[SETUP] Registering agents...")
    manager_config = build_research_manager_config()
    agent_config = build_research_agent_config()

    orch.agent.create(
        id=manager_config["agent_id"],
        describe=manager_config["description"],
        instructions=manager_config["instructions"],
        tools=manager_config["tools"],
        model=manager_config.get("force_model"),
    )
    orch.agent.create(
        id=agent_config["agent_id"],
        describe=agent_config["description"],
        instructions=agent_config["instructions"],
        tools=agent_config["tools"],
        model=agent_config.get("force_model"),
    )
    print(f"  - research_manager")
    print(f"  - research_agent")

    # Register tools
    print("[SETUP] Registering tools...")

    # search_web tool - using Claude's built-in web search
    orch.register_tool(
        name="search_web",
        description="Search the web for information",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        },
        handler=lambda x: {"result": f"Web search placeholder for: {x.get('query', '')}"},
    )

    # route_to_research_agent tool
    orch.register_tool(
        name="route_to_research_agent",
        description="Delegate research to the research agent specialist",
        input_schema={
            "type": "object",
            "properties": {
                "request": {"type": "string", "description": "Research request"}
            },
            "required": ["request"]
        },
        handler=lambda x: {},
        tool_type="route_to",
    )

    print("  - search_web")
    print("  - route_to_research_agent")
    print()

    # Simple research query
    query = "What is vibe coding?"
    print(f"[START] Query: '{query}'")
    print("-" * 60)
    print()

    # Start research
    result = await orch.start_root_task(
        task=query,
        main_agent="research_manager",
        initiator="human",
    )

    print()
    print("=" * 60)
    print("[RESULT]")
    print("=" * 60)
    print(result)
    print()
    print(f"[INFO] Logs saved to: {orch._run_dir}")


if __name__ == "__main__":
    asyncio.run(main())
