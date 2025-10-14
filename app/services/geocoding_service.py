"""
Geocoding service for converting city/state to ZIP codes
"""

import httpx
import asyncio
from typing import List, Optional, Tuple
import logging
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Service for converting city/state to ZIP codes using multiple strategies:
    1. Nominatim (OpenStreetMap) - Free, no API key
    2. ZipCodeAPI fallback
    3. Hardcoded mapping as last resort
    """
    
    def __init__(self):
        # Initialize Nominatim (OpenStreetMap) geocoder
        self.geolocator = Nominatim(
            user_agent="ActivityGuide/1.0",
            timeout=10
        )
        # Add rate limiting (1 request per second for free tier)
        self.geocode = RateLimiter(
            self.geolocator.geocode,
            min_delay_seconds=1
        )
        
        # Hardcoded mapping as fallback
        self.city_zip_mapping = {
            # Michigan cities
            ("troy", "mi"): ["48007", "48083", "48084", "48085", "48098", "48099"],
            ("troy", "michigan"): ["48007", "48083", "48084", "48085", "48098", "48099"],
            ("detroit", "mi"): ["48201", "48202", "48204", "48205", "48206", "48207", "48208", "48209", "48210", "48211", "48212", "48213", "48214", "48215", "48216", "48217", "48219", "48221", "48223", "48224", "48226", "48227", "48228", "48234", "48235", "48238"],
            ("detroit", "michigan"): ["48201", "48202", "48204", "48205", "48206", "48207", "48208", "48209", "48210", "48211", "48212", "48213", "48214", "48215", "48216", "48217", "48219", "48221", "48223", "48224", "48226", "48227", "48228", "48234", "48235", "48238"],
            ("ann arbor", "mi"): ["48103", "48104", "48105", "48108", "48109"],
            ("ann arbor", "michigan"): ["48103", "48104", "48105", "48108", "48109"],
            ("sterling heights", "mi"): ["48310", "48311", "48312", "48313", "48314"],
            ("sterling heights", "michigan"): ["48310", "48311", "48312", "48313", "48314"],
            ("rochester", "mi"): ["48306", "48307", "48308", "48309"],
            ("rochester", "michigan"): ["48306", "48307", "48308", "48309"],
            ("rochester hills", "mi"): ["48307", "48309"],
            ("rochester hills", "michigan"): ["48307", "48309"],
            ("royal oak", "mi"): ["48067", "48068", "48073"],
            ("royal oak", "michigan"): ["48067", "48068", "48073"],
            ("birmingham", "mi"): ["48009", "48012"],
            ("birmingham", "michigan"): ["48009", "48012"],
            ("bloomfield hills", "mi"): ["48301", "48302", "48303", "48304"],
            ("bloomfield hills", "michigan"): ["48301", "48302", "48303", "48304"],
            ("novi", "mi"): ["48374", "48375", "48377"],
            ("novi", "michigan"): ["48374", "48375", "48377"],
            ("farmington", "mi"): ["48331", "48332", "48333", "48334", "48335", "48336"],
            ("farmington", "michigan"): ["48331", "48332", "48333", "48334", "48335", "48336"],
        }
    
    async def get_zip_codes_for_city(
        self, 
        city: str, 
        state: str,
        radius_miles: int = 25
    ) -> Tuple[List[str], str]:
        """
        Get ZIP codes for a city using geocoding APIs
        
        Returns:
            Tuple[List[str], str]: (list of ZIP codes, method used)
        """
        city_normalized = city.lower().strip()
        state_normalized = state.lower().strip()
        
        # Strategy 1: Try hardcoded mapping first (fastest)
        zip_codes = self._get_from_hardcoded_mapping(city_normalized, state_normalized)
        if zip_codes:
            logger.info(f"Found {len(zip_codes)} ZIP codes for {city}, {state} from hardcoded mapping")
            return zip_codes, "hardcoded_mapping"
        
        # Strategy 2: Try Nominatim (OpenStreetMap)
        try:
            zip_codes = await self._get_from_nominatim(city, state, radius_miles)
            if zip_codes:
                logger.info(f"Found {len(zip_codes)} ZIP codes for {city}, {state} from Nominatim")
                return zip_codes, "nominatim_geocoding"
        except Exception as e:
            logger.warning(f"Nominatim geocoding failed for {city}, {state}: {e}")
        
        # Strategy 3: Try ZipCodeAPI (if we add it later)
        # try:
        #     zip_codes = await self._get_from_zipcodeapi(city, state, radius_miles)
        #     if zip_codes:
        #         return zip_codes, "zipcodeapi"
        # except Exception as e:
        #     logger.warning(f"ZipCodeAPI failed for {city}, {state}: {e}")
        
        # No results found
        raise ValueError(
            f"Could not find ZIP codes for '{city}, {state}'. "
            f"Try using a major city name or add it to the hardcoded mapping."
        )
    
    def _get_from_hardcoded_mapping(
        self, 
        city_normalized: str, 
        state_normalized: str
    ) -> Optional[List[str]]:
        """Get ZIP codes from hardcoded mapping"""
        for (mapped_city, mapped_state), zips in self.city_zip_mapping.items():
            if city_normalized in mapped_city and state_normalized in mapped_state:
                return zips
        return None
    
    async def _get_from_nominatim(
        self, 
        city: str, 
        state: str,
        radius_miles: int = 25
    ) -> Optional[List[str]]:
        """
        Get ZIP codes using Nominatim (OpenStreetMap) geocoding
        
        Strategy:
        1. Geocode the city to get lat/lon
        2. Use ZIPCodeAPI or similar to get ZIP codes within radius
        3. Or use reverse geocoding on a grid of points
        """
        
        # Normalize state name to abbreviation
        state_abbr = self._normalize_state(state)
        
        # Geocode the city
        query = f"{city}, {state_abbr}, USA"
        
        try:
            # Run in thread pool since geopy is synchronous
            location = await asyncio.to_thread(self.geocode, query)
            
            if not location:
                logger.warning(f"Nominatim could not geocode: {query}")
                return None
            
            lat, lon = location.latitude, location.longitude
            logger.info(f"Geocoded {city}, {state} to {lat}, {lon}")
            
            # Now get ZIP codes in the area
            # For simplicity, we'll use a bounding box and query for ZIP codes
            # This is a simplified approach - in production, you'd use a proper ZIP code database
            
            # Calculate rough bounding box (1 mile ≈ 0.0145 degrees)
            radius_degrees = radius_miles * 0.0145
            
            # Get ZIP codes from nearby areas using reverse geocoding
            # This is a simplified implementation
            zip_codes = await self._get_zips_in_bounding_box(
                lat, lon, radius_degrees
            )
            
            return zip_codes if zip_codes else None
            
        except Exception as e:
            logger.error(f"Nominatim geocoding error for {city}, {state}: {e}")
            return None
    
    async def _get_zips_in_bounding_box(
        self,
        center_lat: float,
        center_lon: float,
        radius_degrees: float
    ) -> List[str]:
        """
        Get ZIP codes in a bounding box using ZIPCodeAPI
        
        This uses the free ZIPCodeAPI.com service
        """
        try:
            # Use ZIPCodeAPI free tier to get ZIP codes by location
            # Free tier: 10 requests per hour, no API key needed
            url = f"https://www.zipcodeapi.com/rest/demo/radius.json/{center_lat}/{center_lon}/{int(radius_degrees * 69)}/mile"
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract ZIP codes from response
                    if "zip_codes" in data:
                        zip_codes = [item["zip_code"] for item in data["zip_codes"]]
                        return zip_codes[:20]  # Limit to 20 ZIP codes
                    
        except Exception as e:
            logger.warning(f"ZIPCodeAPI request failed: {e}")
        
        # Fallback: return a single ZIP code based on reverse geocoding
        try:
            # Get the ZIP code for the center point
            location = await asyncio.to_thread(
                self.geolocator.reverse,
                f"{center_lat}, {center_lon}",
                exactly_one=True
            )
            
            if location and hasattr(location, 'raw') and 'address' in location.raw:
                address = location.raw['address']
                if 'postcode' in address:
                    return [address['postcode']]
                    
        except Exception as e:
            logger.warning(f"Reverse geocoding failed: {e}")
        
        return []
    
    def _normalize_state(self, state: str) -> str:
        """Normalize state name to abbreviation"""
        state_lower = state.lower().strip()
        
        state_mapping = {
            "michigan": "MI",
            "mi": "MI",
            "illinois": "IL",
            "il": "IL",
            "ohio": "OH",
            "oh": "OH",
            "indiana": "IN",
            "in": "IN",
            "wisconsin": "WI",
            "wi": "WI",
            "new york": "NY",
            "ny": "NY",
            "california": "CA",
            "ca": "CA",
            "texas": "TX",
            "tx": "TX",
            "florida": "FL",
            "fl": "FL",
            "pennsylvania": "PA",
            "pa": "PA",
        }
        
        return state_mapping.get(state_lower, state.upper())
    
    def get_available_cities(self) -> List[Tuple[str, str]]:
        """Get list of cities in hardcoded mapping"""
        return list(self.city_zip_mapping.keys())


# Global service instance
geocoding_service = GeocodingService()

