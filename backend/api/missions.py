"""
API routes — /api/missions
POST /api/missions            — create mission + kick off agent
GET  /api/missions            — list all missions
GET  /api/missions/{id}       — get mission detail
POST /api/missions/{id}/approve — approve or deny pending approval
POST /api/missions/{id}/cancel  — cancel a mission
GET  /api/missions/{id}/events  — get agent event log
"""
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from backend.models.database import get_db
from backend.models.schemas import (
    MissionCreate, MissionResponse, MissionsResponse, MissionStep,
    ApprovalAction, ApprovalResponse,
    AgentEvent, AgentEventsResponse,
)
from backend.models.mission_states import (
    MissionState, can_transition, progress_percentage, HAPPY_PATH_SEQUENCE
)
from backend.agent.tools.human_approval import get_approval_store

logger = logging.getLogger("raahi.api.missions")
router = APIRouter(prefix="/api/missions", tags=["Missions"])

DEMO_USER_ID = "user_demo"

# Default mission steps, matched to the happy path
MISSION_STEP_DEFS = [
    ("step_discover",  "DISCOVERING",         "Discover Opportunity"),
    ("step_qualify",   "CHECKING_ELIGIBILITY","Check Eligibility"),
    ("step_docs",      "COLLECTING_DOCUMENTS","Verify Documents"),
    ("step_prepare",   "PREPARING",           "Prepare Application"),
    ("step_approve",   "WAITING_FOR_APPROVAL","Human Approval"),
    ("step_submit",    "EXECUTING",           "Submit Application"),
    ("step_verify",    "VERIFYING",           "Verify Submission"),
    ("step_monitor",   "MONITORING",          "Monitor Status"),
]


