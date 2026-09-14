"""
Tool: human_approval
Pauses agent execution and raises a human-in-the-loop approval request.
The agent will NOT proceed past this tool until the approval is granted or denied via the API.
"""
import json
from datetime import datetime, timedelta
from strands import tool

# In-memory approval store (keyed by mission_id).
# In production this is persisted to the database via the API.
_APPROVAL_STORE: dict[str, dict] = {}


def get_approval_store() -> dict:
    """Expose the internal store so the API layer can read/write it."""
    return _APPROVAL_STORE


@tool
def human_approval(
    mission_id: str,
    action_type: str,
    summary: str,
    details: str = "",
    expires_in_hours: int = 48,
) -> str:
    """
    Request human approval before proceeding with a sensitive action.

    This is the human-in-the-loop gate. The agent MUST call this before
    executing any irreversible action (e.g., submitting an application).
    The tool will return 'pending' immediately; the orchestrator checks
    the approval status before allowing the next step.

    Args:
        mission_id: The ID of the mission requiring approval.
        action_type: Short label for the action, e.g. 'application_submit'.
        summary: One-sentence summary shown to the user in the approval UI.
        details: Longer description of what will happen if approved.
        expires_in_hours: How long the approval request remains valid.

    Returns:
        JSON with approval_id, status ('pending'|'approved'|'denied'), and instructions.
    """
    existing = _APPROVAL_STORE.get(mission_id)
    if existing and existing.get("status") == "approved":
        return json.dumps({
            "approval_id": existing["approval_id"],
            "mission_id": mission_id,
            "status": "approved",
            "message": "Previously approved — proceeding.",
        })

    if existing and existing.get("status") == "denied":
        return json.dumps({
            "approval_id": existing["approval_id"],
            "mission_id": mission_id,
            "status": "denied",
            "message": "Approval was denied. Mission halted.",
        })

    approval_id = f"apr_{mission_id}_{int(datetime.utcnow().timestamp())}"
    expires_at = (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat() + "Z"

    record = {
        "approval_id": approval_id,
        "mission_id": mission_id,
        "action_type": action_type,
        "summary": summary,
        "details": details,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "expires_at": expires_at,
    }
    _APPROVAL_STORE[mission_id] = record

    return json.dumps({
        "approval_id": approval_id,
        "mission_id": mission_id,
        "status": "pending",
        "message": (
            "Approval request created. The agent is paused. "
            "A human must approve via the /api/missions/{id}/approve endpoint before execution continues."
        ),
        "expires_at": expires_at,
    }, indent=2)
