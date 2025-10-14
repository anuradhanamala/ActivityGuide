"""
RAG (Retrieval-Augmented Generation) endpoints for AI-powered recommendations

Includes:
- Simple RAG (SQL-based)
- Vector RAG (semantic search with ChromaDB)
- Hybrid RAG (best of both)
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional, List
from app.services.simple_rag import simple_rag_service
from app.services.vector_rag import vector_rag_service
from app.services.hybrid_rag import hybrid_rag_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/recommend")
async def get_rag_recommendations(
    query: str = Query(..., description="User question or request", min_length=3),
    city: Optional[str] = Query("Troy", description="City to search in"),
    age_min: Optional[int] = Query(None, description="Minimum age", ge=0, le=18),
    age_max: Optional[int] = Query(None, description="Maximum age", ge=0, le=18),
    category: Optional[str] = Query(None, description="Activity category"),
    is_free: Optional[bool] = Query(None, description="Free activities only")
):
    """
    Get AI-powered activity recommendations using RAG
    
    This endpoint uses simple SQL retrieval (no vector search) combined with
    LLM generation to provide personalized, conversational recommendations.
    
    Examples:
        - "What activities for my shy 8-year-old?"
        - "Fun things to do this weekend"
        - "Best martial arts schools for beginners"
        - "Free outdoor activities for toddlers"
    """
    
    try:
        result = await simple_rag_service.recommend_activities(
            user_query=query,
            city=city,
            age_min=age_min,
            age_max=age_max,
            category=category,
            is_free=is_free
        )
        
        return result
        
    except Exception as e:
        logger.error(f"RAG recommendation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/compare")
async def compare_activities(
    activity_ids: list[str] = Query(..., description="Activity IDs to compare"),
    user_question: Optional[str] = Query(None, description="Specific comparison question")
):
    """
    Compare multiple activities using RAG
    
    Example:
        Compare 3 martial arts schools and explain differences
    """
    
    try:
        from app.core.database import get_db
        from app.models.unified_event import UnifiedEvent
        
        db = next(get_db())
        
        # Retrieve the specific activities
        events = db.query(UnifiedEvent).filter(
            UnifiedEvent.id.in_(activity_ids)
        ).all()
        
        if not events:
            return {"comparison": "No activities found with those IDs"}
        
        # Build comparison context
        context = ""
        for i, event in enumerate(events, 1):
            context += f"""
Activity {i}: {event.title}
- Source: {event.source.value}
- Location: {event.city}, {event.state}
- Category: {event.primary_category}
- Ages: {event.age_range_min}-{event.age_range_max}
- Price: {'FREE' if event.is_free else 'Paid'}
- Tags: {', '.join(event.tags or [])}
- Description: {event.description or 'N/A'}

"""
        
        # Generate comparison
        comparison_query = user_question or "Compare these activities and help me choose"
        
        messages = [
            SystemMessage(content="You are a helpful activity assistant. Compare activities clearly and provide a recommendation."),
            HumanMessage(content=f"""
{comparison_query}

Activities to compare:
{context}

Provide a clear comparison highlighting key differences and similarities.
End with a recommendation on which to choose based on different needs.""")
        ]
        
        if simple_rag_service.llm:
            response = await simple_rag_service.llm.ainvoke(messages)
            comparison = response.content
        else:
            comparison = "RAG service not available"
        
        db.close()
        
        return {
            "comparison": comparison,
            "activities_compared": len(events)
        }
        
    except Exception as e:
        logger.error(f"Activity comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan-day")
async def plan_activity_day(
    children_ages: list[int] = Query(..., description="Ages of children"),
    city: str = Query("Troy", description="City to plan activities in"),
    day_of_week: Optional[str] = Query(None, description="Day of week (e.g., 'Saturday')"),
    preferences: Optional[str] = Query(None, description="Any preferences or constraints")
):
    """
    Generate a full day activity plan using RAG
    
    Example:
        Plan a Saturday for kids ages 7 and 10 in Troy
    """
    
    try:
        from app.core.database import get_db
        from app.models.unified_event import UnifiedEvent
        
        db = next(get_db())
        
        # Retrieve activities for these ages
        min_age = min(children_ages)
        max_age = max(children_ages)
        
        events = db.query(UnifiedEvent).filter(
            UnifiedEvent.city.like(f"%{city}%"),
            UnifiedEvent.is_active == True,
            ((UnifiedEvent.age_range_min <= max_age) & 
             (UnifiedEvent.age_range_max >= min_age)) |
            (UnifiedEvent.age_range_min.is_(None))
        ).limit(20).all()
        
        # Build context
        context = simple_rag_service._build_context(events)
        
        # Generate day plan
        messages = [
            SystemMessage(content="You are a family activity planning assistant. Create practical, fun day itineraries."),
            HumanMessage(content=f"""
Create a fun day itinerary for children ages {', '.join(map(str, children_ages))} in {city}.
{f'Day: {day_of_week}' if day_of_week else ''}
{f'Preferences: {preferences}' if preferences else ''}

Available activities:
{context}

Create a schedule including:
1. Morning activity (9am-12pm)
2. Lunch suggestion
3. Afternoon activity (1pm-4pm)
4. Backup indoor option (if rain)
5. Estimated total cost
6. Any helpful tips

