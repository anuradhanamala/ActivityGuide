"""
Simplified Natural Language Processing service without external dependencies
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class SimpleParentQueryParser:
    """Simple parser for natural language queries from parents"""
    
    def __init__(self):
        # Common age patterns
        self.age_patterns = [
            r'(\d+)[\s\-–](\d+)\s*years?',
            r'ages?\s*(\d+)[\s\-–](\d+)',
            r'(\d+)[\s\-–](\d+)\s*year\s*olds?',
            r'for\s*(\d+)[\s\-–](\d+)',
        ]
        
        # Common location patterns
        self.location_patterns = [
            r'near\s+([A-Za-z\s]+)',
            r'in\s+([A-Za-z\s]+)',
            r'at\s+([A-Za-z\s]+)',
            r'around\s+([A-Za-z\s]+)',
        ]
        
        # Day patterns
        self.day_patterns = [
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(today|tomorrow|this\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday))',
            r'(next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday))',
        ]
        
        # ZIP code patterns
        self.zip_pattern = r'\b(\d{5}(?:-\d{4})?)\b'
        
        # Activity categories mapping
        self.activity_categories = {
            'basketball': 'sports',
            'soccer': 'sports',
            'tennis': 'sports',
            'swimming': 'sports',
            'gymnastics': 'sports',
            'dance': 'arts',
            'music': 'music',
            'art': 'arts',
            'theater': 'arts',
            'drama': 'arts',
            'storytime': 'education',
            'reading': 'education',
            'library': 'education',
            'museum': 'museum',
            'playground': 'outdoor',
            'park': 'outdoor',
            'hiking': 'outdoor',
            'camping': 'outdoor',
            'indoor': 'indoor',
            'outdoor': 'outdoor',
            'free': 'free',
            'paid': 'paid'
        }
    
    async def parse_query(self, query: str) -> Dict:
        """
        Parse a natural language query into structured search parameters
        """
        
        # Initialize result
        result = {
            "original_query": query,
            "parsed_params": {},
            "confidence": 0.0,
            "missing_info": [],
            "suggestions": [],
            "needs_clarification": False
        }
        
        query_lower = query.lower()
        
        # Parse age range
        age_min, age_max = self._parse_age_range(query_lower)
        if age_min is not None and age_max is not None:
            result["parsed_params"]["age_min"] = age_min
            result["parsed_params"]["age_max"] = age_max
        
        # Parse location
        location = self._parse_location(query_lower)
        if location:
            result["parsed_params"]["location"] = location
        
        # Parse ZIP code
        zip_code = self._parse_zip_code(query)
        if zip_code:
            result["parsed_params"]["zip_code"] = zip_code
        else:
            result["missing_info"].append("zip_code")
        
        # Parse day/date
        day, start_date = self._parse_day(query_lower)
        if day:
            result["parsed_params"]["day"] = day
        if start_date:
            result["parsed_params"]["start_date"] = start_date
        
        # Parse activity category
        category = self._parse_category(query_lower)
        if category:
            result["parsed_params"]["category"] = category
        
        # Generate suggestions for missing information
        result["suggestions"].extend(self._generate_suggestions(result))
        
        # Calculate overall confidence
        result["confidence"] = self._calculate_confidence(result)
        
        # Determine if clarification is needed
        result["needs_clarification"] = len(result["missing_info"]) > 0 or result["confidence"] < 0.7
        
        return result
    
    def _parse_age_range(self, query: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse age range from query"""
        for pattern in self.age_patterns:
            match = re.search(pattern, query)
            if match:
                try:
                    age_min = int(match.group(1))
                    age_max = int(match.group(2))
                    return age_min, age_max
                except (ValueError, IndexError):
                    continue
        return None, None
    
    def _parse_location(self, query: str) -> Optional[str]:
        """Parse location from query"""
        for pattern in self.location_patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                # Clean up common words
                location = re.sub(r'\b(near|in|at|around)\b', '', location).strip()
                return location.title()
        return None
    
    def _parse_zip_code(self, query: str) -> Optional[str]:
        """Parse ZIP code from query"""
        match = re.search(self.zip_pattern, query)
        if match:
            return match.group(1)
        return None
    
    def _parse_day(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse day/date from query"""
        for pattern in self.day_patterns:
            match = re.search(pattern, query)
            if match:
                day_text = match.group(1).lower()
                
                # Map day names
                day_mapping = {
                    'monday': 'monday',
                    'tuesday': 'tuesday',
                    'wednesday': 'wednesday',
                    'thursday': 'thursday',
                    'friday': 'friday',
                    'saturday': 'saturday',
                    'sunday': 'sunday',
                    'today': datetime.now().strftime('%A').lower(),
                    'tomorrow': (datetime.now() + timedelta(days=1)).strftime('%A').lower()
                }
                
                if day_text in day_mapping:
                    day = day_mapping[day_text]
                    start_date = self._get_date_for_day(day)
                    return day, start_date
        
        return None, None
    
    def _parse_category(self, query: str) -> Optional[str]:
        """Parse activity category from query"""
        for activity, category in self.activity_categories.items():
            if activity in query:
                return category
        return None
    
    def _get_date_for_day(self, day: str) -> str:
        """Get the next occurrence of a given day"""
        today = datetime.now()
        days_ahead = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_day = days_ahead[day]
        days_until_target = (target_day - today.weekday()) % 7
        if days_until_target == 0 and today.weekday() == target_day:
            # If it's the same day, look for next week
            days_until_target = 7
        
        target_date = today + timedelta(days=days_until_target)
        return target_date.strftime('%Y-%m-%d')
    
    def _generate_suggestions(self, result: Dict) -> List[str]:
        """Generate helpful suggestions for missing information"""
        suggestions = []
        
        if "zip_code" in result["missing_info"]:
            suggestions.append("What ZIP code would you like to search in?")
        
        if "category" not in result["parsed_params"]:
            suggestions.append("What type of activity are you looking for? (sports, arts, education, etc.)")
        
        if "start_date" not in result["parsed_params"]:
            suggestions.append("When would you like to do this activity?")
        
        # Check for indoor/outdoor preference
        if result["parsed_params"].get("category") == "sports":
            suggestions.append("Do you prefer indoor or outdoor activities?")
        
        return suggestions
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score based on parsed information"""
        score = 0.0
        total_weight = 0.0
        
        # Age range (weight: 0.3)
        if "age_min" in result["parsed_params"] and "age_max" in result["parsed_params"]:
            score += 0.3
        total_weight += 0.3
        
        # Location/ZIP (weight: 0.3)
        if "zip_code" in result["parsed_params"] or "location" in result["parsed_params"]:
            score += 0.3
        total_weight += 0.3
        
        # Category (weight: 0.2)
        if "category" in result["parsed_params"]:
            score += 0.2
        total_weight += 0.2
        
        # Time/Date (weight: 0.2)
        if "start_date" in result["parsed_params"] or "day" in result["parsed_params"]:
            score += 0.2
        total_weight += 0.2
        
        return score / total_weight if total_weight > 0 else 0.0


# Global parser instance
simple_nlp_parser = SimpleParentQueryParser()
