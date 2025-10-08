"""
Vector-based RAG service using ChromaDB for semantic search
Combines with SQLite for structured filtering
"""

import chromadb
from chromadb.config import Settings
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any, Optional, Tuple
import logging
import os

from app.core.config import settings
from app.core.database import get_db
from app.models.unified_event import UnifiedEvent

logger = logging.getLogger(__name__)


class VectorRAGService:
    """
    Advanced RAG using ChromaDB for semantic/vector search
    
    Benefits:
    - Semantic understanding (finds concepts, not just keywords)
    - Synonym matching (swim = aquatics = water sports)
    - Fuzzy matching (handles typos)
    - "Find similar" functionality
    - Better for vague/concept queries
    """
    
    def __init__(self):
        # Initialize LLM
        if settings.ANTHROPIC_API_KEY:
            self.llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0.7,
                anthropic_api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            logger.warning("Anthropic API key not configured")
            self.llm = None
        
        # Initialize embeddings (free, runs locally!)
        # Using sentence-transformers instead of OpenAI to save costs
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",  # Fast, good quality, free!
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # ChromaDB settings
        self.chroma_persist_directory = "./chroma_db"
        self.collection_name = "activity_events"
        
        # Initialize ChromaDB client
        self.chroma_client = None
        self.vector_store = None
        self._initialize_chroma()
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.chroma_persist_directory, exist_ok=True)
            
            # Initialize ChromaDB with persistent storage
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"Loaded existing ChromaDB collection: {self.collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Activity events for semantic search"}
                )
                logger.info(f"Created new ChromaDB collection: {self.collection_name}")
            
            # Initialize LangChain vector store wrapper
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            self.chroma_client = None
            self.vector_store = None
    
    async def build_vector_index(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Build vector embeddings for all events in database
        
        This is a one-time setup (or periodic rebuild)
        Stores embeddings in ChromaDB for fast semantic search
        """
        
        if not self.vector_store:
            return {"error": "ChromaDB not initialized"}
        
        try:
            # Check if already indexed
            existing_count = self.collection.count()
            
            if existing_count > 0 and not force_rebuild:
                return {
                    "status": "already_indexed",
                    "count": existing_count,
                    "message": "Vector index already exists. Use force_rebuild=True to rebuild."
                }
            
            # Get all events from database
            db = next(get_db())
            events = db.query(UnifiedEvent).filter(
                UnifiedEvent.is_active == True
            ).all()
            db.close()
            
            if not events:
                return {"error": "No events found in database"}
            
            logger.info(f"Building vector index for {len(events)} events...")
            
            # Prepare documents for embedding
            documents = []
            metadatas = []
            ids = []
            
            for event in events:
                # Create rich text representation for embedding
                doc_text = self._create_document_text(event)
                
                # Metadata for filtering
                metadata = {
                    "id": str(event.id),
                    "title": event.title,
                    "source": event.source.value,
                    "city": event.city or "",
                    "state": event.state or "",
                    "zip_code": event.zip_code or "",
                    "primary_category": event.primary_category or "",
                    "age_min": event.age_range_min or 0,
                    "age_max": event.age_range_max or 18,
                    "is_free": event.is_free or False,
                    "is_indoor": event.is_indoor or False
                }
                
                documents.append(doc_text)
                metadatas.append(metadata)
                ids.append(str(event.id))
            
            # Clear existing if rebuilding
            if force_rebuild and existing_count > 0:
                self.chroma_client.delete_collection(self.collection_name)
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Activity events for semantic search"}
                )
                self.vector_store = Chroma(
                    client=self.chroma_client,
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings
                )
            
            # Add documents to ChromaDB (in batches for efficiency)
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                self.vector_store.add_texts(
                    texts=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
                
                logger.info(f"Indexed {min(i+batch_size, len(documents))}/{len(documents)} events")
            
            return {
                "status": "success",
                "events_indexed": len(events),
                "collection": self.collection_name,
                "persist_directory": self.chroma_persist_directory,
                "message": f"Successfully indexed {len(events)} events in ChromaDB"
            }
            
        except Exception as e:
            logger.error(f"Error building vector index: {e}")
            return {"error": str(e)}
    
    def _create_document_text(self, event: UnifiedEvent) -> str:
        """
        Create rich text representation of event for embedding
        
        This text captures the semantic meaning of the activity
        """
        
        # Build comprehensive text
        parts = []
        
        # Title (most important)
        parts.append(f"Title: {event.title}")
        
        # Description
        if event.description:
            parts.append(f"Description: {event.description}")
        
        if event.summary:
            parts.append(f"Summary: {event.summary}")
        
        # Type and category
        parts.append(f"Type: {event.event_type.value}")
        parts.append(f"Category: {event.primary_category or 'general'}")
        
        # Tags (important for semantic matching)
        if event.tags:
            parts.append(f"Tags: {', '.join(event.tags)}")
        
        # Age information
        if event.age_range_min and event.age_range_max:
            parts.append(f"Suitable for ages {event.age_range_min} to {event.age_range_max}")
        elif event.age_range_min:
            parts.append(f"For ages {event.age_range_min} and up")
        
        # Location context
        parts.append(f"Location: {event.city or 'Unknown'}, {event.state or 'MI'}")
        if event.location_name:
            parts.append(f"Venue: {event.location_name}")
        
        # Activity characteristics
        if event.is_free:
            parts.append("Free activity")
        
        if event.is_indoor:
            parts.append("Indoor activity")
        elif event.is_outdoor:
            parts.append("Outdoor activity")
        
        # Join all parts
        return " | ".join(parts)
    
    async def semantic_search(
        self,
        query: str,
        city: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        is_free: Optional[bool] = None,
        limit: int = 15
    ) -> List[UnifiedEvent]:
        """
        Semantic search using vector embeddings
        
        This finds activities based on MEANING, not just keywords!
        
        Examples:
            "confidence building" → finds martial arts, theater, leadership
            "educational fun" → finds museums, science centers, STEM
            "burn energy" → finds sports, playgrounds, active games
        """
        
        if not self.vector_store:
            logger.warning("Vector store not initialized, falling back to SQL")
            return self._fallback_sql_search(query, city, age_min, age_max, is_free, limit)
        
        try:
            # Build metadata filter for structured criteria
            where_filter = {}
            
            if city:
                where_filter["city"] = {"$eq": city}
            
            if is_free is not None:
                where_filter["is_free"] = {"$eq": is_free}
            
            # Perform semantic search
            if where_filter:
                results = self.vector_store.similarity_search(
                    query,
                    k=limit,
                    filter=where_filter
                )
            else:
                results = self.vector_store.similarity_search(
                    query,
                    k=limit
                )
            
            # Get full event objects from database
            event_ids = [doc.metadata["id"] for doc in results]
            
            db = next(get_db())
            events = db.query(UnifiedEvent).filter(
                UnifiedEvent.id.in_(event_ids)
            ).all()
            
            # Sort events in the same order as vector search results
            event_dict = {str(e.id): e for e in events}
            ordered_events = [event_dict[eid] for eid in event_ids if eid in event_dict]
            
            # Apply age filter if needed (post-processing)
            if age_min is not None or age_max is not None:
                ordered_events = [
                    e for e in ordered_events
                    if self._matches_age_range(e, age_min, age_max)
                ]
            
            db.close()
            
            return ordered_events[:limit]
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            # Fallback to SQL
            return self._fallback_sql_search(query, city, age_min, age_max, is_free, limit)
    
    def _matches_age_range(
        self,
        event: UnifiedEvent,
        age_min: Optional[int],
        age_max: Optional[int]
    ) -> bool:
        """Check if event matches age range"""
        
        if age_min is None and age_max is None:
            return True
        
        # If event has no age range, include it (assume all ages)
        if event.age_range_min is None and event.age_range_max is None:
            return True
        
        # Check overlap
        if age_min and age_max:
            return (event.age_range_min <= age_max and event.age_range_max >= age_min)
        elif age_min:
            return event.age_range_max is None or event.age_range_max >= age_min
        elif age_max:
            return event.age_range_min is None or event.age_range_min <= age_max
        
        return True
    
    def _fallback_sql_search(
        self,
        query: str,
        city: Optional[str],
        age_min: Optional[int],
        age_max: Optional[int],
        is_free: Optional[bool],
        limit: int
    ) -> List[UnifiedEvent]:
        """Fallback to simple SQL search if vector search fails"""
        
        db = next(get_db())
        
        query_obj = db.query(UnifiedEvent).filter(UnifiedEvent.is_active == True)
        
        if city:
            query_obj = query_obj.filter(UnifiedEvent.city.like(f"%{city}%"))
        
        if is_free is not None:
            query_obj = query_obj.filter(UnifiedEvent.is_free == is_free)
        
        if age_min and age_max:
            query_obj = query_obj.filter(
                (UnifiedEvent.age_range_min <= age_max) &
                (UnifiedEvent.age_range_max >= age_min)
            )
        
        events = query_obj.limit(limit).all()
        db.close()
        
        return events
    
    async def get_recommendations(
        self,
        user_query: str,
        city: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        category: Optional[str] = None,
        is_free: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get AI recommendations using semantic search
        
        This is the main RAG method combining:
        1. Vector search for semantic retrieval
        2. SQL filters for structured criteria
        3. LLM generation for recommendations
        """
        
        if not self.llm:
            return {
                "error": "LLM not configured",
                "recommendations": "RAG service requires Anthropic API key"
            }
        
        try:
            # STEP 1: RETRIEVE using vector search (semantic!)
            events = await self.semantic_search(
                query=user_query,
                city=city,
                age_min=age_min,
                age_max=age_max,
                is_free=is_free,
                limit=15
            )
            
            if not events:
                return {
                    "query": user_query,
                    "recommendations": "No matching activities found. Try different search terms or location.",
                    "events_count": 0,
                    "retrieval_method": "vector_search"
                }
            
            logger.info(f"Vector search retrieved {len(events)} events for: {user_query}")
            
            # STEP 2: AUGMENT - Build context
            context = self._build_context(events)
            
            # STEP 3: GENERATE - LLM creates recommendations
            recommendations = await self._generate_recommendations(
                user_query, context, city, age_min, age_max
            )
            
            return {
                "query": user_query,
                "recommendations": recommendations,
                "events_count": len(events),
                "retrieval_method": "vector_search_semantic",
                "events_included": [
                    {
                        "id": str(e.id),
                        "title": e.title,
                        "source": e.source.value,
                        "city": e.city,
                        "category": e.primary_category
                    } for e in events[:10]
                ]
            }
            
        except Exception as e:
            logger.error(f"Vector RAG error: {e}")
            return {
                "error": str(e),
                "recommendations": f"Error generating recommendations: {str(e)}"
            }
    
    def _build_context(self, events: List[UnifiedEvent]) -> str:
        """Build context from events for LLM"""
        
        context_parts = []
        
        for i, event in enumerate(events, 1):
            age_range = "All ages"
            if event.age_range_min and event.age_range_max:
                age_range = f"{event.age_range_min}-{event.age_range_max} years"
            
            price = "FREE" if event.is_free else "Paid"
            location_type = "Indoor" if event.is_indoor else "Outdoor" if event.is_outdoor else "Flexible"
            
            context_parts.append(f"""
{i}. {event.title}
   Source: {event.source.value.upper()}
   Type: {event.event_type.value}
   Location: {event.city}, {event.state}
   Venue: {event.location_name or 'N/A'}
   Category: {event.primary_category or 'General'}
   Ages: {age_range}
   Price: {price}
   Setting: {location_type}
   Tags: {', '.join(event.tags[:5]) if event.tags else 'None'}
   Description: {(event.description or '')[:200]}
""")
        
        return "\n".join(context_parts)
    
    async def _generate_recommendations(
        self,
        user_query: str,
        context: str,
        city: Optional[str],
        age_min: Optional[int],
        age_max: Optional[int]
    ) -> str:
        """Generate personalized recommendations using LLM"""
        
        age_context = ""
        if age_min and age_max:
            if age_min == age_max:
                age_context = f"for a {age_min}-year-old"
            else:
                age_context = f"for ages {age_min}-{age_max}"
        
        location_context = f"in {city}" if city else ""
        
        messages = [
            SystemMessage(content="""You are a knowledgeable and friendly family activity assistant.

Your strengths:
- Understanding parent needs and concerns
- Matching activities to children's developmental stages
- Providing practical, actionable recommendations
- Being warm and supportive

Guidelines:
- Recommend 3-5 specific activities
- Explain WHY each matches the user's needs
- Include practical details (price, location, age-appropriateness)
- Be honest about pros and cons
- Prioritize safety and age-appropriateness
- Keep responses conversational and helpful"""),
            
            HumanMessage(content=f"""
User Query: "{user_query}"
{f"Looking for activities {age_context} {location_context}".strip()}

Available Activities (sorted by relevance):
{context}

Based on these activities, provide personalized recommendations.
Focus on activities that best match the user's specific needs and concerns.""")
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def find_similar_activities(
        self,
        event_id: str,
        limit: int = 10
    ) -> List[UnifiedEvent]:
        """
        Find activities similar to a given event
        This is only possible with vector embeddings!
        """
        
        if not self.vector_store:
            return []
        
        try:
            # Get the original event
            db = next(get_db())
            source_event = db.query(UnifiedEvent).filter(
                UnifiedEvent.id == event_id
            ).first()
            
            if not source_event:
                return []
            
            # Create query from source event
            query_text = self._create_document_text(source_event)
            
            # Find similar using vector search
            results = self.vector_store.similarity_search(
                query_text,
                k=limit + 1  # +1 because it will include itself
            )
            
            # Get event IDs (exclude the source event)
            similar_ids = [
                doc.metadata["id"] for doc in results 
                if doc.metadata["id"] != event_id
            ][:limit]
            
            # Get full events
            similar_events = db.query(UnifiedEvent).filter(
                UnifiedEvent.id.in_(similar_ids)
            ).all()
            
            db.close()
            
            return similar_events
            
        except Exception as e:
            logger.error(f"Find similar error: {e}")
            return []
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index"""
        
        if not self.collection:
            return {"error": "ChromaDB not initialized"}
        
        try:
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "total_embeddings": count,
                "persist_directory": self.chroma_persist_directory,
                "embedding_model": "all-MiniLM-L6-v2 (HuggingFace)",
                "embedding_dimension": 384,
                "storage": "ChromaDB + SQLite",
                "status": "ready" if count > 0 else "empty"
            }
            
        except Exception as e:
            return {"error": str(e)}


# Global instance
vector_rag_service = VectorRAGService()
