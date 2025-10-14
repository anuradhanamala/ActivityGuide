# 🔄 Unified Sync - Complete Input & Configuration Guide

## 📋 **What Input Does Unified Sync Need?**

### **API Endpoint:**
```http
POST /api/v1/unified/sync/trigger
```

### **Input Parameters (ALL Optional):**

```json
{
  "zip_codes": ["48083", "48084", "48085"],  // Optional - defaults to Ann Arbor
  "sources": ["yelp", "eventbrite"]          // Optional - defaults to ALL
}
```

### **Or as Query Parameters:**
```
POST /api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084&sources=yelp&sources=eventbrite
```

## ✅ **Currently Working (With Your APIs):**

Based on your current configuration:

| Source | API Key Status | Will Sync | Data You'll Get |
|--------|----------------|-----------|-----------------|
| **Eventbrite** | ✅ Configured | ✅ Yes | Events & classes (if org created) |
| **Yelp** | ✅ Configured | ✅ Yes | 50+ businesses per ZIP code |
| **OpenStreetMap** | ✅ No key needed | ⚠️ Needs fix | Playgrounds & parks |
| **Google Places** | ❌ Missing | ❌ Skipped | - |
| **Ticketmaster** | ❌ Missing | ❌ Skipped | - |
| **Meetup** | ❌ Missing | ❌ Skipped | - |
| **Recreation.gov** | ❌ Missing | ❌ Skipped | - |
| **YMCA** | ❌ No public API | ❌ Returns [] | - |
| **Boys & Girls** | ❌ No public API | ❌ Returns [] | - |

### **Current Coverage: 2/9 sources (22%)**

## 🎯 **How to Call Unified Sync**

### **Method 1: Minimal Call (Uses Defaults)**
```bash
# No input needed - uses defaults
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger"
```

**What it does:**
- Syncs: ALL configured sources (Eventbrite + Yelp)
- ZIP codes: `["48104", "48105", "48108"]` (Ann Arbor default)
- Result: Events from 2 working sources

### **Method 2: Specific ZIP Codes**
```bash
# Sync Troy, MI area
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084&zip_codes=48085"
```

**What it does:**
- Syncs: ALL configured sources
- ZIP codes: Troy, MI (as specified)
- Result: Events from Troy area only

### **Method 3: Specific Sources Only**
```bash
# Only sync Yelp
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?sources=yelp"
```

**What it does:**
- Syncs: Only Yelp
- ZIP codes: Default Ann Arbor
- Result: Only Yelp businesses

### **Method 4: Combined (Specific ZIPs + Sources)**
```bash
# Sync Yelp for Troy
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&sources=yelp"
```

## 📊 **What Inputs Each API Needs Internally**

When sync runs, it creates `SearchParams` for each API:

```python
params = SearchParams(
    location="48083",                    # INPUT: ZIP code
    zip_code="48083",                    # INPUT: ZIP code
    radius_miles=25,                     # Fixed: 25 miles
    categories=["family", "kids", "education", "sports", "arts"],  # Fixed
    start_date=datetime.now(),          # Fixed: Today
    end_date=datetime.now() + timedelta(days=90),  # Fixed: +90 days
    limit=50                            # Fixed: 50 results per source
)
```

### **Source-Specific Inputs:**

#### **Eventbrite:**
```python
await client.search_events(
    location="48083",           # From your input
    categories=["family"],      # Fixed
    start_date=datetime.now(),  # Fixed
    end_date=+90 days           # Fixed
)
```

#### **Yelp:**
```python
await client.search_businesses(
    location="48083",                                  # From your input
    categories=["museums", "playgrounds", "amusementparks"]  # Fixed
)
```

#### **Google Places (when configured):**
```python
await client.search_places(
    location="48083",                          # From your input
    types=["park", "museum", "amusement_park", "gym"]  # Fixed
)
```

#### **Meetup (when configured):**
```python
await client.search_events(
    params.location,      # From your input
    params.radius_miles,  # 25 miles
    params.categories     # ["family", "kids", etc.]
)
```

## 🔧 **Current Working Example**

With your current setup (Eventbrite + Yelp):

**Input:**
```bash
POST /api/v1/unified/sync/trigger?zip_codes=48083
```

**What Happens:**
```
1. Tries Eventbrite API
   - If org exists: Gets events ✅
   - If no org: Returns [] ⚠️
   
2. Tries Yelp API
   - Searches businesses in 48083 ✅
   - Returns ~50 family venues ✅
   
3. Tries Meetup API
   - No API key: Logs error ❌
   - Continues to next source
   
4. Tries Recreation.gov API
   - No API key: Logs error ❌
   - Continues to next source
   
5. Tries OpenStreetMap API
   - Has bug: Logs error ❌
   - Continues to next source
   
6. Skips YMCA/Boys & Girls (no public API)
   
7. RESULT:
   - Events from: Yelp ✅ (~50 businesses)
   - Events from: Eventbrite (if org exists)
   - Total: 50-100 events
   - Errors: 3-4 (for missing APIs)
```

## 💡 **Key Insight**

### **Unified Sync DOES NOT require all APIs!**

✅ **It works with whatever APIs you have configured**
✅ **Skips missing APIs gracefully**
✅ **Logs errors but continues**
✅ **Returns data from working sources**

### **Current Reality:**

**You have 2/9 APIs configured:**
- ✅ Eventbrite (OAuth working)
- ✅ Yelp (API working)

**Sync will:**
- ✅ Get 50+ businesses from Yelp
- ✅ Get events from Eventbrite (if org exists)
- ⚠️ Log errors for 5 missing APIs
- ✅ Still return results!

## 🚀 **Recommended Next Steps**

### **Priority 1: Get More FREE API Keys**

| API | Cost | Setup Time | Coverage |
|-----|------|------------|----------|
| **Google Places** | $200 credit | 10 min | ⭐⭐⭐⭐⭐ |
| **Recreation.gov** | FREE | 5 min | ⭐⭐⭐ |
| **OpenStreetMap** | FREE | 0 min (no key) | ⭐⭐⭐⭐ |

### **Priority 2: Test What You Have**

Run sync with current APIs:
```bash
POST /api/v1/unified/sync/trigger?zip_codes=48083
```

You'll get data from Yelp immediately!

### **Priority 3: Fix OpenStreetMap Bug**

The OSM client has a bug - I can fix it if you want.

## 📦 **Complete Input Summary**

### **Minimal Input:**
```python
# No input needed - uses defaults!
POST /api/v1/unified/sync/trigger
```

### **Full Input:**
```python
{
  "zip_codes": ["48083", "48084", "48085"],  # List of ZIP codes
  "sources": ["yelp", "eventbrite", "google_places"]  # List of sources
}
```

### **What You Get Back:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48083", "48084", "48085"],
  "sources": ["yelp", "eventbrite"]
}
```

## 🎯 **The Bottom Line**

**Input for Unified Sync:**
- ✅ **ZIP codes** (optional - defaults to Ann Arbor)
- ✅ **Sources** (optional - uses all configured)
- ✅ **That's it!** Super simple!

**The sync handles everything else:**
- ✅ Checks which APIs are configured
- ✅ Skips missing APIs
- ✅ Normalizes data
- ✅ Saves to database
- ✅ Returns results

**You can run it RIGHT NOW with just:**
```bash
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger"
```

And it will sync Yelp data for Ann Arbor! 🎉
