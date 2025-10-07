"""
Unified API clients for all event data sources
"""

import httpx
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.core.config import settings
from app.models.unified_event import UnifiedEvent, EventSource, EventType, AgeCategory

logger = logging.getLogger(__name__)


@dataclass
class SearchParams:
    """Standardized search parameters for all APIs"""
    location: str
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    radius_miles: int = 25
    categories: Optional[List[str]] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_free: Optional[bool] = None
    is_indoor: Optional[bool] = None
    limit: int = 50


class BaseAPIClient:
    """Base class for all API clients with common functionality"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    def calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score based on completeness"""
        required_fields = ['title', 'location_name', 'start_time']
        optional_fields = ['description', 'address', 'image_url', 'contact_info']
        
        score = 0.0
        for field in required_fields:
            if data.get(field):
                score += 0.3
        
        for field in optional_fields:
            if data.get(field):
                score += 0.05
        
        return min(score, 1.0)
    
    def normalize_age_range(self, age_min: Optional[int], age_max: Optional[int]) -> List[AgeCategory]:
        """Convert age range to age categories"""
        categories = []
        
        if age_min is None and age_max is None:
            return [AgeCategory.ALL_AGES]
        
        if age_min is not None:
            if age_min <= 2:
                categories.append(AgeCategory.TODDLER)
            if age_min <= 5:
                categories.append(AgeCategory.PRESCHOOL)
            if age_min <= 11:
                categories.append(AgeCategory.ELEMENTARY)
            if age_min <= 14:
                categories.append(AgeCategory.MIDDLE_SCHOOL)
            if age_min <= 17:
                categories.append(AgeCategory.HIGH_SCHOOL)
        
        if not categories:
            categories.append(AgeCategory.ALL_AGES)
        
        return categories


class MeetupAPIClient(BaseAPIClient):
    """Meetup.com API client for community events"""
    
    def __init__(self):
        super().__init__(
            api_key=settings.MEETUP_API_KEY,
            base_url="https://api.meetup.com"
        )
    
    async def search_events(self, params: SearchParams) -> List[Dict[str, Any]]:
        """Search Meetup events"""
        if not self.api_key:
            logger.warning("Meetup API key not configured")
            return []
        
        try:
            search_params = {
                "key": self.api_key,
                "location": params.location,
                "radius": params.radius_miles,
                "category": "25",  # Family & Kids category
                "page": 50
            }
            
            if params.start_date:
                search_params["time"] = f"{int(params.start_date.timestamp() * 1000)},{int((params.end_date or params.start_date + timedelta(days=30)).timestamp() * 1000)}"
            
            response = await self.session.get(
                f"{self.base_url}/find/events",
                params=search_params
            )
            response.raise_for_status()
            
            events = []
            for event in response.json():
                normalized = self._normalize_event(event)
                if normalized:
                    events.append(normalized)
            
            return events
            
        except Exception as e:
            logger.error(f"Meetup API error: {e}")
            return []
    
    def _normalize_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize Meetup event data"""
        try:
            venue = event_data.get("venue", {})
            
            return {
                "external_id": str(event_data.get("id", "")),
                "source": EventSource.MEETUP,
                "event_type": EventType.EVENT,
                "title": event_data.get("name", ""),
                "description": event_data.get("description", ""),
                "start_time": datetime.fromtimestamp(event_data.get("time", 0) / 1000) if event_data.get("time") else None,
                "duration": event_data.get("duration", 0),
                "location_name": venue.get("name", ""),
                "address": f"{venue.get('address_1', '')}, {venue.get('city', '')}, {venue.get('state', '')}",
                "city": venue.get("city", ""),
                "state": venue.get("state", ""),
                "zip_code": venue.get("zip", ""),
                "latitude": venue.get("lat"),
                "longitude": venue.get("lon"),
                "primary_category": "community",
                "tags": ["meetup", "community"] + [group.get("name", "") for group in event_data.get("group", {}).get("topics", [])],
                "is_free": event_data.get("fee", {}).get("amount", 0) == 0,
                "price_min": event_data.get("fee", {}).get("amount", 0),
                "source_url": event_data.get("link", ""),
                "image_url": event_data.get("featured_photo", {}).get("photo_link", ""),
                "data_quality_score": self.calculate_data_quality_score(event_data),
                "source_data": event_data
            }
        except Exception as e:
            logger.error(f"Error normalizing Meetup event: {e}")
            return None


class RecreationGovAPIClient(BaseAPIClient):
    """Recreation.gov RIDB API client for national park programs"""
    
    def __init__(self):
        super().__init__(
            api_key=settings.RECREATION_GOV_API_KEY,
            base_url="https://ridb.recreation.gov/api/v1"
        )
    
    async def search_facilities(self, params: SearchParams) -> List[Dict[str, Any]]:
        """Search recreation facilities and programs"""
        if not self.api_key:
            logger.warning("Recreation.gov API key not configured")
            return []
        
        try:
            search_params = {
                "apikey": self.api_key,
                "limit": params.limit,
                "offset": 0
            }
            
            # Search by state if provided
            if params.state:
                search_params["state"] = params.state
            elif params.zip_code:
                search_params["zip"] = params.zip_code
            
            response = await self.session.get(
                f"{self.base_url}/facilities",
                params=search_params
            )
            response.raise_for_status()
            
            facilities = []
            for facility in response.json().get("RECDATA", []):
                normalized = self._normalize_facility(facility)
                if normalized:
                    facilities.append(normalized)
            
            return facilities
            
        except Exception as e:
            logger.error(f"Recreation.gov API error: {e}")
            return []
    
    def _normalize_facility(self, facility_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize recreation facility data"""
        try:
            return {
                "external_id": facility_data.get("FacilityID", ""),
                "source": EventSource.RECREATION_GOV,
                "event_type": EventType.VENUE,
                "title": facility_data.get("FacilityName", ""),
                "description": facility_data.get("FacilityDescription", ""),
                "location_name": facility_data.get("FacilityName", ""),
                "address": facility_data.get("FacilityAddress", ""),
                "city": facility_data.get("FacilityCity", ""),
                "state": facility_data.get("FacilityState", ""),
                "zip_code": facility_data.get("FacilityZip", ""),
                "latitude": facility_data.get("FacilityLatitude"),
                "longitude": facility_data.get("FacilityLongitude"),
                "primary_category": "outdoor_recreation",
                "tags": ["national_park", "recreation", "federal"] + facility_data.get("FACILITYADMIN", []),
                "is_free": True,  # Most federal recreation is free
                "source_url": facility_data.get("FacilityURL", ""),
                "data_quality_score": self.calculate_data_quality_score(facility_data),
                "source_data": facility_data
            }
        except Exception as e:
            logger.error(f"Error normalizing recreation facility: {e}")
            return None


