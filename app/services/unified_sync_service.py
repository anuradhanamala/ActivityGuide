"""
Unified sync service for all event data sources
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.models.unified_event import (
    UnifiedEvent, EventSource, EventType, AgeCategory, EventSyncLog
)
from app.services.unified_api_clients import unified_api_manager, SearchParams
from app.services.api_clients import (
    EventbriteClient, YelpClient, GooglePlacesClient, TicketmasterClient
)

logger = logging.getLogger(__name__)


class UnifiedSyncService:
    """Service for syncing events from all data sources"""
    
    def __init__(self):
        self.api_manager = unified_api_manager
        self.legacy_clients = {
            EventSource.EVENTBRITE: EventbriteClient(),
            EventSource.YELP: YelpClient(),  # Enabled - only Business Details API disabled
            EventSource.GOOGLE_PLACES: GooglePlacesClient(),
            EventSource.TICKETMASTER: TicketmasterClient(),
        }
    
    def _get_configured_sources(self) -> List[EventSource]:
        """Get only sources with valid API keys configured"""
        from app.core.config import settings
        
        configured = []
        
        # Yelp enabled - only Business Details API is disabled (fetch_details=False)
        if settings.YELP_API_KEY and not settings.YELP_API_KEY.startswith("your_"):
            configured.append(EventSource.YELP)
        
        if settings.EVENTBRITE_API_KEY and not settings.EVENTBRITE_API_KEY.startswith("your_"):
            configured.append(EventSource.EVENTBRITE)
        
        # Skip Google Places, Ticketmaster, and new sources with placeholder keys
        # They will only show errors
        
        logger.info(f"Configured sources with valid API keys: {[s.value for s in configured]}")
        return configured
    
    async def sync_all_sources(
        self, 
        db: Session, 
        zip_codes: List[str] = None, 
        sources: Optional[List[EventSource]] = None
    ) -> Dict[str, Any]:
        """Sync events from all or specific sources"""
        if not zip_codes:
            zip_codes = ["48104", "48105", "48108"]  # Default Ann Arbor area
        
        results = {
            "total_sources": 0,
            "successful_sources": 0,
            "total_events": 0,
            "events_created": 0,
            "events_updated": 0,
            "errors": [],
            "sources_synced": []
        }
        
        # Get sources to sync
        if sources:
            # Use specified sources only
            available_sources = sources
            logger.info(f"Syncing specific sources: {[s.value for s in sources]}")
        else:
            # Only sync sources with valid API keys (no console errors!)
            available_sources = self._get_configured_sources()
            logger.info(f"Syncing configured sources only: {[s.value for s in available_sources]}")
        
        results["total_sources"] = len(available_sources)
        
        # Sync each source
        for source in available_sources:
            try:
                logger.info(f"Starting sync for {source.value} with {len(zip_codes)} ZIP codes")
                source_result = await self._sync_source(db, source, zip_codes)
                results["total_events"] += source_result["total_events"]
                results["events_created"] += source_result["events_created"]
                results["events_updated"] += source_result["events_updated"]
                results["successful_sources"] += 1
                results["sources_synced"].append({
                    "source": source.value,
                    "events": source_result["total_events"],
                    "created": source_result["events_created"],
                    "updated": source_result["events_updated"]
                })
                logger.info(f"Completed sync for {source.value}: {source_result}")
            except Exception as e:
                error_msg = f"Error syncing {source.value}: {str(e)}"
                logger.error(error_msg)
                import traceback
                logger.error(traceback.format_exc())
                results["errors"].append(error_msg)
        
        # Create sync log
        await self._create_sync_log(db, results)
        
        logger.info(f"Sync completed: {results}")
        return results
    
    async def _sync_source(self, db: Session, source: EventSource, zip_codes: List[str]) -> Dict[str, Any]:
        """Sync events from a single source"""
        start_time = datetime.now()
        events_created = 0
        events_updated = 0
        total_events = 0
        
        try:
            # Get events from source
            events_data = await self._fetch_source_events(source, zip_codes)
            total_events = len(events_data)
            
            # Process each event
            for event_data in events_data:
                try:
                    # Normalize and save event
                    event = await self._save_event(db, event_data)
                    if event:
                        if event.created_at == event.updated_at:
                            events_created += 1
                        else:
                            events_updated += 1
                except Exception as e:
                    logger.error(f"Error saving event from {source}: {e}")
                    continue
            
            logger.info(f"Synced {source}: {events_created} created, {events_updated} updated")
            
        except Exception as e:
            logger.error(f"Error syncing {source}: {e}")
            raise
        
        return {
            "source": source,
            "total_events": total_events,
            "events_created": events_created,
            "events_updated": events_updated,
            "duration": (datetime.now() - start_time).total_seconds()
        }
    
    async def _fetch_source_events(self, source: EventSource, zip_codes: List[str]) -> List[Dict[str, Any]]:
        """Fetch events from a specific source"""
        all_events = []
        
        # Validate entire ZIP codes list first
        if not zip_codes or len(zip_codes) == 0:
            logger.error(f"❌ No ZIP codes provided to _fetch_source_events! zip_codes={zip_codes}")
            return []
        
        # Filter out any empty/invalid ZIP codes
        valid_zip_codes = [z for z in zip_codes if z and str(z).strip() != ""]
        if len(valid_zip_codes) == 0:
            logger.error(f"❌ All ZIP codes were empty! Original list: {zip_codes}")
            return []
        
        if len(valid_zip_codes) < len(zip_codes):
            logger.warning(f"⚠️ Filtered out {len(zip_codes) - len(valid_zip_codes)} empty ZIP codes")
        
        for zip_code in valid_zip_codes:
            
            try:
                logger.info(f"📍 Processing ZIP code: {zip_code}")
                
                # Create search parameters
                params = SearchParams(
                    location=zip_code,
                    zip_code=zip_code,
                    radius_miles=25,
                    categories=["family", "kids", "education", "sports", "arts"],
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=90),
                    limit=50
                )
                
                # Use new unified clients for new sources
                if source in [EventSource.MEETUP, EventSource.RECREATION_GOV, 
                             EventSource.YMCA, EventSource.BOYS_GIRLS_CLUB, 
                             EventSource.OPENSTREETMAP]:
                    client = self.api_manager.clients[source]
                    if client:
                        async with client:
                            if source == EventSource.MEETUP:
                                events = await client.search_events(params)
                            elif source == EventSource.RECREATION_GOV:
                                events = await client.search_facilities(params)
                            elif source == EventSource.YMCA:
                                events = await client.search_programs(params)
                            elif source == EventSource.BOYS_GIRLS_CLUB:
                                events = await client.search_clubs(params)
                            elif source == EventSource.OPENSTREETMAP:
                                events = await client.search_playgrounds(params)
                            else:
                                events = []
                        all_events.extend(events)
                
                # Use legacy clients for existing sources
                elif source in self.legacy_clients:
                    client = self.legacy_clients[source]
                    if source == EventSource.EVENTBRITE:
                        events = await client.search_events(
                            location=zip_code,
                            categories=["family"],
                            start_date=params.start_date,
                            end_date=params.end_date
                        )
                    elif source == EventSource.YELP:
                        logger.info(f"🔍 Calling Yelp API with location='{zip_code}' (type: {type(zip_code)})")
                        events = await client.search_businesses(
                            location=zip_code,
                            categories=["museums", "playgrounds", "amusementparks"],
                            fetch_details=False  # Explicitly disable Business Details API
                        )
                        logger.info(f"✅ Yelp returned {len(events)} events for ZIP {zip_code}")
                    elif source == EventSource.GOOGLE_PLACES:
                        events = await client.search_places(
                            location=zip_code,
                            types=["park", "museum", "amusement_park", "gym"]
                        )
                    elif source == EventSource.TICKETMASTER:
                        events = await client.search_events(
                            city="Ann Arbor",  # Extract city from zip
                            state="MI",
                            classifications=["Family"]
                        )
                    else:
                        events = []
                    
                    all_events.extend(events)
                
            except Exception as e:
                logger.error(f"Error fetching events from {source} for {zip_code}: {e}")
                continue
        
        return all_events
    
    async def _save_event(self, db: Session, event_data: Dict[str, Any]) -> Optional[UnifiedEvent]:
        """Save or update an event in the database"""
        try:
            # Check if event already exists
            existing_event = db.query(UnifiedEvent).filter(
                and_(
                    UnifiedEvent.external_id == event_data.get("external_id"),
                    UnifiedEvent.source == event_data.get("source")
                )
            ).first()
            
            if existing_event:
                # Update existing event
                for key, value in event_data.items():
                    if hasattr(existing_event, key) and value is not None:
                        setattr(existing_event, key, value)
                
                existing_event.updated_at = datetime.now()
                existing_event.last_synced = datetime.now()
                db.commit()
                db.refresh(existing_event)
                return existing_event
            else:
                # Filter event_data to only include valid UnifiedEvent fields
                # Remove legacy fields that don't exist in UnifiedEvent model
                filtered_data = {k: v for k, v in event_data.items() 
                                if hasattr(UnifiedEvent, k) and k not in ['id', 'created_at', 'updated_at', 'last_synced']}
                
                # Map source to EventSource enum if it's a string
                if 'source' in filtered_data and isinstance(filtered_data['source'], str):
                    filtered_data['source'] = EventSource(filtered_data['source'])
                
                # Create new event with filtered data
                new_event = UnifiedEvent(**filtered_data)
                new_event.created_at = datetime.now()
                new_event.updated_at = datetime.now()
                new_event.last_synced = datetime.now()
                new_event.is_active = True  # Set active by default
                new_event.event_type = event_data.get('event_type', EventType.VENUE)  # Default to venue for Yelp businesses
                
                db.add(new_event)
                db.commit()
                db.refresh(new_event)
                return new_event
                
        except Exception as e:
            logger.error(f"Error saving event: {e}")
            import traceback
            logger.error(traceback.format_exc())
            db.rollback()
            return None
    
    async def _create_sync_log(self, db: Session, results: Dict[str, Any]):
        """Create a sync log entry"""
        try:
            # Create separate log for each source
            for source in EventSource:
                sync_log = EventSyncLog(
                    source=source,
                    sync_type="full",
                    status="success" if not results["errors"] else "partial",
                    events_processed=results["total_events"],
                    events_created=results["events_created"],
                    events_updated=results["events_updated"],
                    errors=results["errors"],
                    started_at=datetime.now() - timedelta(minutes=5),
                    completed_at=datetime.now()
                )
                
                db.add(sync_log)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error creating sync log: {e}")
            db.rollback()
    
    async def cleanup_old_events(self, db: Session, days_old: int = 30):
        """Remove events that haven't been updated in specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Mark old events as inactive instead of deleting
            old_events = db.query(UnifiedEvent).filter(
                and_(
                    UnifiedEvent.last_synced < cutoff_date,
                    UnifiedEvent.is_active == True
                )
            ).all()
            
            for event in old_events:
                event.is_active = False
                event.updated_at = datetime.now()
            
            db.commit()
            
            logger.info(f"Marked {len(old_events)} old events as inactive")
            return len(old_events)
            
        except Exception as e:
            logger.error(f"Error cleaning up old events: {e}")
            db.rollback()
            return 0


# Global sync service instance
unified_sync_service = UnifiedSyncService()
