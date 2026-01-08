"""
Core Orchestrator for the UKNOW multi-agent system.

Coordinates the flow between agents and manages task state.
"""

import structlog

from uknow.agents import (
    AppPackager,
    DebateAnalyst,
    DeepResearcher,
    SlidesPackager,
    SparringPartner,
)
from uknow.agents.base import AgentResult
from uknow.config import get_settings
from uknow.models.task import OutputFormat, Task, TaskState

logger = structlog.get_logger()


class Orchestrator:
    """
    Central orchestrator that coordinates all agents.

    Flow:
    1. Sparring Round 1: Initial analysis
    2. Claude Round 1: Critique and expand
    3. Sparring Round 2: Refine after critique
    4. Claude Round 2: Final synthesis
    5. Gemini Research: Deep research
    6. Packaging: Transform to output format
    """

    def __init__(self):
        self.settings = get_settings()
        self.logger = logger.bind(component="orchestrator")

        # Initialize agents
        self.sparring = SparringPartner()
        self.debate = DebateAnalyst()
        self.researcher = DeepResearcher()
        self.slides_packager = SlidesPackager()
        self.app_packager = AppPackager()

    async def process_task(self, task: Task) -> Task:
        """
        Process a task through the entire multi-agent pipeline.

        Args:
            task: The task to process

        Returns:
            The processed task with all outputs
        """
        self.logger.info(
            "Starting task processing",
            task_id=str(task.task_id),
            initial_state=task.state.value,
        )

        try:
            # Execute the pipeline based on current state
            while not task.state.is_terminal:
                task = await self._execute_step(task)

        except Exception as e:
            self.logger.error(
                "Task processing failed",
                task_id=str(task.task_id),
                error=str(e),
            )
            task.transition_to(TaskState.ERROR)
            task.error_message = str(e)

        self.logger.info(
            "Task processing completed",
            task_id=str(task.task_id),
            final_state=task.state.value,
            total_tokens=task.total_tokens_used,
            total_duration_ms=task.total_duration_ms,
        )

        return task

    async def _execute_step(self, task: Task) -> Task:
        """Execute the current step based on task state."""
        state = task.state

        if state == TaskState.RECEIVED:
            task.transition_to(TaskState.SPARRING_ROUND_1)
            return task

        elif state == TaskState.SPARRING_ROUND_1:
            return await self._run_sparring_round_1(task)

        elif state == TaskState.CLAUDE_ROUND_1:
            return await self._run_claude_round_1(task)

        elif state == TaskState.SPARRING_ROUND_2:
            return await self._run_sparring_round_2(task)

        elif state == TaskState.CLAUDE_ROUND_2:
            return await self._run_claude_round_2(task)

        elif state == TaskState.GEMINI_RESEARCH:
            return await self._run_gemini_research(task)

        elif state == TaskState.PACKAGING:
            return await self._run_packaging(task)

        else:
            raise ValueError(f"Unknown state: {state}")

    async def _run_sparring_round_1(self, task: Task) -> Task:
        """Execute Sparring Partner Round 1."""
        self.logger.info("Running Sparring Round 1", task_id=str(task.task_id))

        result = await self.sparring.execute_round_1(
            user_question=task.initial_question,
        )

        self._record_result(task, "sparring_round_1", TaskState.SPARRING_ROUND_1, result)

        if result.success:
            task.transition_to(TaskState.CLAUDE_ROUND_1)
        else:
            task.transition_to(TaskState.ERROR)
            task.error_message = result.error

        return task

    async def _run_claude_round_1(self, task: Task) -> Task:
        """Execute Debate Analyst Round 1."""
        self.logger.info("Running Claude Round 1", task_id=str(task.task_id))

        sparring_output = task.get_sparring_round_1()
        if not sparring_output:
            task.transition_to(TaskState.ERROR)
            task.error_message = "Missing Sparring Round 1 output"
            return task

        result = await self.debate.execute_round_1(
            user_question=task.initial_question,
            sparring_output=sparring_output,
        )

        self._record_result(task, "claude_round_1", TaskState.CLAUDE_ROUND_1, result)

        if result.success:
            task.transition_to(TaskState.SPARRING_ROUND_2)
        else:
            task.transition_to(TaskState.ERROR)
            task.error_message = result.error

        return task

    async def _run_sparring_round_2(self, task: Task) -> Task:
        """Execute Sparring Partner Round 2."""
        self.logger.info("Running Sparring Round 2", task_id=str(task.task_id))

        sparring_r1 = task.get_sparring_round_1()
        claude_r1 = task.get_claude_round_1()

        if not sparring_r1 or not claude_r1:
            task.transition_to(TaskState.ERROR)
            task.error_message = "Missing previous outputs for Round 2"
            return task

        result = await self.sparring.execute_round_2(
            user_question=task.initial_question,
            sparring_round_1=sparring_r1,
            claude_round_1=claude_r1,
        )

        self._record_result(task, "sparring_round_2", TaskState.SPARRING_ROUND_2, result)

        if result.success:
            task.transition_to(TaskState.CLAUDE_ROUND_2)
        else:
            task.transition_to(TaskState.ERROR)
            task.error_message = result.error

        return task

    async def _run_claude_round_2(self, task: Task) -> Task:
        """Execute Debate Analyst Round 2 (Final)."""
        self.logger.info("Running Claude Round 2 (Final)", task_id=str(task.task_id))

        sparring_r1 = task.get_sparring_round_1()
        claude_r1 = task.get_claude_round_1()
        sparring_r2 = task.get_sparring_round_2()

        if not all([sparring_r1, claude_r1, sparring_r2]):
            task.transition_to(TaskState.ERROR)
            task.error_message = "Missing previous outputs for final round"
            return task

        result = await self.debate.execute_round_2(
            user_question=task.initial_question,
            sparring_round_1=sparring_r1,
            claude_round_1=claude_r1,
            sparring_round_2=sparring_r2,
        )

        self._record_result(task, "claude_round_2", TaskState.CLAUDE_ROUND_2, result)

        if result.success:
            task.transition_to(TaskState.GEMINI_RESEARCH)
        else:
            task.transition_to(TaskState.ERROR)
            task.error_message = result.error

        return task

    async def _run_gemini_research(self, task: Task) -> Task:
        """Execute Deep Researcher (Gemini)."""
        self.logger.info("Running Gemini Research", task_id=str(task.task_id))

        claude_final = task.get_claude_final()
        if not claude_final:
            task.transition_to(TaskState.ERROR)
            task.error_message = "Missing Claude final output"
            return task

        result = await self.researcher.execute_from_claude_output(
            claude_final=claude_final,
            meta=task.meta,
        )

        self._record_result(task, "gemini_research", TaskState.GEMINI_RESEARCH, result)

        if result.success:
            task.transition_to(TaskState.PACKAGING)
        else:
            task.transition_to(TaskState.ERROR)
            task.error_message = result.error

        return task

    async def _run_packaging(self, task: Task) -> Task:
        """Execute the appropriate packager based on output format."""
        self.logger.info(
            "Running Packaging",
            task_id=str(task.task_id),
            format=task.meta.output_format.value,
        )

        research_output = task.get_research_output()
        if not research_output:
            task.transition_to(TaskState.ERROR)
            task.error_message = "Missing research output"
            return task

        # For 'report' format, skip packaging
        if task.meta.output_format == OutputFormat.REPORT:
            task.add_history(
                agent="packaging",
                state=TaskState.PACKAGING,
                output_data={"format": "report", "content": research_output},
            )
            task.transition_to(TaskState.COMPLETED)
            return task

        # Run appropriate packager
        if task.meta.output_format == OutputFormat.SLIDES:
            result = await self.slides_packager.execute(research_output)
            agent_name = "slides_packager"
        else:  # APP
            result = await self.app_packager.execute(research_output)
            agent_name = "app_packager"

        self._record_result(task, agent_name, TaskState.PACKAGING, result)

        if result.success:
            task.transition_to(TaskState.COMPLETED)
        else:
            task.transition_to(TaskState.ERROR)
            task.error_message = result.error

        return task

    def _record_result(
        self,
        task: Task,
        agent: str,
        state: TaskState,
        result: AgentResult,
    ) -> None:
        """Record an agent result in the task history."""
        task.add_history(
            agent=agent,
            state=state,
            output_data=result.output,
            tokens_used=result.tokens_used,
            duration_ms=result.duration_ms,
            error=result.error,
        )
