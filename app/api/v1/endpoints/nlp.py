"""
Natural Language Processing endpoints for parent queries
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.services.llm_parser import llm_parser as nlp_parser
# Removed parallel_ai_client import - now using database queries only
from app.api.v1.endpoints.events import search_events
from app.core.database import get_db
from app.config.parallel_ai_queries import ParallelAIQueries, QueryConfig
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ParentQueryRequest(BaseModel):
    """Request model for parent natural language queries"""
    query: str
    user_id: Optional[str] = None


class ParentQueryResponse(BaseModel):
    """Response model for parsed parent queries"""
    original_query: str
    parsed_params: Dict
    confidence: float
    missing_info: List[str]
    suggestions: List[str]
    needs_clarification: bool
    events: Optional[List[Dict]] = None


@router.post("/parse", response_model=ParentQueryResponse)
async def parse_parent_query(request: ParentQueryRequest):
    """
    Parse a natural language query from a parent and return structured search parameters
    
    Example queries:
    - "Basketball classes for 8-10 near me this Saturday"
    - "Free art activities for my 5 year old this weekend"
    - "Indoor activities near 48083 for toddlers"
    - "Swimming lessons for kids aged 6-8"
    """
    
    try:
        # Parse the natural language query
        parse_result = await nlp_parser.parse_query(request.query)
        
        # If we have enough information and high confidence, search for events
        events = None
        if parse_result["confidence"] >= 0.7 and len(parse_result["missing_info"]) <= 1:
            try:
                # Convert parsed parameters to search format
                search_params = parse_result["parsed_params"]
                
                # Extract ZIP code from location if available
                if "location" in search_params and "zip_code" not in search_params:
                    # Try to get ZIP code from location (this would typically use a geocoding service)
                    # For now, we'll use a default or ask for clarification
                    pass
                
                # If we have a ZIP code, perform the search
                if "zip_code" in search_params:
                    # This would call the actual search function
                    # For now, we'll return the parsed parameters
                    pass
                    
            except Exception as e:
                logger.error(f"Error searching events: {e}")
        
        return ParentQueryResponse(
            original_query=parse_result["original_query"],
            parsed_params=parse_result["parsed_params"],
            confidence=parse_result["confidence"],
            missing_info=parse_result["missing_info"],
            suggestions=parse_result["suggestions"],
            needs_clarification=parse_result["needs_clarification"],
            events=events
        )
        
    except Exception as e:
        logger.error(f"Error parsing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing query: {str(e)}")


@router.post("/parse-and-search", response_model=ParentQueryResponse)
async def parse_and_search(
    request: ParentQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Parse a natural language query and search the local database for matching events
    
    This endpoint combines parsing and database searching in one call for better UX.
    It queries the local database instead of making realtime Parallel AI API calls.
    """
    
    try:
        # Parse the natural language query
        parse_result = await nlp_parser.parse_query(request.query)
        
        # If we have enough information, search for events
        events = None
        if parse_result["confidence"] >= 0.6:  # Lower threshold for combined endpoint
            try:
                # Convert parsed parameters to search format
                search_params = parse_result["parsed_params"]
                
                # Always use all Troy zip codes when user mentions Troy or any Troy zip code
                troy_zip_codes = ["48007", "48083", "48084", "48085", "48098", "48099"]
                
                # Check if user mentioned Troy or any Troy zip code
                should_search_troy = False
                if "location" in search_params and "troy" in search_params["location"].lower():
                    should_search_troy = True
                elif "zip_code" in search_params and search_params["zip_code"] in troy_zip_codes:
                    should_search_troy = True
                
                if should_search_troy:
                    # Use all Troy zip codes for comprehensive search
                    search_params["zip_codes"] = troy_zip_codes
                    if "zip_code" in search_params:
                        del search_params["zip_code"]  # Remove single zip code
                    parse_result["suggestions"].append("Searching across all Troy, MI zip codes for comprehensive results.")
                elif "zip_code" not in search_params:
                    parse_result["missing_info"].append("zip_code")
                    parse_result["suggestions"].append("What ZIP code would you like to search in?")
                
                # Use the events/query API internally
                logger.info(f"About to search with params: {search_params}")
                
                # Import the events/query function
                from app.api.v1.endpoints.events import query_events
                
                # Convert parsed parameters to events/query format
                query_params = {}
                
                # Handle location - prefer city over zip_code for events/query
                if "location" in search_params and "troy" in search_params["location"].lower():
                    query_params["city"] = "Troy"
                elif "zip_code" in search_params:
                    query_params["zip_code"] = search_params["zip_code"]
                elif "zip_codes" in search_params and search_params["zip_codes"]:
                    # If multiple zip codes, use the first one or default to Troy
                    troy_zip_codes = ["48007", "48083", "48084", "48085", "48098", "48099"]
                    if any(zip_code in troy_zip_codes for zip_code in search_params["zip_codes"]):
                        query_params["city"] = "Troy"
                    else:
                        query_params["zip_code"] = search_params["zip_codes"][0]
                
                # Add other parameters
                if "category" in search_params:
                    query_params["category"] = search_params["category"]
                if "age_min" in search_params:
                    query_params["age_min"] = search_params["age_min"]
                if "age_max" in search_params:
                    query_params["age_max"] = search_params["age_max"]
                if "is_indoor" in search_params:
                    query_params["is_indoor"] = search_params["is_indoor"]
                if "is_free" in search_params:
                    query_params["is_free"] = search_params["is_free"]
                
                query_params["limit"] = 50  # Increased limit for comprehensive search
                
                logger.info(f"Calling events/query with params: {query_params}")
                
                # Call the internal events query function
                from app.api.v1.endpoints.events import _query_events_internal
                
                # Extract parameters, ensuring None for missing values
                city = query_params.get("city")
                zip_code = query_params.get("zip_code")
                category = query_params.get("category")
                age_min = query_params.get("age_min")
                age_max = query_params.get("age_max")
                is_indoor = query_params.get("is_indoor") if "is_indoor" in query_params else None
                is_free = query_params.get("is_free") if "is_free" in query_params else None
                limit = query_params.get("limit", 50)
                
                # Call the internal function with proper parameters
                search_result = await _query_events_internal(
                    city=city,
                    zip_code=zip_code,
                    category=category,
                    age_min=age_min,
                    age_max=age_max,
                    is_indoor=is_indoor,
                    is_free=is_free,
                    limit=limit,
                    db=db
                )
                
                logger.info(f"Events/query result: {len(search_result.events)} events found")
                events = search_result.dict()["events"]
                
            except Exception as e:
                logger.error(f"Error searching events: {e}")
                parse_result["suggestions"].append("I had trouble searching for events. Please try rephrasing your request.")
        
        return ParentQueryResponse(
            original_query=parse_result["original_query"],
            parsed_params=parse_result["parsed_params"],
            confidence=parse_result["confidence"],
            missing_info=parse_result["missing_info"],
            suggestions=parse_result["suggestions"],
            needs_clarification=parse_result["needs_clarification"],
            events=events
        )
        
    except Exception as e:
        logger.error(f"Error parsing and searching: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/examples")