class YMCAAPIClient(BaseAPIClient):
    """YMCA API client (using web scraping approach)"""
    
    def __init__(self):
        super().__init__(
            api_key="",  # YMCA doesn't have public API
            base_url="https://www.ymca.net"
        )
    
    async def search_programs(self, params: SearchParams) -> List[Dict[str, Any]]:
        """Search YMCA programs (simulated - would need web scraping)"""
        # This would typically involve web scraping YMCA websites
        # For now, return mock data structure
        logger.info("YMCA API client - would implement web scraping for program data")
        return []
    
    def _normalize_ymca_program(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize YMCA program data"""
        return {
            "external_id": program_data.get("id", ""),
            "source": EventSource.YMCA,
            "event_type": EventType.PROGRAM,
            "title": program_data.get("name", ""),
            "description": program_data.get("description", ""),
            "primary_category": "fitness_recreation",
            "tags": ["ymca", "fitness", "swimming", "youth_programs"],
            "is_free": False,
            "data_quality_score": self.calculate_data_quality_score(program_data),
            "source_data": program_data
        }


class BoysGirlsClubAPIClient(BaseAPIClient):
    """Boys & Girls Clubs API client"""
    
    def __init__(self):
        super().__init__(
            api_key="",  # BGC doesn't have public API
            base_url="https://www.bgca.org"
        )
    
    async def search_clubs(self, params: SearchParams) -> List[Dict[str, Any]]:
        """Search Boys & Girls Clubs (simulated)"""
        logger.info("Boys & Girls Club API client - would implement club locator")
        return []


class OpenStreetMapAPIClient(BaseAPIClient):
    """OpenStreetMap Overpass API client for playgrounds and parks"""
    
    def __init__(self):
        super().__init__(
            api_key="",  # OSM doesn't require API key
            base_url="https://overpass-api.de/api/interpreter"
        )
    
    async def search_playgrounds(self, params: SearchParams) -> List[Dict[str, Any]]:
        """Search playgrounds and parks using Overpass API"""
        try:
            # Build Overpass QL query for playgrounds and parks
            query = f"""
            [out:json][timeout:25];
            (
              node["leisure"="playground"](around:{params.radius_miles * 1609.34},{params.latitude},{params.longitude});
              node["leisure"="park"](around:{params.radius_miles * 1609.34},{params.latitude},{params.longitude});
              way["leisure"="playground"](around:{params.radius_miles * 1609.34},{params.latitude},{params.longitude});
              way["leisure"="park"](around:{params.radius_miles * 1609.34},{params.latitude},{params.longitude});
            );
            out center meta;
            """
            
            response = await self.session.post(
                self.base_url,
                data=query,
                headers={"Content-Type": "text/plain"}
            )
            response.raise_for_status()
            
            playgrounds = []
            for element in response.json().get("elements", []):
                normalized = self._normalize_osm_element(element)
                if normalized:
                    playgrounds.append(normalized)
            
            return playgrounds
            
        except Exception as e:
            logger.error(f"OpenStreetMap API error: {e}")
            return []
    
    def _normalize_osm_element(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize OSM element data"""
        try:
            tags = element.get("tags", {})
            lat = element.get("lat") or element.get("center", {}).get("lat")
            lon = element.get("lon") or element.get("center", {}).get("lon")
            
            return {
                "external_id": f"osm_{element.get('id', '')}",
                "source": EventSource.OPENSTREETMAP,
                "event_type": EventType.VENUE,
                "title": tags.get("name", f"{tags.get('leisure', 'place').title()}"),
                "description": f"Public {tags.get('leisure', 'space')}",
                "location_name": tags.get("name", ""),
                "address": tags.get("addr:full", ""),
                "city": tags.get("addr:city", ""),
                "state": tags.get("addr:state", ""),
                "zip_code": tags.get("addr:postcode", ""),
                "latitude": lat,
                "longitude": lon,
                "primary_category": "outdoor_recreation",
                "tags": [tags.get("leisure", ""), "free", "public"] + [tag for tag in tags.get("amenity", "").split(",") if tag],
                "is_free": True,
                "is_outdoor": True,
                "data_quality_score": self.calculate_data_quality_score(element),
                "source_data": element
            }
        except Exception as e:
            logger.error(f"Error normalizing OSM element: {e}")
            return None


class UnifiedAPIManager:
    """Manager class to coordinate all API clients"""
    
    def __init__(self):
        self.clients = {
            EventSource.EVENTBRITE: None,  # Will use existing EventbriteClient
            EventSource.YELP: None,  # Will use existing YelpClient
            EventSource.GOOGLE_PLACES: None,  # Will use existing GooglePlacesClient
            EventSource.TICKETMASTER: None,  # Will use existing TicketmasterClient
            EventSource.MEETUP: MeetupAPIClient(),
            EventSource.RECREATION_GOV: RecreationGovAPIClient(),
            EventSource.YMCA: YMCAAPIClient(),
            EventSource.BOYS_GIRLS_CLUB: BoysGirlsClubAPIClient(),
            EventSource.OPENSTREETMAP: OpenStreetMapAPIClient(),
        }
    
    async def search_all_sources(self, params: SearchParams) -> Dict[EventSource, List[Dict[str, Any]]]:
        """Search all configured data sources"""
        results = {}
        
        # Run searches in parallel
        tasks = []
        for source, client in self.clients.items():
            if client:
                task = self._search_source(client, source, params)
                tasks.append(task)
        
        if tasks:
            search_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(search_results):
                source = list(self.clients.keys())[i]
                if isinstance(result, Exception):
                    logger.error(f"Error searching {source}: {result}")
                    results[source] = []
                else:
                    results[source] = result
        
        return results
    
    async def _search_source(self, client: BaseAPIClient, source: EventSource, params: SearchParams) -> List[Dict[str, Any]]:
        """Search a single source"""
        try:
            async with client:
                if source == EventSource.MEETUP:
                    return await client.search_events(params)
                elif source == EventSource.RECREATION_GOV:
                    return await client.search_facilities(params)
                elif source == EventSource.YMCA:
                    return await client.search_programs(params)
                elif source == EventSource.BOYS_GIRLS_CLUB:
                    return await client.search_clubs(params)
                elif source == EventSource.OPENSTREETMAP:
                    return await client.search_playgrounds(params)
                else:
                    return []
        except Exception as e:
            logger.error(f"Error searching {source}: {e}")
            return []
    
    def get_available_sources(self) -> List[EventSource]:
        """Get list of available data sources"""
        return [source for source, client in self.clients.items() if client is not None]


# Global instance
unified_api_manager = UnifiedAPIManager()
