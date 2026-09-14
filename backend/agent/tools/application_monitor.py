"""
Tool: application_monitor
Monitors a submitted application for status changes and surfaces only
what requires a human decision — keeping humans out of the loop for routine checks.
"""
import json
import random
from datetime import datetime, timedelta
from strands import tool
from backend.data.seed import OPPORTUNITIES


# In-memory monitor store (keyed by confirmation_number)
_MONITOR_STORE: dict[str, list] = {}

_STATUS_SEQUENCE = [
    ("submitted", "Application received by the portal."),
    ("under_review", "Application is under initial review."),
    ("documents_verified", "Documents have been verified by the committee."),
    ("shortlisted", "You have been shortlisted for the next stage."),
    ("decision_pending", "Final decision is being prepared."),
    ("approved", "Congratulations! Your application has been approved. 🎉"),
]


@tool
def application_monitor(
    confirmation_number: str,
    opportunity_id: str,
    last_known_status: str = "submitted",
) -> str:
    """
    Monitor the status of a submitted application.

    Polls the application portal (simulated) and returns any status changes.
    Only raises a notification when human attention is truly needed
    (e.g., approval, additional documents requested, or rejection).

    Args:
        confirmation_number: The portal confirmation number for the application.
        opportunity_id: The ID of the opportunity being monitored.
        last_known_status: The status from the previous monitoring check.

    Returns:
        JSON with current_status, status_history, requires_human_action (bool),
        action_required (description if human action needed), and next_check_at.
    """
    opp = next((o for o in OPPORTUNITIES if o["id"] == opportunity_id), None)
    opp_title = opp["title"] if opp else "Unknown Opportunity"

    history = _MONITOR_STORE.get(confirmation_number, [])

    # Simulate status progression (in production: real portal polling)
    known_keys = [s[0] for s in _STATUS_SEQUENCE]
    current_idx = known_keys.index(last_known_status) if last_known_status in known_keys else 0
    next_idx = min(current_idx + 1, len(_STATUS_SEQUENCE) - 1)
    current_status, status_message = _STATUS_SEQUENCE[next_idx]

    event = {
        "status": current_status,
        "message": status_message,
        "checked_at": datetime.utcnow().isoformat() + "Z",
    }
    history.append(event)
    _MONITOR_STORE[confirmation_number] = history

    requires_human = current_status in ("approved", "decision_pending", "shortlisted")
    action_required = ""
    if current_status == "approved":
        action_required = "Your application was approved! Log in to accept the award and provide bank details."
    elif current_status == "shortlisted":
        action_required = "You've been shortlisted. Check if an interview or additional documents are required."
    elif current_status == "decision_pending":
        action_required = "Decision is imminent. Be ready to respond within 48 hours of notification."

    next_check_at = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"

    return json.dumps({
        "confirmation_number": confirmation_number,
        "opportunity_id": opportunity_id,
        "opportunity_title": opp_title,
        "current_status": current_status,
        "status_message": status_message,
        "status_history": history,
        "requires_human_action": requires_human,
        "action_required": action_required,
        "next_check_at": next_check_at,
    }, indent=2)
