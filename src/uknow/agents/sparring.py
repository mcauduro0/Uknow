"""
Sparring Partner Agent (OpenAI GPT).

The Sparring Partner challenges assumptions, identifies blind spots,
and prepares research briefs through skeptical questioning.
"""

from typing import Any

from uknow.agents.base import AgentResult, OpenAIAgent
from uknow.agents.prompts import SPARRING_PARTNER_ROUND_1, SPARRING_PARTNER_ROUND_2
from uknow.models.agents import SparringOutput, SparringRound2Output


class SparringPartner:
    """
    Sparring Partner agent using OpenAI GPT.

    Responsibilities:
    - Round 1: Analyze user's question, identify assumptions and blind spots
    - Round 2: Refine analysis after Claude's critique
    """

    def __init__(self):
        self.round_1_agent = OpenAIAgent(
            name="sparring_round_1",
            system_prompt=SPARRING_PARTNER_ROUND_1,
        )
        self.round_2_agent = OpenAIAgent(
            name="sparring_round_2",
            system_prompt=SPARRING_PARTNER_ROUND_2,
        )

    async def execute_round_1(
        self,
        user_question: str,
        context: dict[str, Any] | None = None,
    ) -> AgentResult:
        """
        Execute Round 1: Initial analysis of user's question.

        Args:
            user_question: The user's original question/request
            context: Optional additional context

        Returns:
            AgentResult with SparringOutput structure
        """
        input_data = {
            "user_question": user_question,
        }
        if context:
            input_data["context"] = context

        result = await self.round_1_agent.execute(input_data)

        # Validate output structure if successful
        if result.success and result.output:
            try:
                SparringOutput.model_validate(result.output)
            except Exception as e:
                result.success = False
                result.error = f"Output validation failed: {e}"

        return result

    async def execute_round_2(
        self,
        user_question: str,
        sparring_round_1: dict[str, Any],
        claude_round_1: dict[str, Any],
    ) -> AgentResult:
        """
        Execute Round 2: Refine analysis after Claude's critique.

        Args:
            user_question: The user's original question
            sparring_round_1: Output from Sparring Round 1
            claude_round_1: Output from Claude Round 1

        Returns:
            AgentResult with SparringRound2Output structure
        """
        input_data = {
            "original_question": user_question,
            "sparring_round_1_output": sparring_round_1,
            "debate_analyst_critique": claude_round_1,
        }

        result = await self.round_2_agent.execute(input_data)

        # Validate output structure if successful
        if result.success and result.output:
            try:
                SparringRound2Output.model_validate(result.output)
            except Exception as e:
                result.success = False
                result.error = f"Output validation failed: {e}"

        return result