async def _create_mission_steps(db, mission_id: str) -> None:
    now = datetime.utcnow().isoformat() + "Z"
    for idx, (step_name, state_name, label) in enumerate(MISSION_STEP_DEFS):
        step_id = f"{mission_id}_{step_name}"
        await db.execute(
            """
            INSERT INTO mission_steps (id, mission_id, step_order, name, label, state)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (step_id, mission_id, idx, step_name, label, "pending")
        )


async def _row_to_mission_response(db, row: dict) -> MissionResponse:
    cursor = await db.execute(
        "SELECT * FROM mission_steps WHERE mission_id = ? ORDER BY step_order",
        (row["id"],)
    )
    step_rows = await cursor.fetchall()
    steps = [
        MissionStep(
            id=s["id"],
            step_order=s["step_order"],
            name=s["name"],
            label=s["label"],
            state=s["state"],
            started_at=s.get("started_at"),
            completed_at=s.get("completed_at"),
            result=json.loads(s.get("result") or "{}"),
        )
        for s in step_rows
    ]
    return MissionResponse(
        id=row["id"],
        user_id=row["user_id"],
        opportunity_id=row["opportunity_id"],
        title=row["title"],
        goal=row["goal"],
        state=row["state"],
        progress=row["progress"],
        eligibility_score=row["eligibility_score"] or 0.0,
        confirmation_number=row.get("confirmation_number"),
        submission_id=row.get("submission_id"),
        steps=steps,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def _run_agent_mission(mission_id: str, opportunity_id: str, goal: str):
    """
    Background task: runs the Strands agent for a mission.
    Updates mission state and writes AgentEvents to the DB as the agent progresses.
    """
    from backend.agent.raahi_agent import get_agent
    from backend.models.database import get_db as _get_db

    async def _emit_event(db, event_type: str, message: str, metadata: dict = {}):
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat() + "Z"
        await db.execute(
            "INSERT INTO agent_events (id, mission_id, event_type, message, metadata, created_at) VALUES (?,?,?,?,?,?)",
            (event_id, mission_id, event_type, message, json.dumps(metadata), now)
        )
        await db.commit()

    async def _update_state(db, new_state: MissionState):
        now = datetime.utcnow().isoformat() + "Z"
        pct = progress_percentage(new_state)
        await db.execute(
            "UPDATE missions SET state=?, progress=?, updated_at=? WHERE id=?",
            (new_state.value, pct, now, mission_id)
        )
        await db.commit()

    # Build agent prompt
    prompt = (
        f"Start a new mission for opportunity_id='{opportunity_id}'.\n"
        f"Goal: {goal}\n"
        f"Mission ID: {mission_id}\n"
        "Run the full workflow: DISCOVER → QUALIFY → COLLECT DOCUMENTS → PREPARE → APPROVE → SUBMIT → VERIFY → MONITOR.\n"
        "Use your tools at each step. After human_approval returns 'pending', stop and wait — "
        "the API will update the approval status and restart the mission."
    )

    # Collected text output
    output_chunks: list[str] = []

    def sync_callback(**kwargs):
        if "data" in kwargs:
            output_chunks.append(kwargs["data"])

    try:
        async with await _get_db() as db:
            await _update_state(db, MissionState.DISCOVERING)
            await _emit_event(db, "mission_started", f"Agent started mission for opportunity {opportunity_id}")

        # Run Strands agent (blocking in executor to avoid blocking event loop)
        agent = get_agent()
        loop = asyncio.get_event_loop()

        def _invoke():
            agent_with_cb = type(agent)(
                model=agent.model,
                system_prompt=agent.system_prompt,
                tools=agent.tools,
                callback_handler=sync_callback,
            )
            return agent_with_cb(prompt)

        result = await loop.run_in_executor(None, _invoke)
        full_output = "".join(output_chunks)

        async with await _get_db() as db:
            # Check if paused for approval
            approval_store = get_approval_store()
            approval = approval_store.get(mission_id)
            if approval and approval.get("status") == "pending":
                await _update_state(db, MissionState.WAITING_FOR_APPROVAL)
                await _emit_event(db, "waiting_approval", "Agent paused — waiting for human approval.", approval)
                # Persist approval request to DB
                await db.execute(
                    """
                    INSERT OR REPLACE INTO approval_requests
                    (id, mission_id, action_type, summary, details, status, created_at, expires_at)
                    VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (
                        approval["approval_id"], mission_id,
                        approval["action_type"], approval["summary"],
                        approval.get("details", ""), "pending",
                        approval["created_at"], approval["expires_at"],
                    )
                )
            else:
                await _update_state(db, MissionState.MONITORING)
                await _emit_event(db, "mission_completed", "Agent completed mission workflow.", {"output": full_output[:500]})

            await db.commit()

    except Exception as exc:
        logger.exception("Agent mission failed: %s", exc)
        async with await _get_db() as db:
            await _update_state(db, MissionState.FAILED)
            await _emit_event(db, "mission_failed", f"Error: {str(exc)[:300]}")


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("", response_model=MissionResponse, status_code=201)
async def create_mission(body: MissionCreate, background_tasks: BackgroundTasks):
    now = datetime.utcnow().isoformat() + "Z"
    mission_id = f"msn_{uuid.uuid4().hex[:10]}"

    async with await get_db() as db:
        # Verify opportunity exists
        cursor = await db.execute("SELECT * FROM opportunities WHERE id = ?", (body.opportunity_id,))
        opp = await cursor.fetchone()
        if not opp:
            raise HTTPException(status_code=404, detail=f"Opportunity '{body.opportunity_id}' not found.")

        await db.execute(
            """
            INSERT INTO missions (id, user_id, opportunity_id, title, goal, state, progress, eligibility_score, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mission_id, DEMO_USER_ID, body.opportunity_id,
                f"Apply for {opp['title']}", body.goal,
                MissionState.DISCOVERING.value, 0, 0.0, now, now
            )
        )
        await _create_mission_steps(db, mission_id)
        await db.commit()

        cursor = await db.execute("SELECT * FROM missions WHERE id = ?", (mission_id,))
        row = await cursor.fetchone()
        mission = await _row_to_mission_response(db, dict(row))

    # Start agent in background
    background_tasks.add_task(_run_agent_mission, mission_id, body.opportunity_id, body.goal)
    return mission


@router.get("", response_model=MissionsResponse)
async def list_missions():
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM missions WHERE user_id = ? ORDER BY created_at DESC",
            (DEMO_USER_ID,)
        )
        rows = await cursor.fetchall()
        missions = [await _row_to_mission_response(db, dict(r)) for r in rows]
    return MissionsResponse(count=len(missions), missions=missions)


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: str):
    async with await get_db() as db:
        cursor = await db.execute("SELECT * FROM missions WHERE id = ?", (mission_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Mission '{mission_id}' not found.")
        return await _row_to_mission_response(db, dict(row))


@router.post("/{mission_id}/approve", response_model=ApprovalResponse)
async def approve_mission(mission_id: str, body: ApprovalAction, background_tasks: BackgroundTasks):
    now = datetime.utcnow().isoformat() + "Z"

    async with await get_db() as db:
        cursor = await db.execute("SELECT * FROM missions WHERE id = ?", (mission_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Mission '{mission_id}' not found.")

        if row["state"] != MissionState.WAITING_FOR_APPROVAL.value:
            raise HTTPException(
                status_code=400,
                detail=f"Mission is in state '{row['state']}', not WAITING_FOR_APPROVAL."
            )

        # Update approval record in DB
        new_status = "approved" if body.action == "approve" else "denied"
        await db.execute(
            "UPDATE approval_requests SET status=?, resolved_at=?, resolved_by=? WHERE mission_id=? AND status='pending'",
            (new_status, now, "user_demo", mission_id)
        )

        # Get approval_id for response
        cursor2 = await db.execute(
            "SELECT id FROM approval_requests WHERE mission_id=? ORDER BY created_at DESC LIMIT 1",
            (mission_id,)
        )
        apr_row = await cursor2.fetchone()
        approval_id = apr_row["id"] if apr_row else f"apr_{mission_id}"

        if body.action == "approve":
            await db.execute(
                "UPDATE missions SET state=?, progress=?, updated_at=? WHERE id=?",
                (MissionState.EXECUTING.value, progress_percentage(MissionState.EXECUTING), now, mission_id)
            )
            await db.execute(
                "INSERT INTO agent_events (id, mission_id, event_type, message, metadata, created_at) VALUES (?,?,?,?,?,?)",
                (f"evt_{uuid.uuid4().hex[:8]}", mission_id, "approved", "Human approved — resuming execution.", "{}", now)
            )
        else:
            await db.execute(
                "UPDATE missions SET state=?, updated_at=? WHERE id=?",
                (MissionState.CANCELLED.value, now, mission_id)
            )
            await db.execute(
                "INSERT INTO agent_events (id, mission_id, event_type, message, metadata, created_at) VALUES (?,?,?,?,?,?)",
                (f"evt_{uuid.uuid4().hex[:8]}", mission_id, "denied", "Human denied approval — mission cancelled.", "{}", now)
            )

        await db.commit()

    # Update in-memory approval store too
    approval_store = get_approval_store()
    if mission_id in approval_store:
        approval_store[mission_id]["status"] = new_status

    # If approved, resume agent in background
    if body.action == "approve":
        opp_id = row["opportunity_id"]
        resume_prompt = (
            f"Approval granted for mission_id='{mission_id}'. "
            f"opportunity_id='{opp_id}'. "
            "Now call application_submit, then application_verify, then application_monitor. "
            "Complete the workflow."
        )
        background_tasks.add_task(_run_agent_mission, mission_id, opp_id, resume_prompt)

    message = (
        "Mission approved — agent is now submitting the application."
        if body.action == "approve"
        else "Mission cancelled by user."
    )

    return ApprovalResponse(
        approval_id=approval_id,
        mission_id=mission_id,
        status=new_status,
        resolved_at=now,
        message=message,
    )


@router.post("/{mission_id}/cancel")
async def cancel_mission(mission_id: str):
    now = datetime.utcnow().isoformat() + "Z"
    async with await get_db() as db:
        cursor = await db.execute("SELECT * FROM missions WHERE id = ?", (mission_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Mission '{mission_id}' not found.")
        if row["state"] in (MissionState.COMPLETED.value, MissionState.CANCELLED.value):
            raise HTTPException(status_code=400, detail=f"Mission already in terminal state: {row['state']}")
        await db.execute(
            "UPDATE missions SET state=?, updated_at=? WHERE id=?",
            (MissionState.CANCELLED.value, now, mission_id)
        )
        await db.execute(
            "INSERT INTO agent_events (id, mission_id, event_type, message, metadata, created_at) VALUES (?,?,?,?,?,?)",
            (f"evt_{uuid.uuid4().hex[:8]}", mission_id, "cancelled", "Mission cancelled by user.", "{}", now)
        )
        await db.commit()
    return {"mission_id": mission_id, "status": "CANCELLED", "cancelled_at": now}


@router.get("/{mission_id}/events", response_model=AgentEventsResponse)
async def get_mission_events(mission_id: str):
    async with await get_db() as db:
        cursor = await db.execute("SELECT * FROM missions WHERE id = ?", (mission_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Mission '{mission_id}' not found.")
        cursor = await db.execute(
            "SELECT * FROM agent_events WHERE mission_id = ? ORDER BY created_at ASC",
            (mission_id,)
        )
        rows = await cursor.fetchall()

    events = [
        AgentEvent(
            id=r["id"],
            mission_id=r["mission_id"],
            event_type=r["event_type"],
            message=r["message"],
            metadata=json.loads(r.get("metadata") or "{}"),
            created_at=r["created_at"],
        )
        for r in rows
    ]
    return AgentEventsResponse(mission_id=mission_id, count=len(events), events=events)
