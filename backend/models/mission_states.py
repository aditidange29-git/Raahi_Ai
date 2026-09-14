"""
Mission State Machine — Raahi AI
Defines all valid states, transitions, and terminal states for a mission lifecycle.
"""
from enum import Enum
from typing import Set


class MissionState(str, Enum):
    """All possible states in the RAAHI mission lifecycle."""
    DISCOVERING = "DISCOVERING"
    UNDERSTANDING = "UNDERSTANDING"
    CHECKING_ELIGIBILITY = "CHECKING_ELIGIBILITY"
    COLLECTING_DOCUMENTS = "COLLECTING_DOCUMENTS"
    PREPARING = "PREPARING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    MONITORING = "MONITORING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# Valid forward transitions: state → set of states it may move to
VALID_TRANSITIONS: dict[MissionState, list[MissionState]] = {
    MissionState.DISCOVERING: [
        MissionState.UNDERSTANDING,
        MissionState.BLOCKED,
        MissionState.FAILED,
    ],
    MissionState.UNDERSTANDING: [
        MissionState.CHECKING_ELIGIBILITY,
        MissionState.BLOCKED,
        MissionState.FAILED,
    ],
    MissionState.CHECKING_ELIGIBILITY: [
        MissionState.COLLECTING_DOCUMENTS,
        MissionState.BLOCKED,
        MissionState.FAILED,
    ],
    MissionState.COLLECTING_DOCUMENTS: [
        MissionState.PREPARING,
        MissionState.BLOCKED,
        MissionState.FAILED,
    ],
    MissionState.PREPARING: [
        MissionState.WAITING_FOR_APPROVAL,
        MissionState.BLOCKED,
        MissionState.FAILED,
    ],
    MissionState.WAITING_FOR_APPROVAL: [
        MissionState.EXECUTING,
        MissionState.CANCELLED,
        MissionState.FAILED,
    ],
    MissionState.EXECUTING: [
        MissionState.VERIFYING,
        MissionState.FAILED,
    ],
    MissionState.VERIFYING: [
        MissionState.MONITORING,
        MissionState.FAILED,
    ],
    MissionState.MONITORING: [
        MissionState.COMPLETED,
        MissionState.FAILED,
    ],
    # Terminal states — no further transitions
    MissionState.COMPLETED: [],
    MissionState.BLOCKED: [MissionState.COLLECTING_DOCUMENTS, MissionState.CANCELLED],
    MissionState.FAILED: [],
    MissionState.CANCELLED: [],
}

TERMINAL_STATES = {MissionState.COMPLETED, MissionState.FAILED, MissionState.CANCELLED}

ACTIVE_STATES = {
    MissionState.DISCOVERING,
    MissionState.UNDERSTANDING,
    MissionState.CHECKING_ELIGIBILITY,
    MissionState.COLLECTING_DOCUMENTS,
    MissionState.PREPARING,
    MissionState.EXECUTING,
    MissionState.VERIFYING,
    MissionState.MONITORING,
}

# Human action required in these states
HUMAN_GATE_STATES = {MissionState.WAITING_FOR_APPROVAL}

# Display labels for the UI
STATE_LABELS: dict[MissionState, str] = {
    MissionState.DISCOVERING: "Discovering",
    MissionState.UNDERSTANDING: "Understanding",
    MissionState.CHECKING_ELIGIBILITY: "Checking Eligibility",
    MissionState.COLLECTING_DOCUMENTS: "Collecting Documents",
    MissionState.PREPARING: "Preparing Application",
    MissionState.WAITING_FOR_APPROVAL: "Waiting for Approval",
    MissionState.EXECUTING: "Submitting",
    MissionState.VERIFYING: "Verifying",
    MissionState.MONITORING: "Monitoring",
    MissionState.COMPLETED: "Completed",
    MissionState.BLOCKED: "Blocked",
    MissionState.FAILED: "Failed",
    MissionState.CANCELLED: "Cancelled",
}

# Ordered sequence for progress display (happy path)
HAPPY_PATH_SEQUENCE = [
    MissionState.DISCOVERING,
    MissionState.UNDERSTANDING,
    MissionState.CHECKING_ELIGIBILITY,
    MissionState.COLLECTING_DOCUMENTS,
    MissionState.PREPARING,
    MissionState.WAITING_FOR_APPROVAL,
    MissionState.EXECUTING,
    MissionState.VERIFYING,
    MissionState.MONITORING,
    MissionState.COMPLETED,
]


def can_transition(from_state: MissionState, to_state: MissionState) -> bool:
    """Return True if the transition from_state → to_state is valid."""
    return to_state in VALID_TRANSITIONS.get(from_state, [])


def progress_percentage(state: MissionState) -> int:
    """Return a 0–100 progress percentage based on position in the happy path."""
    try:
        idx = HAPPY_PATH_SEQUENCE.index(state)
        return round((idx / (len(HAPPY_PATH_SEQUENCE) - 1)) * 100)
    except ValueError:
        return 0
