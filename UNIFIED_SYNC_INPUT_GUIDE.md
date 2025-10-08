# 🔄 Unified Sync API Call - Input Guide

Complete guide to calling the unified sync endpoint with all required inputs.

## 📋 **Unified Sync Endpoint**

```http
POST /api/v1/unified/sync/trigger
```

## 🎯 **Input Parameters**

### **Optional Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `zip_codes` | List[string] | ❌ No | `["48104", "48105", "48108"]` | ZIP codes to sync |
| `sources` | List[string] | ❌ No | `all` | Specific sources to sync |

### **If NO parameters provided:**
- Uses default ZIP codes: Ann Arbor area
- Syncs ALL configured sources

## 🚀 **Example API Calls**

### **1. Sync All Sources (Default)**
```bash
# Simplest call - uses defaults
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger"
```

**Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48104", "48105", "48108"],
  "sources": "all"
}
```

### **2. Sync Specific ZIP Codes**
```bash
# Sync Troy, MI area
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084&zip_codes=48085"
```

**Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48083", "48084", "48085"],
  "sources": "all"
}
```

### **3. Sync Specific Sources Only**
```bash
# Only sync Yelp and Google Places
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?sources=yelp&sources=google_places"
```

**Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48104", "48105", "48108"],
  "sources": ["yelp", "google_places"]
}
```

### **4. Sync Specific ZIP Codes AND Sources**
```bash
# Sync Yelp and Eventbrite for Troy area
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084&sources=yelp&sources=eventbrite"
```

**Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48083", "48084"],
  "sources": ["yelp", "eventbrite"]
}
```

## 📊 **Available Sources**

You can specify these source values:

```
✅ eventbrite
✅ yelp
✅ google_places
✅ ticketmaster
✅ meetup
✅ recreation_gov
✅ ymca
✅ boys_girls_club
✅ openstreetmap
```

## 🔄 **What Happens During Sync**

### **Step-by-Step Process:**

```
1. REQUEST RECEIVED
   Input: zip_codes=["48083"], sources=["yelp", "eventbrite"]
   ↓
2. BACKGROUND TASK STARTED
   Sync runs asynchronously (doesn't block)
   ↓
3. FOR EACH SOURCE:
   ├─ Check if API key configured
   ├─ If YES: Fetch events
   ├─ If NO: Skip and log error
   ↓
4. FOR EACH ZIP CODE:
   ├─ Create SearchParams
   ├─ Call API with params
   ├─ Normalize data
   ├─ Save to database
   ↓
5. DEDUPLICATION
   ├─ Check if (external_id + source) exists
   ├─ If exists: UPDATE
   ├─ If new: CREATE
   ↓
6. RETURN RESULTS
   {
     "total_events": 150,
     "events_created": 75,
     "events_updated": 75,
     "successful_sources": 2,
     "errors": []
   }
```

## 📝 **Input Schema**

### **Full Input Structure:**

```python
{
  "zip_codes": [
    "48083",    # Troy, MI
    "48084",    # Troy, MI
    "48104"     # Ann Arbor, MI
  ],
  "sources": [
    "eventbrite",
    "yelp",
    "google_places",
    "meetup"
  ]
}
```

### **Or Using Query Parameters:**

```
POST /api/v1/unified/sync/trigger?
  zip_codes=48083&
  zip_codes=48084&
  zip_codes=48104&
  sources=yelp&
  sources=eventbrite
```

## 🎯 **Python Example**

```python
import httpx
import asyncio

async def trigger_sync():
    """Trigger unified sync from Python"""
    
    # Option 1: Sync all sources, default ZIP codes
    response = await httpx.AsyncClient().post(
        "http://localhost:8000/api/v1/unified/sync/trigger"
    )
    
    # Option 2: Sync specific ZIP codes
    response = await httpx.AsyncClient().post(
        "http://localhost:8000/api/v1/unified/sync/trigger",
        params={
            "zip_codes": ["48083", "48084", "48085"]
        }
    )
    
    # Option 3: Sync specific sources
    response = await httpx.AsyncClient().post(
        "http://localhost:8000/api/v1/unified/sync/trigger",
        params={
            "zip_codes": ["48104"],
            "sources": ["yelp", "google_places", "meetup"]
        }
    )
    
    return response.json()
```

## 📦 **Internal Sync Service Call**

If calling from Python code directly:

```python
from app.services.unified_sync_service import unified_sync_service
from app.core.database import get_db

async def run_sync():
    db = next(get_db())
    
    # Input: list of ZIP codes
    result = await unified_sync_service.sync_all_sources(
        db=db,
        zip_codes=["48083", "48084", "48085"]  # ← Input here
    )
    
    print(result)
    db.close()
```

**Output:**
```python
{
    "total_sources": 9,
    "successful_sources": 3,      # Only sources with API keys
    "total_events": 150,
    "events_created": 75,
    "events_updated": 75,
    "errors": [
        "Error syncing google_places: API key not configured",
        "Error syncing meetup: API key not configured",
        # ... etc
    ]
}
```

## ⚙️ **SearchParams Structure (Internal)**

When sync calls each API, it creates SearchParams:

```python
params = SearchParams(
    location="48083",              # ZIP code
    zip_code="48083",             # ZIP code (explicit)
    radius_miles=25,              # Search radius
    categories=["family", "kids", "education", "sports", "arts"],
    start_date=datetime.now(),    # Current date
    end_date=datetime.now() + timedelta(days=90),  # 90 days ahead
    limit=50                      # Max results per source
)
```

## 🧪 **Test the Unified Sync**

### **Simple Test:**
```bash
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger"
```

### **With ZIP Codes:**
```bash
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084"
```

### **Check Sync Status:**
```bash
curl "http://localhost:8000/api/v1/unified/sync/status"
```

## 📊 **Current Configuration Status**

Based on your current setup:

| Source | API Key | Will Sync |
|--------|---------|-----------|
| Eventbrite | ✅ Configured | ✅ Yes |
| Yelp | ✅ Configured | ✅ Yes |
| Google Places | ❌ Missing | ❌ Skipped (with error) |
| Ticketmaster | ❌ Missing | ❌ Skipped (with error) |
| Meetup | ❌ Missing | ❌ Skipped (with error) |
| Recreation.gov | ❌ Missing | ❌ Skipped (with error) |
| YMCA | ❌ No API | ❌ Returns empty |
| Boys & Girls | ❌ No API | ❌ Returns empty |
| OpenStreetMap | ✅ No key needed | ✅ Yes (if lat/lon available) |

## 💡 **Key Points**

1. **Sync DOES NOT FAIL if some APIs are missing** ✅
2. **It syncs ONLY configured sources** ✅
3. **Errors are logged but not blocking** ✅
4. **Currently will sync: Eventbrite + Yelp** ✅

## 🎯 **Summary**

**Minimal Input (Uses Defaults):**
```bash
POST /api/v1/unified/sync/trigger
# No input needed!
```

**Full Input (All Options):**
```bash
POST /api/v1/unified/sync/trigger?
  zip_codes=48083&
  zip_codes=48084&
  zip_codes=48085&
  sources=yelp&
  sources=eventbrite
```

**Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48083", "48084", "48085"],
  "sources": ["yelp", "eventbrite"]
}
```

**With your current setup:**
- Will sync **Eventbrite + Yelp** ✅
- Will skip sources without API keys ⚠️
- Will log errors for missing APIs ℹ️
- Will return events from configured sources ✅

The unified sync is **designed to work even with partial API coverage**! 🎉
