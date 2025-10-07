"""
Parallel AI Search Query Configuration
Externalized queries for better maintainability and configurability
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class QueryTemplate:
    """Template for Parallel AI queries"""
    template: str
    description: str
    parameters: List[str]
    example: str


class ParallelAIQueries:
    """Centralized Parallel AI query configurations"""
    
    # Base query templates
    FAMILY_ACTIVITIES = QueryTemplate(
        template="Family activities for kids in {location}",
        description="Search for family activities in a specific location",
        parameters=["location"],
        example="Family activities for kids in Troy, MI"
    )
    
    KIDS_ACTIVITIES_NEAR = QueryTemplate(
        template="Kids activities and family events near {zip_code}",
        description="Search for kids activities near a specific ZIP code",
        parameters=["zip_code"],
        example="Kids activities and family events near 48007"
    )
    
    SPECIFIC_ACTIVITY = QueryTemplate(
        template="{activity_type} activities for {age_range} in {location}",
        description="Search for specific activity type with age range and location",
        parameters=["activity_type", "age_range", "location"],
        example="Basketball activities for 8-10 year olds in Troy, MI"
    )
    
    FREE_ACTIVITIES = QueryTemplate(
        template="Free {activity_type} activities for kids in {location}",
        description="Search for free activities of specific type",
        parameters=["activity_type", "location"],
        example="Free art activities for kids in Troy, MI"
    )
    
    INDOOR_ACTIVITIES = QueryTemplate(
        template="Indoor {activity_type} activities for {age_range} in {location}",
        description="Search for indoor activities with age range",
        parameters=["activity_type", "age_range", "location"],
        example="Indoor basketball activities for 5-8 year olds in Troy, MI"
    )
    
    WEEKEND_ACTIVITIES = QueryTemplate(
        template="Weekend {activity_type} activities for kids in {location}",
        description="Search for weekend activities",
        parameters=["activity_type", "location"],
        example="Weekend swimming activities for kids in Troy, MI"
    )
    
    # Natural language query examples for frontend
    NATURAL_LANGUAGE_EXAMPLES = [
        "Basketball classes for 8-10 near me this Saturday",
        "Free art activities for my 5 year old this weekend",
        "Indoor activities near 12345 for toddlers",
        "Swimming lessons for kids aged 6-8",
        "Music classes this Tuesday near me",
        "Outdoor family activities this Sunday"
    ]
    
    # Query categories for different use cases
    QUERY_CATEGORIES = {
        "family": {
            "templates": [FAMILY_ACTIVITIES, KIDS_ACTIVITIES_NEAR],
            "description": "General family and kids activities"
        },
        "sports": {
            "templates": [SPECIFIC_ACTIVITY, INDOOR_ACTIVITIES],
            "description": "Sports and physical activities"
        },
        "arts": {
            "templates": [FREE_ACTIVITIES, SPECIFIC_ACTIVITY],
            "description": "Arts and creative activities"
        },
        "education": {
            "templates": [SPECIFIC_ACTIVITY, INDOOR_ACTIVITIES],
            "description": "Educational activities and classes"
        }
    }
    
    # Fallback queries when primary queries fail
    FALLBACK_QUERIES = [
        "Family fun activities in {location}",
        "Kids events and activities near {zip_code}",
        "Children's activities in {location}",
        "Family entertainment in {location}"
    ]
    
    @classmethod
    def get_query(cls, template: QueryTemplate, **kwargs) -> str:
        """Generate a query from a template with provided parameters"""
        try:
            return template.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
    
    @classmethod
    def get_family_activities_query(cls, location: str) -> str:
        """Get family activities query for a location"""
        return cls.get_query(cls.FAMILY_ACTIVITIES, location=location)
    
    @classmethod
    def get_kids_activities_query(cls, zip_code: str) -> str:
        """Get kids activities query for a ZIP code"""
        return cls.get_query(cls.KIDS_ACTIVITIES_NEAR, zip_code=zip_code)
    
    @classmethod
    def get_specific_activity_query(cls, activity_type: str, age_range: str, location: str) -> str:
        """Get specific activity query with age range"""
        return cls.get_query(cls.SPECIFIC_ACTIVITY, 
                           activity_type=activity_type, 
                           age_range=age_range, 
                           location=location)
    
    @classmethod
    def get_free_activities_query(cls, activity_type: str, location: str) -> str:
        """Get free activities query"""
        return cls.get_query(cls.FREE_ACTIVITIES, 
                           activity_type=activity_type, 
                           location=location)
    
    @classmethod
    def get_indoor_activities_query(cls, activity_type: str, age_range: str, location: str) -> str:
        """Get indoor activities query"""
        return cls.get_query(cls.INDOOR_ACTIVITIES, 
                           activity_type=activity_type, 
                           age_range=age_range, 
                           location=location)
    
    @classmethod
    def get_weekend_activities_query(cls, activity_type: str, location: str) -> str:
        """Get weekend activities query"""
        return cls.get_query(cls.WEEKEND_ACTIVITIES, 
                           activity_type=activity_type, 
                           location=location)
    
    @classmethod
    def get_fallback_queries(cls, location: str = None, zip_code: str = None) -> List[str]:
        """Get fallback queries when primary queries fail"""
        queries = []
        for template in cls.FALLBACK_QUERIES:
            try:
                if location:
                    query = template.format(location=location)
                elif zip_code:
                    query = template.format(zip_code=zip_code)
                else:
                    continue
                queries.append(query)
            except KeyError:
                continue
        return queries
    
    @classmethod
    def get_queries_by_category(cls, category: str, **kwargs) -> List[str]:
        """Get queries for a specific category"""
        if category not in cls.QUERY_CATEGORIES:
            return []
        
        queries = []
        for template in cls.QUERY_CATEGORIES[category]["templates"]:
            try:
                query = cls.get_query(template, **kwargs)
                queries.append(query)
            except (KeyError, ValueError):
                continue
        
        return queries


# Query configuration for different environments
class QueryConfig:
    """Configuration for different environments and use cases"""
    
    # Default query parameters
    DEFAULT_PARAMS = {
        "location": "Troy, MI",
        "zip_code": "48007",
        "activity_type": "family",
        "age_range": "5-12 year olds"
    }
    
    # Query limits for different endpoints
    QUERY_LIMITS = {
        "search": 20,
        "findall": 50,
        "fallback": 10
    }
    
    # Timeout settings
    TIMEOUTS = {
        "search": 30.0,
        "findall_ingest": 30.0,
        "findall_execute": 60.0
    }
    
    # Retry settings
    RETRY_SETTINGS = {
        "max_retries": 3,
        "retry_delay": 5.0,
        "backoff_factor": 2.0
    }


# Export the main query class
__all__ = ['ParallelAIQueries', 'QueryConfig', 'QueryTemplate']
