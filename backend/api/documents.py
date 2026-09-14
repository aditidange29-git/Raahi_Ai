"""
API routes — /api/documents
GET  /api/documents
POST /api/documents
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.models.database import get_db
from backend.models.schemas import DocumentBase, DocumentCreate, DocumentsResponse

router = APIRouter(prefix="/api/documents", tags=["Documents"])
DEMO_USER_ID = "user_demo"


@router.get("", response_model=DocumentsResponse)
async def list_documents():
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY name", (DEMO_USER_ID,)
        )
        rows = await cursor.fetchall()
    docs = [
        DocumentBase(
            id=r["id"],
            name=r["name"],
            status=r["status"],
            last_updated=r["last_updated"],
        )
        for r in rows
    ]
    return DocumentsResponse(count=len(docs), documents=docs)


@router.post("", response_model=DocumentBase, status_code=201)
async def add_document(body: DocumentCreate):
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    today = datetime.utcnow().strftime("%Y-%m-%d")
    async with get_db() as db:
        # Prevent duplicates by name
        cursor = await db.execute(
            "SELECT id FROM documents WHERE user_id = ? AND name = ?",
            (DEMO_USER_ID, body.name)
        )
        existing = await cursor.fetchone()
        if existing:
            raise HTTPException(status_code=409, detail=f"Document '{body.name}' already exists.")

        await db.execute(
            "INSERT INTO documents (id, user_id, name, file_path, status, last_updated) VALUES (?,?,?,?,?,?)",
            (doc_id, DEMO_USER_ID, body.name, body.file_path, body.status, today)
        )
        await db.commit()
    return DocumentBase(id=doc_id, name=body.name, status=body.status, last_updated=today)
