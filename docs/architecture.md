# Raahi AI — Architecture

## System Overview

Raahi AI is a full-stack autonomous agent application. The user interacts with a React frontend; all background work is done by a **Strands Agent** running on the FastAPI backend. The agent only surfaces to the user when a genuine human decision is required.

---

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          RAAHI AI SYSTEM                                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      React + Vite Frontend                       │  │
│  │                                                                  │  │
│  │  Dashboard  │  Discover  │  Missions  │  Approvals  │  Settings  │  │
│  │       ↕              ↕          ↕           ↕                    │  │
│  │              HTTP / REST API  (polling every 4–5s)               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                               │                                         │
│                               ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  FastAPI Backend  (Python)                       │  │
│  │                                                                  │  │
│  │  GET /api/opportunities          POST /api/missions              │  │
│  │  GET /api/missions/{id}          POST /api/missions/{id}/approve │  │
│  │  GET /api/missions/{id}/events   POST /api/missions/{id}/cancel  │  │
│  │  GET /api/documents              POST /api/documents             │  │
│  │  GET /api/applications           GET  /api/agent/status          │  │
│  │  GET /api/notifications          POST /api/agent/run             │  │
│  └──────────────────────┬───────────────────────────────────────────┘  │
│                          │  Background Task (asyncio)                   │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               RAAHI Strands Agent  (Core)                        │  │
│  │                                                                  │  │
│  │  System Prompt: "Complete the full workflow end-to-end.          │  │
│  │   Only pause when a human decision is genuinely required."       │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐    │  │
│  │  │                   Agent Loop (Strands)                  │    │  │
│  │  │  Input + Context → Reasoning (LLM) → Tool Selection     │    │  │
│  │  │       ↑                                    ↓            │    │  │
│  │  │  Observation  ←────────── Tool Execution               │    │  │
│  │  └─────────────────────────────────────────────────────────┘    │  │
│  │                                                                  │  │
│  │  8 Strands Tools:                                                │  │
│  │  ┌──────────────────┐  ┌──────────────────┐                     │  │
│  │  │opportunity_search│  │eligibility_checker│                    │  │
│  │  └──────────────────┘  └──────────────────┘                     │  │
│  │  ┌──────────────────┐  ┌──────────────────┐                     │  │
│  │  │ document_search  │  │application_prepare│                    │  │
│  │  └──────────────────┘  └──────────────────┘                     │  │
│  │  ┌──────────────────┐  ┌──────────────────┐                     │  │
│  │  │  human_approval  │  │application_submit │  ← HITL gate       │  │
│  │  └──────────────────┘  └──────────────────┘                     │  │
│  │  ┌──────────────────┐  ┌──────────────────┐                     │  │
│  │  │application_verify│  │application_monitor│                    │  │
│  │  └──────────────────┘  └──────────────────┘                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  Amazon Bedrock                                  │  │
│  │          Claude Sonnet 4  (us.anthropic.claude-sonnet-4-5)       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               SQLite Database  (aiosqlite)                       │  │
│  │                                                                  │  │
│  │  users · opportunities · missions · mission_steps · documents    │  │
│  │  applications · approval_requests · agent_events · notifications │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Mission Workflow (Happy Path)

```
User clicks "Start Mission"
        │
        ▼
┌───────────────────┐
│   DISCOVERING     │  opportunity_search → find the opportunity
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  UNDERSTANDING    │  Load full opportunity details
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│CHECKING_ELIGIBILITY│ eligibility_checker → score user vs criteria
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│COLLECTING_DOCUMENTS│ document_search → confirm all docs ready
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│    PREPARING      │  application_prepare → draft pre-filled form
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│WAITING_FOR_APPROVAL│◄─── human_approval tool fires ──► USER NOTIFIED
└────────┬──────────┘      Agent PAUSES here
         │  User approves via /api/missions/{id}/approve
         ▼
┌───────────────────┐
│    EXECUTING      │  application_submit → send to portal
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│    VERIFYING      │  application_verify → confirm receipt
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│    MONITORING     │  application_monitor → poll for status changes
└────────┬──────────┘
         │  Status = approved
         ▼
┌───────────────────┐
│    COMPLETED      │  User notified of final outcome 🎉
└───────────────────┘
```

---

## Key Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Runs quietly in background** | FastAPI BackgroundTasks + asyncio executor |
| **Only surfaces for real decisions** | `human_approval` tool is the only hard pause point |
| **Cannot skip the HITL gate** | `application_submit` checks approval store before proceeding |
| **Full observability** | Every agent step writes to `agent_events` table; frontend polls it |
| **Graceful failure** | All states include FAILED/CANCELLED transitions; errors are logged as events |
| **Open source** | MIT License, Strands Agents SDK, no proprietary lock-in |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent SDK | [Strands Agents SDK](https://strandsagents.com) 1.0.0 |
| LLM | Amazon Bedrock — Claude Sonnet 4 |
| Backend | Python 3.11, FastAPI 0.115, uvicorn |
| Database | SQLite via aiosqlite |
| Frontend | React 18, TypeScript, Vite 6 |
| Styling | Custom CSS design system (Inter + Manrope) |
