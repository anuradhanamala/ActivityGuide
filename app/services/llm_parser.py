"""
Enhanced LLM-powered text parsing for parent queries
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from app.core.config import settings
import openai
import anthropic
import logging

logger = logging.getLogger(__name__)


class LLMParentQueryParser:
    """LLM-powered parser for natural language queries from parents"""
    
    def __init__(self):
        # Initialize LLM clients
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # Fallback patterns for basic parsing
        self.age_patterns = [
            r'(\d+)[\s\-–](\d+)\s*years?',
            r'ages?\s*(\d+)[\s\-–](\d+)',
            r'(\d+)[\s\-–](\d+)\s*year\s*olds?',
            r'for\s*(\d+)[\s\-–](\d+)',
        ]
        
        self.location_patterns = [
            r'near\s+([A-Za-z\s]+)',
            r'in\s+([A-Za-z\s]+)',
            r'at\s+([A-Za-z\s]+)',
        ]
        
        self.zip_pattern = r'\b(\d{5}(?:-\d{4})?)\b'
        
        self.activity_categories = {
            'basketball': 'sports', 'soccer': 'sports', 'tennis': 'sports',
            'swimming': 'sports', 'gymnastics': 'sports', 'dance': 'arts',
            'music': 'music', 'art': 'arts', 'theater': 'arts',
            'storytime': 'education', 'reading': 'education',
            'museum': 'museum', 'playground': 'outdoor', 'park': 'outdoor'
        }
    
    async def parse_query(self, query: str) -> Dict:
        """
        Parse a natural language query using LLM + fallback patterns
        """
        
        result = {
            "original_query": query,
            "parsed_params": {},
            "confidence": 0.0,
            "missing_info": [],
            "suggestions": [],
            "needs_clarification": False,
            "llm_used": None
        }
        
        # Try LLM parsing first
        llm_result = await self._llm_parse_query(query)
        
        if llm_result:
            result.update(llm_result)
            result["llm_used"] = "anthropic" if self.anthropic_client else "openai"
        else:
            # Fallback to pattern matching
            result.update(self._pattern_parse_query(query))
            result["llm_used"] = "patterns"
        
        # Generate suggestions for missing info
        result["suggestions"].extend(self._generate_suggestions(result))
        
        # Calculate confidence
        result["confidence"] = self._calculate_confidence(result)
        result["needs_clarification"] = len(result["missing_info"]) > 0 or result["confidence"] < 0.7
        
        return result
    
    async def _llm_parse_query(self, query: str) -> Optional[Dict]:
        """Use LLM to parse the query"""
        
        # Try Anthropic first (primary choice)
        if self.anthropic_client:
            try:
                return await self._anthropic_parse(query)
            except Exception as e:
                logger.error(f"Anthropic parsing failed: {e}")
        
        # Try OpenAI as fallback
        if self.openai_client:
            try:
                return await self._openai_parse(query)
            except Exception as e:
                logger.error(f"OpenAI parsing failed: {e}")
        
        return None
    
    async def _openai_parse(self, query: str) -> Dict:
        """Parse using OpenAI GPT"""
        
        system_prompt = """You are an expert at parsing parent queries for kids' activities. 

Extract structured information from natural language and return ONLY a JSON object with this exact format:

{
  "parsed_params": {
    "age_min": number or null,
    "age_max": number or null,
    "category": "sports/arts/education/museum/outdoor/indoor" or null,
    "zip_code": "12345" or null,
    "location": "City Name" or null,
    "start_date": "YYYY-MM-DD" or null,
    "day": "saturday" or null,
    "is_indoor": true/false or null,
    "is_free": true/false or null,
    "price_max": number or null
  },
  "suggestions": ["helpful follow-up questions if info is missing"],
  "confidence": 0.0 to 1.0
}

Rules:
- Extract age ranges from phrases like "8-10", "for my 5 year old", "toddlers"
- Map activities to categories: basketball→sports, art→arts, storytime→education
- Parse locations: "near me" → location: "near me"
- Parse dates: "this Saturday" → day: "saturday", start_date: "YYYY-MM-DD"
- If ZIP code found, use it; otherwise suggest asking for location
- Generate helpful follow-up questions for missing critical info
- Be conservative with confidence scores"""

        user_prompt = f"Parse this parent query: '{query}'"
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Invalid JSON response from OpenAI")
    
    async def _anthropic_parse(self, query: str) -> Dict:
        """Parse using Anthropic Claude"""
        
        system_prompt = """You are an expert at parsing parent queries for kids' activities. 

Extract structured information from natural language and return ONLY a JSON object with this exact format:

{
  "parsed_params": {
    "age_min": number or null,
    "age_max": number or null,
    "category": "sports/arts/education/museum/outdoor/indoor" or null,
    "zip_code": "12345" or null,
    "location": "City Name" or null,
    "start_date": "YYYY-MM-DD" or null,
    "day": "saturday" or null,
    "is_indoor": true/false or null,
    "is_free": true/false or null,
    "price_max": number or null
  },
  "suggestions": ["helpful follow-up questions if info is missing"],
  "confidence": 0.0 to 1.0
}

Rules:
- Extract age ranges from phrases like "8-10", "for my 5 year old", "toddlers"
- Map activities to categories: basketball→sports, art→arts, storytime→education
- Parse locations: "near me" → location: "near me"
- Parse dates: "this Saturday" → day: "saturday", start_date: "YYYY-MM-DD"
- If ZIP code found, use it; otherwise suggest asking for location
- Generate helpful follow-up questions for missing critical info
- Be conservative with confidence scores"""

        user_prompt = f"Parse this parent query: '{query}'"
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        content = response.content[0].text.strip()
        
        # Try to parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Invalid JSON response from Anthropic")
    
    def _pattern_parse_query(self, query: str) -> Dict:
        """Fallback pattern-based parsing"""
        
        result = {
            "parsed_params": {},
            "confidence": 0.0,
            "missing_info": [],
            "suggestions": []
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
        
        # Parse category
        category = self._parse_category(query_lower)
        if category:
            result["parsed_params"]["category"] = category
        
        return result
    
    def _parse_age_range(self, query: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse age range from query"""
        for pattern in self.age_patterns:
            match = re.search(pattern, query)
            if match:
                try:
                    return int(match.group(1)), int(match.group(2))
                except (ValueError, IndexError):
                    continue
        return None, None
    
    def _parse_location(self, query: str) -> Optional[str]:
        """Parse location from query"""
        for pattern in self.location_patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                location = re.sub(r'\b(near|in|at)\b', '', location).strip()
                return location.title()
        return None
    
    def _parse_zip_code(self, query: str) -> Optional[str]:
        """Parse ZIP code from query"""
        match = re.search(self.zip_pattern, query)
        return match.group(1) if match else None
    
    def _parse_category(self, query: str) -> Optional[str]:
        """Parse activity category from query"""
        for activity, category in self.activity_categories.items():
            if activity in query:
                return category
        return None
    
    def _generate_suggestions(self, result: Dict) -> List[str]:
        """Generate helpful suggestions for missing information"""
        suggestions = []
        
        if "zip_code" in result["missing_info"]:
            suggestions.append("What ZIP code would you like to search in?")
        
        if "category" not in result["parsed_params"]:
            suggestions.append("What type of activity are you looking for? (sports, arts, education, etc.)")
        
        if "start_date" not in result["parsed_params"]:
            suggestions.append("When would you like to do this activity?")
        
        # Contextual suggestions
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


# Global LLM parser instance
llm_parser = LLMParentQueryParser()
