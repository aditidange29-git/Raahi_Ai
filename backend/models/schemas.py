"""
Pydantic schemas for API request / response validation.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Opportunity ────────────────────────────────────────────────────────────────
class OpportunityBase(BaseModel):
    id: str
    title: str
    category: str
    description: str
    deadline: str
    prize_amount: Optional[str] = None
    eligibility_score: float = 0.0
    portal_url: Optional[str] = None

class OpportunityDetail(OpportunityBase):
    decision_date: Optional[str] = None
    criteria: list[dict[str, Any]] = []
    required_documents: list[dict[str, Any]] = []
    application_form: list[dict[str, Any]] = []

class OpportunitiesResponse(BaseModel):
    count: int
    opportunities: list[OpportunityBase]


# ── Mission ────────────────────────────────────────────────────────────────────
class MissionCreate(BaseModel):
    opportunity_id: str
    goal: str = Field(default="Complete the application process end-to-end.")

class MissionStep(BaseModel):
    id: str
    step_order: int
    name: str
    label: str
    state: str  # pending | active | done | skipped | failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: dict[str, Any] = {}

class MissionResponse(BaseModel):
    id: str
    user_id: str
    opportunity_id: str
    title: str
    goal: str
    state: str
    progress: int
    eligibility_score: float
    confirmation_number: Optional[str] = None
    submission_id: Optional[str] = None
    steps: list[MissionStep] = []
    created_at: str
    updated_at: str

class MissionsResponse(BaseModel):
    count: int
    missions: list[MissionResponse]


# ── Approval ───────────────────────────────────────────────────────────────────
class ApprovalAction(BaseModel):
    action: str = Field(..., pattern="^(approve|deny)$")
    reason: Optional[str] = None

class ApprovalResponse(BaseModel):
    approval_id: str
    mission_id: str
    status: str
    resolved_at: str
    message: str


# ── Agent Events ───────────────────────────────────────────────────────────────
class AgentEvent(BaseModel):
    id: str
    mission_id: str
    event_type: str
    message: str
    metadata: dict[str, Any] = {}
    created_at: str

class AgentEventsResponse(BaseModel):
    mission_id: str
    count: int
    events: list[AgentEvent]


# ── Documents ──────────────────────────────────────────────────────────────────
class DocumentBase(BaseModel):
    id: str
    name: str
    status: str
    last_updated: str

class DocumentCreate(BaseModel):
    name: str
    file_path: str
    status: str = "ready"

class DocumentsResponse(BaseModel):
    count: int
    documents: list[DocumentBase]


# ── Applications ───────────────────────────────────────────────────────────────
class ApplicationBase(BaseModel):
    id: str
    mission_id: str
    opportunity_id: str
    status: str
    submitted_at: Optional[str] = None
    confirmation_number: Optional[str] = None
    created_at: str

class ApplicationDetail(ApplicationBase):
    draft_data: dict[str, Any] = {}
    verified_at: Optional[str] = None

class ApplicationsResponse(BaseModel):
    count: int
    applications: list[ApplicationBase]


# ── Notifications ──────────────────────────────────────────────────────────────
class NotificationBase(BaseModel):
    id: str
    mission_id: Optional[str] = None
    title: str
    body: str
    type: str
    read: bool
    created_at: str

class NotificationsResponse(BaseModel):
    count: int
    unread_count: int
    notifications: list[NotificationBase]


# ── Agent Status ───────────────────────────────────────────────────────────────
class AgentStatusResponse(BaseModel):
    status: str  # idle | running | waiting_approval
    active_missions: int
    tools_available: list[str]
    model_provider: str
    version: str = "1.0.0"


# ── Mission Run (start agent) ──────────────────────────────────────────────────
class MissionRunRequest(BaseModel):
    message: Optional[str] = None
