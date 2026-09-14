"""Raahi AI — API routes package."""
from .opportunities import router as opportunities_router
from .missions import router as missions_router
from .documents import router as documents_router
from .applications import router as applications_router
from .notifications import router as notifications_router
from .agent import router as agent_router

ALL_ROUTERS = [
    opportunities_router,
    missions_router,
    documents_router,
    applications_router,
    notifications_router,
    agent_router,
]

__all__ = ["ALL_ROUTERS"]
