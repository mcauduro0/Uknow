"""
Packager Agents for transforming research reports.

- SlidesPackager: Converts report to presentation outline (for Manus/GenSpark)
- AppPackager: Converts report to app specification (for Replit Agent)
"""

from typing import Any

from uknow.agents.base import AgentResult, OpenAIAgent
from uknow.agents.prompts import APP_PACKAGER, SLIDES_PACKAGER
from uknow.models.agents import AppSpecOutput, SlidesOutput


class SlidesPackager:
    """
    Slides Packager agent using OpenAI GPT.

    Transforms the research report into a presentation outline
    suitable for Manus or GenSpark.
    """

    def __init__(self):
        self.agent = OpenAIAgent(
            name="slides_packager",
            system_prompt=SLIDES_PACKAGER,
        )

    async def execute(
        self,
        research_output: dict[str, Any],
    ) -> AgentResult:
        """
        Transform research report into slides outline.

        Args:
            research_output: The ResearchOutput from Gemini

        Returns:
            AgentResult with SlidesOutput structure
        """
        input_data = {
            "research_report": research_output,
        }

        result = await self.agent.execute(input_data)

        # Validate output structure if successful
        if result.success and result.output:
            try:
                SlidesOutput.model_validate(result.output)
            except Exception as e:
                result.success = False
                result.error = f"Output validation failed: {e}"

        return result

    def format_for_manus(self, slides_output: dict[str, Any]) -> str:
        """
        Format slides output as text prompt for Manus/GenSpark.

        Args:
            slides_output: The SlidesOutput JSON

        Returns:
            Text prompt for presentation generation
        """
        lines = [
            "Create a professional presentation with the following slides:\n"
        ]

        for slide in slides_output.get("slides", []):
            lines.append(f"\n## Slide {slide['number']}: {slide['title']}")
            for bullet in slide.get("bullet_points", []):
                lines.append(f"- {bullet}")

        lines.append(
            "\n\nDesign guidelines:"
            "\n- Use a clean, modern design"
            "\n- Include relevant icons or simple graphics"
            "\n- Ensure good contrast and readability"
            "\n- Keep animations minimal and professional"
        )

        return "\n".join(lines)


class AppPackager:
    """
    App Packager agent using OpenAI GPT.

    Transforms the research report into an app/webpage specification
    suitable for Replit Agent.
    """

    def __init__(self):
        self.agent = OpenAIAgent(
            name="app_packager",
            system_prompt=APP_PACKAGER,
        )

    async def execute(
        self,
        research_output: dict[str, Any],
    ) -> AgentResult:
        """
        Transform research report into app specification.

        Args:
            research_output: The ResearchOutput from Gemini

        Returns:
            AgentResult with AppSpecOutput structure
        """
        input_data = {
            "research_report": research_output,
        }

        result = await self.agent.execute(input_data)

        # Validate output structure if successful
        if result.success and result.output:
            try:
                AppSpecOutput.model_validate(result.output)
            except Exception as e:
                result.success = False
                result.error = f"Output validation failed: {e}"

        return result

    def format_for_replit(self, app_spec: dict[str, Any]) -> str:
        """
        Format app specification as text prompt for Replit Agent.

        Args:
            app_spec: The AppSpecOutput JSON

        Returns:
            Text prompt for app generation
        """
        lines = [
            f"Build a web application: {app_spec.get('general_description', '')}\n",
            "\n## Features:",
        ]

        for feature in app_spec.get("features", []):
            lines.append(f"- {feature}")

        lines.append("\n## Screens/Sections:")
        for section in app_spec.get("screens_or_sections", []):
            lines.append(f"\n### {section['name']}")
            lines.append(f"Description: {section['description']}")
            lines.append(f"Content: {', '.join(section.get('report_content_used', []))}")

        stack = app_spec.get("suggested_stack", "HTML, CSS, JavaScript")
        lines.append(f"\n## Tech Stack: {stack}")

        lines.append(
            "\n\nRequirements:"
            "\n- Responsive design for mobile and desktop"
            "\n- Clean, professional UI"
            "\n- Easy navigation between sections"
            "\n- Include a way to export or share the content"
        )

        return "\n".join(lines)
