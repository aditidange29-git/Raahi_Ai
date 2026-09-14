"""
Tool: eligibility_checker
Checks whether a user meets the eligibility criteria for a given opportunity.
"""
import json
from strands import tool
from backend.data.seed import OPPORTUNITIES, USER_PROFILE


@tool
def eligibility_checker(opportunity_id: str) -> str:
    """
    Check eligibility for a specific opportunity against the user's profile.

    Args:
        opportunity_id: The unique ID of the opportunity to check.

    Returns:
        JSON string with is_eligible (bool), score (0-100), matched_criteria (list),
        missing_criteria (list), and recommendation.
    """
    opp = next((o for o in OPPORTUNITIES if o["id"] == opportunity_id), None)
    if not opp:
        return json.dumps({"error": f"Opportunity '{opportunity_id}' not found."})

    criteria = opp.get("criteria", [])
    matched = []
    missing = []

    for c in criteria:
        field = c.get("field")
        operator = c.get("operator", "gte")
        required = c.get("value")
        user_val = USER_PROFILE.get(field)

        if user_val is None:
            missing.append({"criterion": c["label"], "reason": "Information not available in profile"})
            continue

        passed = False
        if operator == "gte" and isinstance(user_val, (int, float)):
            passed = float(user_val) >= float(required)
        elif operator == "lte" and isinstance(user_val, (int, float)):
            passed = float(user_val) <= float(required)
        elif operator == "eq":
            passed = str(user_val).lower() == str(required).lower()
        elif operator == "in" and isinstance(required, list):
            passed = str(user_val).lower() in [str(r).lower() for r in required]
        elif operator == "contains" and isinstance(user_val, list):
            passed = str(required).lower() in [str(v).lower() for v in user_val]

        if passed:
            matched.append({"criterion": c["label"], "user_value": user_val, "required": required})
        else:
            missing.append({
                "criterion": c["label"],
                "user_value": user_val,
                "required": required,
                "reason": f"Expected {operator} {required}, got {user_val}"
            })

    total = len(criteria)
    score = round((len(matched) / total * 100) if total else 0)
    is_eligible = len(missing) == 0

    recommendation = (
        "Strong match — proceed to document collection and application."
        if score >= 80
        else "Partial match — review missing criteria before applying."
        if score >= 50
        else "Low match — this opportunity may not be suitable right now."
    )

    return json.dumps({
        "opportunity_id": opportunity_id,
        "opportunity_title": opp["title"],
        "is_eligible": is_eligible,
        "score": score,
        "matched_criteria": matched,
        "missing_criteria": missing,
        "recommendation": recommendation,
    }, indent=2)
