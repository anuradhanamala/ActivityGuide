# 🔍 Unified Search - Complete Guide

## 🎯 **What is Unified Search Used For?**

**Unified Search** is used to **find and filter events** from **ALL data sources** in one API call.

Instead of searching Yelp, Eventbrite, Google Places separately, you search them ALL at once!

---

## 📍 **Endpoint:**

```http
GET /api/v1/unified/search
```

**File:** `app/api/v1/endpoints/unified_events.py` (Lines 25-187)

---

## 🎯 **What It Does:**

### **Single Search Across ALL Sources:**

```
USER QUERY:
"Find free family activities for kids 5-10 in Troy, MI"

         ↓

UNIFIED SEARCH queries the database containing:
├── 2,670 events from Parallel AI
├── 78 venues from Yelp
├── Events from Eventbrite (if any)
├── Events from Google Places (if configured)
├── Events from Meetup (if configured)
└── ... all other sources

         ↓

RETURNS: Combined results from ALL sources
```

---

## 📋 **Search Parameters (ALL Optional):**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `zip_code` | string | ZIP code to search near | `48083` |
| `city` | string | City to search in | `Troy` |
| `state` | string | State to search in | `MI` |
| `radius_miles` | integer | Search radius (1-100) | `25` |
| `categories` | list[string] | Event categories | `["family", "sports"]` |
| `age_min` | integer | Minimum age (0-18) | `5` |
| `age_max` | integer | Maximum age (0-18) | `12` |
| `is_free` | boolean | Free events only | `true` |
| `is_indoor` | boolean | Indoor events only | `false` |
| `event_type` | string | Type: event/venue/class/program | `venue` |
| `sources` | list[string] | Specific sources to search | `["yelp", "eventbrite"]` |
| `start_date` | datetime | Events after this date | `2025-10-08` |
| `end_date` | datetime | Events before this date | `2025-11-08` |
| `limit` | integer | Max results (1-100) | `20` |

---

## 🧪 **Example Searches:**

### **1. Find Family Activities in Troy:**
```bash
GET http://localhost:8000/api/v1/unified/search?city=Troy&categories=family&limit=20
```

**Returns:**
- Yelp businesses in Troy
- Parallel AI events in Troy
- All filtered by "family" category

### **2. Find Free Activities for Kids 5-10:**
```bash
GET http://localhost:8000/api/v1/unified/search?city=Troy&age_min=5&age_max=10&is_free=true
```

**Returns:**
- Free events suitable for ages 5-10
- From all sources
- In Troy area

### **3. Find Sports Activities:**
```bash
GET http://localhost:8000/api/v1/unified/search?city=Troy&categories=sports&categories=martial_arts&limit=30
```

**Returns:**
- Sports facilities from Yelp
- Sports events from Parallel AI
- Martial arts schools
- Combined from all sources

### **4. Find Only Yelp Results:**
```bash
GET http://localhost:8000/api/v1/unified/search?city=Troy&sources=yelp
```

**Returns:**
- Only results from Yelp
- Filters out Parallel AI and other sources

### **5. Find Indoor Activities:**
```bash
GET http://localhost:8000/api/v1/unified/search?zip_code=48083&is_indoor=true&categories=gymnastics&categories=dance
```

**Returns:**
- Indoor gymnastics and dance studios
- From all sources

---

## 📊 **Response Format:**

```json
{
  "events": [
    {
      "id": "uuid",
      "external_id": "yelp_business_id",
      "source": "yelp",
      "title": "Troy Historic Village",
      "city": "Troy",
      "state": "MI",
      "zip_code": "48083",
      "primary_category": "family_venue",
      "tags": ["Museums", "Historical Tours"],
      "is_free": false,
      "latitude": 42.5,
      "longitude": -83.1,
      "source_url": "https://www.yelp.com/..."
    },
    {
      "source": "agentic_parallel_ai",
      "title": "Kids Sports at Troy | Life Time",
      ...
    }
  ],
  "total_count": 78,
  "search_summary": "Found 78 events in family for ages 5-10",
  "filters_applied": {
    "city": "Troy",
    "categories": ["family"],
    "age_min": 5,
    "age_max": 10
  }
}
```

