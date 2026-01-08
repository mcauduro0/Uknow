"""
Deep Researcher Agent (Google Gemini).

The Deep Researcher executes comprehensive research based on
the refined brief and produces the final structured report.
"""

from typing import Any

from uknow.agents.base import AgentResult, GeminiAgent
from uknow.agents.prompts import DEEP_RESEARCHER
from uknow.models.agents import ResearchOutput
from uknow.models.task import TaskMeta


class DeepResearcher:
    """
    Deep Researcher agent using Google Gemini.

    Responsibilities:
    - Execute thorough research based on the final brief
    - Produce structured, actionable reports
    - Cite sources and acknowledge uncertainties
    """

    def __init__(self):
        self.agent = GeminiAgent(
            name="gemini_research",
            system_prompt=DEEP_RESEARCHER,
        )

    async def execute(
        self,
        final_brief: str,
        research_structure: list[str],
        success_criteria: list[str],
        key_risks: list[str],
        meta: TaskMeta | dict[str, Any],
    ) -> AgentResult:
        """
        Execute deep research and produce the final report.

        Args:
            final_brief: The refined research brief from debate rounds
            research_structure: Suggested structure for the report
            success_criteria: What makes the report successful
            key_risks: Critical risks that must be addressed
            meta: Task metadata (language, detail level, format)

        Returns:
            AgentResult with ResearchOutput structure
        """
        # Convert meta to dict if it's a Pydantic model
        if hasattr(meta, "model_dump"):
            meta_dict = meta.model_dump()
        else:
            meta_dict = meta

        input_data = {
            "final_brief": final_brief,
            "final_research_structure": research_structure,
            "success_criteria": success_criteria,
            "key_risks_not_to_ignore": key_risks,
            "meta": meta_dict,
        }

        result = await self.agent.execute(input_data)

        # Validate output structure if successful
        if result.success and result.output:
            try:
                ResearchOutput.model_validate(result.output)
            except Exception as e:
                result.success = False
                result.error = f"Output validation failed: {e}"

        return result

    async def execute_from_claude_output(
        self,
        claude_final: dict[str, Any],
        meta: TaskMeta | dict[str, Any],
    ) -> AgentResult:
        """
        Convenience method to execute directly from Claude's final output.

        Args:
            claude_final: The DebateAnalystFinalOutput from Claude Round 2
            meta: Task metadata

        Returns:
            AgentResult with ResearchOutput structure
        """
        return await self.execute(
            final_brief=claude_final.get("final_brief", ""),
            research_structure=claude_final.get("final_research_structure", []),
            success_criteria=claude_final.get("success_criteria", []),
            key_risks=claude_final.get("key_risks_not_to_ignore", []),
            meta=meta,
        )
