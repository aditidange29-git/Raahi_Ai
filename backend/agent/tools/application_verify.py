"""
Tool: application_verify
Verifies a submitted application by checking the portal for confirmation
and validating all fields were received correctly.
"""
import json
from datetime import datetime
from strands import tool
from backend.data.seed import OPPORTUNITIES


# Simulated verification results keyed by confirmation number.
_VERIFICATION_CACHE: dict[str, dict] = {}


@tool
def application_verify(
    submission_id: str,
    confirmation_number: str,
    opportunity_id: str,
) -> str:
    """
    Verify that a submitted application was received and is complete.

    Checks the application portal for submission confirmation and validates
    that all required fields and documents were accepted.

    Args:
        submission_id: The internal submission ID returned by application_submit.
        confirmation_number: The portal confirmation number (e.g. RAAHI-XXXXXXXX).
        opportunity_id: The ID of the opportunity that was applied to.

    Returns:
        JSON with verification_status, portal_status, field_validation results,
        issues (if any), and recommended_actions.
    """
    # Check cache (or simulate a fresh check)
    cached = _VERIFICATION_CACHE.get(confirmation_number)
    if cached:
        return json.dumps(cached, indent=2)

    opp = next((o for o in OPPORTUNITIES if o["id"] == opportunity_id), None)
    opp_title = opp["title"] if opp else "Unknown Opportunity"

    # Simulate portal verification (in production: HTTP call to the real portal)
    field_validation = [
        {"field": "Full Name", "status": "accepted"},
        {"field": "Date of Birth", "status": "accepted"},
        {"field": "Academic Score", "status": "accepted"},
        {"field": "Personal Statement", "status": "accepted"},
        {"field": "Income Certificate", "status": "accepted"},
        {"field": "Marksheet", "status": "accepted"},
    ]

    result = {
        "submission_id": submission_id,
        "confirmation_number": confirmation_number,
        "opportunity_id": opportunity_id,
        "opportunity_title": opp_title,
        "verification_status": "verified",
        "portal_status": "received",
        "verified_at": datetime.utcnow().isoformat() + "Z",
        "field_validation": field_validation,
        "issues": [],
        "recommended_actions": [
            "Application verified successfully — no action needed.",
            "RAAHI will now switch to monitoring mode.",
        ],
    }

    _VERIFICATION_CACHE[confirmation_number] = result
    return json.dumps(result, indent=2)
