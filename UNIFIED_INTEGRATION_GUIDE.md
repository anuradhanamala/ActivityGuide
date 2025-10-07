# 🎯 Unified Event Integration Guide

This guide explains how to integrate with multiple event data sources using the unified schema and API system.

## 📊 Data Sources Covered

### ✅ Currently Implemented
- **Eventbrite** - Events and classes with family/kids filters
- **Yelp** - Family-friendly businesses (museums, playgrounds, amusement parks)
- **Google Places** - Parks, gyms, dance studios, martial arts schools, museums
- **Ticketmaster** - Big kid-friendly national events (Disney, circus, family shows)

### 🚀 New Sources Added
- **Meetup** - Nationwide community events (STEM, arts, clubs, sports)
- **Recreation.gov (RIDB API)** - National park programs, camps, ranger activities
- **YMCA** - Programs and activities (web scraping approach)
- **Boys & Girls Clubs** - Activities and programs (web scraping approach)
- **OpenStreetMap** - Nationwide playgrounds, public parks, sports facilities

## 🗄️ Unified Database Schema

### Core Tables

#### `unified_events`
The main table storing events from all sources with standardized fields:

```sql
-- Primary identifiers
id (UUID) - Primary key
external_id (String) - Source-specific ID
source (Enum) - Data source
event_type (Enum) - event, venue, class, program

-- Basic information
title, description, summary, short_description

-- Timing
start_time, end_time, start_date, end_date
is_recurring, recurrence_pattern (JSON)

-- Location
location_name, venue_name, address, city, state, zip_code
latitude, longitude, location_accuracy

-- Categorization
primary_category, secondary_categories (JSON), subcategory, tags (JSON)

-- Age targeting
age_range_min, age_range_max, age_categories (JSON), target_audience (JSON)

-- Physical characteristics
is_indoor, is_outdoor, is_virtual, is_accessible, weather_dependent

-- Pricing
is_free, price_min, price_max, price_currency, pricing_model, pricing_notes

-- Capacity
capacity, current_registrations, is_full, requires_registration, registration_deadline

-- Contact & booking
contact_name, contact_email, contact_phone, booking_url, registration_url

-- Media
image_url, image_urls (JSON), video_url, website_url, social_media_urls (JSON)

-- Source data
source_url, source_data (JSON), source_rating, source_review_count

-- Quality & validation
data_quality_score, is_verified, verification_date, verified_by

-- Activity details
activity_level, skill_level, equipment_required (JSON), prerequisites

-- Seasonal
is_seasonal, season_start, season_end, is_holiday_specific, holiday_type

-- Metadata
is_active, is_featured, priority_score, view_count, click_count

-- Timestamps
created_at, updated_at, last_synced, expires_at

-- Relationships
related_events (JSON), parent_event_id, organization_id
```

#### Supporting Tables
- `event_providers` - Track organizations and venues
- `event_categories` - Standardized categories
- `event_sync_logs` - Track sync operations

## 🔧 API Integration

### Search Endpoint
```http
GET /api/v1/unified/search
```

**Parameters:**
- `zip_code` - ZIP code to search near
- `city` - City to search in
- `state` - State to search in
- `radius_miles` - Search radius (1-100 miles)
- `categories` - Event categories array
- `age_min` / `age_max` - Age range filtering
- `is_free` - Free events only
- `is_indoor` - Indoor events only
- `event_type` - Type of event (event, venue, class, program)
- `sources` - Specific data sources to include
- `start_date` / `end_date` - Date range filtering
- `limit` - Number of results (1-100)

**Example:**
```bash
curl "http://localhost:8000/api/v1/unified/search?zip_code=48104&categories=family,sports&age_min=5&age_max=12&is_free=true&limit=20"
```

### Available Sources Endpoint
```http
GET /api/v1/unified/sources
```

### Sync Management
```http
POST /api/v1/unified/sync/trigger
GET /api/v1/unified/sync/status
```

## 🔑 API Keys Setup

Add these to your `.env` file:

```env
# Existing APIs
EVENTBRITE_API_KEY=your_eventbrite_key
YELP_API_KEY=your_yelp_key
GOOGLE_PLACES_API_KEY=your_google_places_key
TICKETMASTER_API_KEY=your_ticketmaster_key

# New APIs
MEETUP_API_KEY=your_meetup_key
RECREATION_GOV_API_KEY=your_recreation_gov_key

# Optional (for web scraping)
YMCA_API_KEY=your_ymca_key
BOYS_GIRLS_CLUB_API_KEY=your_bgc_key

# OpenStreetMap (no API key required)
OSM_USER_AGENT=ActivityGuide/1.0 (Family Event Discovery)
```

