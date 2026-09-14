"""
Database layer — SQLite via aiosqlite for async FastAPI.
Schema matches the models defined in the PDF spec:
User, Opportunity, Mission, MissionStep, Document, Application,
ApprovalRequest, AgentEvent, Notification, Permission, ApplicationStatus.
"""
import os
import json
import aiosqlite
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH", "raahi.db"))

CREATE_TABLES_SQL = [
    # ── Users ─────────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS users (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        email       TEXT UNIQUE NOT NULL,
        role        TEXT NOT NULL DEFAULT 'applicant',
        profile     TEXT NOT NULL DEFAULT '{}',
        created_at  TEXT NOT NULL
    )
    """,

    # ── Opportunities ─────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS opportunities (
        id                  TEXT PRIMARY KEY,
        title               TEXT NOT NULL,
        category            TEXT NOT NULL,
        description         TEXT NOT NULL,
        deadline            TEXT NOT NULL,
        prize_amount        TEXT,
        eligibility_score   REAL DEFAULT 0,
        portal_url          TEXT,
        decision_date       TEXT,
        criteria            TEXT NOT NULL DEFAULT '[]',
        required_documents  TEXT NOT NULL DEFAULT '[]',
        application_form    TEXT NOT NULL DEFAULT '[]',
        created_at          TEXT NOT NULL
    )
    """,

    # ── Missions ──────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS missions (
        id                  TEXT PRIMARY KEY,
        user_id             TEXT NOT NULL,
        opportunity_id      TEXT NOT NULL,
        title               TEXT NOT NULL,
        goal                TEXT NOT NULL,
        state               TEXT NOT NULL DEFAULT 'DISCOVERING',
        progress            INTEGER NOT NULL DEFAULT 0,
        eligibility_score   REAL DEFAULT 0,
        confirmation_number TEXT,
        submission_id       TEXT,
        created_at          TEXT NOT NULL,
        updated_at          TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
    )
    """,

    # ── Mission Steps ─────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS mission_steps (
        id          TEXT PRIMARY KEY,
        mission_id  TEXT NOT NULL,
        step_order  INTEGER NOT NULL,
        name        TEXT NOT NULL,
        label       TEXT NOT NULL,
        state       TEXT NOT NULL DEFAULT 'pending',
        started_at  TEXT,
        completed_at TEXT,
        result      TEXT DEFAULT '{}',
        FOREIGN KEY (mission_id) REFERENCES missions(id)
    )
    """,

    # ── Documents ─────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS documents (
        id          TEXT PRIMARY KEY,
        user_id     TEXT NOT NULL,
        name        TEXT NOT NULL,
        file_path   TEXT NOT NULL,
        status      TEXT NOT NULL DEFAULT 'ready',
        last_updated TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """,

    # ── Applications ──────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS applications (
        id                  TEXT PRIMARY KEY,
        mission_id          TEXT NOT NULL,
        opportunity_id      TEXT NOT NULL,
        user_id             TEXT NOT NULL,
        status              TEXT NOT NULL DEFAULT 'draft',
        draft_data          TEXT NOT NULL DEFAULT '{}',
        submission_id       TEXT,
        confirmation_number TEXT,
        submitted_at        TEXT,
        verified_at         TEXT,
        created_at          TEXT NOT NULL,
        updated_at          TEXT NOT NULL,
        FOREIGN KEY (mission_id) REFERENCES missions(id)
    )
    """,

    # ── Approval Requests ─────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS approval_requests (
        id          TEXT PRIMARY KEY,
        mission_id  TEXT NOT NULL,
        action_type TEXT NOT NULL,
        summary     TEXT NOT NULL,
        details     TEXT DEFAULT '',
        status      TEXT NOT NULL DEFAULT 'pending',
        created_at  TEXT NOT NULL,
        expires_at  TEXT NOT NULL,
        resolved_at TEXT,
        resolved_by TEXT,
        FOREIGN KEY (mission_id) REFERENCES missions(id)
    )
    """,

    # ── Agent Events ──────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS agent_events (
        id          TEXT PRIMARY KEY,
        mission_id  TEXT NOT NULL,
        event_type  TEXT NOT NULL,
        message     TEXT NOT NULL,
        metadata    TEXT DEFAULT '{}',
        created_at  TEXT NOT NULL,
        FOREIGN KEY (mission_id) REFERENCES missions(id)
    )
    """,

    # ── Notifications ─────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id          TEXT PRIMARY KEY,
        user_id     TEXT NOT NULL,
        mission_id  TEXT,
        title       TEXT NOT NULL,
        body        TEXT NOT NULL,
        type        TEXT NOT NULL DEFAULT 'info',
        read        INTEGER NOT NULL DEFAULT 0,
        created_at  TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """,

    # ── Permissions ───────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS permissions (
        id          TEXT PRIMARY KEY,
        user_id     TEXT NOT NULL,
        resource    TEXT NOT NULL,
        action      TEXT NOT NULL,
        granted     INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """,
]


def get_db() -> aiosqlite.Connection:
    """Return an aiosqlite async context manager.
    
    Usage:
        async with get_db() as db:
            await db.execute(...)
    """
    conn = aiosqlite.connect(DB_PATH)
    # We patch row_factory via a wrapper because aiosqlite.connect returns
    # a Connection object whose row_factory must be set after __aenter__.
    return _RowFactoryWrapper(conn)


class _RowFactoryWrapper:
    """Thin wrapper that sets row_factory=aiosqlite.Row after connection opens."""
    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        db: aiosqlite.Connection = await self._conn.__aenter__()
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        return db

    async def __aexit__(self, *args):
        return await self._conn.__aexit__(*args)


async def init_db() -> None:
    """Create all tables if they do not exist and seed demo data."""
    async with get_db() as db:
        for sql in CREATE_TABLES_SQL:
            await db.execute(sql)
        await db.commit()

    # Import here to avoid circular imports
    from backend.data.seed import seed_database
    await seed_database()