async def get_query_examples():
    """
    Get example natural language queries that parents can use
    """
    
    examples = [
        {
            "query": "Basketball classes for 8-10 near me this Saturday",
            "description": "Search for basketball classes for specific age range, location, and day"
        },
        {
            "query": "Free art activities for my 5 year old this weekend",
            "description": "Find free art activities for a specific age on weekends"
        },
        {
            "query": "Indoor activities near 48083 for toddlers",
            "description": "Search for indoor activities in a specific ZIP code for young children"
        },
        {
            "query": "Swimming lessons for kids aged 6-8",
            "description": "Find swimming lessons for a specific age range"
        },
        {
            "query": "Music classes this Tuesday near me",
            "description": "Search for music classes on a specific day and location"
        },
        {
            "query": "Outdoor family activities this Sunday",
            "description": "Find outdoor activities for the whole family on Sunday"
        },
        {
            "query": "Free playground activities near me",
            "description": "Find free playground activities in your area"
        },
        {
            "query": "Dance classes for 12-15 year olds",
            "description": "Search for dance classes for teenagers"
        }
    ]
    
    return {
        "examples": examples,
        "tips": [
            "Include age ranges (e.g., '8-10', 'for my 5 year old')",
            "Specify location (e.g., 'near me', 'in my city', ZIP code)",
            "Mention timing (e.g., 'this Saturday', 'this weekend', 'tomorrow')",
            "Add preferences (e.g., 'indoor', 'outdoor', 'free', 'paid')",
            "Be specific about activity type (e.g., 'basketball', 'art', 'music')"
        ]
    }


