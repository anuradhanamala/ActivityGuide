"""
Agentic Sync endpoints for ActivityGuide
Similar to sync endpoints but using the agentic framework
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


class AgenticSyncRequest(BaseModel):
    """Request model for agentic sync"""
    city: str
    categories: Optional[List[str]] = None
    max_concurrent: Optional[int] = 10
    save_to_database: Optional[bool] = True


class AgenticSyncResponse(BaseModel):
    """Response model for agentic sync results"""
    status: str
    message: str
    city: str
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_activities: int
    categories_searched: List[str]
    results_by_category: Dict[str, List[Dict[str, Any]]]
    execution_stats: Dict[str, Any]
    failed_queries_list: Optional[List[Dict[str, str]]] = None
    database_saved: Optional[bool] = None
    events_processed: Optional[int] = None


@router.post("/manual-agentic-sync", response_model=AgenticSyncResponse)
async def manual_agentic_sync(
    city: str = Query(..., description="City name (e.g., 'Troy MI', 'Troy, MI', 'troy mi')"),
    categories: Optional[List[str]] = Query(None, description="Activity categories to search"),
    max_concurrent: int = Query(10, description="Maximum concurrent searches", ge=1, le=20),
    save_to_database: bool = Query(True, description="Save results to database"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger agentic sync for a specific city
    
    Example: POST /api/v1/agentic-sync/manual-agentic-sync?city=Troy%20MI&categories=sports&categories=music
    """
    try:
        logger.info(f"Manual agentic sync requested for city: {city}, categories: {categories}")
        
        # Convert string categories to enum if provided
        category_enums = None
        if categories:
            category_enums = []
            for cat in categories:
                try:
                    category_enums.append(ActivityCategory(cat.lower()))
                except ValueError:
                    logger.warning(f"Unknown category: {cat}")
        
        # Execute agentic search
        results = await agentic_orchestrator.search_city_activities(
            city=city,
            categories=category_enums,
            max_concurrent=max_concurrent
        )
        
        # Save to database if requested
        events_processed = 0
        if save_to_database and results['total_activities'] > 0:
            try:
                from app.services.sync import sync_service
                # Convert agentic results to events format and save
                events_processed = await _save_agentic_results_to_database(results, db)
                logger.info(f"Saved {events_processed} events to database")
            except Exception as e:
                logger.error(f"Failed to save to database: {e}")
        
        return AgenticSyncResponse(
            status="success",
            message=f"Agentic sync completed for {city}",
            city=city,
            total_queries=results['total_queries'],
            successful_queries=results['successful_queries'],
            failed_queries=results['failed_queries'],
            total_activities=results['total_activities'],
            categories_searched=results['categories_searched'],
            results_by_category=results['results_by_category'],
            execution_stats=results['execution_stats'],
            failed_queries_list=results.get('failed_queries_details', []),
            database_saved=save_to_database,
            events_processed=events_processed
        )
        
    except Exception as e:
        logger.error(f"Manual agentic sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agentic sync failed: {str(e)}")


