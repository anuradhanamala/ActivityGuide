"""
Centralized Category Management
All activity categories defined in one place and mapped to each source
"""

from enum import Enum
from typing import List, Dict


class ActivityType(Enum):
    """Common activity types across all sources"""
    MUSEUMS = "museums"
    PLAYGROUNDS = "playgrounds"
    AMUSEMENT_PARKS = "amusement_parks"
    GYMS = "gyms"
    SPORTS = "sports"
    FITNESS = "fitness"
    DANCE = "dance"
    AQUATIC = "aquatic"
    BASKETBALL = "basketball"
    SOCCER = "soccer"
    MARTIAL_ARTS = "martial_arts"
    MUSIC = "music"
    ART = "art"
    THEATER = "theater"
    SCIENCE = "science"
    PARKS = "parks"
    INDOOR_PLAY = "indoor_play"
    OUTDOOR_ACTIVITIES = "outdoor_activities"


class CategoryMapper:
    """Maps common activity types to source-specific categories"""
    
    # Master category mapping: ActivityType → Source-specific categories
    YELP_CATEGORIES = {
        ActivityType.MUSEUMS: "museums",
        ActivityType.PLAYGROUNDS: "playgrounds",
        ActivityType.AMUSEMENT_PARKS: "amusementparks",
        ActivityType.GYMS: "gyms",
        ActivityType.SPORTS: "sportclubs",
        ActivityType.FITNESS: "fitness",
        ActivityType.DANCE: "dance_schools,dancestudio",
        ActivityType.AQUATIC: "swimmingpools,aquariums",
        ActivityType.BASKETBALL: "basketball",
        ActivityType.SOCCER: "soccer",
        ActivityType.MARTIAL_ARTS: "martialarts,karate",
        ActivityType.MUSIC: "musiclessons,musicvenues",
        ActivityType.ART: "artclasses,artmuseums",
        ActivityType.THEATER: "theater,performingarts",
        ActivityType.SCIENCE: "sciencemuseums",
        ActivityType.PARKS: "parks",
        ActivityType.INDOOR_PLAY: "indoorplaycenter,trampoline",
        ActivityType.OUTDOOR_ACTIVITIES: "active,climbing,hiking",
    }
    
    GOOGLE_PLACES_TYPES = {
        ActivityType.MUSEUMS: "museum",
        ActivityType.PLAYGROUNDS: "park",
        ActivityType.AMUSEMENT_PARKS: "amusement_park",
        ActivityType.GYMS: "gym",
        ActivityType.SPORTS: "sports_complex",
        ActivityType.FITNESS: "gym",
        ActivityType.DANCE: "school",
        ActivityType.AQUATIC: "aquarium",
        ActivityType.BASKETBALL: "sports_complex",
        ActivityType.SOCCER: "sports_complex",
        ActivityType.MARTIAL_ARTS: "gym",
        ActivityType.MUSIC: "school",
        ActivityType.ART: "art_gallery",
        ActivityType.THEATER: "performing_arts_theater",
        ActivityType.SCIENCE: "museum",
        ActivityType.PARKS: "park",
        ActivityType.INDOOR_PLAY: "amusement_park",
        ActivityType.OUTDOOR_ACTIVITIES: "park",
    }
    
    EVENTBRITE_CATEGORIES = {
        ActivityType.MUSEUMS: "family",
        ActivityType.PLAYGROUNDS: "family",
        ActivityType.AMUSEMENT_PARKS: "family",
        ActivityType.GYMS: "sports-fitness",
        ActivityType.SPORTS: "sports-fitness",
        ActivityType.FITNESS: "sports-fitness",
        ActivityType.DANCE: "performing-arts",
        ActivityType.AQUATIC: "sports-fitness",
        ActivityType.BASKETBALL: "sports-fitness",
        ActivityType.SOCCER: "sports-fitness",
        ActivityType.MARTIAL_ARTS: "sports-fitness",
        ActivityType.MUSIC: "music",
        ActivityType.ART: "performing-arts",
        ActivityType.THEATER: "performing-arts",
        ActivityType.SCIENCE: "science-tech",
        ActivityType.PARKS: "family",
        ActivityType.INDOOR_PLAY: "family",
        ActivityType.OUTDOOR_ACTIVITIES: "sports-fitness",
    }
    
    # Default activity types to search (if none specified)
    DEFAULT_ACTIVITY_TYPES = [
        ActivityType.MUSEUMS,
        ActivityType.PLAYGROUNDS,
        ActivityType.AMUSEMENT_PARKS,
        ActivityType.GYMS,
        ActivityType.SPORTS,
        ActivityType.FITNESS,
        ActivityType.DANCE,
        ActivityType.AQUATIC,
        ActivityType.PARKS,
        ActivityType.INDOOR_PLAY,
    ]
    
    @classmethod
    def get_yelp_categories(cls, activity_types: List[ActivityType] = None) -> str:
        """
        Get Yelp category string for specified activity types
        
        Args:
            activity_types: List of ActivityType enums (None = use defaults)
            
        Returns:
            Comma-separated string of Yelp categories
        """
        if not activity_types:
            activity_types = cls.DEFAULT_ACTIVITY_TYPES
        
        categories = []
        for activity_type in activity_types:
            yelp_cat = cls.YELP_CATEGORIES.get(activity_type)
            if yelp_cat:
                categories.extend(yelp_cat.split(','))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_categories = []
        for cat in categories:
            if cat not in seen:
                seen.add(cat)
                unique_categories.append(cat)
        
        return ",".join(unique_categories)
    
    @classmethod
    def get_google_places_types(cls, activity_types: List[ActivityType] = None) -> str:
        """
        Get Google Places type string for specified activity types
        
        Args:
            activity_types: List of ActivityType enums (None = use defaults)
            
        Returns:
            Pipe-separated string of Google Places types
        """
        if not activity_types:
            activity_types = cls.DEFAULT_ACTIVITY_TYPES
        
        types = []
        for activity_type in activity_types:
            google_type = cls.GOOGLE_PLACES_TYPES.get(activity_type)
            if google_type:
                types.append(google_type)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_types = []
        for t in types:
            if t not in seen:
                seen.add(t)
                unique_types.append(t)
        
        return "|".join(unique_types)
    
    @classmethod
    def get_eventbrite_categories(cls, activity_types: List[ActivityType] = None) -> str:
        """
        Get Eventbrite category string for specified activity types
        
        Args:
            activity_types: List of ActivityType enums (None = use defaults)
            
        Returns:
            Comma-separated string of Eventbrite categories
        """
        if not activity_types:
            activity_types = cls.DEFAULT_ACTIVITY_TYPES
        
        categories = []
        for activity_type in activity_types:
            eb_cat = cls.EVENTBRITE_CATEGORIES.get(activity_type)
            if eb_cat:
                categories.append(eb_cat)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_categories = []
        for cat in categories:
            if cat not in seen:
                seen.add(cat)
                unique_categories.append(cat)
        
        return ",".join(unique_categories)
    
    @classmethod
    def get_all_activity_types(cls) -> List[ActivityType]:
        """Get all available activity types"""
        return list(ActivityType)
    
    @classmethod
    def add_activity_type(cls, activity_type: ActivityType, yelp: str, google: str, eventbrite: str):
        """
        Helper to show how to add new activity types
        (For documentation - actual additions should be done in the mappings above)
        """
        return {
            "activity_type": activity_type,
            "yelp": yelp,
            "google": google,
            "eventbrite": eventbrite,
            "example": f"""
# Add to class mappings:
YELP_CATEGORIES[ActivityType.{activity_type.name}] = "{yelp}"
GOOGLE_PLACES_TYPES[ActivityType.{activity_type.name}] = "{google}"
EVENTBRITE_CATEGORIES[ActivityType.{activity_type.name}] = "{eventbrite}"
"""
        }


