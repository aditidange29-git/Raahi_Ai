"""
API routes — /api/applications
GET /api/applications
GET /api/applications/{id}
"""
import json
from fastapi import APIRouter, HTTPException
from backend.models.database import get_db
from backend.models.schemas import ApplicationBase, ApplicationDetail, ApplicationsResponse

router = APIRouter(prefix="/api/applications", tags=["Applications"])
DEMO_USER_ID = "user_demo"


@router.get("", response_model=ApplicationsResponse)
async def list_applications():
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC",
            (DEMO_USER_ID,)
        )
        rows = await cursor.fetchall()
    apps = []
    for _r in rows:
        r = dict(_r)
        apps.append(ApplicationBase(
            id=r["id"],
            mission_id=r["mission_id"],
            opportunity_id=r["opportunity_id"],
            status=r["status"],
            submitted_at=r.get("submitted_at"),
            confirmation_number=r.get("confirmation_number"),
            created_at=r["created_at"],
        ))
    return ApplicationsResponse(count=len(apps), applications=apps)


@router.get("/{application_id}", response_model=ApplicationDetail)
async def get_application(application_id: str):
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM applications WHERE id = ?", (application_id,)
        )
        row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Application '{application_id}' not found.")
    r = dict(row)
    return ApplicationDetail(
        id=r["id"],
        mission_id=r["mission_id"],
        opportunity_id=r["opportunity_id"],
        status=r["status"],
        draft_data=json.loads(r.get("draft_data") or "{}"),
        submitted_at=r.get("submitted_at"),
        confirmation_number=r.get("confirmation_number"),
        verified_at=r.get("verified_at"),
        created_at=r["created_at"],
    )