@router.post("/agentic-sync-city", response_model=AgenticSyncResponse)
async def agentic_sync_city(
    city: str = Query(..., description="City name (e.g., 'Troy MI', 'Troy, MI', 'troy mi')"),
    categories: Optional[List[str]] = Query(None, description="Activity categories to search"),
    max_concurrent: int = Query(10, description="Maximum concurrent searches", ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Agentic sync activities for a specific city
    
    Example: POST /api/v1/agentic-sync/agentic-sync-city?city=Troy%20MI
    """
    try:
        # Normalize city name
        city_lower = city.lower().strip()
        
        # Map city names to their zip codes for reference
        city_zip_mapping = {
            "troy": ["48007", "48083", "48084", "48085", "48098", "48099"],
            "troy mi": ["48007", "48083", "48084", "48085", "48098", "48099"],
            "troy, mi": ["48007", "48083", "48084", "48085", "48098", "48099"],
            "troy michigan": ["48007", "48083", "48084", "48085", "48098", "48099"],
            "troy, michigan": ["48007", "48083", "48084", "48085", "48098", "48099"]
        }
        
        # Find matching city
        zip_codes = None
        for city_key, zips in city_zip_mapping.items():
            if city_key in city_lower:
                zip_codes = zips
                break
        
        if not zip_codes:
            # Default to Troy if no match found
            zip_codes = ["48007", "48083", "48084", "48085", "48098", "48099"]
            logger.warning(f"City '{city}' not recognized, defaulting to Troy, MI")
        
        logger.info(f"Agentic city sync requested for '{city}' -> ZIP codes: {zip_codes}")
        
        # Convert string categories to enum if provided
        category_enums = None
        if categories:
            category_enums = []
            for cat in categories:
                try:
                    category_enums.append(ActivityCategory(cat.lower()))
                except ValueError:
                    logger.warning(f"Unknown category: {cat}")
        
        # Execute agentic search
        results = await agentic_orchestrator.search_city_activities(
            city=city,
            categories=category_enums,
            max_concurrent=max_concurrent
        )
        
        # Save to database
        events_processed = 0
        if results['total_activities'] > 0:
            try:
                events_processed = await _save_agentic_results_to_database(results, db)
                logger.info(f"Saved {events_processed} events to database")
            except Exception as e:
                logger.error(f"Failed to save to database: {e}")
        
        return AgenticSyncResponse(
            status="success",
            message=f"Agentic sync completed for {city} (comprehensive search)",
            city=city,
            total_queries=results['total_queries'],
            successful_queries=results['successful_queries'],
            failed_queries=results['failed_queries'],
            total_activities=results['total_activities'],
            categories_searched=results['categories_searched'],
            results_by_category=results['results_by_category'],
            execution_stats=results['execution_stats'],
            failed_queries_list=results.get('failed_queries_details', []),
            database_saved=True,
            events_processed=events_processed
        )
        
    except Exception as e:
        logger.error(f"Agentic city sync failed for '{city}': {e}")
        raise HTTPException(status_code=500, detail=f"Agentic city sync failed: {str(e)}")


@router.post("/agentic-sync-troy", response_model=AgenticSyncResponse)
async def agentic_sync_troy(db: Session = Depends(get_db)):
    """
    Agentic sync all Troy, MI activities (comprehensive search)
    """
    try:
        logger.info("Agentic Troy sync requested")
        
        # Execute comprehensive agentic search for Troy
        results = await agentic_orchestrator.search_troy_activities()
        
        # Save to database
        events_processed = 0
        if results['total_activities'] > 0:
            try:
                events_processed = await _save_agentic_results_to_database(results, db)
                logger.info(f"Saved {events_processed} events to database")
            except Exception as e:
                logger.error(f"Failed to save to database: {e}")
        
        return AgenticSyncResponse(
            status="success",
            message="Agentic Troy, MI sync completed (comprehensive search)",
            city="Troy, MI",
            total_queries=results['total_queries'],
            successful_queries=results['successful_queries'],
            failed_queries=results['failed_queries'],
            total_activities=results['total_activities'],
            categories_searched=results['categories_searched'],
            results_by_category=results['results_by_category'],
            execution_stats=results['execution_stats'],
            failed_queries_list=results.get('failed_queries_details', []),
            database_saved=True,
            events_processed=events_processed
        )
        
    except Exception as e:
        logger.error(f"Agentic Troy sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agentic Troy sync failed: {str(e)}")


@router.get("/agentic-sync-status")
async def agentic_sync_status():
    """
    Get current agentic sync status and available options
    """
    return {
        "status": "active",
        "framework": "Agentic Parallel AI Search",
        "available_cities": {
            "troy_mi": {
                "zip_codes": ["48007", "48083", "48084", "48085", "48098", "48099"],
                "description": "Troy, Michigan comprehensive search",
                "categories": ["sports", "education", "music", "arts", "instruments", "dance", "stem", "outdoor", "indoor"]
            }
        },
        "available_categories": [
            "sports", "education", "music", "arts", "instruments", 
            "dance", "stem", "outdoor", "indoor"
        ],
        "sync_methods": [
            "POST /api/v1/agentic-sync/agentic-sync-troy",
            "POST /api/v1/agentic-sync/agentic-sync-city?city=Troy%20MI",
            "POST /api/v1/agentic-sync/manual-agentic-sync?city=Troy%20MI&categories=sports&categories=music"
        ],
        "comparison": {
            "current_sync": "6-12 queries, sequential, 3-6 minutes",
            "agentic_sync": "45-90 queries, parallel, 2-5 minutes, comprehensive"
        }
    }


async def _save_agentic_results_to_database(results: Dict[str, Any], db: Session) -> int:
    """Save agentic search results to database"""
    from app.models.event import Event
    from datetime import datetime
    
    events_processed = 0
    
    try:
        # Get the search city from results metadata
        search_city = results.get('city', 'Troy, MI')
        
        for category, activities in results['results_by_category'].items():
            for activity_data in activities:
                # Get city from activity data, fallback to search city
                # Handle both None and empty string cases
                activity_city = activity_data.get("city")
                if not activity_city or activity_city.strip() == "":
                    activity_city = search_city
                
                # Get zip code from activity data, allow empty zip codes
                activity_zip = activity_data.get("zip_code", "")
                if not activity_zip and activity_data.get("address"):
                    # Try to extract zip code from address
                    import re
                    zip_match = re.search(r'\b(\d{5})\b', activity_data.get("address", ""))
                    if zip_match:
                        activity_zip = zip_match.group(1)
                
                # Log activity details for debugging
                logger.debug(f"Processing activity: {activity_data.get('title', 'No title')[:50]}... | City: {activity_city} | Zip: {activity_zip or 'Empty'}")
                
                # Normalize activity data to match Event model
                event_data = {
                    "title": activity_data.get("name", activity_data.get("title", "")),
                    "description": activity_data.get("description", ""),
                    "start_time": datetime.now(),
                    "end_time": None,
                    "location_name": activity_data.get("venue", activity_data.get("location_name", "")),
                    "address": activity_data.get("address", ""),
                    "city": activity_city,
                    "state": activity_data.get("state", "MI"),
                    "zip_code": activity_zip,
                    "latitude": activity_data.get("latitude"),
                    "longitude": activity_data.get("longitude"),
                    "category": activity_data.get("category", category),
                    "age_range_min": activity_data.get("min_age"),
                    "age_range_max": activity_data.get("max_age"),
                    "is_free": activity_data.get("price", 0) == 0,
                    "is_indoor": "indoor" in str(activity_data.get("venue_type", "")).lower(),
                    "source": "agentic_parallel_ai",
                    "source_id": activity_data.get("id", ""),
                    "source_url": activity_data.get("url", ""),
                    "image_url": activity_data.get("image", ""),
                    "tags": activity_data.get("tags", []),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "last_synced": datetime.now()
                }
                
                # Check if event already exists
                existing_event = db.query(Event).filter(
                    Event.source == "agentic_parallel_ai",
                    Event.source_id == event_data["source_id"]
                ).first()
                
                if existing_event:
                    # Update existing event
                    for key, value in event_data.items():
                        if hasattr(existing_event, key):
                            # Always update city field, even if it's currently empty
                            if key == "city" or value is not None:
                                setattr(existing_event, key, value)
                    existing_event.last_synced = datetime.now()
                else:
                    # Create new event
                    event = Event(**event_data)
                    db.add(event)
                
                events_processed += 1
        
        db.commit()
        logger.info(f"Successfully saved {events_processed} events to database")
        
    except Exception as e:
        logger.error(f"Database save error: {e}")
        db.rollback()
        raise e
    
    return events_processed
