"""
Seed data for Raahi AI demo.
Includes: opportunities, user profile, and user documents.
"""
import json
import uuid
from datetime import datetime

# ── Demo User Profile ──────────────────────────────────────────────────────────
USER_PROFILE = {
    "name": "Aditi Dange",
    "email": "aditi@example.com",
    "date_of_birth": "2003-06-15",
    "gender": "female",
    "nationality": "indian",
    "academic_score": 91,
    "annual_income": 280000,  # INR
    "category": "general",
    "state": "maharashtra",
    "field_of_study": "computer_science",
    "skills": ["python", "react", "fastapi", "ai_ml"],
    "languages": ["english", "hindi", "marathi"],
}

# ── Demo User Documents ────────────────────────────────────────────────────────
USER_DOCUMENTS = [
    {
        "id": "doc_01",
        "name": "Income Certificate",
        "file_path": "/documents/income_certificate.pdf",
        "status": "ready",
        "last_updated": "2025-08-20",
    },
    {
        "id": "doc_02",
        "name": "Marksheet",
        "file_path": "/documents/marksheet.pdf",
        "status": "ready",
        "last_updated": "2025-06-10",
    },
    {
        "id": "doc_03",
        "name": "Aadhaar Card",
        "file_path": "/documents/aadhaar.pdf",
        "status": "ready",
        "last_updated": "2024-12-01",
    },
    {
        "id": "doc_04",
        "name": "Passport Photo",
        "file_path": "/documents/photo.jpg",
        "status": "ready",
        "last_updated": "2025-07-15",
    },
]

# ── Demo Opportunities ─────────────────────────────────────────────────────────
OPPORTUNITIES = [
    {
        "id": "opp_01",
        "title": "National Merit Scholarship",
        "category": "scholarship",
        "description": "Merit-based scholarship for undergraduate students with excellent academic records. Covers tuition and provides a stipend for educational expenses.",
        "deadline": "2026-09-18",
        "prize_amount": "₹50,000",
        "eligibility_score": 0.91,
        "portal_url": "https://scholarships.gov.in/nms",
        "decision_date": "2026-10-30",
        "criteria": [
            {"field": "academic_score", "operator": "gte", "value": 85, "label": "Academic score ≥ 85%"},
            {"field": "annual_income", "operator": "lte", "value": 600000, "label": "Annual income ≤ ₹6,00,000"},
            {"field": "nationality", "operator": "eq", "value": "indian", "label": "Indian nationality"},
        ],
        "required_documents": [
            {"name": "Income Certificate", "description": "Government-issued income certificate", "mandatory": True},
            {"name": "Marksheet", "description": "Latest academic marksheet", "mandatory": True},
            {"name": "Aadhaar Card", "description": "Identity proof", "mandatory": True},
            {"name": "Passport Photo", "description": "Recent passport-size photo", "mandatory": True},
        ],
        "application_form": [
            {"name": "Full Name", "type": "text", "source": "name", "required": True},
            {"name": "Email", "type": "email", "source": "email", "required": True},
            {"name": "Date of Birth", "type": "date", "source": "date_of_birth", "required": True},
            {"name": "Academic Score", "type": "number", "source": "academic_score", "required": True},
            {"name": "Annual Income", "type": "number", "source": "annual_income", "required": True},
            {"name": "Personal Statement", "type": "textarea", "source": None, "required": True},
        ],
    },
    {
        "id": "opp_02",
        "title": "Remote Software Engineering Internship",
        "category": "internship",
        "description": "3-month remote internship opportunity at a fast-growing tech startup. Work on real-world projects in AI/ML and web development.",
        "deadline": "2026-09-30",
        "prize_amount": "₹25,000/month",
        "eligibility_score": 0.88,
        "portal_url": "https://internships.example.com/swe",
        "decision_date": "2026-10-10",
        "criteria": [
            {"field": "field_of_study", "operator": "eq", "value": "computer_science", "label": "CS major"},
            {"field": "skills", "operator": "contains", "value": "python", "label": "Python proficiency"},
        ],
        "required_documents": [
            {"name": "Resume", "description": "Updated resume/CV", "mandatory": True},
            {"name": "Portfolio", "description": "GitHub or project portfolio link", "mandatory": False},
        ],
        "application_form": [
            {"name": "Full Name", "type": "text", "source": "name", "required": True},
            {"name": "Email", "type": "email", "source": "email", "required": True},
            {"name": "Skills", "type": "text", "source": "skills", "required": True},
            {"name": "Cover Letter", "type": "textarea", "source": None, "required": True},
        ],
    },
    {
        "id": "opp_03",
        "title": "Education Grant for Women in STEM",
        "category": "grant",
        "description": "Financial grant supporting women pursuing STEM education. One-time grant to support project costs and learning materials.",
        "deadline": "2026-10-05",
        "prize_amount": "₹30,000",
        "eligibility_score": 0.95,
        "portal_url": "https://grants.example.org/stem-women",
        "decision_date": "2026-11-01",
        "criteria": [
            {"field": "gender", "operator": "eq", "value": "female", "label": "Female applicants only"},
            {"field": "field_of_study", "operator": "in", "value": ["computer_science", "engineering", "mathematics"], "label": "STEM field"},
        ],
        "required_documents": [
            {"name": "Academic Records", "description": "Proof of current enrollment", "mandatory": True},
            {"name": "Project Proposal", "description": "Brief project description", "mandatory": True},
        ],
        "application_form": [
            {"name": "Full Name", "type": "text", "source": "name", "required": True},
            {"name": "Email", "type": "email", "source": "email", "required": True},
            {"name": "Field of Study", "type": "text", "source": "field_of_study", "required": True},
            {"name": "Proposal", "type": "textarea", "source": None, "required": True},
        ],
    },
    {
        "id": "opp_04",
        "title": "Community Tech Skills Certificate",
        "category": "program",
        "description": "Free certification program in web development and cloud computing. Earn a certificate upon completion and connect with mentors.",
        "deadline": "2026-09-25",
        "prize_amount": "Free (₹0)",
        "eligibility_score": 0.80,
        "portal_url": "https://community.techskills.org",
        "decision_date": "2026-10-01",
        "criteria": [
            {"field": "nationality", "operator": "eq", "value": "indian", "label": "Open to Indian residents"},
        ],
        "required_documents": [
            {"name": "ID Proof", "description": "Any government ID", "mandatory": True},
        ],
        "application_form": [
            {"name": "Full Name", "type": "text", "source": "name", "required": True},
            {"name": "Email", "type": "email", "source": "email", "required": True},
            {"name": "Motivation", "type": "textarea", "source": None, "required": True},
        ],
    },
    {
        "id": "opp_05",
        "title": "Startup Weekend Participation Grant",
        "category": "grant",
        "description": "Funding for participants attending startup hackathons and competitions. Covers travel and accommodation expenses.",
        "deadline": "2026-10-10",
        "prize_amount": "₹15,000",
        "eligibility_score": 0.75,
        "portal_url": "https://startupweekend.org/grants",
        "decision_date": "2026-10-20",
        "criteria": [
            {"field": "skills", "operator": "contains", "value": "python", "label": "Technical skills required"},
        ],
        "required_documents": [
            {"name": "Event Registration", "description": "Proof of hackathon registration", "mandatory": True},
        ],
        "application_form": [
            {"name": "Full Name", "type": "text", "source": "name", "required": True},
            {"name": "Email", "type": "email", "source": "email", "required": True},
            {"name": "Event Details", "type": "text", "source": None, "required": True},
        ],
    },
]


