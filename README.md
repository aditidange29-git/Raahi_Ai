# RAAHI AI

**From Opportunity to Outcome.**

> Built for the [Agents for Humans Hackathon](https://agentsforhumans.devpost.com/) — Professional Agents track  
> Powered by **AWS Strands Agents SDK** + Amazon Bedrock (Claude Sonnet 4)

---

## What is RAAHI?

Most people miss out on scholarships, grants, and opportunities not because they're unqualified — but because the process is exhausting. Finding options, checking eligibility, collecting documents, filling forms, submitting, tracking: each step is small, but together they drain real time and attention.

**RAAHI is an autonomous AI agent that handles all of it.**

You discover an opportunity. RAAHI takes responsibility for the rest — qualifying you, preparing the application, waiting for your approval on the one thing that truly requires it, submitting, verifying, and then monitoring in the background. It only surfaces when there's a genuine decision to make.

---

## Demo

### The Core Flow

```
User clicks "Start Mission"
        ↓
RAAHI discovers the opportunity
        ↓
RAAHI checks your eligibility automatically
        ↓
RAAHI verifies all required documents
        ↓
RAAHI prepares a pre-filled application
        ↓
⚠  RAAHI pauses — asks for your approval (the only human step)
        ↓
You approve with one click
        ↓
RAAHI submits, verifies receipt, monitors for updates
        ↓
You get notified when there's a real outcome 🎉
```

### Demo Data — Primary Mission

| Field | Value |
|-------|-------|
| Opportunity | National Merit Scholarship |
| Prize | ₹50,000 |
| Deadline | 18 September |
| Eligibility Match | 91% |
| Documents Ready | 4 / 4 |
| Mission Progress | Waiting for Approval |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│             React + Vite Frontend                   │
│   Dashboard · Discover · Missions · Approvals       │
└─────────────────────┬───────────────────────────────┘
                      │  REST API
┌─────────────────────▼───────────────────────────────┐
│              FastAPI Backend (Python)               │
│   /api/opportunities  /api/missions  /api/agent     │
└─────────────────────┬───────────────────────────────┘
                      │  Background Task
┌─────────────────────▼───────────────────────────────┐
│           RAAHI — Strands Agent Core                │
│                                                     │
│  8 Tools: opportunity_search · eligibility_checker  │
│  document_search · application_prepare              │
│  human_approval (HITL gate) · application_submit    │
│  application_verify · application_monitor           │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│       Amazon Bedrock — Claude Sonnet 4              │
└─────────────────────────────────────────────────────┘
```

Full architecture diagram with mission state machine → [`docs/architecture.md`](docs/architecture.md)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Agent SDK** | [Strands Agents SDK](https://strandsagents.com) 1.0.0 |
| **LLM** | Amazon Bedrock — Claude Sonnet 4 (`us.anthropic.claude-sonnet-4-5`) |
| **Backend** | Python 3.11, FastAPI 0.115, uvicorn |
| **Database** | SQLite via aiosqlite (11 tables) |
| **Frontend** | React 18, TypeScript, Vite 6 |
| **Styling** | Custom CSS design system — Inter + Manrope |

---

## Mission States

RAAHI tracks every mission through 13 states:

```
DISCOVERING → UNDERSTANDING → CHECKING_ELIGIBILITY → COLLECTING_DOCUMENTS
     → PREPARING → WAITING_FOR_APPROVAL → EXECUTING → VERIFYING
          → MONITORING → COMPLETED
               ↘ BLOCKED / FAILED / CANCELLED
```

The only state where the agent pauses for humans: **`WAITING_FOR_APPROVAL`**.  
Everything else runs automatically.

---

## The 8 Strands Tools

| Tool | What it does |
|------|-------------|
| `opportunity_search` | Finds relevant opportunities matching user profile |
| `eligibility_checker` | Scores the user against each criterion (0–100%) |
| `document_search` | Checks which documents are ready vs. missing |
| `application_prepare` | Drafts a pre-filled application from the user profile |
| `human_approval` | **HITL gate** — pauses agent, notifies user to review |
| `application_submit` | Submits only after `human_approval` returns `approved` |
| `application_verify` | Confirms the portal received the submission |
| `application_monitor` | Polls for status changes; surfaces only what needs action |

---

## Project Structure

```
Raahi_Ai/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt           # Python dependencies
│   ├── agent/
│   │   ├── raahi_agent.py         # Strands Agent factory + system prompt
│   │   └── tools/                 # 8 @tool-decorated functions
│   ├── api/                       # FastAPI route handlers
│   │   ├── opportunities.py
│   │   ├── missions.py            # Mission CRUD + agent background task
│   │   ├── documents.py
│   │   ├── applications.py
│   │   ├── notifications.py
│   │   └── agent.py               # Status + free-form agent run
│   ├── models/
│   │   ├── database.py            # aiosqlite setup + table creation
│   │   ├── mission_states.py      # State machine + valid transitions
│   │   └── schemas.py             # Pydantic request/response models
│   └── data/
│       └── seed.py                # Demo opportunities, user, documents
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx                # Page router
│       ├── lib/api.ts             # Typed API client
│       ├── hooks/useApi.ts        # useApi + usePoll hooks
│       ├── components/            # Sidebar, Topbar, Card, Badge, ProgressBar
│       ├── pages/                 # Dashboard, Discover, Missions, Approvals…
│       └── types/index.ts         # TypeScript interfaces
├── docs/
│   └── architecture.md            # Full architecture + state diagrams
├── .env.example                   # Environment variable template
├── LICENSE                        # MIT
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS account with Bedrock access enabled for **Claude Sonnet 4**
- AWS credentials configured (`aws configure` or environment variables)

### 1. Clone & configure

```bash
git clone https://github.com/aditidange29-git/Raahi_Ai.git
cd Raahi_Ai
cp .env.example .env
# Edit .env — add your AWS credentials
```

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cd ..
uvicorn backend.main:app --reload --port 8000
```

Backend runs at **http://localhost:8000**  
API docs at **http://localhost:8000/api/docs**

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

### 4. Try the demo

1. Open **http://localhost:5173**
2. Go to **Discover** → click **Start Mission** on the National Merit Scholarship
3. Watch the **Dashboard** as RAAHI works through each step automatically
4. When RAAHI reaches **Waiting for Approval**, go to **Approvals**
5. Click **Approve & Submit** — RAAHI completes the rest
6. Check **Activity** for the final confirmation

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RAAHI_MODEL_PROVIDER` | `bedrock` or `openai` | `bedrock` |
| `AWS_ACCESS_KEY_ID` | AWS credentials | — |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | — |
| `AWS_REGION` | Bedrock region | `us-east-1` |
| `BEDROCK_MODEL_ID` | Bedrock model ID | `us.anthropic.claude-sonnet-4-5` |
| `OPENAI_API_KEY` | OpenAI key (optional fallback) | — |
| `DB_PATH` | SQLite database path | `raahi.db` |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/opportunities` | List opportunities (filter by category/keyword) |
| `GET` | `/api/opportunities/{id}` | Get opportunity detail |
| `POST` | `/api/missions` | Create mission + start agent |
| `GET` | `/api/missions` | List all missions |
| `GET` | `/api/missions/{id}` | Get mission detail + steps |
| `POST` | `/api/missions/{id}/approve` | Approve or deny pending approval |
| `POST` | `/api/missions/{id}/cancel` | Cancel a mission |
| `GET` | `/api/missions/{id}/events` | Get agent event log |
| `GET` | `/api/documents` | List user documents |
| `POST` | `/api/documents` | Add a document |
| `GET` | `/api/applications` | List applications |
| `GET` | `/api/applications/{id}` | Get application detail |
| `GET` | `/api/notifications` | List notifications |
| `GET` | `/api/agent/status` | Agent status + active missions |
| `POST` | `/api/agent/run` | Free-form agent query (SSE) |
| `GET` | `/api/health` | Health check |

---

## Human-in-the-Loop Design

RAAHI is built around a clear principle: **automate everything that doesn't require a human, and surface everything that does.**

The `human_approval` tool is the only hard pause in the workflow. When it fires:

1. The agent writes an `ApprovalRequest` record to the database
2. The mission state transitions to `WAITING_FOR_APPROVAL`
3. The frontend displays a clear approval card with full context
4. The user approves or denies with one click
5. `application_submit` checks the approval before it can proceed — it's impossible to bypass

This means RAAHI **cannot submit on your behalf without explicit consent**. Every other step is automated because those steps don't carry irreversible consequences.

---

## Hackathon Track

**Professional Agents** — RAAHI makes applicants dramatically better at a repetitive, high-stakes task (applying for scholarships, grants, and programs) by handling the full workflow end-to-end. It targets the steps that eat time without requiring judgment: searching, qualifying, document collection, form preparation, verification, and monitoring.

---

## License

[MIT](LICENSE) © 2026 Aditi Dange
