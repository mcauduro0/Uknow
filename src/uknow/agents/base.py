"""
Base agent class and LLM connectors.

Provides a unified interface for calling different LLM providers
with structured JSON outputs.
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import structlog
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from uknow.config import get_settings

logger = structlog.get_logger()

T = TypeVar("T", bound=BaseModel)


class AgentResult(BaseModel):
    """Result from an agent call."""

    success: bool
    output: dict[str, Any] | None = None
    error: str | None = None
    tokens_used: int = 0
    duration_ms: int = 0


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str):
        self.name = name
        self.settings = get_settings()
        self.logger = logger.bind(agent=name)

    @abstractmethod
    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute the agent with given input."""
        pass

    def _parse_json_output(self, text: str) -> dict[str, Any]:
        """Parse JSON from LLM output, handling markdown code blocks."""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())


class OpenAIAgent(BaseAgent):
    """Agent using OpenAI API."""

    def __init__(self, name: str, system_prompt: str):
        super().__init__(name)
        self.system_prompt = system_prompt
        self._client = None

    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(
                api_key=self.settings.openai_api_key.get_secret_value()
            )
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute the agent with OpenAI."""
        start_time = time.time()

        try:
            user_content = json.dumps(input_data, ensure_ascii=False, indent=2)

            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4096,
            )

            output_text = response.choices[0].message.content or ""
            output_json = self._parse_json_output(output_text)

            tokens_used = response.usage.total_tokens if response.usage else 0
            duration_ms = int((time.time() - start_time) * 1000)

            self.logger.info(
                "Agent execution completed",
                tokens_used=tokens_used,
                duration_ms=duration_ms,
            )

            return AgentResult(
                success=True,
                output=output_json,
                tokens_used=tokens_used,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.logger.error("Agent execution failed", error=str(e))
            return AgentResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )


class AnthropicAgent(BaseAgent):
    """Agent using Anthropic Claude API."""

    def __init__(self, name: str, system_prompt: str):
        super().__init__(name)
        self.system_prompt = system_prompt
        self._client = None

    @property
    def client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            from anthropic import AsyncAnthropic

            self._client = AsyncAnthropic(
                api_key=self.settings.anthropic_api_key.get_secret_value()
            )
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute the agent with Claude."""
        start_time = time.time()

        try:
            user_content = json.dumps(input_data, ensure_ascii=False, indent=2)

            response = await self.client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )

            output_text = response.content[0].text if response.content else ""
            output_json = self._parse_json_output(output_text)

            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            duration_ms = int((time.time() - start_time) * 1000)

            self.logger.info(
                "Agent execution completed",
                tokens_used=tokens_used,
                duration_ms=duration_ms,
            )

            return AgentResult(
                success=True,
                output=output_json,
                tokens_used=tokens_used,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.logger.error("Agent execution failed", error=str(e))
            return AgentResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )


class GeminiAgent(BaseAgent):
    """Agent using Google Gemini API."""

    def __init__(self, name: str, system_prompt: str):
        super().__init__(name)
        self.system_prompt = system_prompt
        self._model = None

    @property
    def model(self):
        """Lazy initialization of Gemini model."""
        if self._model is None:
            import google.generativeai as genai

            genai.configure(api_key=self.settings.google_api_key.get_secret_value())
            self._model = genai.GenerativeModel(
                model_name=self.settings.gemini_model,
                system_instruction=self.system_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                },
            )
        return self._model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute the agent with Gemini."""
        start_time = time.time()

        try:
            user_content = json.dumps(input_data, ensure_ascii=False, indent=2)

            # Gemini's async support
            response = await self.model.generate_content_async(user_content)

            output_text = response.text or ""
            output_json = self._parse_json_output(output_text)

            # Gemini token counting is different
            tokens_used = 0
            if hasattr(response, "usage_metadata"):
                tokens_used = (
                    response.usage_metadata.prompt_token_count
                    + response.usage_metadata.candidates_token_count
                )

            duration_ms = int((time.time() - start_time) * 1000)

            self.logger.info(
                "Agent execution completed",
                tokens_used=tokens_used,
                duration_ms=duration_ms,
            )

            return AgentResult(
                success=True,
                output=output_json,
                tokens_used=tokens_used,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.logger.error("Agent execution failed", error=str(e))
            return AgentResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )
