"""
Unified event API endpoints for all data sources
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.unified_event import (
    UnifiedEvent, EventSource, EventType, AgeCategory, EventSyncLog
)
from app.services.unified_sync_service import unified_sync_service
from app.schemas.unified_event import (
    UnifiedEventResponse, EventSearchRequest, EventSearchResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/search", response_model=EventSearchResponse)
async def search_unified_events(
    zip_code: Optional[str] = Query(None, description="ZIP code to search near"),
    city: Optional[str] = Query(None, description="City to search in"),
    state: Optional[str] = Query(None, description="State to search in"),
    radius_miles: Optional[int] = Query(25, description="Search radius in miles", ge=1, le=100),
    categories: Optional[List[str]] = Query(None, description="Event categories"),
    age_min: Optional[int] = Query(None, description="Minimum age", ge=0, le=18),
    age_max: Optional[int] = Query(None, description="Maximum age", ge=0, le=18),
    is_free: Optional[bool] = Query(None, description="Free events only"),
    is_indoor: Optional[bool] = Query(None, description="Indoor events only"),
    event_type: Optional[EventType] = Query(None, description="Type of event"),
    sources: Optional[List[EventSource]] = Query(None, description="Data sources to include"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: Optional[int] = Query(20, description="Number of results", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search unified events from all sources"""
    
    try:
        # Build base query
        query = db.query(UnifiedEvent).filter(UnifiedEvent.is_active == True)
        
        # Location filtering
        if zip_code:
            # For exact zip code match, also search nearby zip codes
            nearby_zips = await _get_nearby_zip_codes(zip_code, radius_miles or 25)
            query = query.filter(
                or_(
                    UnifiedEvent.zip_code == zip_code,
                    UnifiedEvent.zip_code.in_(nearby_zips)
                )
            )
        elif city:
            query = query.filter(
                or_(
                    func.lower(UnifiedEvent.city).like(f"%{city.lower()}%"),
                    func.lower(UnifiedEvent.location_name).like(f"%{city.lower()}%")
                )
            )
        elif state:
            query = query.filter(func.lower(UnifiedEvent.state).like(f"%{state.lower()}%"))
        
        # Category filtering
        if categories:
            category_conditions = []
            for category in categories:
                category_conditions.append(
                    or_(
                        func.lower(UnifiedEvent.primary_category).like(f"%{category.lower()}%"),
                        UnifiedEvent.secondary_categories.contains([category]),
                        UnifiedEvent.tags.contains([category])
                    )
                )
            query = query.filter(or_(*category_conditions))
        
        # Age filtering
        if age_min is not None or age_max is not None:
            age_conditions = []
            
            # Include events with no age range (assume all ages)
            age_conditions.append(
                (UnifiedEvent.age_range_min.is_(None)) & (UnifiedEvent.age_range_max.is_(None))
            )
            
            # Include events that overlap with requested range
            if age_min is not None and age_max is not None:
                age_conditions.append(
                    (UnifiedEvent.age_range_min.isnot(None)) & (UnifiedEvent.age_range_max.isnot(None)) &
                    (UnifiedEvent.age_range_min <= age_max) & (UnifiedEvent.age_range_max >= age_min)
                )
            elif age_min is not None:
                age_conditions.append(
                    (UnifiedEvent.age_range_min.isnot(None)) & 
                    ((UnifiedEvent.age_range_max.is_(None)) | (UnifiedEvent.age_range_max >= age_min))
                )
            elif age_max is not None:
                age_conditions.append(
                    (UnifiedEvent.age_range_max.isnot(None)) & 
                    ((UnifiedEvent.age_range_min.is_(None)) | (UnifiedEvent.age_range_min <= age_max))
                )
            
            query = query.filter(or_(*age_conditions))
        
        # Boolean filters
        if is_free is not None:
            query = query.filter(UnifiedEvent.is_free == is_free)
        
        if is_indoor is not None:
            if is_indoor:
                query = query.filter(UnifiedEvent.is_indoor == True)
            else:
                query = query.filter(UnifiedEvent.is_outdoor == True)
        
        if event_type is not None:
            query = query.filter(UnifiedEvent.event_type == event_type)
        
        # Source filtering
        if sources:
            query = query.filter(UnifiedEvent.source.in_(sources))
        
        # Date filtering
        if start_date:
            query = query.filter(
                or_(
                    UnifiedEvent.start_time >= start_date,
                    UnifiedEvent.start_date >= start_date
                )
            )
        
        if end_date:
            query = query.filter(
                or_(
                    UnifiedEvent.start_time <= end_date,
                    UnifiedEvent.start_date <= end_date
                )
            )
        
        # Order by relevance and date
        query = query.order_by(
            desc(UnifiedEvent.priority_score),
            desc(UnifiedEvent.data_quality_score),
            UnifiedEvent.start_time.asc(),
            UnifiedEvent.title.asc()
        )
        
        # Apply limit
        events = query.limit(limit).all()
        
        # Convert to response format
        event_responses = [UnifiedEventResponse.from_orm(event) for event in events]
        
        # Build search summary
        search_summary = _build_search_summary(
            events, categories, age_min, age_max, is_free, sources
        )
        
        return EventSearchResponse(
            events=event_responses,
            total_count=len(event_responses),
            search_summary=search_summary,
            filters_applied={
                "zip_code": zip_code,
                "city": city,
                "state": state,
                "radius_miles": radius_miles,
                "categories": categories,
                "age_min": age_min,
                "age_max": age_max,
                "is_free": is_free,
                "is_indoor": is_indoor,
                "event_type": event_type.value if event_type else None,
                "sources": [s.value for s in sources] if sources else None,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Error searching unified events: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/sources")
async def get_available_sources():
    """Get list of available data sources"""
    return {
        "sources": [
            {
                "name": source.value,
                "display_name": source.value.replace("_", " ").title(),
                "description": _get_source_description(source)
            }
            for source in EventSource
        ]
    }


@router.get("/categories")
async def get_event_categories():
    """Get standardized event categories"""
    return {
        "categories": [
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
            "recreation",
            "fitness",
            "swimming",
            "martial_arts",
            "dance",
            "gymnastics",
            "soccer",
            "basketball",
            "tennis",
            "science",
            "technology",
            "cooking",
            "art",
            "crafts",
            "music_lessons",
            "language",
            "tutoring",
            "summer_camp",
            "after_school",
            "community",
            "volunteer",
            "free",
            "low_cost"
        ]
    }


@router.post("/sync/trigger")
async def trigger_unified_sync(
    background_tasks: BackgroundTasks,
    zip_codes: Optional[List[str]] = None,
    sources: Optional[List[EventSource]] = None
):
    """Manually trigger sync from all or specific sources"""
    
    try:
        # Add sync task to background
        background_tasks.add_task(
            _run_sync_task,
            zip_codes=zip_codes,
            sources=sources
        )
        
        return {
            "message": "Sync triggered successfully",
            "status": "started",
            "zip_codes": zip_codes,
            "sources": [s.value for s in sources] if sources else "all"
        }
        
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        raise HTTPException(status_code=500, detail=f"Sync trigger failed: {str(e)}")


@router.get("/sync/status")
async def get_sync_status(db: Session = Depends(get_db)):
    """Get recent sync status"""
    
    try:
        # Get last 5 sync logs
        recent_syncs = db.query(EventSyncLog).order_by(
            desc(EventSyncLog.started_at)
        ).limit(5).all()
        
        sync_status = []
        for sync in recent_syncs:
            sync_status.append({
                "source": sync.source.value if sync.source else "all",
                "sync_type": sync.sync_type,
                "status": sync.status,
                "events_processed": sync.events_processed,
                "events_created": sync.events_created,
                "events_updated": sync.events_updated,
                "started_at": sync.started_at.isoformat(),
                "completed_at": sync.completed_at.isoformat() if sync.completed_at else None,
                "duration_seconds": sync.sync_duration_seconds,
                "errors": sync.errors
            })
        
        return {
            "recent_syncs": sync_status,
            "last_sync": sync_status[0] if sync_status else None
        }
        
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")


@router.get("/{event_id}", response_model=UnifiedEventResponse)
async def get_unified_event(event_id: str, db: Session = Depends(get_db)):
    """Get a specific unified event by ID"""
    
    try:
        event = db.query(UnifiedEvent).filter(
            UnifiedEvent.id == event_id,
            UnifiedEvent.is_active == True
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Increment view count
        event.view_count += 1
        db.commit()
        
        return UnifiedEventResponse.from_orm(event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get event: {str(e)}")


# Helper functions

async def _get_nearby_zip_codes(zip_code: str, radius_miles: int) -> List[str]:
    """Get nearby zip codes within radius (simplified implementation)"""
    # This would typically use a zip code database or API
    # For now, return common nearby zip codes
    troy_zips = ["48007", "48083", "48084", "48085", "48098", "48099"]
    ann_arbor_zips = ["48103", "48104", "48105", "48108", "48109"]
    
    if zip_code in troy_zips:
        return troy_zips
    elif zip_code in ann_arbor_zips:
        return ann_arbor_zips
    else:
        return [zip_code]


def _get_source_description(source: EventSource) -> str:
    """Get description for data source"""
    descriptions = {
        EventSource.EVENTBRITE: "Events and classes from Eventbrite",
        EventSource.YELP: "Family-friendly businesses from Yelp",
        EventSource.GOOGLE_PLACES: "Parks, museums, and venues from Google Places",
        EventSource.TICKETMASTER: "Family shows and entertainment from Ticketmaster",
        EventSource.MEETUP: "Community events and groups from Meetup",
        EventSource.RECREATION_GOV: "National park programs and recreation facilities",
        EventSource.YMCA: "YMCA programs and activities",
        EventSource.BOYS_GIRLS_CLUB: "Boys & Girls Clubs activities",
        EventSource.OPENSTREETMAP: "Public playgrounds and parks from OpenStreetMap",
        EventSource.COMMUNITY: "Community-submitted events"
    }
    return descriptions.get(source, "Event data source")


def _build_search_summary(
    events: List[UnifiedEvent],
    categories: Optional[List[str]],
    age_min: Optional[int],
    age_max: Optional[int],
    is_free: Optional[bool],
    sources: Optional[List[EventSource]]
) -> str:
    """Build human-readable search summary"""
    
    total_events = len(events)
    free_events = sum(1 for e in events if e.is_free)
    
    summary_parts = [f"Found {total_events} events"]
    
    if categories:
        summary_parts.append(f"in {', '.join(categories)}")
    
    if age_min or age_max:
        age_range = f"ages {age_min or '0'}-{age_max or '18'}"
        summary_parts.append(f"for {age_range}")
    
    if is_free:
        summary_parts.append(f"({free_events} free events)")
    
    if sources:
        source_names = [s.value.replace('_', ' ').title() for s in sources]
        summary_parts.append(f"from {', '.join(source_names)}")
    
    return " ".join(summary_parts)


async def _run_sync_task(zip_codes: Optional[List[str]] = None, sources: Optional[List[EventSource]] = None):
    """Background task to run sync"""
    from app.core.database import get_db
    
    try:
        db = next(get_db())
        result = await unified_sync_service.sync_all_sources(db, zip_codes)
        logger.info(f"Background sync completed: {result}")
    except Exception as e:
        logger.error(f"Background sync failed: {e}")
    finally:
        db.close()
