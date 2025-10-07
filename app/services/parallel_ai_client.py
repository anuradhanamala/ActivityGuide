"""
Parallel AI client for finding activities
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from app.core.config import settings
from app.config.parallel_ai_queries import ParallelAIQueries, QueryConfig

logger = logging.getLogger(__name__)


class ParallelAIClient:
    """Parallel AI client for finding family activities"""
    
    def __init__(self):
        self.base_url = "https://api.parallel.ai"
        self.api_key = getattr(settings, 'PARALLEL_AI_API_KEY', None)
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "ActivityGuide/1.0"
        }
        
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
    
    async def find_activities(
        self, 
        location: str,
        activity_type: str = "family",
        age_range: Optional[str] = None,
        date_range: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find activities using Parallel AI platform"""
        
        try:
            # Use externalized query templates
            if activity_type == "family":
                query = ParallelAIQueries.get_family_activities_query(location)
            elif age_range:
                query = ParallelAIQueries.get_specific_activity_query(
                    activity_type, age_range, location
                )
            else:
                query = ParallelAIQueries.get_specific_activity_query(
                    activity_type, "kids", location
                )
            
            # Add date range if specified
            if date_range:
                query += f" {date_range}"
            
            # Use the v1beta/search endpoint
            return await self.search_by_query(
                query=query,
                location=location,
                limit=QueryConfig.QUERY_LIMITS["search"]
            )
                    
        except Exception as e:
            logger.error(f"Parallel AI client error: {e}")
            return []
    
    async def search_by_query(
        self, 
        query: str,
        location: str,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """Search for activities using natural language query"""
        
        try:
            # Use externalized configuration
            if limit is None:
                limit = QueryConfig.QUERY_LIMITS["search"]
            
            payload = {
                "objective": f"Find {query} in {location}",
                "search_queries": [f"{query} {location}"],
                "max_results": limit,
                "processor": "pro"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1beta/search",
                    headers=self.headers,
                    json=payload,
                    timeout=QueryConfig.TIMEOUTS["search"]
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Handle different response formats
                    results = data.get("results", data.get("data", []))
                    return self._normalize_activities(results, location)
                else:
                    logger.error(f"Parallel AI search error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Parallel AI search error: {e}")
            return []
    
    async def findall_ingest(
        self, 
        query: str,
        location: str = None
    ) -> Dict[str, Any]:
        """Use Parallel AI's findall ingest endpoint for structured data extraction"""
        
        try:
            # Enhance query with location if provided
            enhanced_query = query
            if location:
                enhanced_query = f"{query} in {location}"
            
            payload = {"query": enhanced_query}
            
            # Add parallel-beta header for FindAll endpoint
            findall_headers = self.headers.copy()
            findall_headers["parallel-beta"] = "true"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1beta/findall/ingest",
                    headers=findall_headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Generated spec with {len(data.get('columns', []))} columns")
                    return data
                else:
                    logger.error(f"Parallel AI findall ingest error: {response.status_code} - {response.text}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Parallel AI findall ingest error: {e}")
            return {}
    
    async def findall_execute(
        self, 
        findall_spec: Dict[str, Any],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Execute the findall spec to get actual data"""
        
        try:
            # Start the findall run
            payload = {
                "findall_spec": findall_spec,
                "processor": "base",
                "result_limit": limit
            }
            
            # Add parallel-beta header for FindAll endpoint
            findall_headers = self.headers.copy()
            findall_headers["parallel-beta"] = "true"
            
            async with httpx.AsyncClient() as client:
                # Start the run
                response = await client.post(
                    f"{self.base_url}/v1beta/findall/runs",
                    headers=findall_headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Parallel AI findall start error: {response.status_code} - {response.text}")
                    return []
                
                run_data = response.json()
                findall_id = run_data.get("findall_id")
                
                if not findall_id:
                    logger.error("No findall_id returned from start request")
                    return []
                
                # Poll for results
                import asyncio
                max_attempts = 20  # 5 minutes max
                attempt = 0
                
                while attempt < max_attempts:
                    await asyncio.sleep(15)  # Wait 15 seconds between polls
                    
                    poll_response = await client.get(
                        f"{self.base_url}/v1beta/findall/runs/{findall_id}",
                        headers=findall_headers,
                        timeout=30.0
                    )
                    
                    if poll_response.status_code == 200:
                        result = poll_response.json()
                        
                        # Check if run is complete
                        if not result.get("is_active", False) and not result.get("are_enrichments_active", False):
                            return self._normalize_findall_results(result.get("results", []), location)
                        
                        logger.info(f"Findall run {findall_id} still active, attempt {attempt + 1}/{max_attempts}")
                    else:
                        logger.error(f"Parallel AI findall poll error: {poll_response.status_code} - {poll_response.text}")
                        break
                    
                    attempt += 1
                
                logger.error(f"Findall run {findall_id} timed out after {max_attempts} attempts")
                return []
                    
        except Exception as e:
            logger.error(f"Parallel AI findall execute error: {e}")
            return []
    
    def _normalize_activities(self, activities: List[Dict[str, Any]], location: str = None) -> List[Dict[str, Any]]:
        """Normalize Parallel AI activity data to our format"""
        
        normalized = []
        
        # Parse location to extract city and zip_code
        city = ""
        zip_code = ""
        if location:
            # Extract zip code from location string like "48083, US" or "Troy, MI"
            import re
            zip_match = re.search(r'\b(\d{5})\b', location)
            if zip_match:
                zip_code = zip_match.group(1)
            
            # Extract city name - if it's a zip code, use default city name
            city_match = re.search(r'^([^,]+)', location)
            if city_match:
                city_part = city_match.group(1).strip()
                # If it's a zip code, use Troy as default city
                if city_part.isdigit():
                    city = "Troy"
                else:
                    city = city_part
        
        # Generate location keywords for filtering based on the search location
        location_keywords = self._generate_location_keywords(location)
        
        for activity in activities:
            # Extract location information for filtering
            activity_title = activity.get("name", activity.get("title", "")).lower()
            activity_description = activity.get("description", "").lower()
            activity_url = activity.get("url", "").lower()
            activity_address = activity.get("address", "").lower()
            
            # Check if activity is related to the search location
            is_location_related = False
            
            # Check title, description, URL, and address for location keywords
            for keyword in location_keywords:
                if (keyword in activity_title or 
                    keyword in activity_description or 
                    keyword in activity_url or 
                    keyword in activity_address):
                    is_location_related = True
                    break
            
            # Skip activities not related to the search location
            if not is_location_related:
                logger.debug(f"Skipping non-local activity: {activity.get('name', activity.get('title', ''))}")
                continue
            
            # Extract zip code if available
            activity_zip = activity.get("zip_code", "")
            if not activity_zip and activity.get("address"):
                import re
                zip_match = re.search(r'\b(\d{5})\b', activity.get("address", ""))
                if zip_match:
                    activity_zip = zip_match.group(1)
            
            # Map Parallel AI fields to our standard format
            normalized_activity = {
                "title": activity.get("name", activity.get("title", "")),
                "description": activity.get("description", ""),
                "start_time": self._parse_datetime(activity.get("start_time")) or datetime.now(),
                "end_time": self._parse_datetime(activity.get("end_time")),
                "location_name": activity.get("venue", activity.get("location_name", "")),
                "address": activity.get("address", ""),
                "city": activity.get("city", city),
                "state": activity.get("state", "MI"),
                "zip_code": activity_zip or zip_code,
                "latitude": activity.get("latitude"),
                "longitude": activity.get("longitude"),
                "category": self._map_category(activity.get("category", "")),
                "age_range_min": activity.get("min_age"),
                "age_range_max": activity.get("max_age"),
                "is_free": activity.get("price", 0) == 0,
                "is_indoor": "indoor" in activity.get("venue_type", "").lower(),
                "source": "parallel_ai",
                "source_id": activity.get("id", ""),
                "source_url": activity.get("url", ""),
                "image_url": activity.get("image", ""),
                "tags": activity.get("tags", []),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            normalized.append(normalized_activity)
        
        return normalized
    
    def _generate_location_keywords(self, location: str) -> List[str]:
        """Generate location keywords for filtering based on the search location"""
        if not location:
            return []
        
        # Parse location to extract city and state
        location_parts = [part.strip() for part in location.split(',')]
        city = location_parts[0].lower()
        state = location_parts[1].lower() if len(location_parts) > 1 else ""
        
        # Generate various keyword combinations
        keywords = [city]
        
        if state:
            # Add city + state combinations
            keywords.extend([
                f"{city} {state}",
                f"{city}, {state}",
                f"{city} {state.upper()}",
                f"{city}, {state.upper()}"
            ])
            
            # Add state-specific variations
            if state in ["mi", "michigan"]:
                keywords.append(f"{city} michigan")
            elif state in ["ca", "california"]:
                keywords.append(f"{city} california")
            elif state in ["ny", "new york"]:
                keywords.append(f"{city} new york")
            # Add more states as needed
        
        # Add common city name variations
        if city.endswith("s"):
            keywords.append(city[:-1])  # Remove 's' for singular form
        
        return list(set(keywords))  # Remove duplicates
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to Python datetime object"""
        if not date_str:
            return None
        
        try:
            # Try to parse various datetime formats
            if isinstance(date_str, str):
                # If it's already in ISO format, parse it
                if "T" in date_str and "Z" in date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                # Try to parse other formats
                parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return parsed
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _map_category(self, category: str) -> str:
        """Map Parallel AI categories to our standard categories"""
        
        category_mapping = {
            "sports": "sports",
            "art": "arts",
            "music": "music",
            "education": "education",
            "museum": "museum",
            "outdoor": "outdoor",
            "indoor": "indoor",
            "family": "family",
            "kids": "family",
            "children": "family"
        }
        
        return category_mapping.get(category.lower(), "family")
    
    def _normalize_findall_results(self, results: List[Dict[str, Any]], location: str = None) -> List[Dict[str, Any]]:
        """Normalize findall results to our activity format"""
        
        normalized = []
        
        # Parse location to extract city and zip_code
        city = ""
        zip_code = ""
        if location:
            # Extract zip code from location string like "48083, US" or "Troy, MI"
            import re
            zip_match = re.search(r'\b(\d{5})\b', location)
            if zip_match:
                zip_code = zip_match.group(1)
            
            # Extract city name - if it's a zip code, use default city name
            city_match = re.search(r'^([^,]+)', location)
            if city_match:
                city_part = city_match.group(1).strip()
                # If it's a zip code, use Troy as default city
                if city_part.isdigit():
                    city = "Troy"
                else:
                    city = city_part
        
        for result in results:
            # Map findall result fields to our standard format
            normalized_activity = {
                "title": result.get("name", result.get("title", result.get("company_name", ""))),
                "description": result.get("description", result.get("summary", "")),
                "start_time": self._parse_datetime(result.get("start_time", result.get("founded_date"))) or datetime.now(),
                "end_time": self._parse_datetime(result.get("end_time")),
                "location_name": result.get("venue", result.get("location", result.get("headquarters", ""))),
                "address": result.get("address", ""),
                "city": result.get("city", city),
                "state": result.get("state", "MI"),
                "zip_code": result.get("zip_code", zip_code),
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "category": self._map_category(result.get("category", result.get("industry", ""))),
                "age_range_min": result.get("min_age"),
                "age_range_max": result.get("max_age"),
                "is_free": result.get("price", 0) == 0,
                "is_indoor": "indoor" in str(result.get("venue_type", "")).lower(),
                "source": "parallel_ai_findall",
                "source_id": result.get("id", ""),
                "source_url": result.get("url", result.get("website", "")),
                "image_url": result.get("image", result.get("logo", "")),
                "tags": result.get("tags", []),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                # Additional fields from findall results
                "funding_amount": result.get("funding_amount"),
                "funding_round": result.get("funding_round"),
                "founded_year": result.get("founded_year"),
                "employees": result.get("employees"),
                "industry": result.get("industry")
            }
            
            normalized.append(normalized_activity)
        
        return normalized


# Global client instance
parallel_ai_client = ParallelAIClient()

