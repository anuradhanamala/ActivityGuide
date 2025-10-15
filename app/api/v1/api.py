"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import users, providers, unified_events, rag, ai_orchestration, agent

api_router = APIRouter()

# Include existing endpoints
# events endpoint removed - use /unified/events instead
# sync endpoint removed - use /unified/sync/city or /ai-orchestration/multi-source/sync instead
# nlp endpoint removed - use /rag endpoints instead
# agentic-search/agentic-sync removed - use /ai-orchestration endpoints instead
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])

# Include new unified endpoints
api_router.include_router(unified_events.router, prefix="/unified", tags=["unified-events"])

# Include RAG endpoints
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])

# Include AI Orchestration API (Industry-grade MCP via API)
api_router.include_router(ai_orchestration.router, prefix="/ai-orchestration", tags=["ai-orchestration"])

# Include Smart AI Agent (LangChain-powered autonomous agent)
api_router.include_router(agent.router, prefix="/agent", tags=["ai-agent"])