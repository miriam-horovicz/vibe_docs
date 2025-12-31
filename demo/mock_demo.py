#!/usr/bin/env python3
"""
Mock Demo: Shows the full research flow without requiring API key
Simulates agent behavior to demonstrate the architecture
"""

import asyncio
from pathlib import Path
from datetime import datetime


class MockTask:
    """Mock task node"""
    def __init__(self, task_id, agent_id, payload, parent=None):
        self.task_id = task_id
        self.agent_id = agent_id
        self.payload = payload
        self.parent = parent
        self.status = "pending"
        self.result = None
        self.children = []


class MockOrchestrator:
    """Mock orchestrator showing the flow"""

    def __init__(self):
        self.tasks = {}
        self.task_counter = 0
        self.logs = []

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {msg}")
        print(f"  [{timestamp}] {msg}")

    async def run(self, query: str):
        """Run the full research flow"""

        print()
        print("=" * 70)
        print("  RESEARCH FLOW SIMULATION")
        print("  Query: " + query)
        print("=" * 70)
        print()

        # Step 1: Create root task
        root = self.create_task("research_manager", query, parent="human")
        self.log(f"ROOT TASK created: task_{root.task_id}")
        self.log(f"  Assigned to: research_manager")
        self.log(f"  Payload: {query}")
        print()

        # Step 2: Research Manager processes
        await asyncio.sleep(0.5)
        print("-" * 70)
        print("  RESEARCH MANAGER thinking...")
        print("-" * 70)
        self.log("research_manager analyzing query...")

        # Manager decision: delegate to research_agent
        await asyncio.sleep(0.5)
        self.log("research_manager calling tool: route_to_research_agent")
        child = self.create_task("research_agent",
            f"Search the web to find information about: {query}",
            parent=root)
        self.log(f"  DELEGATION: Created task_{child.task_id} for research_agent")
        print()

        # Step 3: Research Agent executes
        await asyncio.sleep(0.5)
        print("-" * 70)
        print("  RESEARCH AGENT executing...")
        print("-" * 70)
        self.log("research_agent received task")

        # Agent uses search_web tool
        await asyncio.sleep(0.5)
        self.log("research_agent calling tool: search_web")
        self.log(f'  Query: "{query}"')

        # Mock search results
        await asyncio.sleep(0.5)
        mock_results = {
            "answer": (
                "Vibe coding (also called 'vibe-based programming') is a software development "
                "approach introduced in early 2025 where developers describe what they want "
                "in natural language and AI generates the code. Instead of writing code line-by-line, "
                "developers focus on the 'vibe' or intent, and AI tools like Claude Code, "
                "Cursor, or GitHub Copilot translate that into working software. "
                "Key characteristics include: conversational programming, "
                "AI-assisted debugging, and rapid prototyping."
            ),
            "sources": [
                "https://example.com/vibe-coding-explained",
                "https://example.com/ai-programming-trends-2025"
            ]
        }
        self.log("search_web returned results")
        self.log(f"  Sources found: {len(mock_results['sources'])}")
        print()

        # Agent calls handoff
        await asyncio.sleep(0.5)
        self.log("research_agent calling tool: handoff")
        child.result = {
            "answer": mock_results,
            "summary": "Vibe coding: AI-assisted development approach"
        }
        child.status = "completed"
        self.log(f"  task_{child.task_id} COMPLETED")
        print()

        # Step 4: Back to Research Manager
        await asyncio.sleep(0.5)
        print("-" * 70)
        print("  RESEARCH MANAGER synthesizing results...")
        print("-" * 70)
        self.log("research_manager received results from research_agent")

        # Manager calls handoff with final result
        await asyncio.sleep(0.5)
        self.log("research_manager calling tool: handoff")
        root.result = child.result
        root.status = "completed"
        self.log(f"  task_{root.task_id} COMPLETED")
        print()

        # Final output
        print("=" * 70)
        print("  FINAL RESULT")
        print("=" * 70)
        print()
        print("Answer:")
        print("-" * 70)
        print(mock_results["answer"])
        print("-" * 70)
        print()
        print("Sources:")
        for src in mock_results["sources"]:
            print(f"  - {src}")
        print()

        return root.result

    def create_task(self, agent_id, payload, parent=None):
        task = MockTask(self.task_counter, agent_id, payload, parent)
        self.tasks[self.task_counter] = task
        self.task_counter += 1
        if isinstance(parent, MockTask):
            parent.children.append(task)
        return task


async def demo_ask_master_flow():
    """Show ask_master flow"""
    print()
    print("=" * 70)
    print("  ASK_MASTER FLOW SIMULATION")
    print("  Shows human-in-the-loop interaction")
    print("=" * 70)
    print()

    query = "Tell me about AI"

    print(f"Query: {query}")
    print()
    print("-" * 70)
    print("  RESEARCH MANAGER analyzing...")
    print("-" * 70)
    print()

    await asyncio.sleep(0.5)
    print("  [12:34:56] research_manager: Query is ambiguous")
    print("  [12:34:56] research_manager calling tool: ask_master")
    print()

    print("=" * 70)
    print("  [ASK_MASTER] Agent needs clarification:")
    print("-" * 70)
    print('  "I found several areas of AI to research:')
    print("    1. Machine Learning fundamentals")
    print("    2. Large Language Models (like ChatGPT)")
    print("    3. Computer Vision")
    print("    4. AI in robotics")
    print()
    print('   Which area should I focus on?"')
    print("-" * 70)
    print()
    print("  >>> EXECUTION PAUSED - Waiting for human response")
    print()
    print("  (User would type their answer here)")
    print("  (e.g., 'Focus on Large Language Models')")
    print()
    print("  After user responds, execution resumes with their choice.")
    print("=" * 70)


async def main():
    print("\n" + "=" * 70)
    print("  VIBE DOCS - Mock Demo (no API key needed)")
    print("  Shows full orchestration flow with simulated responses")
    print("=" * 70)
    print()

    # Run simple research demo
    orch = MockOrchestrator()
    await orch.run("What is vibe coding?")

    print()
    print()

    # Show ask_master flow
    await demo_ask_master_flow()

    print()
    print("=" * 70)
    print("  DEMO COMPLETE")
    print()
    print("  To run with real AI responses:")
    print("    export ANTHROPIC_API_KEY='your-api-key'")
    print("    python demo/simple_research.py")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