---

## 🎯 **Key Differences:**

| Feature | Unified Search | Regular Search |
|---------|----------------|----------------|
| **Data Sources** | ALL (Yelp, Eventbrite, Parallel AI, etc.) | Single source |
| **Table** | `unified_events` | `events` |
| **Filters** | 20+ filter options | Limited filters |
| **Coverage** | Comprehensive (all sources) | Limited (one source) |
| **Endpoint** | `/api/v1/unified/search` | `/api/v1/events/search` |

---

## 💡 **Real-World Use Cases:**

### **Use Case 1: Parent Looking for Activities**
```
Parent asks: "What activities are there for my 7-year-old in Troy?"

Search:
GET /api/v1/unified/search?city=Troy&age_min=7&age_max=7&limit=50

Returns:
✅ Yelp businesses (gyms, studios, museums)
✅ Parallel AI events (classes, programs)
✅ All combined in one response!
```

### **Use Case 2: Find Free Weekend Activities**
```
Parent asks: "Free activities this weekend?"

Search:
GET /api/v1/unified/search?
  city=Troy&
  is_free=true&
  start_date=2025-10-11&
  end_date=2025-10-12

Returns:
✅ Free events from all sources
✅ Filtered by date range
```

### **Use Case 3: Find Specific Type of Venue**
```
Parent asks: "Where are the playgrounds and parks?"

Search:
GET /api/v1/unified/search?
  city=Troy&
  categories=playgrounds&
  categories=parks&
  event_type=venue

Returns:
✅ Playgrounds from Yelp
✅ Parks from OpenStreetMap (when configured)
✅ Park events from other sources
```

---

## 🔄 **Unified Search vs Unified Sync:**

| Feature | Unified Search | Unified Sync |
|---------|----------------|--------------|
| **Purpose** | **FIND** events | **IMPORT** events |
| **Method** | `GET` | `POST` |
| **Endpoint** | `/unified/search` | `/unified/sync/trigger` |
| **Action** | Query database | Fetch from APIs & save to DB |
| **Speed** | Fast (milliseconds) | Slow (minutes) |
| **When to use** | **User searches** | **Background job** |
| **Frequency** | Unlimited | Once per day |

---

## 🎯 **Workflow:**

```
1. SYNC (Once per day):
   POST /api/v1/unified/sync/trigger?sources=yelp
   → Fetches Yelp data
   → Saves to unified_events table
   
2. SEARCH (Unlimited):
   GET /api/v1/unified/search?city=Troy&categories=sports
   → Queries unified_events table
   → Returns results instantly
   → No API calls needed!
```

---

## 📊 **Current Database (Your Data):**

**You can search:**
```
✅ 2,670 Parallel AI events
✅ 78 Yelp businesses
✅ Total: 2,748 searchable events
```

**Search examples that will work RIGHT NOW:**

```bash
# Find all activities in Troy
GET /unified/search?city=Troy&limit=50

# Find Yelp businesses only
GET /unified/search?city=Troy&sources=yelp

# Find sports activities
GET /unified/search?city=Troy&categories=sports

# Find playgrounds from Yelp
GET /unified/search?city=Troy&categories=playgrounds&sources=yelp
```

---

## 🎉 **Summary:**

**Unified Search is used to:**

✅ **Find events** from ALL data sources in one query
✅ **Filter** by location, age, category, price, indoor/outdoor
✅ **Combine results** from Yelp + Eventbrite + Parallel AI + others
✅ **Fast search** (queries database, no API calls)
✅ **Provide users** with comprehensive activity discovery

**Think of it as:**
- **Unified Sync** = Import data (background job)
- **Unified Search** = Find data (user queries)

The search is what your users will use to discover activities! 🎯
