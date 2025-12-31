#!/usr/bin/env python3
"""
Real working demo: Research with human-in-the-loop
Run this script to see the full ask_master flow in action.
"""

import asyncio
import sys
from pathlib import Path

# Add parent dirs to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ai-orchestration"))

from ai_orchestration import Orchestrator
from vibe_docs.agents import build_research_manager_config, build_research_agent_config
from vibe_docs.tools import search_web


def create_search_web_handler():
    """Create search_web tool handler for orchestrator."""
    async def handler(inputs: dict) -> dict:
        query = inputs.get("query", "")
        return await search_web(query)

    # Wrap async handler for sync tool registration
    def sync_handler(inputs: dict) -> dict:
        return asyncio.get_event_loop().run_until_complete(handler(inputs))

    return sync_handler


async def run_interactive_session():
    """Run an interactive research session with human-in-the-loop."""

    print("=" * 60)
    print("  VIBE DOCS - Interactive Research Demo")
    print("  Human-in-the-loop with ask_master flow")
    print("=" * 60)
    print()

    # Create orchestrator
    logs_dir = Path("./demo_runs")
    orch = Orchestrator(logs_dir=logs_dir, default_model="claude-sonnet-4-20250514")

    # Register agents
    print("[SETUP] Registering agents...")
    manager_config = build_research_manager_config()
    agent_config = build_research_agent_config()

    orch.agent.create(**manager_config)
    orch.agent.create(**agent_config)
    print(f"  - {manager_config['agent_id']}: {manager_config['description']}")
    print(f"  - {agent_config['agent_id']}: {agent_config['description']}")

    # Register tools
    print("[SETUP] Registering tools...")

    # search_web tool
    orch.register_tool(
        name="search_web",
        description="Search the web for information",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        },
        handler=create_search_web_handler(),
    )
    print("  - search_web: Web search using Claude")

    # route_to_research_agent tool (delegation)
    orch.register_tool(
        name="route_to_research_agent",
        description="Delegate research to the research agent specialist",
        input_schema={
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "Research request to delegate"
                }
            },
            "required": ["request"]
        },
        handler=lambda x: {},  # Handled internally by orchestrator
        tool_type="route_to",
    )
    print("  - route_to_research_agent: Delegation tool")

    print()
    print("-" * 60)

    # Get user query
    print("Enter your research question (or 'quit' to exit):")
    print()

    user_query = input(">>> ").strip()

    if user_query.lower() == 'quit':
        print("Goodbye!")
        return

    if not user_query:
        user_query = "What is vibe coding and why is it trending?"
        print(f"Using default query: {user_query}")

    print()
    print("-" * 60)
    print(f"[START] Starting research: '{user_query}'")
    print("-" * 60)
    print()

    # Start the research task
    result = await orch.start_root_task(
        task=user_query,
        main_agent="research_manager",
        initiator="human",
    )

    # Check if we got an ask_master request
    ready_tasks = orch.graph_ops.get_ready_tasks()
    human_tasks = [
        tid for tid in ready_tasks
        if orch.graph_ops.modal.nodes[tid].agent_id == "human"
    ]

    while human_tasks:
        for task_id in human_tasks:
            node = orch.graph_ops.modal.nodes[task_id]
            question = node.task_payload

            print()
            print("=" * 60)
            print("[ASK_MASTER] Agent is asking for your input:")
            print("-" * 60)
            print(f"  {question}")
            print("-" * 60)
            print()

            user_answer = input("Your answer >>> ").strip()

            # Complete the human task with user's answer
            orch.graph_ops.complete_task(task_id, {"answer": user_answer})
            orch._save()

        # Continue execution
        result = await orch.start_root_task(
            task=user_query,
            main_agent="research_manager",
            initiator="human",
        )

        # Check for more human tasks
        ready_tasks = orch.graph_ops.get_ready_tasks()
        human_tasks = [
            tid for tid in ready_tasks
            if orch.graph_ops.modal.nodes[tid].agent_id == "human"
        ]

    # Display results
    print()
    print("=" * 60)
    print("[COMPLETE] Research Results")
    print("=" * 60)
    print()

    if result.get("result"):
        res = result["result"]
        if isinstance(res, dict):
            if "answer" in res:
                answer_data = res["answer"]
                if isinstance(answer_data, dict):
                    print("ANSWER:")
                    print("-" * 40)
                    print(answer_data.get("answer", str(answer_data)))
                    print()
                    if answer_data.get("sources"):
                        print("SOURCES:")
                        for src in answer_data["sources"]:
                            print(f"  - {src}")
                else:
                    print(answer_data)
            else:
                print(res)
        else:
            print(res)
    else:
        print("No results returned.")

    print()
    print(f"[INFO] Logs saved to: {orch._run_dir}")


if __name__ == "__main__":
    print()
    asyncio.run(run_interactive_session())