## 🚀 Getting Started

### 1. Database Migration
```bash
# Create new tables
python -c "
from app.core.database import engine
from app.models.unified_event import Base
Base.metadata.create_all(bind=engine)
"
```

### 2. Initial Data Sync
```bash
# Trigger full sync
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger"
```

### 3. Search Events
```bash
# Search for family events in Ann Arbor
curl "http://localhost:8000/api/v1/unified/search?city=Ann%20Arbor&categories=family&limit=10"
```

## 📈 Data Quality & Scoring

Each event gets a `data_quality_score` (0-1) based on:
- **Required fields** (title, location, start_time): 0.3 points each
- **Optional fields** (description, address, image_url, contact_info): 0.05 points each
- **Maximum score**: 1.0

Events are ranked by:
1. `priority_score` (customizable)
2. `data_quality_score`
3. `start_time` (earliest first)
4. `title` (alphabetical)

## 🔄 Sync Process

### Automatic Sync
- Runs every 6 hours by default
- Processes all configured sources
- Updates existing events or creates new ones
- Logs all operations for monitoring

### Manual Sync
```python
from app.services.unified_sync_service import unified_sync_service
from app.core.database import get_db

db = next(get_db())
result = await unified_sync_service.sync_all_sources(db, zip_codes=["48104"])
print(f"Synced {result['total_events']} events")
```

## 🎯 Category Mapping

### Standardized Categories
The system maps source-specific categories to standardized ones:

| Source | Source Categories | Standardized |
|--------|------------------|--------------|
| Eventbrite | family, kids | family, kids |
| Yelp | museums, playgrounds | family_venue, outdoor |
| Google Places | park, museum, gym | outdoor_recreation, family_venue, fitness |
| Meetup | STEM, arts, sports | education, arts, sports |
| Recreation.gov | camping, hiking | outdoor_recreation |
| OpenStreetMap | playground, park | outdoor_recreation |

### Age Categories
- `toddler` (0-2)
- `preschool` (3-5)
- `elementary` (6-11)
- `middle_school` (12-14)
- `high_school` (15-17)
- `all_ages`
- `family`

## 🔍 Advanced Search Examples

### Find Free Outdoor Activities for Kids 5-10
```bash
curl "http://localhost:8000/api/v1/unified/search?zip_code=48104&age_min=5&age_max=10&is_free=true&is_indoor=false&categories=outdoor,recreation"
```

### Find STEM Programs for Teens
```bash
curl "http://localhost:8000/api/v1/unified/search?city=Ann%20Arbor&age_min=13&age_max=17&categories=science,technology&sources=meetup,eventbrite"
```

### Find Summer Camps
```bash
curl "http://localhost:8000/api/v1/unified/search?state=MI&categories=summer_camp,education&start_date=2024-06-01&end_date=2024-08-31"
```

## 📊 Monitoring & Analytics

### Sync Status
```bash
curl "http://localhost:8000/api/v1/unified/sync/status"
```

### Event Statistics
- Total events by source
- Category distribution
- Geographic coverage
- Data quality metrics

## 🛠️ Customization

### Adding New Sources
1. Create new client in `app/services/unified_api_clients.py`
2. Add source to `EventSource` enum
3. Implement normalization logic
4. Add to sync service

### Custom Categories
1. Add to `EventCategory` table
2. Update category mapping logic
3. Add to API response schemas

### Quality Scoring
Modify `calculate_data_quality_score()` method to adjust scoring criteria.

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Check `.env` file configuration
   - Verify API key permissions
   - Check rate limits

2. **Sync Failures**
   - Check sync logs: `/api/v1/unified/sync/status`
   - Verify network connectivity
   - Check source API status

3. **Data Quality Issues**
   - Review normalization logic
   - Check source data format changes
   - Update data quality scoring

### Debug Mode
```python
import logging
logging.getLogger("app.services.unified_api_clients").setLevel(logging.DEBUG)
```

## 📚 API Documentation

Full API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new sources
4. Update documentation
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.
