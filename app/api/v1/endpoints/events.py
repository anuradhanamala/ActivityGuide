"""
Event-related API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.cache import CacheManager, event_search_cache_key
from app.models.event import Event
from app.schemas.event import (
    EventSearchFilters, 
    EventSearchResponse, 
    Event as EventSchema,
    EventUpdate
)
from app.services.simple_ai import simple_personalization_agent as EventPersonalizationAgent
from app.services.api_clients import EventbriteClient, YelpClient, GooglePlacesClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI agent
ai_agent = EventPersonalizationAgent


@router.get("/search", response_model=EventSearchResponse)
async def search_events(
    zip_code: Optional[str] = Query(None, description="ZIP code to search near"),
    zip_codes: Optional[List[str]] = Query(None, description="Multiple ZIP codes to search near"),
    start_date: Optional[datetime] = Query(None, description="Start date for events"),
    end_date: Optional[datetime] = Query(None, description="End date for events"),
    category: Optional[str] = Query(None, description="Event category filter"),
    age_min: Optional[int] = Query(None, description="Minimum age", ge=0, le=18),
    age_max: Optional[int] = Query(None, description="Maximum age", ge=0, le=18),
    is_indoor: Optional[bool] = Query(None, description="Indoor/outdoor filter"),
    is_free: Optional[bool] = Query(None, description="Free events only"),
    price_max: Optional[float] = Query(None, description="Maximum price", ge=0),
    max_distance_miles: Optional[int] = Query(25, description="Max distance in miles", ge=1, le=100),
    limit: Optional[int] = Query(20, description="Number of results", ge=1, le=100),
    user_id: Optional[str] = Query(None, description="User ID for personalization"),
    db: Session = Depends(get_db)
):
    """Search for events with AI-powered personalization"""
    
    # Build search filters
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "category": category,
        "age_min": age_min,
        "age_max": age_max,
        "is_indoor": is_indoor,
        "is_free": is_free,
        "price_max": price_max,
        "max_distance_miles": max_distance_miles,
        "limit": limit
    }
    
    # Determine search location(s)
    search_locations = []
    if zip_codes:
        search_locations = zip_codes
    elif zip_code:
        search_locations = [zip_code]
    
    # Check cache first (disabled for debugging)
    # cache_key = event_search_cache_key(search_locations, filters)
    # cached_result = await CacheManager.get(cache_key)
    
    # if cached_result:
    #     logger.info(f"Cache hit for search: {search_locations}")
    #     return EventSearchResponse(**cached_result)
    
    # Build database query
    query = db.query(Event).filter(Event.is_active == True)
    
    # Apply filters
    if start_date:
        query = query.filter(Event.start_time >= start_date)
    if end_date:
        query = query.filter(Event.start_time <= end_date)
    if category:
        # More flexible category matching - include activities that might be relevant
        # even if category doesn't exactly match
        category_conditions = []
        
        # Exact category match
        category_conditions.append(Event.category.ilike(f"%{category}%"))
        
        # If looking for sports, also include family activities that might have sports
        if category.lower() in ['sports', 'sport']:
            category_conditions.append(Event.category.ilike("%family%"))
            category_conditions.append(Event.title.ilike(f"%{category}%"))
            category_conditions.append(Event.description.ilike(f"%{category}%"))
        
        # If looking for arts, also include family activities that might have arts
        elif category.lower() in ['arts', 'art']:
            category_conditions.append(Event.category.ilike("%family%"))
            category_conditions.append(Event.title.ilike(f"%{category}%"))
            category_conditions.append(Event.description.ilike(f"%{category}%"))
        
        # For other categories, also check title and description
        else:
            category_conditions.append(Event.title.ilike(f"%{category}%"))
            category_conditions.append(Event.description.ilike(f"%{category}%"))
        
        # Combine all category conditions with OR
        from sqlalchemy import or_
        query_with_category = query.filter(or_(*category_conditions))
        
        # Test if category search returns results
        test_events = query_with_category.limit(1).all()
        
        if test_events:
            # Category search found results, use it
            query = query_with_category
            logger.info(f"Category '{category}' search found results, using category filter")
        else:
            # No results for specific category, search all categories
            logger.info(f"Category '{category}' search returned no results, searching all categories")
            # Don't apply category filter - search all categories
    if age_min is not None or age_max is not None:
        # Very flexible age filtering - include activities even if age is not specified
        age_conditions = []
        
        # Always include activities with no age range specified (assume they're for all ages)
        age_conditions.append(
            (Event.age_range_min.is_(None)) & (Event.age_range_max.is_(None))
        )
        
        # Include family activities even if they have age ranges (they might be relevant)
        age_conditions.append(Event.category.ilike("%family%"))
        
        # If event has age range, check if it overlaps with requested range
        if age_min is not None and age_max is not None:
            # Requested range overlaps if: event_min <= requested_max AND event_max >= requested_min
            age_conditions.append(
                (Event.age_range_min.isnot(None)) & (Event.age_range_max.isnot(None)) &
                (Event.age_range_min <= age_max) & (Event.age_range_max >= age_min)
            )
        elif age_min is not None:
            # Only minimum age specified - include if event has no max or event_max >= age_min
            age_conditions.append(
                (Event.age_range_min.isnot(None)) & 
                ((Event.age_range_max.is_(None)) | (Event.age_range_max >= age_min))
            )
        elif age_max is not None:
            # Only maximum age specified - include if event has no min or event_min <= age_max
            age_conditions.append(
                (Event.age_range_max.isnot(None)) & 
                ((Event.age_range_min.is_(None)) | (Event.age_range_min <= age_max))
            )
        
        # Combine all conditions with OR
        from sqlalchemy import or_
        query = query.filter(or_(*age_conditions))
    if is_indoor is not None:
        query = query.filter(Event.is_indoor == is_indoor)
    if is_free is not None:
        query = query.filter(Event.is_free == is_free)
    if price_max is not None:
        query = query.filter(
            (Event.price_max.is_(None)) | (Event.price_max <= price_max)
        )
    
    # ZIP code filtering with 25-mile radius fallback
    if search_locations:
        logger.info(f"Searching for events in zip codes: {search_locations}")
        # First try exact zip code match
        exact_query = query.filter(Event.zip_code.in_(search_locations))
        events = exact_query.limit(limit).all()
        logger.info(f"Exact match found {len(events)} events")
        
        # If no results found, expand search to nearby zip codes within 25 miles
        if not events and len(search_locations) == 1:
            logger.info(f"No events found for zip code {search_locations[0]}, expanding to 25-mile radius")
            
            # Define nearby zip codes for Troy, MI area (25-mile radius)
            troy_zip_codes = ["48007", "48083", "48084", "48085", "48098", "48099"]
            
            # If searching for a Troy zip code, search all Troy zip codes
            if search_locations[0] in troy_zip_codes:
                logger.info(f"Searching Troy area zip codes: {troy_zip_codes}")
                expanded_query = query.filter(Event.zip_code.in_(troy_zip_codes))
                events = expanded_query.limit(limit).all()
                logger.info(f"Expanded search found {len(events)} events in Troy area")
            else:
                # For other zip codes, search all available zip codes in database
                all_zip_codes_query = db.query(Event.zip_code).distinct().all()
                all_zip_codes = [row[0] for row in all_zip_codes_query if row[0]]
                logger.info(f"Searching all available zip codes: {all_zip_codes}")
                if all_zip_codes:
                    expanded_query = query.filter(Event.zip_code.in_(all_zip_codes))
                    events = expanded_query.limit(limit).all()
                    logger.info(f"Expanded search found {len(events)} events in available areas")
    else:
        # No location specified, get all events
        logger.info("No location specified, getting all events")
        events = query.limit(limit).all()
        logger.info(f"Found {len(events)} events")
    
    # Order by start time
    events = sorted(events, key=lambda x: x.start_time)
    
    # Get user profile for personalization
    user_profile = None
    if user_id:
        from app.models.event import UserProfile
        user_profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if user_profile:
            user_profile = {
                "children_ages": user_profile.children_ages or [],
                "preferred_categories": user_profile.preferred_categories or [],
                "preferred_activity_types": user_profile.preferred_activity_types or []
            }
    
    # AI personalization
    try:
        result = await ai_agent.personalize_events(events, user_profile, zip_code)
    except Exception as e:
        logger.error(f"AI personalization failed: {e}")
        # Fallback to basic response without personalization
        from app.schemas.event import EventSearchResponse
        result = EventSearchResponse(
            events=events,
            total_count=len(events),
            filters_applied=filters,
            search_summary=f"Found {len(events)} events"
        )
    
    # Cache the result for 1 hour (disabled for debugging)
    # await CacheManager.set(
    #     cache_key, 
    #     result.dict(), 
    #     timedelta(hours=1)
    # )
    
    return result


async def _query_events_internal(
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    category: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    is_indoor: Optional[bool] = None,
    is_free: Optional[bool] = None,
    limit: int = 20,
    db: Session = None
):
    """
    Query events from database with smart location and category matching:
    - If zipcode is empty: look for city matches
    - If city is provided: use city itself and ignore zipcode
    - If exact category not found: search for partial string matching
    """
    
    try:
        # Build base query
        query = db.query(Event).filter(Event.is_active == True)
        
        # Location filtering logic
        if city:
            # If city is provided, use city and ignore zipcode
            logger.info(f"Searching by city: {city}")
            query = query.filter(
                or_(
                    func.lower(Event.city).like(f"%{city.lower()}%"),
                    func.lower(Event.title).like(f"%{city.lower()}%"),
                    func.lower(Event.description).like(f"%{city.lower()}%"),
                    Event.city.is_(None)  # Include events with no city if city search is broad
                )
            )
        elif zip_code:
            # If only zipcode provided, search by zipcode
            logger.info(f"Searching by zipcode: {zip_code}")
            query = query.filter(Event.zip_code == zip_code)
        else:
            # If neither provided, return all events
            logger.info("No location filter provided, returning all events")
        
        # Category filtering with partial matching only
        if category:
            logger.info(f"Searching for category: {category} (partial matching)")
            query = query.filter(
                or_(
                    func.lower(Event.category).like(f"%{category.lower()}%"),
                    func.lower(Event.title).like(f"%{category.lower()}%"),
                    func.lower(Event.description).like(f"%{category.lower()}%")
                )
            )
            partial_count = query.count()
            logger.info(f"Found {partial_count} partial category matches")
        
        # No additional filters - simplified API
        
        # Order by relevance (recent events first, then by title)
        query = query.order_by(Event.last_synced.desc(), Event.title.asc())
        
        # Apply limit
        events = query.limit(limit).all()
        
        # Convert to response format
        event_schemas = [EventSchema.from_orm(event) for event in events]
        
        logger.info(f"Query returned {len(event_schemas)} events")
        
        return EventSearchResponse(
            events=event_schemas,
            total_count=len(event_schemas),
            filters_applied={
                "city": city,
                "zip_code": zip_code if not city else None,
                "category": category,
                "limit": limit,
                "search_type": "city" if city else "zipcode" if zip_code else "all",
                "category_match_type": "partial" if category else "none",
                "location_filter": f"city={city}" if city else f"zipcode={zip_code}" if zip_code else "none"
            }
        )
        
    except Exception as e:
        logger.error(f"Query events failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/query", response_model=EventSearchResponse)
async def query_events(
    city: Optional[str] = Query(None, description="City to search in"),
    zip_code: Optional[str] = Query(None, description="ZIP code to search near (ignored if city provided)"),
    category: Optional[str] = Query(None, description="Event category (partial match)"),
    limit: Optional[int] = Query(20, description="Number of results", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Query events from database with smart location and category matching:
    - If zipcode is empty: look for city matches
    - If city is provided: use city itself and ignore zipcode
    - If exact category not found: search for partial string matching
    """
    
    try:
        # Build base query
        query = db.query(Event).filter(Event.is_active == True)
        
        # Location filtering logic
        if city:
            # If city is provided, use city and ignore zipcode
            logger.info(f"Searching by city: {city}")
            query = query.filter(
                or_(
                    func.lower(Event.city).like(f"%{city.lower()}%"),
                    Event.city.is_(None)  # Include events with no city if city search is broad
                )
            )
        elif zip_code:
            # If only zipcode provided, search by zipcode
            logger.info(f"Searching by zipcode: {zip_code}")
            query = query.filter(Event.zip_code == zip_code)
        else:
            # If neither provided, return all events
            logger.info("No location filter provided, returning all events")
        
        # Category filtering with partial matching only
        if category:
            logger.info(f"Searching for category: {category} (partial matching)")
            query = query.filter(
                or_(
                    func.lower(Event.category).like(f"%{category.lower()}%"),
                    func.lower(Event.title).like(f"%{category.lower()}%"),
                    func.lower(Event.description).like(f"%{category.lower()}%")
                )
            )
            partial_count = query.count()
            logger.info(f"Found {partial_count} partial category matches")
        
        # No additional filters - simplified API
        
        # Order by relevance (recent events first, then by title)
        query = query.order_by(Event.last_synced.desc(), Event.title.asc())
        
        # Apply limit
        events = query.limit(limit).all()
        
        # Convert to response format
        event_schemas = [EventSchema.from_orm(event) for event in events]
        
        logger.info(f"Query returned {len(event_schemas)} events")
        
        return EventSearchResponse(
            events=event_schemas,
            total_count=len(event_schemas),
            filters_applied={
                "city": city,
                "zip_code": zip_code if not city else None,
                "category": category,
                "limit": limit,
                "search_type": "city" if city else "zipcode" if zip_code else "all",
                "category_match_type": "partial" if category else "none",
                "location_filter": f"city={city}" if city else f"zipcode={zip_code}" if zip_code else "none"
            }
        )
        
    except Exception as e:
        logger.error(f"Query events failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/{event_id}", response_model=EventSchema)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event by ID"""
    
    event = db.query(Event).filter(Event.id == event_id, Event.is_active == True).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event


@router.get("/", response_model=List[EventSchema])
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List events with optional filtering and 25-mile radius fallback"""
    
    query = db.query(Event).filter(Event.is_active == True)
    
    if category:
        # Test if category search returns results
        test_query = query.filter(Event.category.ilike(f"%{category}%"))
        test_events = test_query.limit(1).all()
        
        if test_events:
            # Category search found results, use it
            query = test_query
            logger.info(f"Category '{category}' search found results, using category filter")
        else:
            # No results for specific category, search all categories
            logger.info(f"Category '{category}' search returned no results, searching all categories")
            # Don't apply category filter - search all categories
    
    if zip_code:
        # First try exact zip code match
        exact_query = query.filter(Event.zip_code == zip_code)
        events = exact_query.offset(skip).limit(limit).all()
        
        # If no results found, expand search to nearby zip codes within 25 miles
        if not events:
            logger.info(f"No events found for zip code {zip_code}, expanding to 25-mile radius")
            
            # Define nearby zip codes for Troy, MI area (25-mile radius)
            troy_zip_codes = ["48007", "48083", "48084", "48085", "48098", "48099"]
            
            # If searching for a Troy zip code, search all Troy zip codes
            if zip_code in troy_zip_codes:
                logger.info(f"Searching Troy area zip codes: {troy_zip_codes}")
                expanded_query = query.filter(Event.zip_code.in_(troy_zip_codes))
                events = expanded_query.offset(skip).limit(limit).all()
                logger.info(f"Expanded search found {len(events)} events in Troy area")
            else:
                # For other zip codes, search all available zip codes in database
                all_zip_codes_query = db.query(Event.zip_code).distinct().all()
                all_zip_codes = [row[0] for row in all_zip_codes_query if row[0]]
                logger.info(f"Searching all available zip codes: {all_zip_codes}")
                if all_zip_codes:
                    expanded_query = query.filter(Event.zip_code.in_(all_zip_codes))
                    events = expanded_query.offset(skip).limit(limit).all()
                    logger.info(f"Expanded search found {len(events)} events in available areas")
    else:
        # No zip code specified, get all events
        events = query.offset(skip).limit(limit).all()
    
    return events


@router.post("/{event_id}/update", response_model=EventSchema)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db)
):
    """Update an event (admin only)"""
    
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update fields
    for field, value in event_update.dict(exclude_unset=True).items():
        setattr(event, field, value)
    
    event.updated_at = datetime.now()
    db.commit()
    db.refresh(event)
    
    # Clear related cache entries
    await CacheManager.delete(f"event:{event_id}")
    
    return event


@router.get("/categories/list")
async def list_categories():
    """Get list of available event categories"""
    
    categories = [
        "family",
        "kids",
        "education",
        "entertainment",
        "sports",
        "arts",
        "music",
        "theater",
        "museum",
        "outdoor",
        "indoor",
        "free",
        "paid"
    ]
    
    return {"categories": categories}


@router.post("/sync/trigger")
async def trigger_sync():
    """Manually trigger event sync (admin only)"""
    
    from app.services.sync import sync_service
    
    try:
        await sync_service.sync_all_sources()
        return {"message": "Sync triggered successfully", "status": "success"}
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


