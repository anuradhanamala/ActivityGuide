# 🎯 AI Orchestration Flow - Visual Guide

## **How AI Orchestration Actually Works**

---

## **1. Multi-Source Sync Flow**

```
┌─────────────────┐
│  User/Frontend  │
│  Makes Request  │
└────────┬────────┘
         │ POST /api/v1/ai-orchestration/multi-source/sync
         │ Body: {"city": "Warren", "state": "MI", "sources": ["yelp"]}
         ▼
┌─────────────────────────────────────────┐
│   AI Orchestration Endpoint             │
│   (ai_orchestration.py)                 │
├─────────────────────────────────────────┤
│  1. Validate city name                  │
│  2. Check for placeholder values        │
│  3. Log incoming request                │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Geocoding Service                     │
│   (geocoding_service.py)                │
├─────────────────────────────────────────┤
│  Warren, MI → [48093]                   │
│  Uses Nominatim API                     │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Background Task Started               │
│   (_run_multi_source_sync)              │
├─────────────────────────────────────────┤
│  Returns immediately to user:           │
│  {"status": "started", ...}             │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   UnifiedSyncService                    │
│   (unified_sync_service.py)             │
├─────────────────────────────────────────┤
│  Orchestrates sync from all sources:    │
│  - Yelp                                 │
│  - Google Places                        │
│  - Eventbrite                           │
│  - etc.                                 │
└────────┬────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
    ┌─────────┐      ┌─────────────┐    ┌──────────┐
    │  Yelp   │      │Google Places│    │Eventbrite│
    │   API   │      │     API     │    │   API    │
    └────┬────┘      └──────┬──────┘    └─────┬────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            ▼
                ┌───────────────────────┐
                │  Normalize Data       │
                │  (API Clients)        │
                ├───────────────────────┤
                │  Convert to           │
                │  UnifiedEvent format  │
                └──────────┬────────────┘
                           │
                           ▼
                ┌───────────────────────┐
                │  Save to Database     │
                │  (UnifiedEvent model) │
                ├───────────────────────┤
                │  - Create new events  │
                │  - Update existing    │
                │  - Log sync stats     │
                └──────────┬────────────┘
                           │
                           ▼
                ┌───────────────────────┐
                │  Log Results          │
                │  (Console Output)     │
                ├───────────────────────┤
                │  ✅ SYNC COMPLETED    │
                │  📊 Created: 15       │
                │  📝 Updated: 3        │
                │  ⏱️  Duration: 4.5s   │
                └───────────────────────┘
```

---

## **2. Intelligent Search Flow (RAG)**

```
┌─────────────────┐
│  User Query     │
│  "swim lessons" │
└────────┬────────┘
         │ POST /api/v1/ai-orchestration/intelligent-search
         ▼
┌─────────────────────────────────────────┐
│   AI Orchestration Endpoint             │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Hybrid RAG Service                    │
│   (hybrid_rag.py)                       │
├─────────────────────────────────────────┤
│  1. Analyze query intent                │
│  2. Determine best RAG approach:        │
│     - Vector RAG (semantic search)      │
│     - SQL RAG (structured filters)      │
│     - Hybrid (both)                     │
└────────┬────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
    ┌─────────────┐   ┌──────────┐    ┌──────────────┐
    │ Vector RAG  │   │ SQL RAG  │    │  Hybrid RAG  │
    │(ChromaDB)   │   │(Database)│    │  (Combined)  │
    └──────┬──────┘   └────┬─────┘    └──────┬───────┘
           │               │                  │
           └───────────────┼──────────────────┘
                           ▼
                ┌───────────────────────┐
                │  Retrieve Events      │
                │  from Database        │
                └──────────┬────────────┘
                           │
                           ▼
                ┌───────────────────────┐
                │  LLM Processing       │
                │  (OpenAI GPT)         │
                ├───────────────────────┤
                │  - Analyze events     │
                │  - Generate recs      │
                │  - Add reasoning      │
                └──────────┬────────────┘
                           │
                           ▼
                ┌───────────────────────┐
                │  Return Results       │
                ├───────────────────────┤
                │  {                    │
                │    events: [...],     │
                │    reasoning: "..."   │
                │  }                    │
                └───────────────────────┘
```

---

## **3. Data Quality Orchestration Flow**