@router.post("/suggest-follow-up")
async def suggest_follow_up_questions(request: ParentQueryRequest):
    """
    Get intelligent follow-up questions based on the parsed query
    """
    
    try:
        parse_result = await nlp_parser.parse_query(request.query)
        
        # Generate contextual follow-up questions
        follow_up_questions = []
        
        if "category" in parse_result["parsed_params"]:
            category = parse_result["parsed_params"]["category"]
            
            if category == "sports":
                follow_up_questions.extend([
                    "Do you prefer indoor or outdoor sports?",
                    "Are you looking for group classes or individual lessons?",
                    "What's your budget range for sports activities?"
                ])
            elif category == "arts":
                follow_up_questions.extend([
                    "Are you interested in visual arts, performing arts, or both?",
                    "Do you prefer structured classes or open studio time?",
                    "Are you looking for beginner-friendly activities?"
                ])
            elif category == "education":
                follow_up_questions.extend([
                    "Are you looking for academic support or enrichment activities?",
                    "Do you prefer hands-on learning or traditional classroom settings?",
                    "Are you interested in STEM, language arts, or general learning?"
                ])
        
        if "age_min" in parse_result["parsed_params"] and "age_max" in parse_result["parsed_params"]:
            age_min = parse_result["parsed_params"]["age_min"]
            age_max = parse_result["parsed_params"]["age_max"]
            
            if age_max - age_min <= 2:
                follow_up_questions.append("Would you like activities specifically designed for this age group?")
            else:
                follow_up_questions.append("Would you like activities that can accommodate the full age range?")
        
        if "zip_code" not in parse_result["parsed_params"]:
            follow_up_questions.append("What ZIP code would you like to search in?")
        
        if "start_date" not in parse_result["parsed_params"]:
            follow_up_questions.extend([
                "When would you like to do this activity?",
                "Are you looking for one-time events or ongoing classes?",
                "Do you prefer weekday or weekend activities?"
            ])
        
        return {
            "original_query": request.query,
            "follow_up_questions": follow_up_questions,
            "missing_info": parse_result["missing_info"],
            "suggestions": parse_result["suggestions"]
        }
        
    except Exception as e:
        logger.error(f"Error generating follow-up questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating follow-up questions: {str(e)}")


class ParallelAITestRequest(BaseModel):
    """Request model for testing database search"""
    query: str
    location: Optional[str] = None
    test_type: str = "database_search"  # "database_search"


class ParallelAITestResponse(BaseModel):
    """Response model for Parallel AI test results"""
    query: str
    location: Optional[str]
    test_type: str
    findall_spec: Optional[Dict] = None
    findall_results: Optional[List[Dict]] = None
    search_results: Optional[List[Dict]] = None
    total_found: Optional[int] = None
    search_filters: Optional[Dict] = None
    error: Optional[str] = None


