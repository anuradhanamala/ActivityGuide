# 🌍 Geocoding Integration for City-Based Sync

## Overview

The unified sync endpoint now supports **automatic geocoding** to convert city/state names to ZIP codes! No more manual ZIP code mapping needed.

---

## ✨ Features

### **Multi-Strategy Geocoding:**
1. **Hardcoded Mapping** (Fastest) - Pre-configured cities
2. **Nominatim/OpenStreetMap** (Free) - Any US city
3. **ZipCodeAPI** (Future) - Premium fallback option

### **Benefits:**
- ✅ **Works with ANY US city** - Not just pre-configured ones
- ✅ **Free** - Uses OpenStreetMap (Nominatim)
- ✅ **No API key required** - For basic usage
- ✅ **Automatic fallback** - Multiple strategies ensure success
- ✅ **Radius support** - Get all ZIP codes within 25 miles

---

## 📡 API Endpoint

### **POST /api/v1/unified/sync/city**

**Parameters:**
- `city` (required) - City name (e.g., "Troy", "Detroit", "Chicago")
- `state` (required) - State (e.g., "MI", "Michigan", "IL", "Illinois")
- `sources` (optional) - Specific sources to sync (e.g., "yelp", "eventbrite")

---

## 🚀 Usage Examples

### **Example 1: Pre-configured City (Troy, MI)**
```bash
POST http://localhost:8000/api/v1/unified/sync/city?city=Troy&state=MI
```

**Response:**
```json
{
  "message": "Sync triggered for Troy, MI",
  "status": "started",
  "city": "Troy",
  "state": "MI",
  "zip_codes": ["48007", "48083", "48084", "48085", "48098", "48099"],
  "zip_code_count": 6,
  "sources": "all",
  "estimated_radius_miles": 25,
  "geocoding_method": "hardcoded_mapping"
}
```

### **Example 2: Any US City (Chicago, IL)**
```bash
POST http://localhost:8000/api/v1/unified/sync/city?city=Chicago&state=IL
```

**Response:**
```json
{
  "message": "Sync triggered for Chicago, IL",
  "status": "started",
  "city": "Chicago",
  "state": "IL",
  "zip_codes": ["60601", "60602", "60603", ...],
  "zip_code_count": 15,
  "sources": "all",
  "estimated_radius_miles": 25,
  "geocoding_method": "nominatim_geocoding"
}
```

### **Example 3: Specific Sources Only**
```bash
POST http://localhost:8000/api/v1/unified/sync/city?city=Detroit&state=Michigan&sources=yelp&sources=eventbrite
```

**Response:**
```json
{
  "message": "Sync triggered for Detroit, Michigan",
  "status": "started",
  "city": "Detroit",
  "state": "Michigan",
  "zip_codes": ["48201", "48202", ...],
  "zip_code_count": 26,
  "sources": ["yelp", "eventbrite"],
  "estimated_radius_miles": 25,
  "geocoding_method": "hardcoded_mapping"
}
```

---

## 🔧 How It Works

### **Geocoding Flow:**

```
1. User Request: "Chicago, IL"
         ↓
2. Try Hardcoded Mapping (Fastest)
   → Found? Return ZIP codes
   → Not found? Continue...
         ↓
3. Try Nominatim (OpenStreetMap)
   → Geocode city to lat/lon
   → Get ZIP codes in 25-mile radius
   → Found? Return ZIP codes
   → Not found? Continue...
         ↓
4. Try ZipCodeAPI (Future Enhancement)
   → Premium API with more coverage
   → Return ZIP codes
         ↓
5. Return Error with Suggestions
```

### **Response Includes:**
- `geocoding_method` - Which strategy was used:
  - `"hardcoded_mapping"` - Pre-configured city
  - `"nominatim_geocoding"` - OpenStreetMap API
  - `"zipcodeapi"` - Premium API (future)

---

## 🏙️ Pre-configured Cities

These cities use **hardcoded mappings** (fastest response):

| City | State | ZIP Codes Count |
|------|-------|-----------------|
| Troy | MI | 6 |
| Detroit | MI | 26 |
| Ann Arbor | MI | 5 |
| Sterling Heights | MI | 5 |
| Rochester | MI | 4 |
| Royal Oak | MI | 3 |
| Birmingham | MI | 2 |
| Bloomfield Hills | MI | 4 |
| Novi | MI | 3 |
| Farmington | MI | 6 |

