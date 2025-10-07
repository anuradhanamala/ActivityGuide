"""
Agentic Framework for Multiple Parallel AI Searches
Fires multiple parallel searches for different kids activity categories
"""

import asyncio
import httpx
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
from app.core.config import settings
from app.config.parallel_ai_queries import QueryConfig

logger = logging.getLogger(__name__)


class ActivityCategory(Enum):
    """Kids activity categories for agentic search"""
    SPORTS = "sports"
    EDUCATION = "education"
    MUSIC = "music"
    ARTS = "arts"
    INSTRUMENTS = "instruments"
    DANCE = "dance"
    STEM = "stem"
    OUTDOOR = "outdoor"
    INDOOR = "indoor"
    FAMILY = "family"


@dataclass
class SearchAgent:
    """Individual search agent for a specific activity category"""
    category: ActivityCategory
    query_template: str
    age_ranges: List[str]
    priority: int = 1  # Higher number = higher priority
    max_results: int = 20
    timeout: float = 30.0


@dataclass
class SearchResult:
    """Result from a single search agent"""
    agent: SearchAgent
    query: str
    results: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None
    execution_time: float = 0.0


class AgenticSearchOrchestrator:
    """Orchestrates multiple parallel AI searches for kids activities"""
    
    def __init__(self):
        self.base_url = "https://api.parallel.ai"
        self.api_key = getattr(settings, 'PARALLEL_AI_API_KEY', None)
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "ActivityGuide-Agentic/1.0"
        }
        
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
        
        # Define search agents for different categories
        self.search_agents = self._initialize_search_agents()
    
    def _initialize_search_agents(self) -> List[SearchAgent]:
        """Initialize search agents for different activity categories"""
        
        agents = [
            # Sports activities
            SearchAgent(
                category=ActivityCategory.SPORTS,
                query_template="{sport_type} classes and activities for {age_range} in {location}",
                age_ranges=["5-8 year olds", "8-12 year olds", "12-16 year olds"],
                priority=1,
                max_results=25
            ),
            
            # Education classes
            SearchAgent(
                category=ActivityCategory.EDUCATION,
                query_template="{subject} classes and tutoring for {age_range} in {location}",
                age_ranges=["5-8 year olds", "8-12 year olds", "12-16 year olds"],
                priority=1,
                max_results=20
            ),
            
            # Music activities
            SearchAgent(
                category=ActivityCategory.MUSIC,
                query_template="music lessons and {music_type} classes for {age_range} in {location}",
                age_ranges=["3-6 year olds", "6-10 year olds", "10-16 year olds"],
                priority=1,
                max_results=20
            ),
            
            # Arts activities
            SearchAgent(
                category=ActivityCategory.ARTS,
                query_template="{art_type} classes and art activities for {age_range} in {location}",
                age_ranges=["3-6 year olds", "6-10 year olds", "10-16 year olds"],
                priority=1,
                max_results=20
            ),
            
            # Musical instruments
            SearchAgent(
                category=ActivityCategory.INSTRUMENTS,
                query_template="{instrument} lessons and instrument classes for {age_range} in {location}",
                age_ranges=["5-8 year olds", "8-12 year olds", "12-16 year olds"],
                priority=2,
                max_results=15
            ),
            
            # Dance activities
            SearchAgent(
                category=ActivityCategory.DANCE,
                query_template="{dance_type} classes and dance lessons for {age_range} in {location}",
                age_ranges=["3-6 year olds", "6-10 year olds", "10-16 year olds"],
                priority=1,
                max_results=20
            ),
            
            # STEM activities
            SearchAgent(
                category=ActivityCategory.STEM,
                query_template="STEM classes and {stem_type} activities for {age_range} in {location}",
                age_ranges=["6-10 year olds", "10-14 year olds", "14-18 year olds"],
                priority=1,
                max_results=20
            ),
            
            # Outdoor activities
            SearchAgent(
                category=ActivityCategory.OUTDOOR,
                query_template="outdoor activities and {outdoor_type} for {age_range} in {location}",
                age_ranges=["5-8 year olds", "8-12 year olds", "12-16 year olds"],
                priority=2,
                max_results=20
            ),
            
            # Indoor activities
            SearchAgent(
                category=ActivityCategory.INDOOR,
                query_template="indoor activities and {indoor_type} for {age_range} in {location}",
                age_ranges=["3-6 year olds", "6-10 year olds", "10-16 year olds"],
                priority=2,
                max_results=20
            )
        ]
        
        return agents
    
    def _generate_queries_for_agent(self, agent: SearchAgent, location: str) -> List[str]:
        """Generate multiple queries for a single agent based on category"""
        
        queries = []
        
        # Category-specific query variations
        if agent.category == ActivityCategory.SPORTS:
            sport_types = ["basketball", "soccer", "swimming", "tennis", "gymnastics", "martial arts"]
            for sport in sport_types:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        sport_type=sport,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        elif agent.category == ActivityCategory.EDUCATION:
            subjects = ["math", "science", "reading", "writing", "coding", "languages"]
            for subject in subjects:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        subject=subject,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        elif agent.category == ActivityCategory.MUSIC:
            music_types = ["piano", "guitar", "voice", "drums", "violin", "singing"]
            for music_type in music_types:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        music_type=music_type,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        elif agent.category == ActivityCategory.ARTS:
            art_types = ["painting", "drawing", "sculpture", "pottery", "crafts", "digital art"]
            for art_type in art_types:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        art_type=art_type,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        elif agent.category == ActivityCategory.INSTRUMENTS:
            instruments = ["piano", "guitar", "violin", "drums", "flute", "trumpet", "saxophone"]
            for instrument in instruments:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        instrument=instrument,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        elif agent.category == ActivityCategory.DANCE:
            dance_types = ["ballet", "jazz", "hip hop", "tap", "contemporary", "ballroom"]
            for dance_type in dance_types:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        dance_type=dance_type,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        elif agent.category == ActivityCategory.STEM:
            stem_types = ["robotics", "programming", "engineering", "math", "science experiments"]
            for stem_type in stem_types:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        stem_type=stem_type,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        elif agent.category == ActivityCategory.OUTDOOR:
            outdoor_types = ["hiking", "camping", "sports", "nature", "adventure", "playground"]
            for outdoor_type in outdoor_types:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        outdoor_type=outdoor_type,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        elif agent.category == ActivityCategory.INDOOR:
            indoor_types = ["games", "puzzles", "board games", "video games", "reading", "crafts"]
            for indoor_type in indoor_types:
                for age_range in agent.age_ranges:
                    query = agent.query_template.format(
                        indoor_type=indoor_type,
                        age_range=age_range,
                        location=location
                    )
                    queries.append(query)
        
        # Return all queries for comprehensive coverage
        return queries
    
    async def _execute_single_search(self, agent: SearchAgent, query: str, location: str) -> SearchResult:
        """Execute a single search query"""
        
        start_time = datetime.now()
        
        try:
            payload = {
                "objective": f"Find {query} in {location}",
                "search_queries": [f"{query} {location}"],
                "max_results": agent.max_results,
                "processor": "pro"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1beta/search",
                    headers=self.headers,
                    json=payload,
                    timeout=agent.timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", data.get("data", []))
                    
                    # Assign the agent's category to each result
                    for result in results:
                        result['category'] = agent.category.value
                    
                    return SearchResult(
                        agent=agent,
                        query=query,
                        results=results,
                        success=True,
                        execution_time=execution_time
                    )
                else:
                    return SearchResult(
                        agent=agent,
                        query=query,
                        results=[],
                        success=False,
                        error=f"HTTP {response.status_code}: {response.text}",
                        execution_time=execution_time
                    )
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return SearchResult(
                agent=agent,
                query=query,
                results=[],
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def search_city_activities(
        self, 
        city: str, 
        categories: Optional[List[ActivityCategory]] = None,
        max_concurrent: int = 10
    ) -> Dict[str, Any]:
        """Search for kids activities in a city using multiple parallel agents"""
        
        logger.info(f"Starting agentic search for {city} with categories: {categories}")
        
        # Filter agents by requested categories
        if categories:
            # Handle both enum and string categories
            if categories and isinstance(categories[0], str):
                active_agents = [agent for agent in self.search_agents if agent.category.value in categories]
            else:
                active_agents = [agent for agent in self.search_agents if agent.category in categories]
        else:
            active_agents = self.search_agents
        
        # Generate all queries for all agents
        all_queries = []
        for agent in active_agents:
            queries = self._generate_queries_for_agent(agent, city)
            for query in queries:
                all_queries.append((agent, query))
        
        logger.info(f"Generated {len(all_queries)} total queries across {len(active_agents)} agents")
        
        # Execute searches with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(agent, query):
            async with semaphore:
                return await self._execute_single_search(agent, query, city)
        
        # Execute all searches in parallel
        tasks = [execute_with_semaphore(agent, query) for agent, query in all_queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_results = []
        total_activities = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Search task failed with exception: {result}")
                continue
            
            if result.success:
                successful_results.append(result)
                total_activities += len(result.results)
            else:
                failed_results.append(result)
        
        # Group results by category
        results_by_category = {}
        for result in successful_results:
            category = result.agent.category.value
            if category not in results_by_category:
                results_by_category[category] = []
            results_by_category[category].extend(result.results)
        
        # Calculate statistics
        total_queries = len(all_queries)
        successful_queries = len(successful_results)
        failed_queries = len(failed_results)
        avg_execution_time = sum(r.execution_time for r in successful_results) / max(successful_queries, 1)
        
        logger.info(f"Agentic search completed: {successful_queries}/{total_queries} queries successful, {total_activities} total activities found")
        
        return {
            "city": city,
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "total_activities": total_activities,
            "categories_searched": [agent.category.value for agent in active_agents],
            "results_by_category": results_by_category,
            "execution_stats": {
                "avg_execution_time": avg_execution_time,
                "total_execution_time": sum(r.execution_time for r in successful_results),
                "max_concurrent": max_concurrent
            },
            "failed_queries_details": [
                {
                    "category": r.agent.category.value,
                    "query": r.query,
                    "error": r.error
                } for r in failed_results
            ]
        }
    
    async def search_troy_activities(self) -> Dict[str, Any]:
        """Convenience method to search Troy, MI activities"""
        return await self.search_city_activities("Troy, MI")
    
    async def search_specific_categories(
        self, 
        city: str, 
        categories: List[str]
    ) -> Dict[str, Any]:
        """Search specific activity categories in a city"""
        
        # Convert string categories to enum
        category_enums = []
        for cat in categories:
            try:
                category_enums.append(ActivityCategory(cat.lower()))
            except ValueError:
                logger.warning(f"Unknown category: {cat}")
        
        return await self.search_city_activities(city, category_enums)


# Global orchestrator instance
agentic_orchestrator = AgenticSearchOrchestrator()
