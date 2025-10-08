# 🤖 Simple RAG Without Vector Search or Embeddings

## ✅ **YES! RAG Works Without Vectors**

**RAG = Retrieval + Augmentation + Generation**

You can do the **Retrieval** using simple database queries instead of vector search!

---

## 🎯 **Simple RAG Architecture**

```
┌─────────────────────────────────────────────────────────┐
│  1. RETRIEVAL (No Vectors Needed!)                     │
├─────────────────────────────────────────────────────────┤
│  Use regular database queries:                         │
│  • SQL WHERE clauses                                   │
│  • Filter by city, age, category                       │
│  • Simple text matching (LIKE)                         │
│  • No embeddings required! ✅                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  2. AUGMENTATION (Just Formatting!)                    │
├─────────────────────────────────────────────────────────┤
│  Collect event details into text:                      │
│  • Title, description, location                        │
│  • Price, age range, category                          │
│  • Format as readable text                             │
│  • No fancy processing! ✅                             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  3. GENERATION (Your LLM - Already Have!)              │
├─────────────────────────────────────────────────────────┤
│  Send to Claude/Anthropic:                             │
│  • Context from database                               │
│  • User question                                       │
│  • Get AI-generated response                           │
│  • You already have Anthropic API! ✅                  │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 **Real Implementation (No Vectors!)**

### **Simple RAG Example:**

```python
from langchain_anthropic import ChatAnthropic
from app.core.config import settings
from app.core.database import get_db
from app.models.unified_event import UnifiedEvent

class SimpleRAG:
    """RAG without vector search - uses simple database queries"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )
    
    async def get_recommendations(self, user_query: str, city: str, age: int = None):
        """
        Simple RAG:
        1. Retrieve with SQL (no vectors!)
        2. Augment with formatting
        3. Generate with LLM
        """
        
        # ===== STEP 1: RETRIEVE (Simple SQL Query) =====
        db = next(get_db())
        
        query = db.query(UnifiedEvent).filter(
            UnifiedEvent.city.like(f"%{city}%"),
            UnifiedEvent.is_active == True
        )
        
        # Add age filter if provided
        if age:
            query = query.filter(
                (UnifiedEvent.age_range_min <= age) & 
                (UnifiedEvent.age_range_max >= age)
            )
        
        # Get top 15 events
        events = query.limit(15).all()
        
        
        # ===== STEP 2: AUGMENT (Just Format Text) =====
        context = ""
        for i, event in enumerate(events, 1):
            context += f"""
Activity {i}: {event.title}
- Source: {event.source.value}
- Type: {event.event_type.value}
- Location: {event.location_name or event.address}
- City: {event.city}, {event.state}
- Category: {event.primary_category}
- Ages: {event.age_range_min}-{event.age_range_max} years
- Price: {'FREE' if event.is_free else 'Paid'}
- Indoor/Outdoor: {'Indoor' if event.is_indoor else 'Outdoor' if event.is_outdoor else 'Unknown'}
- Tags: {', '.join(event.tags[:5]) if event.tags else 'None'}
- URL: {event.source_url or 'N/A'}

"""
        
        
        # ===== STEP 3: GENERATE (LLM Response) =====
        prompt = f"""You are a helpful family activity assistant.

User Question: {user_query}

Available Activities in {city}:
{context}

Based on these activities, provide 3-5 personalized recommendations.
For each recommendation:
1. Name the specific activity
2. Explain why it's a good match
3. Include practical details (price, location)
4. Be warm and conversational

