"""
UKNOW - Multi-Agent AI Research and Business Intelligence System

A channel-agnostic AI orchestration system that coordinates multiple LLMs
for deep research and business intelligence tasks.

Architecture:
- Sparring Partner (OpenAI): Challenges assumptions, identifies blind spots
- Debate Analyst (Claude): Critiques, expands perspectives, structures analysis
- Deep Researcher (Gemini): Executes thorough research with external tools
- Packagers: Transform reports into slides or apps

Flow:
User → Orchestrator → Sparring → Claude → Sparring → Claude → Gemini → Packager → User
"""

__version__ = "0.1.0"
__author__ = "Uknow Team"
