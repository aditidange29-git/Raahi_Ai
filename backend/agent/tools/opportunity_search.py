"""
Tool: opportunity_search
Searches for scholarships, internships, grants, and programs matching the user profile.
"""
import json
from strands import tool
from backend.data.seed import OPPORTUNITIES


@tool
def opportunity_search(
    category: str = "all",
    min_eligibility: float = 0.0,
    keyword: str = "",
) -> str:
    """
    Search for opportunities (scholarships, internships, grants, programs).

    Args:
        category: Filter by category — 'scholarship', 'internship', 'grant', 'program', or 'all'.
        min_eligibility: Minimum eligibility match score between 0.0 and 1.0.
        keyword: Optional keyword to search in title or description.

    Returns:
        JSON string of matching opportunities with id, title, category, deadline,
        prize_amount, eligibility_score, and short description.
    """
    results = []
    for opp in OPPORTUNITIES:
        if category != "all" and opp["category"] != category:
            continue
        if opp["eligibility_score"] < min_eligibility:
            continue
        if keyword and keyword.lower() not in (opp["title"] + opp["description"]).lower():
            continue
        results.append({
            "id": opp["id"],
            "title": opp["title"],
            "category": opp["category"],
            "deadline": opp["deadline"],
            "prize_amount": opp["prize_amount"],
            "eligibility_score": opp["eligibility_score"],
            "description": opp["description"][:120] + "...",
        })

    return json.dumps({
        "count": len(results),
        "opportunities": results
    }, indent=2)
