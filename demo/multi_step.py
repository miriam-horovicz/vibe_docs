#!/usr/bin/env python3
"""
Demo: Multi-step research
Shows Research Manager delegating multiple subtasks to Research Agent
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
    print("  Multi-Step Research Demo")
    print("  Manager delegates multiple subtasks to Research Agent")
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
        handler=lambda x: {"result": f"Web search for: {x.get('query', '')}"},
    )

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

    # Multi-part research query
    query = "Compare Python and JavaScript: which is better for web development and which for data science?"
    print(f"[START] Multi-part query:")
    print(f"  '{query}'")
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