```
┌─────────────────┐
│  Quality Audit  │
│  Request        │
└────────┬────────┘
         │ GET /api/v1/ai-orchestration/quality/audit
         ▼
┌─────────────────────────────────────────┐
│   AI Orchestration Endpoint             │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Query Database                        │
│   - Get all events                      │
│   - Analyze each field                  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Calculate Quality Scores              │
├─────────────────────────────────────────┤
│   For each event:                       │
│   - Check required fields               │
│   - Validate data format                │
│   - Check completeness                  │
│   - Assign score (0-1)                  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Generate Report                       │
├─────────────────────────────────────────┤
│   {                                     │
│     total_events: 231,                  │
│     avg_score: 0.85,                    │
│     issues: [                           │
│       "15 events missing phone",        │
│       "8 events missing address"        │
│     ],                                  │
│     recommendations: [...]              │
│   }                                     │
└─────────────────────────────────────────┘
```

---

## **4. Duplicate Detection Flow**

```
┌─────────────────┐
│  Find Duplicates│
│  Request        │
└────────┬────────┘
         │ POST /api/v1/ai-orchestration/multi-source/find-duplicates
         ▼
┌─────────────────────────────────────────┐
│   AI Orchestration Endpoint             │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Query Events from Multiple Sources    │
│   - Group by city/area                  │
│   - Get events from different sources   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Compare Events                        │
├─────────────────────────────────────────┤
│   For each pair:                        │
│   1. Calculate title similarity         │
│   2. Check address match                │
│   3. Compare categories                 │
│   4. Check date overlap                 │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Identify Duplicates                   │
├─────────────────────────────────────────┤
│   Threshold: > 0.8 similarity           │
│   Return groups of likely duplicates    │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Return Duplicate Groups               │
├─────────────────────────────────────────┤
│   [                                     │
│     {                                   │
│       events: [event1, event2],         │
│       similarity: 0.95,                 │
│       reason: "Same title & address"    │
│     }                                   │
│   ]                                     │
└─────────────────────────────────────────┘
```

---

## **Key Orchestration Components**

### **1. API Endpoint Layer**
- **Location:** `app/api/v1/endpoints/ai_orchestration.py`
- **Role:** Entry point, validation, coordination
- **What it does:**
  - Receives HTTP requests
  - Validates inputs
  - Routes to appropriate services
  - Manages background tasks
  - Returns responses

### **2. Service Layer**
- **UnifiedSyncService:** Multi-source data synchronization
- **GeocodingService:** City → ZIP code conversion
- **HybridRAGService:** AI-powered search
- **API Clients:** External API communication

### **3. Data Layer**
- **Database:** Stores unified events
- **ChromaDB:** Vector embeddings for semantic search
- **Models:** Data structures (UnifiedEvent, EventSyncLog)

### **4. External APIs**
- **Yelp Fusion API**
- **Google Places API**
- **Eventbrite API**
- **Nominatim (Geocoding)**

---

## **Orchestration Patterns Used**

### **1. Background Task Pattern**
```python
# Start task immediately, run in background
background_tasks.add_task(
    _run_multi_source_sync,
    zip_codes,
    sources
)

# Return to user right away
return {"status": "started"}
```

### **2. Service Composition Pattern**
```python
# Compose multiple services
geocoding_service = GeocodingService()
sync_service = UnifiedSyncService()
rag_service = HybridRAGService()

# Orchestrate them
zip_codes = await geocoding_service.get_zip_codes(city)
results = await sync_service.sync_all_sources(zip_codes)
recommendations = await rag_service.recommend(query, results)
```

### **3. Strategy Pattern**
```python
# Choose RAG strategy based on query
if is_structured_query(query):
    results = sql_rag.search(query)
elif is_semantic_query(query):
    results = vector_rag.search(query)
else:
    results = hybrid_rag.search(query)
```

### **4. Fan-Out Pattern**
```python
# Call multiple sources in parallel
async def sync_all_sources():
    tasks = [
        yelp_client.search(),
        google_client.search(),
        eventbrite_client.search()
    ]
    results = await asyncio.gather(*tasks)
    return merge_results(results)
```

---

## **Summary**

**AI Orchestration in this app means:**

1. **Coordinating** multiple services and APIs
2. **Managing** asynchronous operations
3. **Combining** data from different sources
4. **Providing** AI-enhanced results through RAG
5. **Monitoring** data quality and coverage
6. **Logging** detailed statistics

**It's NOT using MCP protocol, but provides the same orchestration capabilities through REST APIs.** 🚀

