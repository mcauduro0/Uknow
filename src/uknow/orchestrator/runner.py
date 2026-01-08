"""
Task Runner for processing tasks asynchronously.

Provides utilities for running tasks with quick mode support
and progress callbacks.
"""

import asyncio
from typing import Any, Callable

import structlog

from uknow.config import get_settings
from uknow.models.task import Task, TaskCreate, TaskState
from uknow.orchestrator.core import Orchestrator

logger = structlog.get_logger()


# Type for progress callbacks
ProgressCallback = Callable[[Task, str], None]


class TaskRunner:
    """
    High-level task runner with configuration options.

    Features:
    - Quick mode: Skip debate rounds for faster results
    - Progress callbacks: Get notified as task progresses
    - Concurrent task processing
    """

    def __init__(
        self,
        quick_mode: bool | None = None,
        on_progress: ProgressCallback | None = None,
    ):
        """
        Initialize the task runner.

        Args:
            quick_mode: Skip debate rounds (uses setting if None)
            on_progress: Callback for progress updates
        """
        self.settings = get_settings()
        self.quick_mode = (
            quick_mode if quick_mode is not None else self.settings.enable_quick_mode
        )
        self.on_progress = on_progress
        self.orchestrator = Orchestrator()
        self.logger = logger.bind(component="task_runner")

    def create_task(self, task_create: TaskCreate) -> Task:
        """
        Create a new task from input data.

        Args:
            task_create: The task creation schema

        Returns:
            A new Task instance
        """
        return Task(
            channel=task_create.channel,
            user_id=task_create.user_id,
            initial_question=task_create.initial_question,
            meta=task_create.meta,
        )

    async def run(self, task: Task) -> Task:
        """
        Run a task through the pipeline.

        Args:
            task: The task to process

        Returns:
            The completed task
        """
        self.logger.info(
            "Starting task run",
            task_id=str(task.task_id),
            quick_mode=self.quick_mode,
        )

        if self.quick_mode:
            return await self._run_quick_mode(task)
        else:
            return await self._run_full_mode(task)

    async def _run_full_mode(self, task: Task) -> Task:
        """Run the full multi-agent pipeline."""
        previous_state = None

        while not task.state.is_terminal:
            # Notify progress if callback registered
            if self.on_progress and task.state != previous_state:
                self._notify_progress(task, f"Entering {task.state.value}")
                previous_state = task.state

            # Execute one step
            task = await self.orchestrator._execute_step(task)

        return task

    async def _run_quick_mode(self, task: Task) -> Task:
        """
        Run a simplified pipeline (skip second debate round).

        Quick mode flow:
        1. Sparring Round 1
        2. Claude Round 1
        3. Gemini Research (using Claude Round 1 output)
        4. Packaging
        """
        self.logger.info("Running in quick mode", task_id=str(task.task_id))

        # Sparring Round 1
        task.transition_to(TaskState.SPARRING_ROUND_1)
        self._notify_progress(task, "Starting analysis")
        task = await self.orchestrator._run_sparring_round_1(task)

        if task.state == TaskState.ERROR:
            return task

        # Claude Round 1
        self._notify_progress(task, "Expanding perspectives")
        task = await self.orchestrator._run_claude_round_1(task)

        if task.state == TaskState.ERROR:
            return task

        # Skip Round 2, go directly to research
        # Construct a simplified final brief from Claude Round 1
        claude_r1 = task.get_claude_round_1()
        if claude_r1:
            # Create a mock Claude Round 2 output from Round 1
            mock_final = {
                "final_brief": claude_r1.get("refined_brief", ""),
                "final_research_structure": claude_r1.get(
                    "suggested_research_structure", []
                ),
                "success_criteria": ["Comprehensive coverage", "Actionable insights"],
                "key_risks_not_to_ignore": [],
            }

            task.add_history(
                agent="claude_round_2",
                state=TaskState.CLAUDE_ROUND_2,
                output_data=mock_final,
            )
            task.transition_to(TaskState.GEMINI_RESEARCH)

        # Gemini Research
        self._notify_progress(task, "Conducting deep research")
        task = await self.orchestrator._run_gemini_research(task)

        if task.state == TaskState.ERROR:
            return task

        # Packaging
        self._notify_progress(task, "Packaging results")
        task = await self.orchestrator._run_packaging(task)

        return task

    def _notify_progress(self, task: Task, message: str) -> None:
        """Send progress notification if callback is registered."""
        if self.on_progress:
            try:
                self.on_progress(task, message)
            except Exception as e:
                self.logger.warning("Progress callback failed", error=str(e))


class BatchRunner:
    """
    Run multiple tasks concurrently.
    """

    def __init__(self, max_concurrent: int = 5):
        """
        Initialize batch runner.

        Args:
            max_concurrent: Maximum concurrent tasks
        """
        self.max_concurrent = max_concurrent
        self.logger = logger.bind(component="batch_runner")

    async def run_batch(
        self,
        tasks: list[Task],
        quick_mode: bool = False,
    ) -> list[Task]:
        """
        Process multiple tasks concurrently.

        Args:
            tasks: List of tasks to process
            quick_mode: Use quick mode for all tasks

        Returns:
            List of processed tasks (same order as input)
        """
        self.logger.info(
            "Starting batch run",
            task_count=len(tasks),
            max_concurrent=self.max_concurrent,
        )

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def run_with_semaphore(task: Task) -> Task:
            async with semaphore:
                runner = TaskRunner(quick_mode=quick_mode)
                return await runner.run(task)

        results = await asyncio.gather(
            *[run_with_semaphore(task) for task in tasks],
            return_exceptions=True,
        )

        # Handle exceptions in results
        processed_tasks = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(
                    "Task failed in batch",
                    task_index=i,
                    error=str(result),
                )
                tasks[i].transition_to(TaskState.ERROR)
                tasks[i].error_message = str(result)
                processed_tasks.append(tasks[i])
            else:
                processed_tasks.append(result)

        return processed_tasks
