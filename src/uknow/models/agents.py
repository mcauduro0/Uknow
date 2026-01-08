"""
Agent output models for the UKNOW system.

Each agent produces structured JSON output that feeds into
the next stage of the pipeline.
"""

from typing import Literal

from pydantic import BaseModel, Field


# =============================================================================
# SPARRING PARTNER (OpenAI) - Round 1
# =============================================================================


class ClarificationQuestion(BaseModel):
    """A clarification question from the Sparring Partner."""

    id: str = Field(..., description="Question identifier (e.g., Q1, Q2)")
    question: str = Field(..., description="The clarification question")
    why_it_matters: str = Field(..., description="Why this question is important")
    hypothetical_answers: list[str] = Field(
        default_factory=list,
        description="Possible answers based on general knowledge",
    )


class SparringOutput(BaseModel):
    """
    Output from Sparring Partner Round 1.

    The Sparring Partner challenges the user's request, identifies
    assumptions, blind spots, and prepares a research brief.
    """

    summarized_objective: str = Field(
        ...,
        description="The user's goal restated in the agent's own words",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Implicit assumptions the user appears to be making",
    )
    risks_and_blindspots: list[str] = Field(
        default_factory=list,
        description="Potential risks and blind spots identified",
    )
    clarification_questions: list[ClarificationQuestion] = Field(
        default_factory=list,
        description="Questions that could change the research direction",
    )
    recommended_brief: str = Field(
        ...,
        description="Initial research brief incorporating hypotheses",
    )


class SparringRound2Output(BaseModel):
    """
    Output from Sparring Partner Round 2.

    After receiving Claude's critique, the Sparring Partner refines
    their analysis, resolves divergences, and improves the brief.
    """

    updated_risks_and_blindspots: list[str] = Field(
        default_factory=list,
        description="Refined list of risks and blind spots",
    )
    resolved_divergences: list[str] = Field(
        default_factory=list,
        description="Key disagreements that were resolved",
    )
    updated_brief: str = Field(
        ...,
        description="Improved research brief",
    )


# =============================================================================
# DEBATE ANALYST (Claude) - Round 1
# =============================================================================


class AdditionalQuestion(BaseModel):
    """An additional question from the Debate Analyst."""

    id: str = Field(..., description="Question identifier (e.g., CQ1, CQ2)")
    question: str = Field(..., description="The additional question")
    justification: str = Field(..., description="Why this question matters")


class DebateAnalystOutput(BaseModel):
    """
    Output from Debate Analyst (Claude) Round 1.

    Claude critiques the Sparring Partner's analysis, adds new perspectives,
    and suggests a structured approach for research.
    """

    comments_on_sparring: list[str] = Field(
        default_factory=list,
        description="Critique of the Sparring Partner's analysis",
    )
    new_perspectives: list[str] = Field(
        default_factory=list,
        description="Additional angles not covered by Sparring Partner",
    )
    additional_questions: list[AdditionalQuestion] = Field(
        default_factory=list,
        description="Important questions to add",
    )
    suggested_research_structure: list[str] = Field(
        default_factory=list,
        description="Proposed structure for the research/report",
    )
    refined_brief: str = Field(
        ...,
        description="Improved research brief",
    )


class DebateAnalystFinalOutput(BaseModel):
    """
    Final output from Debate Analyst (Claude) Round 2.

    This is the converged brief that will be sent to the Deep Researcher.
    Focus is on synthesis and clarity.
    """

    final_brief: str = Field(
        ...,
        description="The definitive research brief for Gemini",
    )
    final_research_structure: list[str] = Field(
        default_factory=list,
        description="Final structure the report should follow",
    )
    success_criteria: list[str] = Field(
        default_factory=list,
        description="What makes a successful report",
    )
    key_risks_not_to_ignore: list[str] = Field(
        default_factory=list,
        description="Critical risks that must be addressed",
    )


# =============================================================================
# DEEP RESEARCHER (Gemini)
# =============================================================================


class AnalysisSection(BaseModel):
    """A section of detailed analysis in the research output."""

    topic: str = Field(..., description="Topic or section name")
    content: str = Field(..., description="Detailed analysis content")
    risks_and_uncertainties: list[str] = Field(
        default_factory=list,
        description="Risks and uncertainties for this topic",
    )
    contrarian_views: list[str] = Field(
        default_factory=list,
        description="Alternative or opposing perspectives",
    )


class PrioritizedRecommendation(BaseModel):
    """A prioritized recommendation from the research."""

    id: str = Field(..., description="Recommendation identifier (e.g., R1, R2)")
    description: str = Field(..., description="The recommendation")
    priority: Literal["high", "medium", "low"] = Field(
        ...,
        description="Priority level",
    )
    rationale: str = Field(..., description="Why this recommendation matters")


class ResearchOutput(BaseModel):
    """
    Complete output from the Deep Researcher (Gemini).

    This is the comprehensive research report that addresses
    the refined brief from the debate rounds.
    """

    executive_summary: str = Field(
        ...,
        description="High-level summary of findings",
    )
    context: str = Field(
        ...,
        description="Background and context for the research",
    )
    key_questions: list[str] = Field(
        default_factory=list,
        description="Key questions addressed in the research",
    )
    detailed_analysis: list[AnalysisSection] = Field(
        default_factory=list,
        description="In-depth analysis sections",
    )
    prioritized_recommendations: list[PrioritizedRecommendation] = Field(
        default_factory=list,
        description="Actionable recommendations",
    )
    suggested_appendices: list[str] = Field(
        default_factory=list,
        description="Additional materials that could be helpful",
    )
    summarized_references: list[str] = Field(
        default_factory=list,
        description="Brief references (author, year, or site)",
    )


# =============================================================================
# PACKAGERS
# =============================================================================


class Slide(BaseModel):
    """A single slide in a presentation."""

    number: int = Field(..., description="Slide number")
    title: str = Field(..., description="Slide title")
    bullet_points: list[str] = Field(
        default_factory=list,
        description="Content bullet points",
    )


class SlidesOutput(BaseModel):
    """
    Output from the Slides Packager.

    Transforms the research report into a presentation outline
    suitable for Manus or GenSpark.
    """

    slides: list[Slide] = Field(
        default_factory=list,
        description="List of slides in order",
    )


class ScreenSection(BaseModel):
    """A section/screen in the app specification."""

    name: str = Field(..., description="Screen or section name")
    description: str = Field(..., description="What this section does")
    report_content_used: list[str] = Field(
        default_factory=list,
        description="Which parts of the report are displayed here",
    )


class AppSpecOutput(BaseModel):
    """
    Output from the App Packager.

    Transforms the research report into an app/webpage specification
    suitable for Replit Agent.
    """

    general_description: str = Field(
        ...,
        description="Overall purpose of the app/page",
    )
    features: list[str] = Field(
        default_factory=list,
        description="Main features/functionality",
    )
    screens_or_sections: list[ScreenSection] = Field(
        default_factory=list,
        description="App screens or page sections",
    )
    suggested_stack: str = Field(
        ...,
        description="Recommended tech stack for prototyping",
    )