@router.post("/test-database-search", response_model=ParallelAITestResponse)
async def test_database_search(
    request: ParallelAITestRequest,
    db: Session = Depends(get_db)
):
    """
    Test database search functionality instead of Parallel AI
    
    This endpoint searches the local database for activities matching the query
    """
    
    try:
        response_data = {
            "query": request.query,
            "location": request.location,
            "test_type": "database_search"
        }
        
        # Parse the query to extract search parameters
        parse_result = await nlp_parser.parse_query(request.query)
        search_params = parse_result["parsed_params"]
        
        # Convert to search filters for database query
        search_filters = {
            "category": search_params.get("category"),
            "age_min": search_params.get("age_min"),
            "age_max": search_params.get("age_max"),
            "is_free": search_params.get("is_free"),
            "price_max": search_params.get("price_max"),
            "is_indoor": search_params.get("is_indoor"),
            "max_distance_miles": 25,
            "limit": 20
        }
        
        # Handle location - use Troy zip codes if location mentions Troy
        troy_zip_codes = ["48007", "48083", "48084", "48085", "48098", "48099"]
        
        if "location" in search_params and search_params["location"] and "troy" in search_params["location"].lower():
            search_filters["zip_codes"] = troy_zip_codes
        elif "zip_code" in search_params and search_params["zip_code"] in troy_zip_codes:
            search_filters["zip_codes"] = troy_zip_codes
        elif "zip_code" in search_params:
            search_filters["zip_code"] = search_params["zip_code"]
        else:
            # Default to Troy if no location specified
            search_filters["zip_codes"] = troy_zip_codes
        
        # Remove None values
        search_filters = {k: v for k, v in search_filters.items() if v is not None}
        
        # Search the database
        from app.api.v1.endpoints.events import search_events
        
        search_result = await search_events(
            zip_code=search_filters.get("zip_code"),
            zip_codes=search_filters.get("zip_codes"),
            start_date=search_filters.get("start_date"),
            end_date=search_filters.get("end_date"),
            category=search_filters.get("category"),
            age_min=search_filters.get("age_min"),
            age_max=search_filters.get("age_max"),
            is_indoor=search_filters.get("is_indoor"),
            is_free=search_filters.get("is_free"),
            price_max=search_filters.get("price_max"),
            max_distance_miles=search_filters.get("max_distance_miles", 25),
            limit=search_filters.get("limit", 20),
            user_id=None,
            db=db
        )
        
        response_data["search_results"] = search_result.dict()["events"]
        response_data["total_found"] = len(search_result.dict()["events"])
        response_data["search_filters"] = search_filters
        
        return ParallelAITestResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error testing database search: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing database search: {str(e)}")


@router.get("/query-examples")
async def get_query_examples():
    """
    Get externalized query examples from configuration
    """
    try:
        return {
            "natural_language_examples": ParallelAIQueries.NATURAL_LANGUAGE_EXAMPLES,
            "query_templates": {
                "family_activities": {
                    "template": ParallelAIQueries.FAMILY_ACTIVITIES.template,
                    "description": ParallelAIQueries.FAMILY_ACTIVITIES.description,
                    "example": ParallelAIQueries.FAMILY_ACTIVITIES.example
                },
                "kids_activities": {
                    "template": ParallelAIQueries.KIDS_ACTIVITIES_NEAR.template,
                    "description": ParallelAIQueries.KIDS_ACTIVITIES_NEAR.description,
                    "example": ParallelAIQueries.KIDS_ACTIVITIES_NEAR.example
                },
                "specific_activity": {
                    "template": ParallelAIQueries.SPECIFIC_ACTIVITY.template,
                    "description": ParallelAIQueries.SPECIFIC_ACTIVITY.description,
                    "example": ParallelAIQueries.SPECIFIC_ACTIVITY.example
                }
            },
            "query_categories": ParallelAIQueries.QUERY_CATEGORIES,
            "configuration": {
                "query_limits": QueryConfig.QUERY_LIMITS,
                "timeouts": QueryConfig.TIMEOUTS,
                "default_params": QueryConfig.DEFAULT_PARAMS
            }
        }
    except Exception as e:
        logger.error(f"Error getting query examples: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting query examples: {str(e)}")
