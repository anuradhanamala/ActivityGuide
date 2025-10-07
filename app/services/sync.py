"""
Background sync service for external API data
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.event import Event
from app.services.api_clients import EventbriteClient, YelpClient, GooglePlacesClient, TicketmasterClient
from app.services.parallel_ai_client import parallel_ai_client
from app.config.parallel_ai_queries import ParallelAIQueries, QueryConfig
from app.services.simple_ai import simple_summarization_agent as EventSummarizationAgent
import logging

logger = logging.getLogger(__name__)


class DataSyncService:
    """Service for syncing external API data"""
    
    def __init__(self):
        self.eventbrite_client = EventbriteClient()
        self.yelp_client = YelpClient()
        self.google_places_client = GooglePlacesClient()
        self.ticketmaster_client = TicketmasterClient()
        self.ai_agent = EventSummarizationAgent
    
    async def sync_all_sources(self, zip_codes: List[str] = None):
        """Sync data from all external sources"""
        if not zip_codes:
            raise ValueError("zip_codes parameter is required - no default zip codes provided")
        
        logger.info(f"Starting sync for {len(zip_codes)} zip codes")
        
        # Sync each source (Using Parallel AI for activities)
        tasks = [
            self.sync_parallel_ai(zip_codes),
            # self.sync_eventbrite(zip_codes),  # Disabled - API key not working
            # self.sync_yelp(zip_codes),  # Disabled - no valid API key
            # self.sync_google_places(zip_codes),  # Disabled - no valid API key
            # self.sync_ticketmaster(zip_codes)  # Disabled - no valid API key
        ]
        
        # Run all sync tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process and log results
        total_processed = 0
        sync_results = {}
        source_names = ["Parallel AI", "Eventbrite", "Yelp", "Google Places", "Ticketmaster"]
        
        for i, result in enumerate(results):
            source_name = source_names[i]
            if isinstance(result, Exception):
                logger.error(f"{source_name} sync failed: {result}")
                sync_results[source_name] = {"status": "error", "error": str(result), "events_processed": 0}
            else:
                logger.info(f"{source_name} sync completed: {result} events processed")
                sync_results[source_name] = {"status": "success", "events_processed": result}
                total_processed += result
        
        # Return detailed results
        return {
            "total_events_processed": total_processed,
            "zip_codes": zip_codes,
            "sources": sync_results,
            "summary": f"Sync completed for {len(zip_codes)} zip codes, processed {total_processed} events"
        }
    
    async def sync_eventbrite(self, zip_codes: List[str]) -> int:
        """Sync events from Eventbrite"""
        total_processed = 0
        
        for zip_code in zip_codes:
            try:
                events = await self.eventbrite_client.search_events(
                    location=f"{zip_code}, US",
                    categories=["family", "kids", "education"],
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=30)
                )
                
                processed = await self._save_events(events, "eventbrite")
                total_processed += processed
                
                logger.info(f"Eventbrite: {processed} events processed for {zip_code}")
                
            except Exception as e:
                logger.error(f"Eventbrite sync error for {zip_code}: {e}")
        
        return total_processed
    
    async def sync_yelp(self, zip_codes: List[str]) -> int:
        """Sync venues from Yelp"""
        total_processed = 0
        
        for zip_code in zip_codes:
            try:
                venues = await self.yelp_client.search_businesses(
                    location=f"{zip_code}",
                    categories=["museums", "playgrounds", "amusementparks", "kidactivities"]
                )
                
                # Convert venues to events (assuming they're ongoing activities)
                events = []
                for venue in venues:
                    venue["start_time"] = datetime.now().isoformat()
                    venue["end_time"] = (datetime.now() + timedelta(hours=8)).isoformat()
                    events.append(venue)
                
                processed = await self._save_events(events, "yelp")
                total_processed += processed
                
                logger.info(f"Yelp: {processed} venues processed for {zip_code}")
                
            except Exception as e:
                logger.error(f"Yelp sync error for {zip_code}: {e}")
        
        return total_processed
    
    async def sync_google_places(self, zip_codes: List[str]) -> int:
        """Sync places from Google Places"""
        total_processed = 0
        
        for zip_code in zip_codes:
            try:
                places = await self.google_places_client.search_places(
                    location=f"{zip_code}, US",
                    types=["park", "museum", "amusement_park", "playground"]
                )
                
                # Convert places to events
                events = []
                for place in places:
                    place["start_time"] = datetime.now().isoformat()
                    place["end_time"] = (datetime.now() + timedelta(hours=8)).isoformat()
                    events.append(place)
                
                processed = await self._save_events(events, "google_places")
                total_processed += processed
                
                logger.info(f"Google Places: {processed} places processed for {zip_code}")
                
            except Exception as e:
                logger.error(f"Google Places sync error for {zip_code}: {e}")
        
        return total_processed
    
    async def sync_ticketmaster(self, zip_codes: List[str]) -> int:
        """Sync events from Ticketmaster"""
        total_processed = 0
        
        # Map zip codes to city/state (simplified for Troy area)
        zip_to_city = {
            "48007": ("Troy", "MI"),
            "48083": ("Troy", "MI"),
            "48084": ("Troy", "MI"),
            "48085": ("Troy", "MI"),
            "48098": ("Troy", "MI"),
            "48099": ("Troy", "MI")
        }
        
        for zip_code in zip_codes:
            if zip_code in zip_to_city:
                city, state = zip_to_city[zip_code]
                
                try:
                    events = await self.ticketmaster_client.search_events(
                        city=city,
                        state=state,
                        classifications=["Family", "Kids", "Children"]
                    )
                    
                    processed = await self._save_events(events, "ticketmaster")
                    total_processed += processed
                    
                    logger.info(f"Ticketmaster: {processed} events processed for {city}, {state}")
                    
                except Exception as e:
                    logger.error(f"Ticketmaster sync error for {city}, {state}: {e}")
        
        return total_processed
    
    async def sync_parallel_ai(self, zip_codes: List[str]) -> int:
        """Sync activities from Parallel AI"""
        total_processed = 0
        
        for zip_code in zip_codes:
            try:
                logger.info(f"Syncing Parallel AI activities for {zip_code}")
                
                # Search for family activities in the area using externalized queries
                activities = await parallel_ai_client.find_activities(
                    location=f"{zip_code}, US",
                    activity_type="family"
                )
                
                # Try fallback queries if no activities found
                if not activities:
                    fallback_queries = ParallelAIQueries.get_fallback_queries(zip_code=zip_code)
                    for query in fallback_queries:
                        activities = await parallel_ai_client.search_by_query(
                            query=query,
                            location=f"{zip_code}, US"
                        )
                        if activities:
                            break
                
                if activities:
                    processed = await self._save_events(activities, "parallel_ai")
                    total_processed += processed
                    logger.info(f"Processed {processed} Parallel AI activities for {zip_code}")
                else:
                    logger.info(f"No Parallel AI activities found for {zip_code}")
                    
            except Exception as e:
                logger.error(f"Parallel AI sync error for {zip_code}: {e}")
                continue
        
        return total_processed
    
    async def _save_events(self, events_data: List[Dict[str, Any]], source: str) -> int:
        """Save events to database"""
        db = SessionLocal()
        processed = 0
        
        try:
            for event_data in events_data:
                # Check if event already exists
                existing_event = db.query(Event).filter(
                    Event.source == source,
                    Event.source_id == event_data.get("source_id")
                ).first()
                
                if existing_event:
                    # Update existing event
                    for key, value in event_data.items():
                        if hasattr(existing_event, key) and value is not None:
                            setattr(existing_event, key, value)
                    existing_event.last_synced = datetime.now()
                else:
                    # Create new event
                    event = Event(**event_data)
                    event.last_synced = datetime.now()
                    db.add(event)
                
                processed += 1
            
            db.commit()
            
            # Generate AI summaries for new events
            await self._generate_summaries_for_new_events(db, source)
            
        except Exception as e:
            logger.error(f"Database save error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return processed
    
    async def _generate_summaries_for_new_events(self, db: Session, source: str):
        """Generate AI summaries for events that don't have them"""
        try:
            events_without_summaries = db.query(Event).filter(
                Event.source == source,
                Event.summary.is_(None)
            ).limit(10).all()
            
            if events_without_summaries:
                summaries = await self.ai_agent.generate_batch_summaries(events_without_summaries)
                
                for event in events_without_summaries:
                    if event.id in summaries:
                        event.summary = summaries[event.id]
                
                db.commit()
                logger.info(f"Generated {len(summaries)} AI summaries for {source}")
                
        except Exception as e:
            logger.error(f"Summary generation error: {e}")


# Global sync service instance
sync_service = DataSyncService()


def start_sync_scheduler():
    """Start the background sync scheduler"""
    logger.info("Starting background sync scheduler")
    
    # Schedule sync every 6 hours
    schedule.every(settings.SYNC_INTERVAL_HOURS).hours.do(
        lambda: asyncio.create_task(sync_service.sync_all_sources())
    )
    
    # Run initial sync
    asyncio.create_task(sync_service.sync_all_sources())
    
    # Start scheduler in background thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    import threading
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
