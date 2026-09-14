"""
Tool: application_submit
Submits the prepared application for an opportunity.
Only callable AFTER human_approval has status='approved'.
"""
import json
import uuid
from datetime import datetime
from strands import tool
from backend.data.seed import OPPORTUNITIES
from backend.agent.tools.human_approval import get_approval_store


@tool
def application_submit(mission_id: str, opportunity_id: str) -> str:
    """
    Submit the application for an opportunity.

    IMPORTANT: This tool should only be called after human_approval returns 'approved'.
    If no approval exists or it's pending/denied, submission is blocked.

    Args:
        mission_id: The ID of the active mission.
        opportunity_id: The ID of the opportunity being applied to.

    Returns:
        JSON with submission_id, submitted_at, status, confirmation_number,
        and next_steps for tracking.
    """
    # Gate: verify human approval
    approval_store = get_approval_store()
    approval = approval_store.get(mission_id)

    if not approval:
        return json.dumps({
            "error": "No approval request found for this mission. Call human_approval first.",
            "status": "blocked",
        })

    if approval.get("status") != "approved":
        return json.dumps({
            "error": f"Approval status is '{approval.get('status')}'. Submission requires 'approved'.",
            "status": "blocked",
            "approval_id": approval.get("approval_id"),
        })

    opp = next((o for o in OPPORTUNITIES if o["id"] == opportunity_id), None)
    if not opp:
        return json.dumps({"error": f"Opportunity '{opportunity_id}' not found."})

    submission_id = f"sub_{uuid.uuid4().hex[:10]}"
    confirmation_number = f"RAAHI-{uuid.uuid4().hex[:8].upper()}"
    submitted_at = datetime.utcnow().isoformat() + "Z"

    return json.dumps({
        "submission_id": submission_id,
        "mission_id": mission_id,
        "opportunity_id": opportunity_id,
        "opportunity_title": opp["title"],
        "status": "submitted",
        "submitted_at": submitted_at,
        "confirmation_number": confirmation_number,
        "portal_url": opp.get("portal_url", "https://example-portal.gov/track"),
        "next_steps": [
            f"Save confirmation number: {confirmation_number}",
            f"Check application status at: {opp.get('portal_url', 'the official portal')}",
            "RAAHI will monitor for status updates and notify you of any changes.",
            f"Expected response by: {opp.get('decision_date', 'within 30 days')}",
        ],
    }, indent=2)
