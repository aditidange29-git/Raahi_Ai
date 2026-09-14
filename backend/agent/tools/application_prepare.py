"""
Tool: application_prepare
Drafts and pre-fills an application form for a given opportunity using the user profile.
"""
import json
from datetime import datetime
from strands import tool
from backend.data.seed import OPPORTUNITIES, USER_PROFILE


@tool
def application_prepare(opportunity_id: str, additional_notes: str = "") -> str:
    """
    Prepare a pre-filled application for an opportunity using the user's profile.

    Args:
        opportunity_id: The unique ID of the opportunity to apply for.
        additional_notes: Any extra context or personal statement text to include.

    Returns:
        JSON string with application_draft (pre-filled fields), validation_warnings,
        estimated_completion_time, and a checklist of items needing human review.
    """
    opp = next((o for o in OPPORTUNITIES if o["id"] == opportunity_id), None)
    if not opp:
        return json.dumps({"error": f"Opportunity '{opportunity_id}' not found."})

    form_fields = opp.get("application_form", [])
    draft_fields = {}
    validation_warnings = []

    for field in form_fields:
        field_name = field["name"]
        source = field.get("source")  # maps to user profile key
        field_type = field.get("type", "text")

        if source and source in USER_PROFILE:
            val = USER_PROFILE[source]
            draft_fields[field_name] = str(val) if not isinstance(val, list) else ", ".join(val)
        elif field.get("required", False):
            draft_fields[field_name] = ""
            validation_warnings.append(f"Required field '{field_name}' could not be auto-filled — needs manual entry.")
        else:
            draft_fields[field_name] = ""

    # Inject additional notes into personal_statement if present
    if additional_notes:
        for key in ("Personal Statement", "Statement of Purpose", "Cover Letter", "Essay"):
            if key in draft_fields or any(key.lower() in k.lower() for k in draft_fields):
                target_key = next((k for k in draft_fields if key.lower() in k.lower()), None)
                if target_key:
                    draft_fields[target_key] = additional_notes

    human_review_items = [
        "Verify personal statement reads naturally and reflects your voice.",
        "Confirm all dates and numbers are accurate.",
        "Check that uploaded documents match the application fields.",
        "Review declaration / signature section before final submission.",
    ]

    return json.dumps({
        "opportunity_id": opportunity_id,
        "opportunity_title": opp["title"],
        "prepared_at": datetime.utcnow().isoformat() + "Z",
        "application_draft": draft_fields,
        "validation_warnings": validation_warnings,
        "estimated_completion_time": "~5 minutes for human review",
        "human_review_items": human_review_items,
        "status": "draft_ready",
    }, indent=2)
