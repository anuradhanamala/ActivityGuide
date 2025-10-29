"""
Smart Orchestration Agent using LangChain
Autonomous AI agent that manages activity data across USA

Features:
- Auto-syncs cities based on intelligent decisions
- Creates embeddings automatically
- Optimizes search thresholds contextually
- Self-monitors and self-heals
- Works across any US city
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic  # Using Claude instead of GPT!
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy import func

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.unified_event import UnifiedEvent, EventSource
from app.services.unified_sync_service import UnifiedSyncService
from app.services.geocoding_service import geocoding_service
from app.services.hybrid_rag import hybrid_rag_service

# Configure logging with file handler
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Add file handler for agent operations
file_handler = logging.FileHandler("logs/agent_service.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


# ============================================================================
# LANGCHAIN TOOLS - Agent's Capabilities
# ============================================================================

@tool
async def check_city_data_freshness(city: str, state: str = "MI") -> Dict[str, Any]:
    """
    Check how fresh the activity data is for a given city.
    
    Args:
        city: City name (e.g., 'Troy', 'Detroit', 'New York')
        state: State code (e.g., 'MI', 'NY', 'CA')
    
    Returns:
        Data freshness metrics including age, event count, last sync time
    """
    db = SessionLocal()
    try:
        # Get event count for city
        event_count = db.query(UnifiedEvent).filter(
            func.lower(UnifiedEvent.city) == city.lower(),
            func.lower(UnifiedEvent.state) == state.upper()
        ).count()
        
        # Get most recent event
        latest_event = db.query(UnifiedEvent).filter(
            func.lower(UnifiedEvent.city) == city.lower()
        ).order_by(UnifiedEvent.created_at.desc()).first()
        
        if latest_event:
            age_hours = (datetime.now() - latest_event.created_at).total_seconds() / 3600
            last_sync = latest_event.created_at.isoformat()
        else:
            age_hours = None
            last_sync = None
        
        return {
            "city": city,
            "state": state,
            "event_count": event_count,
            "data_age_hours": age_hours,
            "last_sync": last_sync,
            "needs_sync": age_hours is None or age_hours > 24 or event_count < 5
        }
    finally:
        db.close()


@tool
async def sync_city_data(city: str, state: str = "MI", sources: List[str] = None) -> Dict[str, Any]:
    """
    Sync activity data for a specific city from multiple sources.
    
    Args:
        city: City name
        state: State code
        sources: List of sources to sync from (default: all sources)
    
    Returns:
        Sync results including events created and updated
    """
    try:
        logger.info(f"🤖 Agent: Syncing {city}, {state}")
        
        # Convert city to ZIP codes
        zip_codes, method = await geocoding_service.get_zip_codes_for_city(city, state)
        logger.info(f"🤖 Agent: {city} → {len(zip_codes)} ZIP codes")
        
        # Convert source strings to EventSource enums
        source_enums = None
        if sources:
            source_enums = [EventSource(s) for s in sources]
        
        # Perform sync
        db = SessionLocal()
        try:
            sync_service = UnifiedSyncService()
            result = await sync_service.sync_all_sources(db, zip_codes, source_enums)
            
            logger.info(f"✅ Agent: Sync completed - Created: {result.get('events_created', 0)}, Updated: {result.get('events_updated', 0)}")
            
            return {
                "success": True,
                "city": city,
                "state": state,
                "zip_codes": zip_codes,
                "events_created": result.get('events_created', 0),
                "events_updated": result.get('events_updated', 0),
                "duration": result.get('duration', 0)
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Agent: Sync failed for {city}: {e}")
        return {
            "success": False,
            "city": city,
            "error": str(e)
        }


@tool
async def create_embeddings_for_city(city: str, state: str = "MI") -> Dict[str, Any]:
    """
    Create vector embeddings for events in a city that don't have embeddings yet.
    
    Args:
        city: City name
        state: State code
    
    Returns:
        Number of embeddings created
    """
    from sentence_transformers import SentenceTransformer
    import chromadb
    import os
    
    try:
        logger.info(f"🤖 Agent: Creating embeddings for {city}, {state}")
        
        # Initialize
        model = SentenceTransformer('all-MiniLM-L6-v2')
        os.environ['CHROMA_TELEMETRY'] = 'false'
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_or_create_collection(name="unified_events")
        
        # Get events without embeddings
        db = SessionLocal()
        try:
            # Get events for this city
            events = db.query(UnifiedEvent).filter(
                func.lower(UnifiedEvent.city) == city.lower(),
                func.lower(UnifiedEvent.state) == state.upper()
            ).all()
            
            embedded_count = 0
            for event in events:
                # Create document text
                doc_text = f"""
                Title: {event.title}
                Description: {event.description or 'N/A'}
                Category: {event.primary_category}
                Location: {event.city}, {event.state}
                Tags: {', '.join(event.tags or [])}
                """
                
                # Generate embedding
                embedding = model.encode(doc_text)
                
                # Store in ChromaDB
                collection.add(
                    ids=[str(event.id)],
                    embeddings=[embedding.tolist()],
                    documents=[doc_text],
                    metadatas=[{
                        "city": event.city,
                        "state": event.state,
                        "category": event.primary_category
                    }]
                )
                embedded_count += 1
            
            logger.info(f"✅ Agent: Created {embedded_count} embeddings for {city}")
            
            return {
                "success": True,
                "city": city,
                "state": state,
                "embeddings_created": embedded_count
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Agent: Embedding creation failed for {city}: {e}")
        return {
            "success": False,
            "city": city,
            "error": str(e)
        }


@tool
async def analyze_search_quality(city: str, state: str = "MI") -> Dict[str, Any]:
    """
    Analyze search quality for a city to determine if data refresh is needed.
    
    Args:
        city: City name
        state: State code
    
    Returns:
        Quality metrics and recommendations
    """
    db = SessionLocal()
    try:
        # Get events for city
        events = db.query(UnifiedEvent).filter(
            func.lower(UnifiedEvent.city) == city.lower()
        ).all()
        
        if not events:
            return {
                "city": city,
                "quality_score": 0,
                "recommendation": "No data found - sync immediately",
                "needs_sync": True
            }
        
        # Calculate quality metrics
        total = len(events)
        with_description = sum(1 for e in events if e.description)
        with_phone = sum(1 for e in events if e.contact_phone)
        with_website = sum(1 for e in events if e.website_url)
        with_category = sum(1 for e in events if e.primary_category)
        
        quality_score = (
            (with_description / total) * 0.3 +
            (with_phone / total) * 0.2 +
            (with_website / total) * 0.2 +
            (with_category / total) * 0.3
        )
        
        # Determine recommendation
        if quality_score < 0.5:
            recommendation = "Low quality - sync with enhanced extraction"
            needs_sync = True
        elif quality_score < 0.7:
            recommendation = "Medium quality - consider refresh"
            needs_sync = False
        else:
            recommendation = "Good quality - no immediate action needed"
            needs_sync = False
        
        return {
            "city": city,
            "state": state,
            "total_events": total,
            "quality_score": round(quality_score, 2),
            "completeness": {
                "description": f"{(with_description/total)*100:.0f}%",
                "phone": f"{(with_phone/total)*100:.0f}%",
                "website": f"{(with_website/total)*100:.0f}%",
                "category": f"{(with_category/total)*100:.0f}%"
            },
            "recommendation": recommendation,
            "needs_sync": needs_sync
        }
    finally:
        db.close()


@tool
async def get_popular_cities_usa() -> List[Dict[str, str]]:
    """
    Get list of popular US cities that should have activity data.
    
    Returns:
        List of cities with state codes
    """
    return [
        # Michigan
        {"city": "Troy", "state": "MI"},
        {"city": "Detroit", "state": "MI"},
        {"city": "Warren", "state": "MI"},
        {"city": "Sterling Heights", "state": "MI"},
        {"city": "Novi", "state": "MI"},
        {"city": "Ann Arbor", "state": "MI"},
        
        # California
        {"city": "Los Angeles", "state": "CA"},
        {"city": "San Francisco", "state": "CA"},
        {"city": "San Diego", "state": "CA"},
        {"city": "San Jose", "state": "CA"},
        
        # New York
        {"city": "New York", "state": "NY"},
        {"city": "Buffalo", "state": "NY"},
        {"city": "Rochester", "state": "NY"},
        
        # Texas
        {"city": "Houston", "state": "TX"},
        {"city": "Dallas", "state": "TX"},
        {"city": "Austin", "state": "TX"},
        
        # Florida
        {"city": "Miami", "state": "FL"},
        {"city": "Orlando", "state": "FL"},
        {"city": "Tampa", "state": "FL"},
        
        # Illinois
        {"city": "Chicago", "state": "IL"},
        
        # Washington
        {"city": "Seattle", "state": "WA"},
        
        # Massachusetts
        {"city": "Boston", "state": "MA"},
    ]


@tool
async def optimize_search_threshold(query: str, city: str, current_results: int) -> float:
    """
    Determine optimal search threshold based on query and context.
    
    Args:
        query: User's search query
        city: City being searched
        current_results: Number of results with current threshold
    
    Returns:
        Recommended threshold value
    """
    # Analyze query specificity
    specific_keywords = ['swim', 'basketball', 'soccer', 'karate', 'piano']
    is_specific = any(keyword in query.lower() for keyword in specific_keywords)
    
    # Broad keywords
    broad_keywords = ['fun', 'activities', 'things to do', 'events']
    is_broad = any(keyword in query.lower() for keyword in broad_keywords)
    
    # Base threshold
    threshold = 1.20
    
    # Adjust based on specificity
    if is_specific and current_results >= 5:
        threshold = 1.10  # Strict - we have enough specific results
    elif is_specific and current_results < 5:
        threshold = 1.30  # Relaxed - need more results
    elif is_broad:
        threshold = 1.40  # Very relaxed for broad queries
    
    # Adjust for result count
    if current_results == 0:
        threshold = 1.50  # Very relaxed if no results
    elif current_results > 20:
        threshold = 1.00  # Very strict if too many results
    
    return threshold


@tool
async def calculate_city_thresholds(city: str, state: str = "MI") -> Dict[str, Any]:
    """
    Calculate optimal default search thresholds for a city based on data characteristics.
    
    Args:
        city: City name
        state: State code
    
    Returns:
        Recommended thresholds for different query types
    """
    db = SessionLocal()
    try:
        # Get city statistics
        total_events = db.query(UnifiedEvent).filter(
            func.lower(UnifiedEvent.city) == city.lower(),
            func.lower(UnifiedEvent.state) == state.upper()
        ).count()
        
        # Count categories
        categories = db.query(UnifiedEvent.primary_category).filter(
            func.lower(UnifiedEvent.city) == city.lower()
        ).distinct().count()
        
        # Calculate recommended thresholds based on data volume
        if total_events < 10:
            # Very few events - use relaxed thresholds
            base_threshold = 1.50
            specific_threshold = 1.40
            broad_threshold = 1.60
        elif total_events < 50:
            # Small dataset - slightly relaxed
            base_threshold = 1.30
            specific_threshold = 1.20
            broad_threshold = 1.40
        elif total_events < 200:
            # Medium dataset - balanced
            base_threshold = 1.20
            specific_threshold = 1.10
            broad_threshold = 1.30
        else:
            # Large dataset - can be strict
            base_threshold = 1.10
            specific_threshold = 1.00
            broad_threshold = 1.20
        
        return {
            "city": city,
            "state": state,
            "total_events": total_events,
            "categories": categories,
            "recommended_thresholds": {
                "base": base_threshold,
                "specific_queries": specific_threshold,
                "broad_queries": broad_threshold
            },
            "data_quality": "excellent" if total_events > 100 else "good" if total_events > 50 else "limited"
        }
    finally:
        db.close()


# ============================================================================
# SMART ORCHESTRATION AGENT
# ============================================================================

class SmartOrchestrationAgent:
    """
    Autonomous AI agent powered by LangChain that intelligently manages
    activity data across the USA.
    """
    
    def __init__(self):
        """Initialize the agent with LangChain"""
        
        # Initialize LLM - Using Claude-3 Haiku (best value: cheap, fast, intelligent)
        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",  # 50% cheaper than GPT-3.5, faster, more intelligent!
            temperature=0.1,  # Low temperature for consistent decisions
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )
        
        # Define agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Smart Orchestration Agent for a Kid Activity Aggregator platform 
            that operates across the entire USA.
            
            Your responsibilities:
            1. Monitor data freshness for cities and decide when to sync
            2. Automatically create embeddings when new data is added
            3. Optimize search thresholds based on context
            4. Ensure high-quality data across all cities
            5. Proactively maintain the system
            
            Decision-making principles:
            - Prioritize cities with stale data (>24 hours old)
            - Sync cities with < 5 events
            - Create embeddings immediately after sync
            - Use strict thresholds for specific queries
            - Use relaxed thresholds for broad queries
            
            You can work with ANY city in the USA - the geocoding service will handle
            converting any city to appropriate ZIP codes.
            
            Be proactive, intelligent, and autonomous."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create tools list
        self.tools = [
            check_city_data_freshness,
            sync_city_data,
            create_embeddings_for_city,
            analyze_search_quality,
            get_popular_cities_usa,
            optimize_search_threshold,
            calculate_city_thresholds
        ]
        
        # Create agent
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create executor (without deprecated memory)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=200  # High limit for batch city processing (20 cities × ~10 steps each)
        )
        
        # Manual chat history management (modern approach)
        self.chat_history = []
        
        logger.info("🤖 Smart Orchestration Agent initialized with LangChain")
    
    async def run_autonomous_cycle(self):
        """
        Run one cycle of autonomous operations.
        Agent decides what to do based on system state.
        """
        try:
            logger.info("="*80)
            logger.info("🤖 AGENT: Starting autonomous cycle")
            logger.info("="*80)
            
            # Ask agent to analyze and act
            response = await self.agent_executor.ainvoke({
                "input": """Perform your autonomous cycle:
                
                1. Check popular cities and see which ones need data refresh
                2. For cities with stale data (>24 hours) or low event count (<5), sync them
                3. After syncing, create embeddings for the new data
                4. Analyze data quality for at least 3 cities
                
                Focus on Michigan cities (Troy, Warren, Detroit) first, then expand to other states.
                
                Provide a summary of your actions and decisions.""",
                "chat_history": self.chat_history
            })
            
            logger.info("="*80)
            logger.info("🤖 AGENT: Cycle complete")
            logger.info(f"📊 Result: {response['output']}")
            logger.info("="*80)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ AGENT: Autonomous cycle failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def handle_user_request(self, request: str):
        """
        Handle a specific user request.
        
        Args:
            request: Natural language request from user
        """
        try:
            logger.info(f"🤖 AGENT: Handling request: {request}")
            
            response = await self.agent_executor.ainvoke({
                "input": request,
                "chat_history": self.chat_history
            })
            
            # Extract text from response (handle both string and list formats)
            output = response['output']
            if isinstance(output, list):
                # New Anthropic format: list of message parts
                text_parts = [part.get('text', '') for part in output if part.get('type') == 'text']
                output_text = ' '.join(text_parts)
            elif isinstance(output, str):
                # Standard string format
                output_text = output
            else:
                # Unknown format, convert to string
                output_text = str(output)
            
            # Update chat history for conversational context
            self.chat_history.append(HumanMessage(content=request))
            self.chat_history.append(AIMessage(content=output_text))
            
            # Keep history manageable (last 10 messages)
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return output_text
            
        except Exception as e:
            logger.error(f"❌ AGENT: Request handling failed: {e}")
            return f"Error: {str(e)}"
    
    async def run_forever(self, interval_minutes: int = 60):
        """
        Run agent autonomously on a schedule.
        
        Args:
            interval_minutes: How often to run the autonomous cycle
        """
        logger.info(f"🤖 AGENT: Starting autonomous mode (interval: {interval_minutes} minutes)")
        
        while True:
            try:
                await self.run_autonomous_cycle()
                
                logger.info(f"⏰ AGENT: Sleeping for {interval_minutes} minutes...")
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("🛑 AGENT: Stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ AGENT: Error in main loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry


# ============================================================================
# AGENT INSTANCE
# ============================================================================

# Global agent instance
smart_agent = SmartOrchestrationAgent()