# Quick reference guide
CATEGORY_GUIDE = """
🎯 How to Add New Activity Types:

1. Add to ActivityType enum:
   BOWLING = "bowling"

2. Add to each source mapping:
   YELP_CATEGORIES[ActivityType.BOWLING] = "bowling"
   GOOGLE_PLACES_TYPES[ActivityType.BOWLING] = "bowling_alley"
   EVENTBRITE_CATEGORIES[ActivityType.BOWLING] = "sports-fitness"

3. Optionally add to DEFAULT_ACTIVITY_TYPES

4. Done! All sources will automatically use it.

📚 Category Documentation:
- Yelp: https://docs.developer.yelp.com/docs/resources-categories
- Google: https://developers.google.com/maps/documentation/places/web-service/supported_types
- Eventbrite: https://www.eventbrite.com/platform/api#/reference/category
"""


# Example usage:
if __name__ == "__main__":
    # Get default categories for each source
    print("=" * 70)
    print("Default Categories for Each Source")
    print("=" * 70)
    print()
    
    print("Yelp Categories:")
    print(CategoryMapper.get_yelp_categories())
    print()
    
    print("Google Places Types:")
    print(CategoryMapper.get_google_places_types())
    print()
    
    print("Eventbrite Categories:")
    print(CategoryMapper.get_eventbrite_categories())
    print()
    
    print("=" * 70)
    print(CATEGORY_GUIDE)

