"""
API routes — /api/opportunities
GET /api/opportunities
GET /api/opportunities/{id}
"""
import json
from fastapi import APIRouter, HTTPException, Query
from backend.models.database import get_db
from backend.models.schemas import OpportunityBase, OpportunityDetail, OpportunitiesResponse

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


@router.get("", response_model=OpportunitiesResponse)
async def list_opportunities(
    category: str = Query(default="all", description="Filter by category"),
    keyword: str = Query(default="", description="Search keyword"),
):
    async with get_db() as db:
        if category != "all":
            cursor = await db.execute(
                "SELECT * FROM opportunities WHERE category = ?", (category,)
            )
        else:
            cursor = await db.execute("SELECT * FROM opportunities")
        rows = await cursor.fetchall()

    results = []
    for row in rows:
        opp = dict(row)
        if keyword and keyword.lower() not in (opp["title"] + opp["description"]).lower():
            continue
        results.append(OpportunityBase(
            id=opp["id"],
            title=opp["title"],
            category=opp["category"],
            description=opp["description"],
            deadline=opp["deadline"],
            prize_amount=opp.get("prize_amount"),
            eligibility_score=opp["eligibility_score"],
            portal_url=opp.get("portal_url"),
        ))

    return OpportunitiesResponse(count=len(results), opportunities=results)


@router.get("/{opportunity_id}", response_model=OpportunityDetail)
async def get_opportunity(opportunity_id: str):
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM opportunities WHERE id = ?", (opportunity_id,)
        )
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"Opportunity '{opportunity_id}' not found.")

    opp = dict(row)
    return OpportunityDetail(
        id=opp["id"],
        title=opp["title"],
        category=opp["category"],
        description=opp["description"],
        deadline=opp["deadline"],
        prize_amount=opp.get("prize_amount"),
        eligibility_score=opp["eligibility_score"],
        portal_url=opp.get("portal_url"),
        decision_date=opp.get("decision_date"),
        criteria=json.loads(opp.get("criteria") or "[]"),
        required_documents=json.loads(opp.get("required_documents") or "[]"),
        application_form=json.loads(opp.get("application_form") or "[]"),
    )
