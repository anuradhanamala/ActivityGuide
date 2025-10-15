"""
Hybrid RAG Service - Best of Both Worlds!
Combines SQL queries (fast, structured) with Vector search (semantic, concept-based)
"""

from typing import Dict, Any, Optional, List
import logging
import re

from app.services.simple_rag import simple_rag_service
from app.services.vector_rag import vector_rag_service
from app.models.unified_event import UnifiedEvent

logger = logging.getLogger(__name__)


class HybridRAGService:
    """
    Intelligent RAG that chooses the best retrieval method
    
    Strategy:
    - Structured queries (age, city, category) → SQL RAG (fast)
    - Semantic queries (concepts, feelings) → Vector RAG (smart)
    - Complex queries → Combine both!
    """
    
    def __init__(self):
        self.sql_rag = simple_rag_service
        self.vector_rag = vector_rag_service
    
    async def recommend(
        self,
        user_query: str,
        city: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        category: Optional[str] = None,
        is_free: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Smart recommendation using hybrid approach
        
        Automatically chooses best retrieval method based on query type
        """
        
        # Extract city from query if not provided
        if not city:
            extracted_city = self._extract_city_from_query(user_query)
            if extracted_city:
                city = extracted_city
                logger.info(f"Extracted city from query: {city}")
        
        # Analyze query to determine best approach
        query_type = self._analyze_query(user_query)
        
        if query_type == "structured":
            # Use fast SQL RAG
            logger.info(f"Using SQL RAG for structured query: {user_query}")
            result = await self.sql_rag.recommend_activities(
                user_query=user_query,
                city=city,
                age_min=age_min,
                age_max=age_max,
                category=category,
                is_free=is_free
            )
            result["retrieval_strategy"] = "SQL (structured query)"
            result["method_used"] = "sql"
            return result
            
        elif query_type == "semantic":
            # Use vector RAG for semantic understanding
            logger.info(f"Using Vector RAG for semantic query: {user_query}")
            result = await self.vector_rag.get_recommendations(
                user_query=user_query,
                city=city,
                age_min=age_min,
                age_max=age_max,
                category=category,
                is_free=is_free
            )
            result["retrieval_strategy"] = "Vector (semantic query)"
            result["method_used"] = "vector_search_semantic"
            return result
            
        else:
            # Use vector RAG for complex queries
            logger.info(f"Using Vector RAG for complex query: {user_query}")
            result = await self.vector_rag.get_recommendations(
                user_query=user_query,
                city=city,
                age_min=age_min,
                age_max=age_max,
                category=category,
                is_free=is_free
            )
            result["retrieval_strategy"] = "Vector (complex query)"
            result["method_used"] = "vector_search_semantic"
            return result
    
    def _extract_city_from_query(self, query: str) -> Optional[str]:
        """
        Extract city name from natural language query
        
        Examples:
        - "basketball in Detroit" → "Detroit"
        - "museums near Troy" → "Troy"
        - "swimming in birmingham" → "Birmingham"
        """
        
        # Common Michigan cities in the database
        known_cities = [
            'detroit', 'troy', 'birmingham', 'bloomfield hills', 'novi',
            'sterling heights', 'rochester', 'rochester hills', 'royal oak',
            'farmington', 'farmington hills', 'madison heights', 'shelby township',
            'southfield', 'westland', 'livonia', 'ferndale', 'warren',
            'ann arbor', 'sandusky'
        ]
        
        query_lower = query.lower()
        
        # Patterns to extract city: "in [city]", "near [city]", "at [city]"
        city_patterns = [
            r'\bin\s+([a-z\s]+?)(?:\s+for|\s+with|\s+area|$|\s+\w)',
            r'\bnear\s+([a-z\s]+?)(?:\s+for|\s+with|\s+area|$|\s+\w)',
            r'\bat\s+([a-z\s]+?)(?:\s+for|\s+with|\s+area|$|\s+\w)',
            r'\baround\s+([a-z\s]+?)(?:\s+for|\s+with|\s+area|$|\s+\w)',
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, query_lower)
            if match:
                potential_city = match.group(1).strip()
                # Check if it matches a known city
                for known_city in known_cities:
                    if known_city in potential_city or potential_city in known_city:
                        # Return with proper capitalization
                        return known_city.title()
        
        # Also check if query ends with a city name
        for known_city in known_cities:
            if query_lower.endswith(known_city) or query_lower.endswith(known_city + ' '):
                return known_city.title()
        
        return None
    
    def _analyze_query(self, query: str) -> str:
        """
        Analyze query to determine if it's structured or semantic
        
        Returns:
            "structured" - Use SQL RAG
            "semantic" - Use Vector RAG
            "complex" - Use Vector RAG
        """
        
        query_lower = query.lower()
        
        # Structured query indicators
        structured_patterns = [
            r'\b\d+\s*year\s*old',  # "8 year old"
            r'\b\d+\s*to\s*\d+',     # "5 to 12"
            r'\bages?\s*\d+',        # "age 8"
            r'\bin\s+\w+',           # "in Troy"
            r'\bnear\s+\d{5}',       # "near 48083"
        ]
        
        structured_keywords = [
            'museum', 'playground', 'park',
            'free', 'paid', 'indoor', 'outdoor', 'weekend', 'saturday', 'sunday',
            # Sports and specific activities (should use SQL filtering)
            'basketball', 'soccer', 'football', 'baseball', 'tennis', 'swimming',
            'hockey', 'volleyball', 'martial arts', 'karate', 'judo', 'taekwondo',
            'dance', 'ballet', 'gymnastics', 'yoga', 'fitness', 'gym',
            'sports', 'athletics', 'recreation', 'camp', 'class', 'lesson'
        ]
        
        # Semantic query indicators
        semantic_keywords = [
            'confidence', 'shy', 'anxious', 'energetic', 'curious',
            'creative', 'social', 'quiet', 'active', 'calm',
            'learning', 'fun', 'exciting', 'educational',
            'build', 'develop', 'improve', 'help with'
        ]
        
        # Check for structured patterns
        has_structured_pattern = any(re.search(pattern, query_lower) for pattern in structured_patterns)
        has_structured_keywords = any(kw in query_lower for kw in structured_keywords)
        
        # Check for semantic keywords
        has_semantic_keywords = any(kw in query_lower for kw in semantic_keywords)
        
        # Decision logic
        if has_structured_pattern or (has_structured_keywords and not has_semantic_keywords):
            return "structured"
        elif has_semantic_keywords:
            return "semantic"
        else:
            return "complex"


# Global instance
hybrid_rag_service = HybridRAGService()
