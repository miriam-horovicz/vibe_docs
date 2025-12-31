#!/usr/bin/env python3
"""
Demo: ask_master flow - Human in the loop
Shows: Agent asks question → Human answers → Agent continues
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ai-orchestration"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_orchestration import Orchestrator
from ai_orchestration.modals.task_graph_modal import ToolType


async def main():
    print("=" * 60)
    print("  ASK_MASTER Demo - Human in the Loop")
    print("  Agent asks → Human answers → Flow continues")
    print("=" * 60)
    print()

    logs_dir = Path("./demo_runs")
    orch = Orchestrator(logs_dir=logs_dir, default_model="claude-sonnet-4-20250514")

    # Create a simple agent that ALWAYS asks master first
    print("[SETUP] Creating agent that asks for approval...")

    orch.agent.create(
        id="approval_agent",
        describe="Agent that asks master before doing anything",
        instructions="""You are an agent that ALWAYS asks for human approval before researching.

WORKFLOW:
1. FIRST: Call ask_master to ask what the user wants to focus on
2. WAIT for human response
3. After receiving response, do a simple search
4. Call handoff with results

IMPORTANT: You MUST call ask_master first before doing any research.

Example ask_master call:
ask_master("I can research: A) Basic overview, B) Technical details, C) Use cases. Which would you prefer?")
""",
        tools=["ask_master", "search_web", "handoff"],
        model="claude-sonnet-4-20250514",
    )

    # Register search_web tool
    orch.register_tool(
        name="search_web",
        description="Search the web",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        },
        handler=lambda x: {"result": f"Search results for: {x.get('query', '')}"},
    )

    print("  - approval_agent (always asks first)")
    print("  - search_web")
    print()

    # Start with ambiguous query
    query = "Tell me about machine learning"
    print(f"[START] Query: '{query}'")
    print("-" * 60)
    print()

    # First run - agent should call ask_master
    result = await orch.start_root_task(
        task=query,
        main_agent="approval_agent",
        initiator="human",
    )

    # Check for human tasks (ask_master creates these)
    ready_tasks = orch.graph_ops.get_ready_tasks()
    human_tasks = [
        tid for tid in ready_tasks
        if orch.graph_ops.modal.nodes[tid].agent_id == "human"
    ]

    if human_tasks:
        print()
        print("=" * 60)
        print("[ASK_MASTER] Agent is asking for your input!")
        print("=" * 60)

        for task_id in human_tasks:
            node = orch.graph_ops.modal.nodes[task_id]
            print()
            print(f"  Question: {node.task_payload}")
            print()
            print("-" * 60)

            # Simulate human response
            human_answer = "Focus on practical use cases and real-world applications"
            print(f"  [HUMAN RESPONSE]: {human_answer}")
            print("-" * 60)

            # Complete the human task with the answer
            orch.graph_ops.complete_task(task_id, {"answer": human_answer})
            orch._save()

        print()
        print("[RESUMING] Continuing with human's answer...")
        print()

        # Resume execution - agent continues with human's answer
        result = await orch.start_root_task(
            task=query,
            main_agent="approval_agent",
            initiator="human",
        )

    # Show final result
    print()
    print("=" * 60)
    print("[COMPLETE] Final Result")
    print("=" * 60)

    if result and result.get("result"):
        import json
        print(json.dumps(result["result"], indent=2, default=str)[:1000])
    else:
        print(result)

    print()
    print(f"[INFO] Logs: {orch._run_dir}")

    # Show the flow summary
    print()
    print("=" * 60)
    print("[FLOW SUMMARY]")
    print("=" * 60)
    print("  1. ask_master → Agent asked human for preference")
    print("  2. PAUSE → Waiting for human")
    print("  3. Human answered → 'Focus on practical use cases'")
    print("  4. RESUME → Agent continued with human's choice")
    print("  5. search_web → Searched based on human preference")
    print("  6. handoff → Delivered results matching human's request")


if __name__ == "__main__":
    asyncio.run(main())
