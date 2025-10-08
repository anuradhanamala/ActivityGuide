"""
Updated Eventbrite API client with OAuth 2.0 and alternative endpoints
Since /events/search/ is deprecated for public access
"""

import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EventbriteOAuthClient:
    """
    Eventbrite API client using OAuth 2.0
    
    Note: The public /events/search/ endpoint is deprecated.
    This client uses alternative approaches:
    1. Organization events (if you manage organizations)
    2. User-owned events
    3. Featured/recommended events
    """
    
    def __init__(self):
        self.access_token = settings.EVENTBRITE_API_KEY  # This should be OAuth token
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def get_user_organizations(self) -> List[Dict[str, Any]]:
        """Get organizations owned by the authenticated user"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me/organizations/",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("organizations", [])
        except Exception as e:
            logger.error(f"Error fetching user organizations: {e}")
            return []
    
    async def get_organization_events(
        self,
        organization_id: str,
        status: str = "live",
        order_by: str = "start_asc"
    ) -> List[Dict[str, Any]]:
        """
        Get events for a specific organization
        This is the recommended way to access Eventbrite events
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "status": status,
                    "order_by": order_by,
                    "expand": "venue,category"
                }
                
                response = await client.get(
                    f"{self.base_url}/organizations/{organization_id}/events/",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                events = []
                
                for event in data.get("events", []):
                    events.append(self._normalize_event(event))
                
                return events
                
        except Exception as e:
            logger.error(f"Error fetching organization events: {e}")
            return []
    
    async def get_user_owned_events(
        self,
        status: str = "live"
    ) -> List[Dict[str, Any]]:
        """Get events owned by the authenticated user"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "status": status,
                    "expand": "venue,category"
                }
                
                response = await client.get(
                    f"{self.base_url}/users/me/owned_events/",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                events = []
                
                for event in data.get("events", []):
                    events.append(self._normalize_event(event))
                
                return events
                
        except Exception as e:
            logger.error(f"Error fetching user events: {e}")
            return []
    
    async def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/events/{event_id}/",
                    headers=self.headers,
                    params={"expand": "venue,category"},
                    timeout=30.0
                )
                response.raise_for_status()
                
                event_data = response.json()
                return self._normalize_event(event_data)
                
        except Exception as e:
            logger.error(f"Error fetching event {event_id}: {e}")
            return None
    
    async def search_events_alternative(
        self,
        location: str = None,
        categories: List[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Alternative search method:
        1. Get all organizations the user has access to
        2. Fetch events from each organization
        3. Filter by location and categories
        
        Note: This only works if you manage organizations on Eventbrite
        """
        all_events = []
        
        # Get user's organizations
        organizations = await self.get_user_organizations()
        
        if not organizations:
            logger.warning("No organizations found. Cannot search events without organization access.")
            logger.info("To use Eventbrite API, you need to:")
            logger.info("1. Create an organization on Eventbrite")
            logger.info("2. Create events under that organization")
            logger.info("3. Use the organization ID to fetch events")
            return []
        
        # Fetch events from each organization
        for org in organizations:
            org_id = org.get("id")
            org_events = await self.get_organization_events(org_id)
            all_events.extend(org_events)
        
        # Filter by location if provided
        if location:
            all_events = [
                e for e in all_events 
                if location.lower() in (e.get("city", "") or "").lower() or
                   location.lower() in (e.get("address", "") or "").lower()
            ]
        
        # Filter by categories if provided
        if categories:
            all_events = [
                e for e in all_events
                if e.get("category", "").lower() in [c.lower() for c in categories]
            ]
        
        # Filter by date range
        if start_date or end_date:
            filtered_events = []
            for event in all_events:
                event_start = event.get("start_time")
                if event_start:
                    if isinstance(event_start, str):
                        event_start = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                    
                    if start_date and event_start < start_date:
                        continue
                    if end_date and event_start > end_date:
                        continue
                    
                    filtered_events.append(event)
            all_events = filtered_events
        
        return all_events
    
    def _normalize_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Eventbrite event data to unified format"""
        venue = event_data.get("venue", {}) or {}
        address = venue.get("address", {}) or {}
        
        return {
            "external_id": event_data.get("id", ""),
            "source": "eventbrite",
            "event_type": "event",
            "title": event_data.get("name", {}).get("text", "") if isinstance(event_data.get("name"), dict) else event_data.get("name", ""),
            "description": event_data.get("description", {}).get("text", "") if isinstance(event_data.get("description"), dict) else event_data.get("description", ""),
            "start_time": event_data.get("start", {}).get("utc") if isinstance(event_data.get("start"), dict) else event_data.get("start"),
            "end_time": event_data.get("end", {}).get("utc") if isinstance(event_data.get("end"), dict) else event_data.get("end"),
            "location_name": venue.get("name", ""),
            "address": address.get("localized_area_display", "") or f"{address.get('address_1', '')}, {address.get('city', '')}, {address.get('region', '')}",
            "street_address": address.get("address_1", ""),
            "city": address.get("city", ""),
            "state": address.get("region", ""),
            "zip_code": address.get("postal_code", ""),
            "country": address.get("country", "US"),
            "latitude": address.get("latitude"),
            "longitude": address.get("longitude"),
            "primary_category": "family",
            "is_free": event_data.get("is_free", False),
            "source_url": event_data.get("url", ""),
            "image_url": event_data.get("logo", {}).get("url", "") if event_data.get("logo") else None,
            "tags": [],
            "data_quality_score": 0.8
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test API connection and return user info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me/",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                user_data = response.json()
                return {
                    "success": True,
                    "user_id": user_data.get("id"),
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "message": "✅ Eventbrite API connection successful!"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "❌ Eventbrite API connection failed!"
            }


# Global instance
eventbrite_oauth_client = EventbriteOAuthClient()
