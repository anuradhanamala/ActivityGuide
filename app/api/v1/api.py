"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import events, users, providers, sync, agentic_search, agentic_sync, nlp, unified_events

api_router = APIRouter()

# Include existing endpoints
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(agentic_search.router, prefix="/agentic-search", tags=["agentic-search"])
api_router.include_router(agentic_sync.router, prefix="/agentic-sync", tags=["agentic-sync"])
api_router.include_router(nlp.router, prefix="/nlp", tags=["nlp"])

# Include new unified endpoints
api_router.include_router(unified_events.router, prefix="/unified", tags=["unified-events"])