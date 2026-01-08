"""
Webhook handlers for external channels.

Currently supports:
- WhatsApp Business API webhooks
"""

import hashlib
import hmac
from typing import Any

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from pydantic import BaseModel

from uknow.config import get_settings
from uknow.models.task import DetailLevel, OutputFormat, Task, TaskCreate, TaskMeta
from uknow.orchestrator.runner import TaskRunner

router = APIRouter()
logger = structlog.get_logger()

# In-memory storage for webhook tasks (shared with tasks module in production)
_webhook_tasks: dict[str, Task] = {}


# =============================================================================
# WhatsApp Business API
# =============================================================================


class WhatsAppMessage(BaseModel):
    """Simplified WhatsApp incoming message structure."""

    from_number: str
    message_id: str
    text: str
    timestamp: str


def _extract_whatsapp_message(payload: dict[str, Any]) -> WhatsAppMessage | None:
    """
    Extract message from WhatsApp webhook payload.

    The WhatsApp Business API webhook payload is deeply nested.
    This extracts the relevant message information.
    """
    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return None

        msg = messages[0]
        if msg.get("type") != "text":
            return None

        return WhatsAppMessage(
            from_number=msg.get("from", ""),
            message_id=msg.get("id", ""),
            text=msg.get("text", {}).get("body", ""),
            timestamp=msg.get("timestamp", ""),
        )
    except (KeyError, IndexError) as e:
        logger.warning("Failed to extract WhatsApp message", error=str(e))
        return None


def _verify_whatsapp_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify WhatsApp webhook signature."""
    if not signature.startswith("sha256="):
        return False

    expected_sig = signature[7:]  # Remove "sha256=" prefix
    computed_sig = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_sig, computed_sig)


async def _send_whatsapp_message(to: str, message: str) -> None:
    """
    Send a message via WhatsApp Business API.

    This is a placeholder - implement with actual API call.
    """
    settings = get_settings()
    logger.info(
        "Would send WhatsApp message",
        to=to,
        message_preview=message[:100] if message else "",
    )
    # TODO: Implement actual WhatsApp API call
    # import httpx
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}/messages",
    #         headers={"Authorization": f"Bearer {settings.whatsapp_access_token.get_secret_value()}"},
    #         json={
    #             "messaging_product": "whatsapp",
    #             "to": to,
    #             "type": "text",
    #             "text": {"body": message}
    #         }
    #     )


async def _process_whatsapp_task(
    from_number: str,
    question: str,
) -> None:
    """Process a WhatsApp task and send response."""
    try:
        # Create and run task
        task_create = TaskCreate(
            channel="whatsapp",
            user_id=f"whatsapp:{from_number}",
            initial_question=question,
            meta=TaskMeta(
                output_format=OutputFormat.REPORT,
                language="en-US",  # Could be detected from message
                detail_level=DetailLevel.EXECUTIVE,  # Shorter for chat
            ),
        )

        runner = TaskRunner(quick_mode=True)  # Use quick mode for faster responses
        task = runner.create_task(task_create)

        # Store task
        _webhook_tasks[f"whatsapp:{from_number}:{task.task_id}"] = task

        # Process
        processed_task = await runner.run(task)

        # Extract result and send response
        if processed_task.state.is_terminal:
            research = processed_task.get_research_output()
            if research:
                # Send executive summary via WhatsApp
                summary = research.get("executive_summary", "Research complete.")
                await _send_whatsapp_message(from_number, summary)

                # Optionally send recommendations
                recommendations = research.get("prioritized_recommendations", [])
                if recommendations:
                    rec_text = "\n\n*Key Recommendations:*\n"
                    for rec in recommendations[:3]:  # Top 3
                        rec_text += f"• {rec.get('description', '')}\n"
                    await _send_whatsapp_message(from_number, rec_text)
            else:
                await _send_whatsapp_message(
                    from_number,
                    "Sorry, I couldn't complete the research. Please try again.",
                )

    except Exception as e:
        logger.error("WhatsApp task processing failed", error=str(e))
        await _send_whatsapp_message(
            from_number,
            "Sorry, an error occurred. Please try again later.",
        )


@router.get("/whatsapp")
async def whatsapp_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> str:
    """
    WhatsApp webhook verification endpoint.

    Called by Meta when setting up the webhook to verify ownership.
    """
    settings = get_settings()

    if hub_mode == "subscribe" and hub_token == settings.whatsapp_verify_token:
        logger.info("WhatsApp webhook verified")
        return hub_challenge or ""

    logger.warning("WhatsApp webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    WhatsApp incoming message webhook.

    Receives messages from WhatsApp Business API and processes them
    asynchronously.
    """
    settings = get_settings()

    # Verify signature if secret is configured
    if settings.whatsapp_webhook_secret.get_secret_value():
        signature = request.headers.get("X-Hub-Signature-256", "")
        body = await request.body()

        if not _verify_whatsapp_signature(
            body,
            signature,
            settings.whatsapp_webhook_secret.get_secret_value(),
        ):
            logger.warning("Invalid WhatsApp webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse payload
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Extract message
    message = _extract_whatsapp_message(payload)

    if message and message.text:
        logger.info(
            "Received WhatsApp message",
            from_number=message.from_number,
            message_id=message.message_id,
        )

        # Process in background
        background_tasks.add_task(
            _process_whatsapp_task,
            message.from_number,
            message.text,
        )

    return {"status": "ok"}


# =============================================================================
# Generic Webhook (for custom integrations)
# =============================================================================


class GenericWebhookRequest(BaseModel):
    """Generic webhook request for custom integrations."""

    channel: str
    user_id: str
    question: str
    callback_url: str | None = None
    output_format: OutputFormat = OutputFormat.REPORT
    detail_level: DetailLevel = DetailLevel.DEEP
    language: str = "en-US"
    quick_mode: bool = False


async def _process_generic_webhook(
    request: GenericWebhookRequest,
) -> None:
    """Process generic webhook and optionally call back."""
    try:
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
        processed_task = await runner.run(task)

        # Send callback if URL provided
        if request.callback_url:
            import httpx

            async with httpx.AsyncClient() as client:
                await client.post(
                    request.callback_url,
                    json={
                        "task_id": str(processed_task.task_id),
                        "state": processed_task.state.value,
                        "output": processed_task.get_research_output(),
                    },
                    timeout=30.0,
                )

    except Exception as e:
        logger.error("Generic webhook processing failed", error=str(e))


@router.post("/generic")
async def generic_webhook(
    request: GenericWebhookRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Generic webhook for custom channel integrations.

    Accepts a question and processes it asynchronously.
    If callback_url is provided, results will be POSTed there.
    """
    logger.info(
        "Received generic webhook",
        channel=request.channel,
        user_id=request.user_id,
    )

    background_tasks.add_task(_process_generic_webhook, request)

    return {"status": "accepted", "channel": request.channel}
