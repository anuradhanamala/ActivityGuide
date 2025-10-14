# 🔄 Data Aggregation Flow in ActivityGuide

Complete documentation of how data is aggregated from multiple sources (avenues) in your ActivityGuide platform.

## 📊 **Data Aggregation Architecture**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA AGGREGATION PIPELINE                       │
└─────────────────────────────────────────────────────────────────────┘

STEP 1: DATA COLLECTION (Multiple Avenues)
┌─────────────────────────────────────────────────────────────────────┐
│  📡 API SOURCES (9 Different Avenues)                              │
├─────────────────────────────────────────────────────────────────────┤
│  1. 🎫 Eventbrite API        → Events & Classes                    │
│  2. 🍽️ Yelp API              → Family Businesses & Venues          │
│  3. 🗺️ Google Places API     → Parks, Gyms, Museums               │
│  4. 🎪 Ticketmaster API      → Family Shows & Entertainment        │
│  5. 👥 Meetup API            → Community Events & Groups           │
│  6. 🏞️ Recreation.gov API    → National Park Programs             │
│  7. 🏊 YMCA API              → Programs & Activities               │
│  8. 🎯 Boys & Girls Clubs    → Youth Activities                    │
│  9. 🗺️ OpenStreetMap API     → Playgrounds & Public Parks         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
STEP 2: PARALLEL FETCHING
┌─────────────────────────────────────────────────────────────────────┐
│  🔄 UnifiedSyncService.sync_all_sources()                          │
├─────────────────────────────────────────────────────────────────────┤
│  • Iterates through all 9 sources                                  │
│  • Calls _fetch_source_events() for each source                   │
│  • Fetches data for multiple ZIP codes                            │
│  • Executes searches with SearchParams                            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
STEP 3: DATA NORMALIZATION
┌─────────────────────────────────────────────────────────────────────┐
│  🔧 Source-Specific Normalization                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Each API returns different data formats:                          │
│                                                                     │
│  Eventbrite Format:                                                │
│  {                                                                  │
│    "name": {"text": "Event Name"},                                │
│    "start": {"utc": "2024-01-01T10:00:00Z"},                      │
│    "venue": {"address": {...}}                                     │
│  }                                                                  │
│                                                                     │
│  Yelp Format:                                                       │
│  {                                                                  │
│    "name": "Business Name",                                        │
│    "location": {"address1": "123 Main St"},                       │
│    "coordinates": {"latitude": 42.5, "longitude": -83.1}          │
│  }                                                                  │
│                                                                     │
│  ↓ NORMALIZED TO UNIFIED FORMAT ↓                                 │
│                                                                     │
│  Unified Format:                                                    │
│  {                                                                  │
│    "external_id": "source_specific_id",                           │
│    "source": "eventbrite",                                         │
│    "event_type": "event",                                          │
│    "title": "Event Name",                                          │
│    "start_time": datetime,                                         │
│    "location_name": "Venue Name",                                  │
│    "address": "Full Address",                                      │
│    "city": "City",                                                 │
│    "state": "State",                                               │
│    "zip_code": "12345",                                            │
│    "latitude": 42.5,                                               │
│    "longitude": -83.1,                                             │
│    "primary_category": "family",                                   │
│    "tags": ["tag1", "tag2"],                                       │
│    "is_free": true/false,                                          │
│    "data_quality_score": 0.85                                      │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
STEP 4: DEDUPLICATION & VALIDATION
┌─────────────────────────────────────────────────────────────────────┐
│  🔍 _save_event() - Smart Deduplication                            │
├─────────────────────────────────────────────────────────────────────┤
│  • Check if event exists: (external_id + source)                   │
│  • If exists → UPDATE existing record                              │
│  • If new → CREATE new record                                      │
│  • Calculate data_quality_score (0-1)                              │
│  • Set last_synced timestamp                                       │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
STEP 5: DATABASE STORAGE
┌─────────────────────────────────────────────────────────────────────┐
│  💾 unified_events TABLE                                           │
├─────────────────────────────────────────────────────────────────────┤
│  All events stored in single unified table with:                   │
│  • UUID primary key                                                │
│  • Source tracking (which API it came from)                        │
│  • Standardized fields (50+ fields)                                │
│  • Quality scores                                                  │
│  • Timestamps (created_at, updated_at, last_synced)               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
STEP 6: AGGREGATED SEARCH
┌─────────────────────────────────────────────────────────────────────┐
│  🔎 Unified Search API                                             │
├─────────────────────────────────────────────────────────────────────┤
│  Single query searches ALL sources simultaneously:                 │
│                                                                     │
│  GET /api/v1/unified/search?                                       │
│      zip_code=48104&                                               │
│      categories=family,sports&                                     │
│      age_min=5&age_max=12                                          │
│                                                                     │
│  Returns aggregated results from:                                  │
│  • Eventbrite events                                               │
│  • Yelp venues                                                     │
│  • Google Places locations                                         │
│  • Meetup community events                                         │
│  • Recreation.gov programs                                         │
│  • OpenStreetMap playgrounds                                       │
│  • ... and all other sources                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 **Detailed Aggregation Process**

### **1. Parallel Data Fetching**

```python
# UnifiedSyncService coordinates all sources
async def sync_all_sources(self, db: Session, zip_codes: List[str]):
    results = {
        "total_sources": 0,
        "successful_sources": 0,
        "total_events": 0,
        "events_created": 0,
        "events_updated": 0,
        "errors": []
    }
    
    # Get all available sources
    available_sources = self.api_manager.get_available_sources()
    
    # Sync each source sequentially (could be parallel)
    for source in available_sources:
        source_result = await self._sync_source(db, source, zip_codes)
        results["total_events"] += source_result["total_events"]
        results["events_created"] += source_result["events_created"]
        results["events_updated"] += source_result["events_updated"]
    
    return results
```

### **2. Source-Specific Fetching**

```python
async def _fetch_source_events(self, source: EventSource, zip_codes: List[str]):
    all_events = []
    
    for zip_code in zip_codes:
        # Create standardized search parameters
        params = SearchParams(
            location=zip_code,
            zip_code=zip_code,
            radius_miles=25,
            categories=["family", "kids", "education", "sports", "arts"],
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=90),
            limit=50
        )
        
        # Route to appropriate API client
        if source == EventSource.MEETUP:
            events = await client.search_events(params)
        elif source == EventSource.RECREATION_GOV:
            events = await client.search_facilities(params)
        elif source == EventSource.EVENTBRITE:
            events = await client.search_events(location=zip_code, ...)
        # ... etc for each source
        
        all_events.extend(events)
    
    return all_events
```

### **3. Data Normalization**

Each API client has a `_normalize_*()` method:

```python
# Eventbrite Normalization
def _normalize_event(self, event_data: Dict) -> Dict:
    return {
        "external_id": event_data.get("id"),
        "source": EventSource.EVENTBRITE,
        "event_type": EventType.EVENT,
        "title": event_data.get("name", {}).get("text"),
        "start_time": event_data.get("start", {}).get("utc"),
        "location_name": venue.get("name"),
        "address": venue.get("address", {}).get("localized_area_display"),
        "city": venue.get("address", {}).get("city"),
        "latitude": venue.get("address", {}).get("latitude"),
        "is_free": event_data.get("is_free", False),
        "data_quality_score": self.calculate_data_quality_score(event_data)
    }

# Yelp Normalization
def _normalize_business(self, business_data: Dict) -> Dict:
    return {
        "external_id": business_data.get("id"),
        "source": EventSource.YELP,
        "event_type": EventType.VENUE,
        "title": business_data.get("name"),
        "location_name": business_data.get("name"),
        "address": location.get("address1"),
        "city": location.get("city"),
        "latitude": business_data.get("coordinates", {}).get("latitude"),
        "is_free": business_data.get("price") == "$",
        "data_quality_score": self.calculate_data_quality_score(business_data)
    }

# OpenStreetMap Normalization
def _normalize_osm_element(self, element: Dict) -> Dict:
    tags = element.get("tags", {})
    return {
        "external_id": f"osm_{element.get('id')}",
        "source": EventSource.OPENSTREETMAP,
        "event_type": EventType.VENUE,
        "title": tags.get("name", f"{tags.get('leisure', 'place').title()}"),
        "location_name": tags.get("name"),
        "latitude": element.get("lat"),
        "longitude": element.get("lon"),
        "is_free": True,
        "is_outdoor": True,
        "data_quality_score": self.calculate_data_quality_score(element)
    }
```

### **4. Deduplication Logic**

```python
async def _save_event(self, db: Session, event_data: Dict):
    # Check if event already exists
    existing_event = db.query(UnifiedEvent).filter(
        and_(
            UnifiedEvent.external_id == event_data.get("external_id"),
            UnifiedEvent.source == event_data.get("source")
        )
    ).first()
    
    if existing_event:
        # UPDATE existing event
        for key, value in event_data.items():
            if hasattr(existing_event, key) and value is not None:
                setattr(existing_event, key, value)
        
        existing_event.updated_at = datetime.now()
        existing_event.last_synced = datetime.now()
        db.commit()
        return existing_event
    else:
        # CREATE new event
        new_event = UnifiedEvent(**event_data)
        new_event.created_at = datetime.now()
        new_event.last_synced = datetime.now()
        db.add(new_event)
        db.commit()
        return new_event
```

### **5. Aggregated Search**

```python
# Single search queries ALL sources
@router.get("/search")
async def search_unified_events(
    zip_code: str,
    categories: List[str],
    age_min: int,
    age_max: int,
    db: Session = Depends(get_db)
):
    # Build query across ALL sources
    query = db.query(UnifiedEvent).filter(UnifiedEvent.is_active == True)
    
    # Apply filters
    if zip_code:
        query = query.filter(UnifiedEvent.zip_code == zip_code)
    if categories:
        query = query.filter(UnifiedEvent.primary_category.in_(categories))
    if age_min and age_max:
        query = query.filter(
            UnifiedEvent.age_range_min <= age_max,
            UnifiedEvent.age_range_max >= age_min
        )
    
    # Order by quality and relevance
    query = query.order_by(
        desc(UnifiedEvent.priority_score),
        desc(UnifiedEvent.data_quality_score),
        UnifiedEvent.start_time.asc()
    )
    
    # Return aggregated results from ALL sources
    events = query.limit(50).all()
    return events
```

## 📊 **Data Flow Example**

### **User searches: "Find sports activities for 8-year-olds in Troy, MI"**

```
1. REQUEST RECEIVED
   ↓
2. QUERY DATABASE (unified_events table)
   ↓
3. RESULTS AGGREGATED FROM:
   • Eventbrite: 15 sports classes
   • Yelp: 8 sports facilities
   • Google Places: 12 gyms & sports centers
   • Meetup: 5 community sports groups
   • Recreation.gov: 3 park programs
   • OpenStreetMap: 20 sports fields & playgrounds
   ↓
4. FILTERED BY:
   • Location: Troy, MI (zip codes: 48007, 48083, 48084, 48085)
   • Age: 8 years old (age_range_min <= 8 <= age_range_max)
   • Category: sports
   ↓
5. SORTED BY:
   • Priority score (featured events first)
   • Data quality score (complete data first)
   • Start time (upcoming events first)
   ↓
6. RETURN 50 AGGREGATED RESULTS
   [
     {source: "eventbrite", title: "Youth Basketball Camp"},
     {source: "yelp", title: "Troy Sports Center"},
     {source: "google_places", title: "Troy Community Center Gym"},
     {source: "meetup", title: "Kids Soccer Meetup"},
     {source: "openstreetmap", title: "Troy Sports Complex"},
     ...
   ]
```

## 🎯 **Key Aggregation Features**

### **1. Multi-Source Coordination**
- **9 different API sources** feeding into one database
- **Parallel fetching** for faster data collection
- **Source tracking** to know where each event came from

### **2. Data Normalization**
- **50+ standardized fields** across all sources
- **Consistent data format** regardless of source
- **Quality scoring** (0-1) for each event

### **3. Smart Deduplication**
- **Unique key**: (external_id + source)
- **Update existing** events instead of creating duplicates
- **Timestamp tracking** (created_at, updated_at, last_synced)

### **4. Unified Search**
- **Single query** searches all sources
- **20+ filter options** (location, age, category, price, etc.)
- **Intelligent ranking** by quality and relevance

### **5. Sync Monitoring**
- **Sync logs** track each operation
- **Error tracking** for failed sources
- **Statistics** (events processed, created, updated)

## 📈 **Aggregation Statistics**

**Example Sync Results:**
```json
{
  "total_sources": 9,
  "successful_sources": 7,
  "total_events": 2,847,
  "events_created": 1,523,
  "events_updated": 1,324,
  "errors": [
    "YMCA API: No public API available",
    "Boys & Girls Clubs: Web scraping not implemented"
  ],
  "sources_breakdown": {
    "eventbrite": 423,
    "yelp": 567,
    "google_places": 892,
    "ticketmaster": 145,
    "meetup": 234,
    "recreation_gov": 78,
    "openstreetmap": 508
  }
}
```

## 🚀 **Benefits of This Aggregation Approach**

1. **Comprehensive Coverage**: Data from 9+ sources in one place
2. **Single API**: One search endpoint for all sources
3. **Consistent Format**: Standardized data structure
4. **Quality Control**: Automatic scoring and validation
5. **Deduplication**: No duplicate events
6. **Fast Search**: Pre-aggregated data in database
7. **Source Tracking**: Know where each event came from
8. **Easy Expansion**: Add new sources easily

This aggregation system gives you a **powerful unified event database** with comprehensive coverage across multiple data sources! 🎯
