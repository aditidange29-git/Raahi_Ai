"""
API routes — /api/agent
GET  /api/agent/status   — current agent status, active missions, available tools
POST /api/agent/run      — run a free-form agent query (not tied to a mission)
"""
import os
import asyncio
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.models.schemas import AgentStatusResponse, MissionRunRequest
from backend.agent.tools import ALL_TOOLS
from backend.models.database import get_db
from backend.models.mission_states import MissionState

logger = logging.getLogger("raahi.api.agent")
router = APIRouter(prefix="/api/agent", tags=["Agent"])


@router.get("/status", response_model=AgentStatusResponse)
async def agent_status():
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM missions WHERE state NOT IN (?,?,?)",
            (MissionState.COMPLETED.value, MissionState.FAILED.value, MissionState.CANCELLED.value)
        )
        row = await cursor.fetchone()
        active = row["cnt"] if row else 0

        cursor2 = await db.execute(
            "SELECT COUNT(*) as cnt FROM missions WHERE state = ?",
            (MissionState.WAITING_FOR_APPROVAL.value,)
        )
        row2 = await cursor2.fetchone()
        waiting = row2["cnt"] if row2 else 0

    if waiting > 0:
        status = "waiting_approval"
    elif active > 0:
        status = "running"
    else:
        status = "idle"

    return AgentStatusResponse(
        status=status,
        active_missions=active,
        tools_available=[t.name if hasattr(t, "name") else str(t) for t in ALL_TOOLS],
        model_provider=os.getenv("RAAHI_MODEL_PROVIDER", "bedrock"),
        version="1.0.0",
    )


@router.post("/run")
async def run_agent_query(body: MissionRunRequest):
    """
    Free-form agent invocation — useful for testing and the demo.
    Streams the agent's response as server-sent events.
    """
    from backend.agent.raahi_agent import create_agent

    message = body.message or "What opportunities are available for me right now?"

    chunks: list[str] = []

    def callback(**kwargs):
        if "data" in kwargs:
            chunks.append(kwargs["data"])

    async def generate():
        agent = create_agent(callback_handler=callback)
        loop = asyncio.get_event_loop()

        def _invoke():
            return agent(message)

        try:
            await loop.run_in_executor(None, _invoke)
            full = "".join(chunks)
            yield f"data: {full}\n\n"
        except Exception as exc:
            logger.exception("Agent run failed: %s", exc)
            yield f"data: ERROR: {str(exc)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
