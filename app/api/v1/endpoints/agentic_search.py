"""
Agentic Search API endpoints for comprehensive kids activity discovery
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.services.agentic_search import agentic_orchestrator, ActivityCategory
from app.core.database import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class AgenticSearchRequest(BaseModel):
    """Request model for agentic search"""
    city: str
    categories: Optional[List[str]] = None
    max_concurrent: Optional[int] = 10


class AgenticSearchResponse(BaseModel):
    """Response model for agentic search results"""
    city: str
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_activities: int
    categories_searched: List[str]
    results_by_category: Dict[str, List[Dict[str, Any]]]
    execution_stats: Dict[str, Any]
    failed_queries: List[Dict[str, str]]


@router.post("/search-city", response_model=AgenticSearchResponse)
async def search_city_activities(
    request: AgenticSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for kids activities in a city using agentic framework
    
    This endpoint fires multiple parallel AI searches for different activity categories:
    - Sports (basketball, soccer, swimming, tennis, gymnastics, martial arts)
    - Education (math, science, reading, writing, coding, languages)
    - Music (piano, guitar, voice, drums, violin, singing)
    - Arts (painting, drawing, sculpture, pottery, crafts, digital art)
    - Instruments (piano, guitar, violin, drums, flute, trumpet, saxophone)
    - Dance (ballet, jazz, hip hop, tap, contemporary, ballroom)
    - STEM (robotics, programming, engineering, math, science experiments)
    - Outdoor (hiking, camping, sports, nature, adventure, playground)
    - Indoor (games, puzzles, board games, video games, reading, crafts)
    """
    
    try:
        logger.info(f"Agentic search requested for {request.city} with categories: {request.categories}")
        
        # Convert string categories to enum if provided
        category_enums = None
        if request.categories:
            category_enums = []
            for cat in request.categories:
                try:
                    category_enums.append(ActivityCategory(cat.lower()))
                except ValueError:
                    logger.warning(f"Unknown category: {cat}")
        
        # Execute agentic search
        results = await agentic_orchestrator.search_city_activities(
            city=request.city,
            categories=category_enums,
            max_concurrent=request.max_concurrent
        )
        
        return AgenticSearchResponse(**results)
        
    except Exception as e:
        logger.error(f"Agentic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agentic search failed: {str(e)}")


@router.post("/search-troy", response_model=AgenticSearchResponse)
async def search_troy_activities(db: Session = Depends(get_db)):
    """
    Search for kids activities in Troy, MI using agentic framework
    
    This is a convenience endpoint that searches all activity categories in Troy, MI
    """
    
    try:
        logger.info("Agentic search requested for Troy, MI")
        
        results = await agentic_orchestrator.search_troy_activities()
        
        return AgenticSearchResponse(**results)
        
    except Exception as e:
        logger.error(f"Troy agentic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Troy search failed: {str(e)}")


@router.post("/search-categories", response_model=AgenticSearchResponse)
async def search_specific_categories(
    city: str = Query(..., description="City to search in"),
    categories: List[str] = Query(..., description="Activity categories to search"),
    max_concurrent: int = Query(10, description="Maximum concurrent searches", ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Search for specific activity categories in a city
    
    Example: /api/v1/agentic/search-categories?city=Troy%20MI&categories=sports&categories=music
    """
    
    try:
        logger.info(f"Agentic search requested for {city} with specific categories: {categories}")
        
        results = await agentic_orchestrator.search_specific_categories(city, categories)
        
        return AgenticSearchResponse(**results)
        
    except Exception as e:
        logger.error(f"Specific categories search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Categories search failed: {str(e)}")


@router.get("/categories")
async def get_available_categories():
    """Get list of available activity categories"""
    
    categories = [
        {
            "name": "sports",
            "description": "Sports activities and classes",
            "examples": ["basketball", "soccer", "swimming", "tennis", "gymnastics", "martial arts"]
        },
        {
            "name": "education",
            "description": "Educational classes and tutoring",
            "examples": ["math", "science", "reading", "writing", "coding", "languages"]
        },
        {
            "name": "music",
            "description": "Music lessons and classes",
            "examples": ["piano", "guitar", "voice", "drums", "violin", "singing"]
        },
        {
            "name": "arts",
            "description": "Arts and crafts activities",
            "examples": ["painting", "drawing", "sculpture", "pottery", "crafts", "digital art"]
        },
        {
            "name": "instruments",
            "description": "Musical instrument lessons",
            "examples": ["piano", "guitar", "violin", "drums", "flute", "trumpet", "saxophone"]
        },
        {
            "name": "dance",
            "description": "Dance classes and lessons",
            "examples": ["ballet", "jazz", "hip hop", "tap", "contemporary", "ballroom"]
        },
        {
            "name": "stem",
            "description": "STEM and technology activities",
            "examples": ["robotics", "programming", "engineering", "math", "science experiments"]
        },
        {
            "name": "outdoor",
            "description": "Outdoor activities and adventures",
            "examples": ["hiking", "camping", "sports", "nature", "adventure", "playground"]
        },
        {
            "name": "indoor",
            "description": "Indoor activities and games",
            "examples": ["games", "puzzles", "board games", "video games", "reading", "crafts"]
        }
    ]
    
    return {
        "categories": categories,
        "total_categories": len(categories),
        "usage": {
            "search_all": "POST /api/v1/agentic/search-city",
            "search_troy": "POST /api/v1/agentic/search-troy",
            "search_specific": "POST /api/v1/agentic/search-categories?city=CITY&categories=CAT1&categories=CAT2"
        }
    }


@router.get("/search-stats")
async def get_search_statistics():
    """Get statistics about agentic search capabilities"""
    
    return {
        "framework": "Agentic Parallel AI Search",
        "max_concurrent_searches": 20,
        "default_concurrent_searches": 10,
        "query_timeout": 30.0,
        "max_results_per_query": 25,
        "total_agents": len(agentic_orchestrator.search_agents),
        "agents": [
            {
                "category": agent.category.value,
                "priority": agent.priority,
                "max_results": agent.max_results,
                "timeout": agent.timeout,
                "age_ranges": agent.age_ranges
            }
            for agent in agentic_orchestrator.search_agents
        ],
        "estimated_queries_per_city": "45-90 queries (5-10 per category)",
        "estimated_execution_time": "2-5 minutes per city",
        "api_calls_per_search": "45-90 Parallel AI API calls"
    }
