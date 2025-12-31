"""Vibe Docs - Research agents for document and web research"""

from .agents import build_research_manager_config, build_research_agent_config
from .tools import search_web

__version__ = "0.1.0"
__all__ = [
    "build_research_manager_config",
    "build_research_agent_config",
    "search_web",
]
