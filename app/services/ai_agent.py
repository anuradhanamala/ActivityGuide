"""
AI Agent for event personalization and summarization
"""

from typing import List, Dict, Any, Optional
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from app.core.config import settings
from app.schemas.event import Event, EventSearchResponse
import logging

logger = logging.getLogger(__name__)


class EventPersonalizationAgent:
    """AI agent for personalizing event recommendations"""
    
    def __init__(self):
        # Use Anthropic if available, otherwise fallback to OpenAI
        if settings.ANTHROPIC_API_KEY:
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0.7,
                anthropic_api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=settings.OPENAI_API_KEY
            )
        
        self.personalization_prompt = PromptTemplate(
            input_variables=["events", "user_profile", "zip_code"],
            template="""
            You are a helpful assistant that personalizes family activity recommendations for parents.
            
            User Profile:
            - Children ages: {children_ages}
            - Preferred categories: {preferred_categories}
            - Activity preferences: {preferred_activity_types}
            - Default location: {zip_code}
            
            Available Events:
            {events}
            
            Please provide:
            1. A personalized summary of the top 3-5 most relevant events
            2. Brief explanations of why these events are good for this family
            3. Any age-appropriate considerations
            4. Format the response in a friendly, parent-focused tone
            
            Keep the summary concise but informative, focusing on what makes each event special for families.
            """
        )
    
    async def personalize_events(
        self, 
        events: List[Event], 
        user_profile: Optional[Dict[str, Any]] = None,
        zip_code: str = None
    ) -> EventSearchResponse:
        """Personalize event recommendations based on user profile"""
        
        if not events:
            return EventSearchResponse(
                events=[],
                total_count=0,
                filters_applied={},
                search_summary="No events found for your search criteria."
            )
        
        # Extract user profile data
        children_ages = user_profile.get("children_ages", []) if user_profile else []
        preferred_categories = user_profile.get("preferred_categories", []) if user_profile else []
        preferred_activity_types = user_profile.get("preferred_activity_types", []) if user_profile else []
        
        # Format events for AI processing
        events_text = self._format_events_for_ai(events[:10])  # Limit to top 10 for processing
        
        try:
            # Generate personalized summary
            summary = await self._generate_personalized_summary(
                events_text, 
                children_ages, 
                preferred_categories, 
                preferred_activity_types,
                zip_code
            )
            
            # Score and rank events based on user preferences
            scored_events = await self._score_events(events, user_profile)
            
            return EventSearchResponse(
                events=scored_events,
                total_count=len(events),
                filters_applied={"zip_code": zip_code},
                search_summary=summary
            )
            
        except Exception as e:
            logger.error(f"AI personalization error: {e}")
            # Fallback to basic response
            return EventSearchResponse(
                events=events,
                total_count=len(events),
                filters_applied={"zip_code": zip_code},
                search_summary="Here are some great family activities in your area!"
            )
    
    def _format_events_for_ai(self, events: List[Event]) -> str:
        """Format events for AI processing"""
        formatted_events = []
        
        for event in events:
            event_text = f"""
            Title: {event.title}
            Date/Time: {event.start_time}
            Location: {event.location_name} ({event.city})
            Category: {event.category}
            Age Range: {event.age_range_min or 'Any'}-{event.age_range_max or 'Any'} years
            Indoor/Outdoor: {'Indoor' if event.is_indoor else 'Outdoor'}
            Cost: {'Free' if event.is_free else 'Paid'}
            Description: {event.description or 'No description available'}
            """
            formatted_events.append(event_text.strip())
        
        return "\n\n".join(formatted_events)
    
    async def _generate_personalized_summary(
        self, 
        events_text: str, 
        children_ages: List[int],
        preferred_categories: List[str],
        preferred_activity_types: List[str],
        zip_code: str
    ) -> str:
        """Generate personalized summary using AI"""
        
        prompt = self.personalization_prompt.format(
            events=events_text,
            children_ages=children_ages,
            preferred_categories=preferred_categories,
            preferred_activity_types=preferred_activity_types,
            zip_code=zip_code
        )
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            logger.error(f"AI summary generation error: {e}")
            return "Here are some great family activities in your area!"
    
    async def _score_events(
        self, 
        events: List[Event], 
        user_profile: Optional[Dict[str, Any]]
    ) -> List[Event]:
        """Score and rank events based on user preferences"""
        
        if not user_profile:
            return events
        
        scored_events = []
        
        for event in events:
            score = 0
            
            # Age appropriateness scoring
            children_ages = user_profile.get("children_ages", [])
            if children_ages:
                for age in children_ages:
                    if (event.age_range_min is None or age >= event.age_range_min) and \
                       (event.age_range_max is None or age <= event.age_range_max):
                        score += 10
            
            # Category preference scoring
            preferred_categories = user_profile.get("preferred_categories", [])
            if preferred_categories and event.category in preferred_categories:
                score += 15
            
            # Activity type preference scoring
            preferred_activity_types = user_profile.get("preferred_activity_types", [])
            if preferred_activity_types:
                if "indoor" in preferred_activity_types and event.is_indoor:
                    score += 5
                if "outdoor" in preferred_activity_types and not event.is_indoor:
                    score += 5
            
            # Free events bonus for families
            if event.is_free:
                score += 5
            
            scored_events.append((event, score))
        
        # Sort by score (highest first) and return events
        scored_events.sort(key=lambda x: x[1], reverse=True)
        return [event for event, score in scored_events]


