"""
Simple RAG service without vector embeddings
Uses SQL queries for retrieval + LLM for generation
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any, Optional
import logging

from app.core.config import settings
from app.core.database import get_db
from app.models.unified_event import UnifiedEvent

logger = logging.getLogger(__name__)


class SimpleRAGService:
    """
    RAG service using simple SQL retrieval (no vector search needed!)
    
    RAG = Retrieval + Augmentation + Generation
    - Retrieval: SQL queries (simple WHERE clauses)
    - Augmentation: Format data as text context
    - Generation: LLM creates personalized response
    """
    
    def __init__(self):
        if settings.ANTHROPIC_API_KEY:
            self.llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0.7,
                anthropic_api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            logger.warning("Anthropic API key not configured for RAG")
            self.llm = None
    
    async def recommend_activities(
        self, 
        user_query: str,
        city: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        category: Optional[str] = None,
        is_free: Optional[bool] = None,
        limit: int = 15
    ) -> Dict[str, Any]:
        """
        Get AI-powered activity recommendations
        
        Example:
            query = "What should I do with my shy 8-year-old?"
            result = await rag.recommend_activities(
                user_query=query,
                city="Troy",
                age_min=8,
                age_max=8
            )
        """
        
        if not self.llm:
            return {
                "query": user_query,
                "recommendations": "RAG service not available (Anthropic API key not configured)",
                "events_count": 0
            }
        
        try:
            # STEP 1: RETRIEVE events using simple SQL
            events = self._retrieve_events(city, age_min, age_max, category, is_free, limit)
            
            if not events:
                return {
                    "query": user_query,
                    "recommendations": f"No activities found in {city or 'your area'} matching the criteria. Try adjusting your filters or searching a different location.",
                    "events_count": 0
                }
            
            logger.info(f"RAG retrieved {len(events)} events for query: {user_query}")
            
            # STEP 2: AUGMENT - Build context from events
            context = self._build_context(events)
            
            # STEP 3: GENERATE - LLM creates recommendations
            recommendations = await self._generate_recommendations(user_query, context, city, age_min, age_max)
            
            return {
                "query": user_query,
                "recommendations": recommendations,
                "events_count": len(events),
                "retrieval_method": "SQL Query (no vectors)",
                "events_included": [
                    {
                        "id": str(e.id),
                        "title": e.title,
                        "source": e.source.value,
                        "city": e.city
                    } for e in events[:10]  # Include top 10 for reference
                ]
            }
            
        except Exception as e:
            logger.error(f"RAG recommendation error: {e}")
            return {
                "query": user_query,
                "recommendations": f"Error generating recommendations: {str(e)}",
                "events_count": 0
            }
    
    def _retrieve_events(
        self,
        city: Optional[str],
        age_min: Optional[int],
        age_max: Optional[int],
        category: Optional[str],
        is_free: Optional[bool],
        limit: int
    ) -> List[UnifiedEvent]:
        """
        RETRIEVAL: Simple SQL queries (no embeddings needed!)
        """
        
        db = next(get_db())
        
        try:
            # Start with active events
            query = db.query(UnifiedEvent).filter(UnifiedEvent.is_active == True)
            
            # Apply filters using simple WHERE clauses
            if city:
                query = query.filter(UnifiedEvent.city.like(f"%{city}%"))
            
            if age_min is not None and age_max is not None:
                query = query.filter(
                    ((UnifiedEvent.age_range_min <= age_max) & 
                     (UnifiedEvent.age_range_max >= age_min)) |
                    (UnifiedEvent.age_range_min.is_(None))  # Include all-ages
                )
            elif age_min is not None:
                query = query.filter(
                    (UnifiedEvent.age_range_max >= age_min) |
                    (UnifiedEvent.age_range_min.is_(None))
                )
            elif age_max is not None:
                query = query.filter(
                    (UnifiedEvent.age_range_min <= age_max) |
                    (UnifiedEvent.age_range_min.is_(None))
                )
            
            if category:
                query = query.filter(
                    UnifiedEvent.primary_category.like(f"%{category}%")
                )
            
            if is_free is not None:
                query = query.filter(UnifiedEvent.is_free == is_free)
            
            # Order by quality score and limit results
            events = query.order_by(
                UnifiedEvent.data_quality_score.desc(),
                UnifiedEvent.priority_score.desc()
            ).limit(limit).all()
            
            return events
            
        finally:
            db.close()
    
    def _build_context(self, events: List[UnifiedEvent]) -> str:
        """
        AUGMENTATION: Format events as readable context
        No fancy processing - just format as text!
        """
        
        context_lines = []
        
        for i, event in enumerate(events, 1):
            # Build readable description
            age_range = "All ages"
            if event.age_range_min is not None and event.age_range_max is not None:
                age_range = f"{event.age_range_min}-{event.age_range_max} years"
            elif event.age_range_min is not None:
                age_range = f"{event.age_range_min}+ years"
            
            price_info = "FREE" if event.is_free else "Paid"
            if event.price_min and event.price_max:
                price_info = f"${event.price_min}-${event.price_max}"
            
            location_info = "Indoor" if event.is_indoor else "Outdoor" if event.is_outdoor else "Flexible"
            
            context_lines.append(f"""
{i}. {event.title}
   Source: {event.source.value.upper()}
   Type: {event.event_type.value}
   Location: {event.location_name or event.address or event.city}
   City: {event.city}, {event.state}
   Category: {event.primary_category or 'General'}
   Ages: {age_range}
   Price: {price_info}
   Setting: {location_info}
   Tags: {', '.join(event.tags[:5]) if event.tags else 'None'}
   Description: {(event.description or '')[:200]}...
""")
        
        return "\n".join(context_lines)
    
    async def _generate_recommendations(
        self,
        user_query: str,
        context: str,
        city: Optional[str],
        age_min: Optional[int],
        age_max: Optional[int]
    ) -> str:
        """
        GENERATION: LLM creates personalized recommendations
        """
        
        # Build age context
        age_context = ""
        if age_min and age_max:
            if age_min == age_max:
                age_context = f"for a {age_min}-year-old"
            else:
                age_context = f"for ages {age_min}-{age_max}"
        elif age_min:
            age_context = f"for ages {age_min}+"
        
        location_context = f"in {city}" if city else "in your area"
        
        messages = [
            SystemMessage(content="""You are a helpful and friendly family activity assistant for parents.

Your role:
- Provide 3-5 specific activity recommendations
- Explain WHY each is a good match for the user's needs
- Include practical details: price, location, age-appropriateness
- Be warm, conversational, and supportive
- Prioritize activities that best match the user's question
- Be honest about pros and cons
- Keep responses concise but informative

Format your response clearly with numbered recommendations."""),
            
            HumanMessage(content=f"""
User Question: "{user_query}"
{f"Looking for activities {age_context} {location_context}" if age_context or city else ""}

Available Activities:
{context}

Based on these activities, please provide personalized recommendations.
For each recommendation:
1. Name the specific activity
2. Explain why it matches their needs
3. Include key details (price, location, ages)
4. Add any helpful tips or considerations""")
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content


# Global instance
simple_rag_service = SimpleRAGService()