Make it practical and fun!""")
        ]
        
        if simple_rag_service.llm:
            response = await simple_rag_service.llm.ainvoke(messages)
            plan = response.content
        else:
            plan = "RAG service not available"
        
        db.close()
        
        return {
            "day_plan": plan,
            "children_ages": children_ages,
            "city": city,
            "activities_considered": len(events)
        }
        
    except Exception as e:
        logger.error(f"Day planning error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-search")
async def semantic_search_recommendations(
    query: str = Query(..., description="Semantic query (e.g., 'confidence building activities')"),
    city: Optional[str] = Query("Troy", description="City to search in"),
    age_min: Optional[int] = Query(None, description="Minimum age"),
    age_max: Optional[int] = Query(None, description="Maximum age"),
    is_free: Optional[bool] = Query(None, description="Free activities only")
):
    """
    Semantic search using vector embeddings (ChromaDB)
    
    Perfect for concept-based queries:
    - "Confidence building activities"
    - "Things for shy kids"
    - "Educational entertainment"
    - "Activities to burn energy"
    
    Finds activities by MEANING, not just keywords!
    """
    
    try:
        result = await vector_rag_service.get_recommendations(
            user_query=query,
            city=city,
            age_min=age_min,
            age_max=age_max,
            is_free=is_free
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid-recommend")
async def hybrid_recommendations(
    query: str = Query(..., description="Any type of query"),
    city: Optional[str] = Query("Troy", description="City to search in"),
    age_min: Optional[int] = Query(None, description="Minimum age"),
    age_max: Optional[int] = Query(None, description="Maximum age"),
    category: Optional[str] = Query(None, description="Category filter"),
    is_free: Optional[bool] = Query(None, description="Free activities only")
):
    """
    Hybrid RAG - Automatically chooses best method
    
    Analyzes your query and uses:
    - SQL RAG for structured queries ("8-year-old sports")
    - Vector RAG for semantic queries ("confidence building")
    
    Best of both worlds!
    """
    
    try:
        result = await hybrid_rag_service.recommend(
            user_query=query,
            city=city,
            age_min=age_min,
            age_max=age_max,
            category=category,
            is_free=is_free
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Hybrid RAG error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{event_id}")
async def find_similar_activities(
    event_id: str,
    limit: int = Query(10, description="Number of similar activities", ge=1, le=50)
):
    """
    Find activities similar to a given event
    
    Uses vector embeddings to find semantically similar activities.
    Only possible with ChromaDB!
    
    Example: User likes "Troy Historic Village"
    Returns: Similar museums, historical sites, educational venues
    """
    
    try:
        similar = await vector_rag_service.find_similar_activities(
            event_id=event_id,
            limit=limit
        )
        
        return {
            "source_event_id": event_id,
            "similar_activities": [
                {
                    "id": str(e.id),
                    "title": e.title,
                    "source": e.source.value,
                    "city": e.city,
                    "category": e.primary_category,
                    "tags": e.tags[:5] if e.tags else []
                } for e in similar
            ],
            "count": len(similar)
        }
        
    except Exception as e:
        logger.error(f"Find similar error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build-index")
async def build_vector_index(force_rebuild: bool = Query(False, description="Force rebuild of existing index")):
    """
    Build or rebuild vector embeddings index
    
    This is a one-time setup operation.
    Run this after adding new events to make them searchable.
    
    Note: Takes 1-5 minutes depending on database size
    """
    
    try:
        result = await vector_rag_service.build_vector_index(force_rebuild=force_rebuild)
        return result
        
    except Exception as e:
        logger.error(f"Index building error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index-stats")
async def get_index_statistics():
    """Get statistics about the vector index"""
    
    try:
        stats = vector_rag_service.get_index_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Index stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def rag_service_info():
    """Get information about RAG services"""
    
    sql_available = simple_rag_service.llm is not None
    vector_available = vector_rag_service.vector_store is not None
    
    vector_stats = vector_rag_service.get_index_stats() if vector_available else {}
    
    return {
        "services": {
            "sql_rag": {
                "available": sql_available,
                "model": "claude-3-haiku-20240307" if sql_available else None,
                "retrieval": "SQL queries",
                "best_for": "Structured queries (age, city, category)",
                "speed": "Fast (20-50ms)",
                "cost_per_query": "~$0.0006"
            },
            "vector_rag": {
                "available": vector_available,
                "model": "claude-3-haiku-20240307" if sql_available else None,
                "retrieval": "ChromaDB vector search",
                "embeddings": "HuggingFace all-MiniLM-L6-v2 (free, local)",
                "indexed_events": vector_stats.get("total_embeddings", 0),
                "best_for": "Semantic queries (concepts, feelings, vague terms)",
                "speed": "Medium (100-200ms)",
                "cost_per_query": "~$0.0006 (embeddings are free!)"
            },
            "hybrid_rag": {
                "available": sql_available and vector_available,
                "description": "Automatically chooses best method based on query type",
                "best_for": "All query types (recommended!)"
            }
        },
        "features": [
            "Activity recommendations",
            "Semantic search",
            "Activity comparisons",
            "Find similar activities",
            "Day planning",
            "Question answering"
        ],
        "setup_required": "Run: python build_vector_index.py" if not vector_available or vector_stats.get("total_embeddings", 0) == 0 else "Ready to use!"
    }
