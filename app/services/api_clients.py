"""
External API clients for event data ingestion
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EventbriteClient:
    """Eventbrite API client"""
    
    def __init__(self):
        self.api_key = settings.EVENTBRITE_API_KEY
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def search_events(
        self, 
        location: str, 
        categories: List[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Search for events by location and filters"""
        if not self.api_key:
            logger.warning("Eventbrite API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "location.address": location,
                    "categories": ",".join(categories) if categories else "family",
                    "expand": "venue,description",
                    "status": "live"
                }
                
                if start_date:
                    params["start_date.range_start"] = start_date.isoformat()
                if end_date:
                    params["start_date.range_end"] = end_date.isoformat()
                
                response = await client.get(
                    f"{self.base_url}/events/search/",
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
            logger.error(f"Eventbrite API error: {e}")
            return []
    
    def _normalize_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Eventbrite event data to our format"""
        venue = event_data.get("venue", {})
        
        return {
            "title": event_data.get("name", {}).get("text", ""),
            "description": event_data.get("description", {}).get("text", ""),
            "start_time": event_data.get("start", {}).get("utc"),
            "end_time": event_data.get("end", {}).get("utc"),
            "location_name": venue.get("name", ""),
            "address": venue.get("address", {}).get("localized_area_display", ""),
            "city": venue.get("address", {}).get("city", ""),
            "state": venue.get("address", {}).get("region", ""),
            "zip_code": venue.get("address", {}).get("postal_code", ""),
            "latitude": venue.get("address", {}).get("latitude"),
            "longitude": venue.get("address", {}).get("longitude"),
            "category": "family",  # Eventbrite family category
            "is_free": event_data.get("is_free", False),
            "source": "eventbrite",
            "source_id": event_data.get("id", ""),
            "source_url": event_data.get("url", ""),
            "image_url": event_data.get("logo", {}).get("url", ""),
            "tags": [cat.get("name", "") for cat in event_data.get("category", {}).get("subcategories", [])]
        }


class YelpClient:
    """Yelp Fusion API client"""
    
    def __init__(self):
        self.api_key = settings.YELP_API_KEY
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def search_businesses(
        self, 
        location: str, 
        categories: List[str] = None,
        price: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for family-friendly businesses"""
        if not self.api_key:
            logger.warning("Yelp API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "location": location,
                    "categories": ",".join(categories) if categories else "museums,playgrounds,amusementparks",
                    "sort_by": "rating",
                    "limit": 50
                }
                
                if price:
                    params["price"] = price
                
                response = await client.get(
                    f"{self.base_url}/businesses/search",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                businesses = []
                
                for business in data.get("businesses", []):
                    businesses.append(self._normalize_business(business))
                
                return businesses
                
        except Exception as e:
            logger.error(f"Yelp API error: {e}")
            return []
    
    def _normalize_business(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Yelp business data to our format"""
        location = business_data.get("location", {})
        
        return {
            "title": business_data.get("name", ""),
            "description": business_data.get("categories", [{}])[0].get("title", ""),
            "location_name": business_data.get("name", ""),
            "address": location.get("address1", ""),
            "city": location.get("city", ""),
            "state": location.get("state", ""),
            "zip_code": location.get("zip_code", ""),
            "latitude": business_data.get("coordinates", {}).get("latitude"),
            "longitude": business_data.get("coordinates", {}).get("longitude"),
            "category": "family_venue",
            "is_free": business_data.get("price") == "$",
            "source": "yelp",
            "source_id": business_data.get("id", ""),
            "source_url": business_data.get("url", ""),
            "image_url": business_data.get("image_url", ""),
            "tags": [cat.get("title", "") for cat in business_data.get("categories", [])]
        }


class GooglePlacesClient:
    """Google Places API client"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    async def search_places(
        self, 
        location: str, 
        radius: int = 25000,
        types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for places using Google Places API"""
        if not self.api_key:
            logger.warning("Google Places API key not configured")
            return []
        
        try:
            # First, get place IDs
            search_url = f"{self.base_url}/nearbysearch/json"
            params = {
                "location": location,
                "radius": radius,
                "type": "|".join(types) if types else "park|museum|amusement_park",
                "key": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(search_url, params=params, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                places = []
                
                for place in data.get("results", []):
                    place_detail = await self._get_place_details(place.get("place_id"))
                    if place_detail:
                        places.append(self._normalize_place(place, place_detail))
                
                return places
                
        except Exception as e:
            logger.error(f"Google Places API error: {e}")
            return []
    
    async def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a place"""
        try:
            details_url = f"{self.base_url}/details/json"
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,geometry,opening_hours,website,rating,reviews",
                "key": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(details_url, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json().get("result")
                
        except Exception as e:
            logger.error(f"Google Places details error: {e}")
            return None
    
    def _normalize_place(self, place_data: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Google Places data to our format"""
        return {
            "title": details.get("name", place_data.get("name", "")),
            "description": f"Family-friendly {place_data.get('types', ['place'])[0].replace('_', ' ')}",
            "location_name": details.get("name", ""),
            "address": details.get("formatted_address", ""),
            "latitude": place_data.get("geometry", {}).get("location", {}).get("lat"),
            "longitude": place_data.get("geometry", {}).get("location", {}).get("lng"),
            "category": "family_venue",
            "is_free": True,  # Most parks and public venues are free
            "source": "google_places",
            "source_id": place_data.get("place_id", ""),
            "source_url": details.get("website", ""),
            "tags": place_data.get("types", [])
        }


class TicketmasterClient:
    """Ticketmaster Discovery API client"""
    
    def __init__(self):
        self.api_key = settings.TICKETMASTER_API_KEY
        self.base_url = "https://app.ticketmaster.com/discovery/v2"
    
    async def search_events(
        self, 
        city: str, 
        state: str,
        classifications: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for family-friendly events"""
        if not self.api_key:
            logger.warning("Ticketmaster API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "apikey": self.api_key,
                    "city": city,
                    "stateCode": state,
                    "classificationName": ",".join(classifications) if classifications else "Family",
                    "size": 50
                }
                
                response = await client.get(
                    f"{self.base_url}/events.json",
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                events = []
                
                for event in data.get("_embedded", {}).get("events", []):
                    events.append(self._normalize_event(event))
                
                return events
                
        except Exception as e:
            logger.error(f"Ticketmaster API error: {e}")
            return []
    
    def _normalize_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Ticketmaster event data to our format"""
        venue = event_data.get("_embedded", {}).get("venues", [{}])[0]
        dates = event_data.get("dates", {}).get("start", {})
        
        return {
            "title": event_data.get("name", ""),
            "description": event_data.get("info", ""),
            "start_time": dates.get("dateTime"),
            "location_name": venue.get("name", ""),
            "address": f"{venue.get('address', {}).get('line1', '')}, {venue.get('city', {}).get('name', '')}, {venue.get('state', {}).get('name', '')}",
            "city": venue.get("city", {}).get("name", ""),
            "state": venue.get("state", {}).get("name", ""),
            "zip_code": venue.get("postalCode", ""),
            "latitude": venue.get("location", {}).get("latitude"),
            "longitude": venue.get("location", {}).get("longitude"),
            "category": "family_entertainment",
            "is_free": False,  # Ticketmaster events are typically paid
            "source": "ticketmaster",
            "source_id": event_data.get("id", ""),
            "source_url": event_data.get("url", ""),
            "image_url": event_data.get("images", [{}])[0].get("url", ""),
            "tags": [classif.get("name", "") for classif in event_data.get("classifications", [])]
        }
