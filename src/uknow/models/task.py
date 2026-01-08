"""
Task models for the UKNOW orchestration system.

A Task represents a user's research request as it flows through
the multi-agent pipeline.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskState(str, Enum):
    """
    State machine for task processing.

    Flow:
    RECEIVED → SPARRING_ROUND_1 → CLAUDE_ROUND_1 → SPARRING_ROUND_2
    → CLAUDE_ROUND_2 → GEMINI_RESEARCH → PACKAGING → COMPLETED

    Any state can transition to ERROR.
    """

    RECEIVED = "RECEIVED"
    SPARRING_ROUND_1 = "SPARRING_ROUND_1"
    CLAUDE_ROUND_1 = "CLAUDE_ROUND_1"
    SPARRING_ROUND_2 = "SPARRING_ROUND_2"
    CLAUDE_ROUND_2 = "CLAUDE_ROUND_2"
    GEMINI_RESEARCH = "GEMINI_RESEARCH"
    PACKAGING = "PACKAGING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

    @property
    def next_state(self) -> "TaskState | None":
        """Get the next state in the pipeline."""
        transitions = {
            TaskState.RECEIVED: TaskState.SPARRING_ROUND_1,
            TaskState.SPARRING_ROUND_1: TaskState.CLAUDE_ROUND_1,
            TaskState.CLAUDE_ROUND_1: TaskState.SPARRING_ROUND_2,
            TaskState.SPARRING_ROUND_2: TaskState.CLAUDE_ROUND_2,
            TaskState.CLAUDE_ROUND_2: TaskState.GEMINI_RESEARCH,
            TaskState.GEMINI_RESEARCH: TaskState.PACKAGING,
            TaskState.PACKAGING: TaskState.COMPLETED,
        }
        return transitions.get(self)

    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self in (TaskState.COMPLETED, TaskState.ERROR)


class OutputFormat(str, Enum):
    """Available output formats for the final deliverable."""

    REPORT = "report"
    SLIDES = "slides"
    APP = "app"


class DetailLevel(str, Enum):
    """Level of detail for the research output."""

    EXECUTIVE = "executive"
    DEEP = "deep"


class TaskMeta(BaseModel):
    """Metadata for task processing preferences."""

    output_format: OutputFormat = OutputFormat.REPORT
    language: str = "en-US"
    detail_level: DetailLevel = DetailLevel.DEEP


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    channel: str = Field(..., description="Source channel (e.g., 'whatsapp', 'web')")
    user_id: str = Field(..., description="User identifier from the channel")
    initial_question: str = Field(..., description="The user's original question/request")
    meta: TaskMeta = Field(default_factory=TaskMeta)


class TaskUpdate(BaseModel):
    """Schema for updating task state."""

    state: TaskState | None = None
    error_message: str | None = None


class HistoryEntry(BaseModel):
    """A single entry in the task history."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent: str = Field(..., description="Agent that produced this output")
    state: TaskState
    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    tokens_used: int = 0
    duration_ms: int = 0
    error: str | None = None


class Task(BaseModel):
    """
    Complete task model with full state and history.

    This is the central data structure that flows through the entire
    multi-agent pipeline.
    """

    # Identifiers
    task_id: UUID = Field(default_factory=uuid4)
    channel: str
    user_id: str

    # Content
    initial_question: str

    # State
    state: TaskState = TaskState.RECEIVED
    error_message: str | None = None

    # Processing history
    history: list[HistoryEntry] = Field(default_factory=list)

    # Metadata
    meta: TaskMeta = Field(default_factory=TaskMeta)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    # Metrics
    total_tokens_used: int = 0
    total_duration_ms: int = 0

    def add_history(
        self,
        agent: str,
        state: TaskState,
        output_data: dict[str, Any] | None = None,
        input_data: dict[str, Any] | None = None,
        tokens_used: int = 0,
        duration_ms: int = 0,
        error: str | None = None,
    ) -> None:
        """Add an entry to the processing history."""
        entry = HistoryEntry(
            agent=agent,
            state=state,
            input_data=input_data,
            output_data=output_data,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            error=error,
        )
        self.history.append(entry)
        self.total_tokens_used += tokens_used
        self.total_duration_ms += duration_ms
        self.updated_at = datetime.utcnow()

    def transition_to(self, new_state: TaskState) -> None:
        """Transition to a new state."""
        self.state = new_state
        self.updated_at = datetime.utcnow()
        if new_state.is_terminal:
            self.completed_at = datetime.utcnow()

    def get_latest_output(self, agent: str) -> dict[str, Any] | None:
        """Get the most recent output from a specific agent."""
        for entry in reversed(self.history):
            if entry.agent == agent and entry.output_data:
                return entry.output_data
        return None

    def get_sparring_round_1(self) -> dict[str, Any] | None:
        """Get Sparring Partner round 1 output."""
        return self.get_latest_output("sparring_round_1")

    def get_claude_round_1(self) -> dict[str, Any] | None:
        """Get Claude round 1 output."""
        return self.get_latest_output("claude_round_1")

    def get_sparring_round_2(self) -> dict[str, Any] | None:
        """Get Sparring Partner round 2 output."""
        return self.get_latest_output("sparring_round_2")

    def get_claude_final(self) -> dict[str, Any] | None:
        """Get Claude final output (round 2)."""
        return self.get_latest_output("claude_round_2")

    def get_research_output(self) -> dict[str, Any] | None:
        """Get Gemini research output."""
        return self.get_latest_output("gemini_research")
