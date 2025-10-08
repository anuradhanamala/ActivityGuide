# 📊 Unified Sync - Complete Status & Input Requirements

## ✅ **Backend Status: UP AND RUNNING**

## 🎯 **INPUT Required for Unified Sync**

### **API Endpoint:**
```http
POST /api/v1/unified/sync/trigger
```

### **Input Parameters (BOTH Optional):**

```json
{
  "zip_codes": ["48083", "48084"],    // Optional
  "sources": ["yelp", "eventbrite"]   // Optional
}
```

### **Default Values:**
- `zip_codes`: `["48104", "48105", "48108"]` (Ann Arbor, MI)
- `sources`: ALL configured sources

## 📋 **Current API Configuration Status**

| # | API Source | API Key | Status | Will Sync? |
|---|------------|---------|--------|------------|
| 1 | **Eventbrite** | ✅ `MFFZZE6P7U...` | Valid OAuth | ⚠️ Yes (needs org) |
| 2 | **Yelp** | ✅ `6b0MA572ZN...` | Valid | ✅ YES |
| 3 | Google Places | ❌ Missing | Not configured | ❌ Skipped |
| 4 | Ticketmaster | ❌ Missing | Not configured | ❌ Skipped |
| 5 | Meetup | ❌ `your_meetup_api_key` | Invalid | ❌ Error (404) |
| 6 | Recreation.gov | ❌ `your_recreation_gov...` | Invalid | ❌ Error (401) |
| 7 | OpenStreetMap | ✅ No key needed | - | ⚠️ Bug (needs fix) |
| 8 | YMCA | ❌ No public API | - | ❌ Returns [] |
| 9 | Boys & Girls | ❌ No public API | - | ❌ Returns [] |

**Working Sources: 1/9 (Yelp only)** ✅

## 🚀 **How to Call Unified Sync**

### **Option 1: Simple Call (No Input)**
```bash
POST http://localhost:8000/api/v1/unified/sync/trigger
```

**What happens:**
- Uses default ZIP codes (Ann Arbor)
- Tries ALL sources
- Returns data from Yelp only

### **Option 2: Specific ZIP Codes**
```bash
POST http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084
```

**What happens:**
- Uses Troy, MI ZIP codes
- Tries ALL sources
- Returns data from Yelp for Troy area

### **Option 3: Specific Sources**
```bash
POST http://localhost:8000/api/v1/unified/sync/trigger?sources=yelp&sources=eventbrite
```

**What happens:**
- Uses default ZIP codes
- Only tries Yelp and Eventbrite
- Skips other 7 sources

### **Option 4: Combined**
```bash
POST http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&sources=yelp
```

**What happens:**
- Uses Troy ZIP code
- Only tries Yelp
- Fastest option!

## 📊 **Expected Output**

### **With Current Configuration:**

```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48083"],
  "sources": "all"
}
```

**Then in background:**
```json
{
  "total_sources": 9,
  "successful_sources": 1,
  "total_events": 50,
  "events_created": 50,
  "events_updated": 0,
  "errors": [
    "Error syncing google_places: API key not configured",
    "Error syncing ticketmaster: API key not configured",
    "Error syncing meetup: 404 Not Found",
    "Error syncing recreation_gov: 401 Unauthorized",
    "Error syncing openstreetmap: SearchParams missing latitude"
  ]
}
```

## 🎯 **What You Get with Current Setup**

### **From Yelp (WORKING):**
```
✅ ~50 businesses per ZIP code:
   - Museums
   - Playgrounds
   - Activity centers
   - Gyms & sports centers
   - Dance studios
   - Martial arts schools
   - Swimming pools
   - Parks
```

### **From Eventbrite (CONDITIONAL):**
```
⚠️ Only if you create an organization:
   - Your managed events
   - Community events you host
```

### **From Other Sources:**
```
❌ Need API keys to get:
   - Google Places: Parks, gyms, venues
   - Meetup: Community events
   - Recreation.gov: National park programs
   - Ticketmaster: Family shows
```

## 💡 **Key Insights**

### **The Sync DOES NOT FAIL if APIs are missing!**

✅ **It's designed to work with partial coverage**
✅ **Gracefully skips missing APIs**
✅ **Logs errors but continues**
✅ **Returns data from working sources**

### **Current Reality:**

**INPUT:**
```python
zip_codes = ["48083"]  # What you provide
sources = None         # Use all (optional)
```

**PROCESS:**
```
1. Tries 9 sources
2. 1 works (Yelp)
3. 8 skip/error
```

**OUTPUT:**
```
✅ 50 Yelp businesses for Troy, MI
⚠️ 8 errors logged (expected)
✅ Sync succeeds with partial data
```

## 🔑 **To Get Full Coverage, Add These API Keys:**

### **Priority 1: FREE APIs**
```env
# Recreation.gov (FREE)
RECREATION_GOV_API_KEY=get_from_ridb.recreation.gov

# OpenStreetMap (NO KEY NEEDED - just fix the bug)
```

### **Priority 2: TRIAL/PAID APIs**
```env
# Google Places ($200 credit)
GOOGLE_PLACES_API_KEY=get_from_console.cloud.google.com

# Meetup ($75/month - optional)
MEETUP_API_KEY=get_from_meetup.com/api

# Ticketmaster (FREE tier)
TICKETMASTER_API_KEY=get_from_developer.ticketmaster.com
```

## 🎉 **Summary**

**Unified Sync Input:**
- ✅ `zip_codes`: List of ZIP codes (optional)
- ✅ `sources`: List of source names (optional)
- ✅ **That's ALL you need!**

**Current Working Setup:**
- ✅ 1/9 APIs working (Yelp)
- ✅ Sync runs successfully
- ✅ Gets 50 businesses per ZIP code
- ✅ Logs errors for missing APIs
- ✅ Does NOT fail!

**To improve coverage:**
- Add more API keys (see above)
- Each new API = more data
- Currently: 1 source = 50 events
- With 5 sources = 250+ events!

The unified sync is **working as designed** - it uses whatever APIs you have! 🎯
