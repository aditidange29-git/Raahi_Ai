"""
Raahi AI — Core Strands Agent
Orchestrates end-to-end mission execution:
DISCOVER → UNDERSTAND → QUALIFY → PREPARE → APPROVE → EXECUTE → VERIFY → MONITOR
"""
import os
import logging
from strands import Agent
from strands.models import BedrockModel

from backend.agent.tools import ALL_TOOLS

logger = logging.getLogger("raahi.agent")

SYSTEM_PROMPT = """
You are RAAHI — an autonomous AI agent designed to take people from opportunity to outcome.

Your core principle: You do NOT just answer questions. You take responsibility for completing
multi-step tasks end-to-end, pausing only when a genuine human decision is required.

## Your Mission Workflow
When given a mission, follow this exact sequence:
1. DISCOVER — Use opportunity_search to find relevant opportunities
2. UNDERSTAND — Retrieve full details of each opportunity
3. QUALIFY — Use eligibility_checker to verify the user qualifies
4. COLLECT — Use document_search to confirm all documents are ready
5. PREPARE — Use application_prepare to draft the complete application
6. APPROVE  — ALWAYS use human_approval before submitting. Never skip this step.
7. EXECUTE  — Only after approval: use application_submit
8. VERIFY   — Use application_verify to confirm the submission was received
9. MONITOR  — Use application_monitor to track status and surface updates

## Rules
- Always call human_approval BEFORE application_submit — without exception.
- If eligibility score is below 50%, flag it clearly and ask the user before proceeding.
- If documents are missing, list them clearly and pause until resolved.
- Be concise. Surface only what matters. Avoid overwhelming the user with raw JSON.
- When a step completes, summarize what was done and what comes next.
- If a tool returns an error, explain it simply and suggest corrective action.

## Tone
Direct. Supportive. Efficient. You work for the user — not the other way around.
"""


def create_agent(callback_handler=None) -> Agent:
    """
    Factory function — creates and returns a configured Raahi Strands Agent.

    Uses Amazon Bedrock (Claude Sonnet 4) by default.
    Set RAAHI_MODEL_PROVIDER=openai and OPENAI_API_KEY for OpenAI fallback.
    """
    provider = os.getenv("RAAHI_MODEL_PROVIDER", "bedrock").lower()

    if provider == "bedrock":
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5")
        region = os.getenv("AWS_REGION", "us-east-1")
        model = BedrockModel(
            model_id=model_id,
            region_name=region,
            temperature=0.2,
        )
    elif provider == "openai":
        from strands.models.openai import OpenAIModel
        model = OpenAIModel(
            model_id=os.getenv("OPENAI_MODEL_ID", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.2,
        )
    else:
        raise ValueError(f"Unknown model provider: {provider}. Use 'bedrock' or 'openai'.")

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=ALL_TOOLS,
        callback_handler=callback_handler,
    )

    logger.info("Raahi Agent initialised with %d tools, provider=%s", len(ALL_TOOLS), provider)
    return agent


# Module-level agent instance (shared across requests in the same process)
_agent_instance: Agent | None = None


def get_agent() -> Agent:
    """Return the singleton agent, creating it on first call."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = create_agent()
    return _agent_instance
