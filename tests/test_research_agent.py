import pytest
from vibe_docs.agents.research_agent import build_research_agent_config


def test_research_agent_has_no_sql_tools():
    config = build_research_agent_config()
    sql_tools = ["generate_sql", "execute_query", "load_table_metadata", "get_latest_partition"]
    for tool in sql_tools:
        assert tool not in config["tools"], f"Should not have SQL tool: {tool}"


def test_research_agent_has_web_search():
    config = build_research_agent_config()
    assert "search_web" in config["tools"]


def test_research_agent_has_handoff():
    config = build_research_agent_config()
    assert "handoff" in config["tools"]
