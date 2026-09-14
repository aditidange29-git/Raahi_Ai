"""
Tool: document_search
Looks up which documents the user currently has and which are still needed for an opportunity.
"""
import json
from strands import tool
from backend.data.seed import OPPORTUNITIES, USER_DOCUMENTS


@tool
def document_search(opportunity_id: str) -> str:
    """
    Check which documents are required for an opportunity and their availability status.

    Args:
        opportunity_id: The unique ID of the opportunity.

    Returns:
        JSON string with required_docs list, available_docs list, missing_docs list,
        readiness_score (0-100), and next_steps.
    """
    opp = next((o for o in OPPORTUNITIES if o["id"] == opportunity_id), None)
    if not opp:
        return json.dumps({"error": f"Opportunity '{opportunity_id}' not found."})

    required = opp.get("required_documents", [])
    available = []
    missing = []

    user_doc_names = {d["name"].lower(): d for d in USER_DOCUMENTS}

    for doc in required:
        doc_key = doc["name"].lower()
        matched = user_doc_names.get(doc_key)
        if matched:
            available.append({
                "name": doc["name"],
                "status": matched.get("status", "ready"),
                "last_updated": matched.get("last_updated", "unknown"),
                "file_path": matched.get("file_path", ""),
            })
        else:
            available_keys = list(user_doc_names.keys())
            partial = next(
                (k for k in available_keys if any(word in k for word in doc_key.split())),
                None
            )
            if partial:
                matched_doc = user_doc_names[partial]
                available.append({
                    "name": doc["name"],
                    "status": "ready",
                    "last_updated": matched_doc.get("last_updated", "unknown"),
                    "file_path": matched_doc.get("file_path", ""),
                    "matched_as": partial,
                })
            else:
                missing.append({
                    "name": doc["name"],
                    "description": doc.get("description", ""),
                    "mandatory": doc.get("mandatory", True),
                })

    readiness = round(len(available) / len(required) * 100) if required else 100

    next_steps = (
        "All documents ready — proceed to application preparation."
        if not missing
        else f"Collect missing documents: {', '.join(d['name'] for d in missing)}."
    )

    return json.dumps({
        "opportunity_id": opportunity_id,
        "opportunity_title": opp["title"],
        "required_docs": required,
        "available_docs": available,
        "missing_docs": missing,
        "readiness_score": readiness,
        "next_steps": next_steps,
    }, indent=2)
