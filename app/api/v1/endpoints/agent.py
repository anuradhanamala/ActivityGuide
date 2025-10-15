"""
AI Agent Control API

Endpoints to interact with and control the Smart Orchestration Agent
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import logging

from app.agents import smart_agent

logger = logging.getLogger(__name__)
router = APIRouter()

# Track if agent is running
agent_running = False


class AgentRequest(BaseModel):
    """Request model for agent commands"""
    request: str = Field(..., description="Natural language request for the agent")
    example: str = Field(default="Check and sync Troy, Detroit, and Warren")


class AgentResponse(BaseModel):
    """Response from agent"""
    success: bool
    message: str
    agent_response: Optional[str] = None


# ============================================================================
# AGENT CONTROL ENDPOINTS
# ============================================================================

@router.get("/")
async def agent_info():
    """
    🤖 AI Agent Information
    
    Get information about the Smart Orchestration Agent
    """
    return {
        "name": "Smart Orchestration Agent",
        "description": "Autonomous AI agent powered by LangChain",
        "status": "running" if agent_running else "stopped",
        "capabilities": [
            "🔄 Auto-sync cities based on intelligent decisions",
            "🧠 Create embeddings automatically",
            "🎯 Optimize search thresholds contextually",
            "📊 Monitor data quality",
            "🌎 Works across any city in USA",
            "🤖 Fully autonomous operation"
        ],
        "available_tools": [
            "check_city_data_freshness",
            "sync_city_data",
            "create_embeddings_for_city",
            "analyze_search_quality",
            "get_popular_cities_usa",
            "optimize_search_threshold"
        ],
        "endpoints": {
            "info": "GET /agent/",
            "start": "POST /agent/start",
            "stop": "POST /agent/stop",
            "request": "POST /agent/request",
            "cycle": "POST /agent/run-cycle"
        }
    }


@router.post("/start")
async def start_agent(
    background_tasks: BackgroundTasks,
    interval_minutes: int = 60
):
    """
    🚀 Start the autonomous agent
    
    Agent will run continuously, checking and optimizing the system.
    
    Args:
        interval_minutes: How often the agent should run its cycle (default: 60)
    """
    global agent_running
    
    if agent_running:
        return {
            "success": False,
            "message": "Agent is already running"
        }
    
    agent_running = True
    
    # Start agent in background
    background_tasks.add_task(
        smart_agent.run_forever,
        interval_minutes
    )
    
    logger.info(f"🤖 Agent started with {interval_minutes} minute interval")
    
    return {
        "success": True,
        "message": f"Smart Orchestration Agent started (interval: {interval_minutes} minutes)",
        "status": "running",
        "interval_minutes": interval_minutes
    }


@router.post("/stop")
async def stop_agent():
    """
    🛑 Stop the autonomous agent
    """
    global agent_running
    
    if not agent_running:
        return {
            "success": False,
            "message": "Agent is not running"
        }
    
    agent_running = False
    logger.info("🤖 Agent stopped")
    
    return {
        "success": True,
        "message": "Agent stopped successfully",
        "status": "stopped"
    }


@router.post("/run-cycle")
async def run_single_cycle(background_tasks: BackgroundTasks):
    """
    🔄 Run a single autonomous cycle
    
    Agent will check system state and take appropriate actions once.
    """
    logger.info("🤖 Running single agent cycle")
    
    # Run cycle in background
    background_tasks.add_task(smart_agent.run_autonomous_cycle)
    
    return {
        "success": True,
        "message": "Agent cycle started",
        "note": "Check logs to see agent decisions and actions"
    }


@router.post("/request", response_model=AgentResponse)
async def make_agent_request(request: AgentRequest):
    """
    💬 Make a specific request to the agent
    
    Send natural language requests to the agent and get responses.
    
    Examples:
    - "Check data freshness for Troy, Detroit, and Warren"
    - "Sync all Michigan cities"
    - "Create embeddings for New York"
    - "Analyze search quality for Los Angeles"
    """
    try:
        logger.info(f"🤖 Agent request: {request.request}")
        
        # Send request to agent
        response = await smart_agent.handle_user_request(request.request)
        
        return AgentResponse(
            success=True,
            message="Request processed by agent",
            agent_response=response
        )
        
    except Exception as e:
        logger.error(f"❌ Agent request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRESET AGENT COMMANDS
# ============================================================================

@router.post("/commands/sync-michigan")
async def sync_michigan_cities():
    """
    🏙️ Smart sync for all Michigan cities
    
    Agent will check and sync Michigan cities that need updates.
    """
    request = """Check these Michigan cities and sync those that need it:
    - Troy
    - Detroit
    - Warren
    - Sterling Heights
    - Novi
    - Ann Arbor
    
    For each city that needs sync:
    1. Sync the data
    2. Create embeddings
    3. Report results"""
    
    response = await smart_agent.handle_user_request(request)
    
    return {
        "success": True,
        "command": "Sync Michigan Cities",
        "agent_response": response
    }


@router.post("/commands/sync-major-cities")
async def sync_major_us_cities():
    """
    🌎 Smart sync for major US cities
    
    Agent will check and sync major cities across the USA.
    """
    request = """Check these major US cities and sync those that need it:
    - New York, NY
    - Los Angeles, CA
    - Chicago, IL
    - Houston, TX
    - Phoenix, AZ
    - Philadelphia, PA
    - San Antonio, TX
    - San Diego, CA
    - Dallas, TX
    - San Jose, CA
    
    Prioritize cities with no data or very old data."""
    
    response = await smart_agent.handle_user_request(request)
    
    return {
        "success": True,
        "command": "Sync Major US Cities",
        "agent_response": response
    }


@router.post("/commands/quality-audit")
async def run_quality_audit():
    """
    📊 Run data quality audit
    
    Agent will analyze data quality across multiple cities.
    """
    request = """Perform a comprehensive data quality audit:
    
    1. Check quality for at least 10 cities
    2. Identify cities with low quality data
    3. For cities with quality < 0.5, trigger a re-sync
    4. Provide a summary report"""
    
    response = await smart_agent.handle_user_request(request)
    
    return {
        "success": True,
        "command": "Quality Audit",
        "agent_response": response
    }


@router.post("/commands/create-embeddings")
async def create_embeddings_all():
    """
    🧠 Create embeddings for all cities
    
    Agent will create embeddings for cities that need them.
    """
    request = """Create embeddings for cities that don't have them yet:
    
    1. Check which cities have events without embeddings
    2. Create embeddings for those cities
    3. Report how many embeddings were created per city"""
    
    response = await smart_agent.handle_user_request(request)
    
    return {
        "success": True,
        "command": "Create Embeddings",
        "agent_response": response
    }

