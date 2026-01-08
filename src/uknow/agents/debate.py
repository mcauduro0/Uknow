"""
Debate Analyst Agent (Anthropic Claude).

The Debate Analyst critiques the Sparring Partner's analysis,
adds new perspectives, and produces the final research brief.
"""

from typing import Any

from uknow.agents.base import AgentResult, AnthropicAgent
from uknow.agents.prompts import DEBATE_ANALYST_ROUND_1, DEBATE_ANALYST_ROUND_2
from uknow.models.agents import DebateAnalystOutput, DebateAnalystFinalOutput


class DebateAnalyst:
    """
    Debate Analyst agent using Anthropic Claude.

    Responsibilities:
    - Round 1: Critique Sparring Partner, add perspectives
    - Round 2: Synthesize final research brief for Gemini
    """

    def __init__(self):
        self.round_1_agent = AnthropicAgent(
            name="claude_round_1",
            system_prompt=DEBATE_ANALYST_ROUND_1,
        )
        self.round_2_agent = AnthropicAgent(
            name="claude_round_2",
            system_prompt=DEBATE_ANALYST_ROUND_2,
        )

    async def execute_round_1(
        self,
        user_question: str,
        sparring_output: dict[str, Any],
    ) -> AgentResult:
        """
        Execute Round 1: Critique Sparring Partner and add perspectives.

        Args:
            user_question: The user's original question
            sparring_output: Output from Sparring Partner Round 1

        Returns:
            AgentResult with DebateAnalystOutput structure
        """
        input_data = {
            "original_question": user_question,
            "sparring_partner_output": sparring_output,
        }

        result = await self.round_1_agent.execute(input_data)

        # Validate output structure if successful
        if result.success and result.output:
            try:
                DebateAnalystOutput.model_validate(result.output)
            except Exception as e:
                result.success = False
                result.error = f"Output validation failed: {e}"

        return result

    async def execute_round_2(
        self,
        user_question: str,
        sparring_round_1: dict[str, Any],
        claude_round_1: dict[str, Any],
        sparring_round_2: dict[str, Any],
    ) -> AgentResult:
        """
        Execute Round 2: Synthesize final research brief.

        Args:
            user_question: The user's original question
            sparring_round_1: Output from Sparring Partner Round 1
            claude_round_1: Output from Claude Round 1
            sparring_round_2: Output from Sparring Partner Round 2

        Returns:
            AgentResult with DebateAnalystFinalOutput structure
        """
        input_data = {
            "original_question": user_question,
            "sparring_round_1_output": sparring_round_1,
            "debate_analyst_round_1_output": claude_round_1,
            "sparring_round_2_output": sparring_round_2,
        }

        result = await self.round_2_agent.execute(input_data)

        # Validate output structure if successful
        if result.success and result.output:
            try:
                DebateAnalystFinalOutput.model_validate(result.output)
            except Exception as e:
                result.success = False
                result.error = f"Output validation failed: {e}"

        return result
