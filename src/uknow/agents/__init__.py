"""
Agent implementations for the UKNOW system.

Each agent wraps an LLM with specific system prompts and
produces structured JSON outputs.
"""

from uknow.agents.sparring import SparringPartner
from uknow.agents.debate import DebateAnalyst
from uknow.agents.researcher import DeepResearcher
from uknow.agents.packagers import SlidesPackager, AppPackager

__all__ = [
    "SparringPartner",
    "DebateAnalyst",
    "DeepResearcher",
    "SlidesPackager",
    "AppPackager",
]