async def seed_database():
    """
    Insert demo data into the database (users, opportunities, documents).
    Called by init_db() on first run.
    """
    from backend.models.database import get_db

    async with get_db() as db:
        # Check if seed already exists
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM users WHERE id = ?", ("user_demo",))
        row = await cursor.fetchone()
        if row["cnt"] > 0:
            return  # Already seeded

        now = datetime.utcnow().isoformat() + "Z"

        # Seed demo user
        await db.execute(
            "INSERT INTO users (id, name, email, role, profile, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("user_demo", USER_PROFILE["name"], USER_PROFILE["email"], "applicant", json.dumps(USER_PROFILE), now)
        )

        # Seed opportunities
        for opp in OPPORTUNITIES:
            await db.execute(
                """
                INSERT INTO opportunities (
                    id, title, category, description, deadline, prize_amount,
                    eligibility_score, portal_url, decision_date, criteria,
                    required_documents, application_form, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    opp["id"], opp["title"], opp["category"], opp["description"],
                    opp["deadline"], opp["prize_amount"], opp["eligibility_score"],
                    opp.get("portal_url"), opp.get("decision_date"),
                    json.dumps(opp.get("criteria", [])),
                    json.dumps(opp.get("required_documents", [])),
                    json.dumps(opp.get("application_form", [])),
                    now
                )
            )

        # Seed user documents
        for doc in USER_DOCUMENTS:
            await db.execute(
                "INSERT INTO documents (id, user_id, name, file_path, status, last_updated) VALUES (?, ?, ?, ?, ?, ?)",
                (doc["id"], "user_demo", doc["name"], doc["file_path"], doc["status"], doc["last_updated"])
            )

        await db.commit()
        print("✓ Database seeded with demo data")
