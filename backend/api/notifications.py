"""
API routes — /api/notifications
GET  /api/notifications
POST /api/notifications/{id}/read
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.models.database import get_db
from backend.models.schemas import NotificationBase, NotificationsResponse

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])
DEMO_USER_ID = "user_demo"


@router.get("", response_model=NotificationsResponse)
async def list_notifications():
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
            (DEMO_USER_ID,)
        )
        rows = await cursor.fetchall()

    notifs = [
        NotificationBase(
            id=r["id"],
            mission_id=r.get("mission_id"),
            title=r["title"],
            body=r["body"],
            type=r["type"],
            read=bool(r["read"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]
    unread = sum(1 for n in notifs if not n.read)
    return NotificationsResponse(count=len(notifs), unread_count=unread, notifications=notifs)


@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT id FROM notifications WHERE id = ? AND user_id = ?",
            (notification_id, DEMO_USER_ID)
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Notification not found.")
        await db.execute(
            "UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,)
        )
        await db.commit()
    return {"id": notification_id, "read": True}
