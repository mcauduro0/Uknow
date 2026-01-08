"""
Task management API endpoints.
"""

import asyncio
from typing import Any
from uuid import UUID

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

from uknow.models.task import (
    DetailLevel,
    OutputFormat,
    Task,
    TaskCreate,
    TaskMeta,
    TaskState,
)
from uknow.orchestrator.runner import TaskRunner

router = APIRouter()
logger = structlog.get_logger()

# In-memory task storage (replace with database in production)
_tasks: dict[UUID, Task] = {}


class CreateTaskRequest(BaseModel):
    """Request body for creating a new task."""

    question: str = Field(..., description="The research question or request")
    channel: str = Field(default="web", description="Source channel")
    user_id: str = Field(default="anonymous", description="User identifier")
    output_format: OutputFormat = Field(
        default=OutputFormat.REPORT,
        description="Desired output format",
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.DEEP,
        description="Level of detail",
    )
    language: str = Field(default="en-US", description="Output language")
    quick_mode: bool = Field(
        default=False,
        description="Use quick mode (skip second debate round)",
    )


class TaskResponse(BaseModel):
    """Response containing task information."""

    task_id: UUID
    state: TaskState
    channel: str
    initial_question: str
    error_message: str | None = None
    total_tokens_used: int = 0
    total_duration_ms: int = 0
    created_at: str
    completed_at: str | None = None


class TaskDetailResponse(TaskResponse):
    """Detailed task response including outputs."""

    history: list[dict[str, Any]] = []
    final_output: dict[str, Any] | None = None


def _task_to_response(task: Task) -> TaskResponse:
    """Convert Task to TaskResponse."""
    return TaskResponse(
        task_id=task.task_id,
        state=task.state,
        channel=task.channel,
        initial_question=task.initial_question,
        error_message=task.error_message,
        total_tokens_used=task.total_tokens_used,
        total_duration_ms=task.total_duration_ms,
        created_at=task.created_at.isoformat(),
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


def _task_to_detail_response(task: Task) -> TaskDetailResponse:
    """Convert Task to TaskDetailResponse."""
    # Get final output based on state and format
    final_output = None
    if task.state == TaskState.COMPLETED:
        # Look for packaging or research output
        for entry in reversed(task.history):
            if entry.output_data:
                final_output = entry.output_data
                break

    return TaskDetailResponse(
        task_id=task.task_id,
        state=task.state,
        channel=task.channel,
        initial_question=task.initial_question,
        error_message=task.error_message,
        total_tokens_used=task.total_tokens_used,
        total_duration_ms=task.total_duration_ms,
        created_at=task.created_at.isoformat(),
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
        history=[entry.model_dump() for entry in task.history],
        final_output=final_output,
    )


async def _process_task(task_id: UUID, quick_mode: bool = False) -> None:
    """Background task processor."""
    task = _tasks.get(task_id)
    if not task:
        logger.error("Task not found for processing", task_id=str(task_id))
        return

    try:
        runner = TaskRunner(quick_mode=quick_mode)
        processed_task = await runner.run(task)
        _tasks[task_id] = processed_task
    except Exception as e:
        logger.error("Task processing failed", task_id=str(task_id), error=str(e))
        task.transition_to(TaskState.ERROR)
        task.error_message = str(e)
        _tasks[task_id] = task


@router.post("/tasks", response_model=TaskResponse, status_code=202)
async def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
) -> TaskResponse:
    """
    Create a new research task.

    The task will be processed asynchronously in the background.
    Use the GET endpoint to check status and retrieve results.
    """
    # Create task
    task_create = TaskCreate(
        channel=request.channel,
        user_id=request.user_id,
        initial_question=request.question,
        meta=TaskMeta(
            output_format=request.output_format,
            language=request.language,
            detail_level=request.detail_level,
        ),
    )

    runner = TaskRunner()
    task = runner.create_task(task_create)

    # Store task
    _tasks[task.task_id] = task

    logger.info(
        "Task created",
        task_id=str(task.task_id),
        channel=task.channel,
        quick_mode=request.quick_mode,
    )

    # Start background processing
    background_tasks.add_task(_process_task, task.task_id, request.quick_mode)

    return _task_to_response(task)


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(task_id: UUID) -> TaskDetailResponse:
    """
    Get task details and current status.

    Returns full task information including processing history
    and final output when completed.
    """
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return _task_to_detail_response(task)


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    channel: str | None = Query(None, description="Filter by channel"),
    state: TaskState | None = Query(None, description="Filter by state"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> list[TaskResponse]:
    """
    List tasks with optional filtering.

    Supports filtering by channel and state, with pagination.
    """
    tasks = list(_tasks.values())

    # Apply filters
    if channel:
        tasks = [t for t in tasks if t.channel == channel]
    if state:
        tasks = [t for t in tasks if t.state == state]

    # Sort by creation time (newest first)
    tasks.sort(key=lambda t: t.created_at, reverse=True)

    # Apply pagination
    tasks = tasks[offset : offset + limit]

    return [_task_to_response(t) for t in tasks]


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: UUID) -> dict:
    """
    Cancel a running task.

    Note: This may not immediately stop processing if an agent
    call is in progress.
    """
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.state.is_terminal:
        raise HTTPException(
            status_code=400,
            detail=f"Task is already in terminal state: {task.state.value}",
        )

    task.transition_to(TaskState.ERROR)
    task.error_message = "Cancelled by user"
    _tasks[task_id] = task

    return {"status": "cancelled", "task_id": str(task_id)}


@router.post("/tasks/sync", response_model=TaskDetailResponse)
async def create_task_sync(request: CreateTaskRequest) -> TaskDetailResponse:
    """
    Create and process a task synchronously.

    WARNING: This endpoint will block until the task is complete,
    which may take several minutes. Use for testing or when
    async processing is not suitable.
    """
    # Create task
    task_create = TaskCreate(
        channel=request.channel,
        user_id=request.user_id,
        initial_question=request.question,
        meta=TaskMeta(
            output_format=request.output_format,
            language=request.language,
            detail_level=request.detail_level,
        ),
    )

    runner = TaskRunner(quick_mode=request.quick_mode)
    task = runner.create_task(task_create)

    logger.info(
        "Starting synchronous task processing",
        task_id=str(task.task_id),
        quick_mode=request.quick_mode,
    )

    # Process synchronously
    processed_task = await runner.run(task)

    # Store result
    _tasks[processed_task.task_id] = processed_task

    return _task_to_detail_response(processed_task)