class EventSummarizationAgent:
    """AI agent for generating event summaries"""
    
    def __init__(self):
        # Use Anthropic if available, otherwise fallback to OpenAI
        if settings.ANTHROPIC_API_KEY:
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0.5,
                anthropic_api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.5,
                openai_api_key=settings.OPENAI_API_KEY
            )
        
        self.summarization_prompt = PromptTemplate(
            input_variables=["title", "description", "category", "age_range", "is_free"],
            template="""
            Create a concise, parent-friendly summary for this family activity:
            
            Title: {title}
            Description: {description}
            Category: {category}
            Age Range: {age_range}
            Cost: {is_free}
            
            Requirements:
            - Keep it under 100 words
            - Focus on what kids will enjoy
            - Mention age appropriateness
            - Include practical details (cost, indoor/outdoor)
            - Use an engaging, parent-friendly tone
            - Highlight unique or special aspects
            
            Format as a brief, informative paragraph that parents can quickly read and understand.
            """
        )
    
    async def generate_event_summary(self, event: Event) -> str:
        """Generate an AI summary for a single event"""
        
        age_range = f"{event.age_range_min or 'Any'}-{event.age_range_max or 'Any'} years" if event.age_range_min or event.age_range_max else "All ages"
        cost_info = "Free" if event.is_free else "Paid event"
        
        prompt = self.summarization_prompt.format(
            title=event.title,
            description=event.description or "No description provided",
            category=event.category or "Family activity",
            age_range=age_range,
            is_free=cost_info
        )
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            logger.error(f"AI summary generation error: {e}")
            # Fallback to basic summary
            return f"A fun {event.category or 'family'} activity at {event.location_name or 'this location'}. {cost_info}."
    
    async def generate_batch_summaries(self, events: List[Event]) -> Dict[int, str]:
        """Generate summaries for multiple events"""
        
        summaries = {}
        
        # Process events in batches to avoid rate limits
        batch_size = 5
        for i in range(0, len(events), batch_size):
            batch = events[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [self.generate_event_summary(event) for event in batch]
            batch_summaries = await asyncio.gather(*tasks, return_exceptions=True)
            
            for j, summary in enumerate(batch_summaries):
                if isinstance(summary, str):
                    summaries[batch[j].id] = summary
                else:
                    logger.error(f"Summary generation failed for event {batch[j].id}: {summary}")
                    summaries[batch[j].id] = f"Family activity at {batch[j].location_name or 'this location'}."
        
        return summaries