Keep your response concise and actionable."""

        response = await self.llm.ainvoke(prompt)
        
        return {
            "query": user_query,
            "recommendations": response.content,
            "events_considered": len(events),
            "retrieval_method": "Simple SQL (no vectors)"
        }
```

---

## 🧪 **Complete Working Example**

Create this file: `app/services/simple_rag.py`

```python
"""
Simple RAG implementation without vector embeddings
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
    """RAG service using simple SQL retrieval (no vector search)"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0.7,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )
    
    async def recommend_activities(
        self, 
        user_query: str,
        city: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        category: Optional[str] = None,
        is_free: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get AI recommendations based on user query
        
        Args:
            user_query: Natural language question
            city: City to search in
            age_min: Minimum age
            age_max: Maximum age
            category: Activity category
            is_free: Filter for free activities
            
        Returns:
            AI-generated recommendations
        """
        
        try:
            # STEP 1: RETRIEVE (Simple SQL - No Vectors!)
            events = self._retrieve_events(city, age_min, age_max, category, is_free)
            
            if not events:
                return {
                    "query": user_query,
                    "recommendations": "No activities found matching your criteria. Try adjusting your search filters.",
                    "events_count": 0
                }
            
            # STEP 2: AUGMENT (Format Context)
            context = self._build_context(events)
            
            # STEP 3: GENERATE (LLM Response)
            recommendations = await self._generate_recommendations(user_query, context, events)
            
            return {
                "query": user_query,
                "recommendations": recommendations,
                "events_count": len(events),
                "retrieval_method": "SQL Query"
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
        limit: int = 15
    ) -> List[UnifiedEvent]:
        """Retrieve events using simple SQL queries"""
        
        db = next(get_db())
        
        # Build query with filters
        query = db.query(UnifiedEvent).filter(UnifiedEvent.is_active == True)
        
        if city:
            query = query.filter(UnifiedEvent.city.like(f"%{city}%"))
        
        if age_min is not None and age_max is not None:
            query = query.filter(
                (UnifiedEvent.age_range_min <= age_max) &
                (UnifiedEvent.age_range_max >= age_min)
            )
        
        if category:
            query = query.filter(
                UnifiedEvent.primary_category.like(f"%{category}%")
            )
        
        if is_free is not None:
            query = query.filter(UnifiedEvent.is_free == is_free)
        
        # Order by quality and get results
        events = query.order_by(
            UnifiedEvent.data_quality_score.desc()
        ).limit(limit).all()
        
        db.close()
        return events
    
    def _build_context(self, events: List[UnifiedEvent]) -> str:
        """Build context string from events"""
        
        context_parts = []
        
        for i, event in enumerate(events, 1):
            context_parts.append(f"""
Activity {i}: {event.title}
- Source: {event.source.value.upper()}
- Type: {event.event_type.value}
- Location: {event.location_name or event.city}
- Address: {event.address or 'N/A'}
- City: {event.city}, {event.state} {event.zip_code or ''}
- Category: {event.primary_category or 'General'}
- Age Range: {event.age_range_min or 'All'} - {event.age_range_max or 'All'} years
- Price: {'FREE' if event.is_free else 'Paid'}
- Indoor/Outdoor: {'Indoor' if event.is_indoor else 'Outdoor' if event.is_outdoor else 'Flexible'}
- Tags: {', '.join(event.tags[:5]) if event.tags else 'None'}
- Website: {event.source_url or 'N/A'}
""")
        
        return "\n".join(context_parts)
    
    async def _generate_recommendations(
        self,
        user_query: str,
        context: str,
        events: List[UnifiedEvent]
    ) -> str:
        """Generate AI recommendations"""
        
        messages = [
            SystemMessage(content="""You are a helpful family activity assistant.
Your job is to recommend activities to parents based on their needs.

Guidelines:
- Be warm and conversational
- Provide 3-5 specific recommendations
- Explain WHY each activity is a good match
- Include practical details (price, location, time)
- Prioritize based on user needs
- Be honest about pros/cons
- Keep responses concise but informative"""),
            
            HumanMessage(content=f"""
User Question: {user_query}

Available Activities:
{context}

Please provide personalized recommendations based on these activities.
For each recommendation, explain why it's a good match and include key details.""")
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content


# Global instance
simple_rag_service = SimpleRAGService()
```

---

## 🔌 **Add API Endpoint**

Create: `app/api/v1/endpoints/rag.py`

```python
"""
RAG endpoints for AI-powered recommendations
"""

from fastapi import APIRouter, Query
from typing import Optional
from app.services.simple_rag import simple_rag_service

router = APIRouter()


@router.post("/recommend")
async def get_rag_recommendations(
    query: str = Query(..., description="User question or request"),
    city: Optional[str] = Query("Troy", description="City to search in"),
    age_min: Optional[int] = Query(None, description="Minimum age"),
    age_max: Optional[int] = Query(None, description="Maximum age"),
    category: Optional[str] = Query(None, description="Activity category"),
    is_free: Optional[bool] = Query(None, description="Free activities only")
):
    """
    Get AI-powered activity recommendations
    
    Example: POST /api/v1/rag/recommend?query=activities for shy 8 year old&city=Troy&age_min=8&age_max=8
    """
    
    result = await simple_rag_service.recommend_activities(
        user_query=query,
        city=city,
        age_min=age_min,
        age_max=age_max,
        category=category,
        is_free=is_free
    )
    
    return result
```

---

## 🧪 **Test It:**

```bash
# Ask for recommendations
curl -X POST "http://localhost:8000/api/v1/rag/recommend?query=What activities for my 7 year old this weekend?&city=Troy&age_min=7&age_max=7"
```

**Response:**
```json
{
  "query": "What activities for my 7 year old this weekend?",
  "recommendations": "Great options for your 7-year-old this weekend in Troy:\n\n1. **Troy Historic Village** - Educational museum perfect for this age...",
  "events_count": 12,
  "retrieval_method": "SQL Query"
}
```

---

## 💰 **Cost Comparison**

| Approach | Setup | Cost | Complexity |
|----------|-------|------|------------|
| **Simple RAG (SQL)** | 5 minutes | $2/month | ⭐ Easy |
| Vector RAG | 2 hours | $5/month | ⭐⭐⭐ Complex |

---

## 🎯 **When You DON'T Need Vectors:**

✅ **User provides clear filters:**
- "Activities for 8-year-old in Troy"
- "Free sports programs"
- "Indoor activities this weekend"

✅ **You have structured data:**
- Age ranges
- Categories
- Locations
- Tags

✅ **Simple matching works well:**
- SQL LIKE queries
- WHERE clauses
- Category filtering

---

## ❌ **When You WOULD Need Vectors:**

Only if you want:
- Semantic similarity ("shy kid" → martial arts, theater)
- Fuzzy matching ("toddler stuff" → age 0-3 activities)
- Concept search ("confidence building" → relevant activities)

But for 90% of use cases, **simple SQL retrieval works great!**

---

## 🚀 **Your Current Setup is PERFECT for Simple RAG:**

You already have:
- ✅ Database with 2,748 events
- ✅ Structured data (age, category, location)
- ✅ Anthropic API key (Claude)
- ✅ LangChain installed
- ✅ SQL query capabilities

**You can implement RAG in 30 minutes!** 🎉

---

## 📊 **Comparison:**

### **Traditional Search:**
```
User: "Activities for 7-year-old"
↓
Returns: List of 50 events
↓
User: (has to read through all 50)
```

### **Simple RAG (No Vectors):**
```
User: "Activities for 7-year-old"
↓
SQL Retrieves: 15 relevant events
↓
LLM Analyzes: Age-appropriate, quality, variety
↓
Returns: "Top 3 picks: 1. Stemville (hands-on STEM)..."
↓
User: (gets curated recommendations immediately)
```

---

## 🎯 **Bottom Line:**

**RAG WITHOUT vectors is:**
- ✅ Simpler to implement
- ✅ Faster to run
- ✅ Cheaper
- ✅ Easier to maintain
- ✅ Perfect for your use case!

**Only add vectors if you need:**
- Semantic understanding
- Fuzzy concept matching
- Similarity search

**For 90% of ActivityGuide use cases, simple SQL retrieval + LLM generation is perfect!** 🚀

See `RAG_IMPLEMENTATION_IDEAS.md` for full code examples!