**Note:** Any other US city will use geocoding APIs automatically!

---

## 🛠️ Technical Implementation

### **Geocoding Service**
**File:** `app/services/geocoding_service.py`

**Key Components:**
```python
class GeocodingService:
    async def get_zip_codes_for_city(
        city: str, 
        state: str, 
        radius_miles: int = 25
    ) -> Tuple[List[str], str]:
        """
        Get ZIP codes for any city using geocoding APIs
        
        Returns:
            (zip_codes, method_used)
        """
```

### **Dependencies:**
- `geopy>=2.4.0` - Geocoding library
- Nominatim (OpenStreetMap) - Free geocoding service
- Rate limiting (1 req/sec for free tier)

---

## ⚠️ Rate Limits

### **Nominatim (OpenStreetMap) - Free Tier:**
- **Limit:** 1 request per second
- **Usage:** Unlimited requests
- **No API key required**
- **Rate limiter:** Built-in to prevent throttling

### **Best Practices:**
1. **Use pre-configured cities when possible** (instant response)
2. **Cache geocoding results** for frequently used cities
3. **Batch sync requests** to stay under rate limits
4. **Add popular cities to hardcoded mapping** for faster responses

---

## 🔮 Future Enhancements

### **1. ZipCodeAPI Integration**
```python
# Premium API with comprehensive ZIP code data
# - Accurate radius-based search
# - No rate limits on paid tier
# - Detailed ZIP code boundaries
```

### **2. Database Cache**
```sql
CREATE TABLE city_zipcodes (
    city VARCHAR(100),
    state VARCHAR(50),
    zip_codes JSON,
    latitude FLOAT,
    longitude FLOAT,
    cached_at TIMESTAMP
);
```

### **3. Admin UI**
- View geocoding cache
- Add/remove cities from hardcoded mapping
- Monitor API usage and rate limits
- Manual ZIP code override

---

## 🚨 Error Handling

### **City Not Found:**
```json
{
  "detail": "Could not find ZIP codes for 'InvalidCity, XX'. Try using a major city name or add it to the hardcoded mapping. Available pre-configured cities: troy, mi, detroit, mi..."
}
```

### **Geocoding API Failure:**
- Falls back to next strategy automatically
- Logs warning but continues
- Returns hardcoded mapping if available

### **Rate Limit Hit:**
```
WARNING: Nominatim rate limit hit, waiting 1 second...
```

---

## 📊 Monitoring

### **Check Sync Status:**
```bash
GET /api/v1/unified/sync/status
```

### **View Logs:**
```bash
# Backend logs show geocoding method used
INFO: City sync requested for 'Chicago, IL' -> 15 ZIP codes via nominatim_geocoding
```

---

## 🎯 Usage Recommendations

### **For Best Performance:**

1. **Pre-configured Cities** (0ms geocoding)
   ```bash
   POST /sync/city?city=Troy&state=MI
   # Instant: uses hardcoded mapping
   ```

2. **First-Time Cities** (1-2s geocoding)
   ```bash
   POST /sync/city?city=Chicago&state=IL
   # ~1-2 seconds: geocodes via Nominatim
   ```

3. **Add Frequently Used Cities**
   - If you sync a city often, add it to `city_zip_mapping` in `geocoding_service.py`
   - This makes it instant for future requests

---

## 📚 API Documentation

Interactive API docs available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Navigate to `/api/v1/unified/sync/city` to test the endpoint!

---

## ✅ Installation

**Already installed!** The geocoding service is ready to use.

### **If you need to reinstall:**
```bash
pip install geopy>=2.4.0
```

### **Verify Installation:**
```bash
python -c "import geopy; print(f'geopy {geopy.__version__} installed')"
```

---

## 🎉 Summary

✅ **Automatic geocoding** for any US city  
✅ **No API keys** required (free tier)  
✅ **Multiple fallback strategies** for reliability  
✅ **Pre-configured cities** for instant responses  
✅ **Background processing** - doesn't block requests  
✅ **Rate limiting** built-in  
✅ **Production-ready**

**Try it now:**
```bash
POST http://localhost:8000/api/v1/unified/sync/city?city=YourCity&state=YourState
```

🎯 **Any US city now works!**

