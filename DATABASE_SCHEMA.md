# 🗄️ ActivityGuide Database Schema

Complete database schema documentation for the ActivityGuide platform.

## 📊 Database Overview

**Database Type**: SQLite (development) / PostgreSQL (production)  
**ORM**: SQLAlchemy  
**Location**: `app/core/database.py`

## 🏗️ Schema Structure

### 📋 **Core Tables**

#### 1. **`events`** - Original Event Storage
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    summary TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    location_name VARCHAR(255),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    age_range_min INTEGER,
    age_range_max INTEGER,
    is_indoor BOOLEAN DEFAULT TRUE,
    is_free BOOLEAN DEFAULT FALSE,
    price_min FLOAT,
    price_max FLOAT,
    capacity INTEGER,
    source VARCHAR(50) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    source_url VARCHAR(500),
    image_url VARCHAR(500),
    tags JSON,
    is_active BOOLEAN DEFAULT TRUE,
    last_synced DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. **`unified_events`** - Enhanced Multi-Source Events ⭐
```sql
CREATE TABLE unified_events (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(100) NOT NULL,
    source event_source_enum NOT NULL,
    event_type event_type_enum DEFAULT 'event',
    
    -- Basic information
    title VARCHAR(255) NOT NULL,
    description TEXT,
    summary TEXT,
    short_description VARCHAR(500),
    
    -- Timing
    start_time DATETIME,
    end_time DATETIME,
    start_date DATETIME,
    end_date DATETIME,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern JSON,
    
    -- Location
    location_name VARCHAR(255),
    venue_name VARCHAR(255),
    address VARCHAR(500),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'US',
    latitude FLOAT,
    longitude FLOAT,
    location_accuracy VARCHAR(50),
    
    -- Categorization
    primary_category VARCHAR(100),
    secondary_categories JSON,
    subcategory VARCHAR(100),
    tags JSON,
    
    -- Age targeting
    age_range_min INTEGER,
    age_range_max INTEGER,
    age_categories JSON,
    target_audience JSON,
    
    -- Physical characteristics
    is_indoor BOOLEAN,
    is_outdoor BOOLEAN,
    is_virtual BOOLEAN DEFAULT FALSE,
    is_accessible BOOLEAN,
    weather_dependent BOOLEAN DEFAULT FALSE,
    
    -- Pricing
    is_free BOOLEAN,
    price_min FLOAT,
    price_max FLOAT,
    price_currency VARCHAR(3) DEFAULT 'USD',
    pricing_model VARCHAR(50),
    pricing_notes TEXT,
    
    -- Capacity
    capacity INTEGER,
    current_registrations INTEGER,
    is_full BOOLEAN DEFAULT FALSE,
    requires_registration BOOLEAN DEFAULT FALSE,
    registration_deadline DATETIME,
    
    -- Contact & booking
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    booking_url VARCHAR(500),
    registration_url VARCHAR(500),
    
    -- Media
    image_url VARCHAR(500),
    image_urls JSON,
    video_url VARCHAR(500),
    website_url VARCHAR(500),
    social_media_urls JSON,
    
    -- Source data
    source_url VARCHAR(500),
    source_data JSON,
    source_rating FLOAT,
    source_review_count INTEGER,
    
    -- Quality & validation
    data_quality_score FLOAT DEFAULT 1.0,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date DATETIME,
    verified_by VARCHAR(255),
    
    -- Activity details
    activity_level VARCHAR(50),
    skill_level VARCHAR(50),
    equipment_required JSON,
    prerequisites TEXT,
    
    -- Seasonal
    is_seasonal BOOLEAN DEFAULT FALSE,
    season_start VARCHAR(20),
    season_end VARCHAR(20),
    is_holiday_specific BOOLEAN DEFAULT FALSE,
    holiday_type VARCHAR(50),
    
    -- Metadata & tracking
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    priority_score FLOAT DEFAULT 0.0,
    view_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_synced DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    
    -- Relationships
    related_events JSON,
    parent_event_id UUID,
    organization_id VARCHAR(100)
);
```

#### 3. **`user_profiles`** - User Personalization
```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    default_zip_code VARCHAR(10),
    max_distance_miles INTEGER DEFAULT 25,
    children_ages JSON,
    preferred_categories JSON,
    preferred_activity_types JSON,
    email_notifications BOOLEAN DEFAULT TRUE,
    weekly_digest BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. **`provider_submissions`** - Community Events
```sql
CREATE TABLE provider_submissions (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    location_name VARCHAR(255),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    category VARCHAR(100),
    age_range_min INTEGER,
    age_range_max INTEGER,
    is_indoor BOOLEAN DEFAULT TRUE,
    is_free BOOLEAN DEFAULT FALSE,
    price FLOAT,
    status VARCHAR(50) DEFAULT 'pending',
    reviewed_by VARCHAR(255),
    reviewed_at DATETIME,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. **`event_providers`** - Organizations & Venues
```sql
CREATE TABLE event_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(100),
    description TEXT,
    email VARCHAR(255),
    phone VARCHAR(50),
    website VARCHAR(500),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT,
    is_verified BOOLEAN DEFAULT FALSE,
    data_source VARCHAR(100),
    external_id VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. **`event_categories`** - Standardized Categories
```sql
CREATE TABLE event_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id INTEGER,
    icon VARCHAR(100),
    color VARCHAR(7),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 7. **`event_sync_logs`** - Sync Monitoring
```sql
CREATE TABLE event_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source event_source_enum NOT NULL,
    sync_type VARCHAR(50),
    status VARCHAR(50),
    events_processed INTEGER DEFAULT 0,
    events_created INTEGER DEFAULT 0,
    events_updated INTEGER DEFAULT 0,
    events_deleted INTEGER DEFAULT 0,
    errors JSON,
    sync_duration_seconds FLOAT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);
```

## 🔧 **Enums**

### Event Source Enum
```sql
CREATE TYPE event_source_enum AS ENUM (
    'eventbrite',
    'yelp',
    'google_places',
    'ticketmaster',
    'meetup',
    'recreation_gov',
    'ymca',
    'boys_girls_club',
    'openstreetmap',
    'community'
);
```

### Event Type Enum
```sql
CREATE TYPE event_type_enum AS ENUM (
    'event',
    'venue',
    'class',
    'program'
);
```

### Age Category Enum
```sql
CREATE TYPE age_category_enum AS ENUM (
    'toddler',
    'preschool',
    'elementary',
    'middle_school',
    'high_school',
    'all_ages',
    'family'
);
```

## 📊 **Indexes**

### Primary Indexes
```sql
-- Unified Events
CREATE INDEX idx_unified_events_source ON unified_events(source);
CREATE INDEX idx_unified_events_type ON unified_events(event_type);
CREATE INDEX idx_unified_events_title ON unified_events(title);
CREATE INDEX idx_unified_events_start_time ON unified_events(start_time);
CREATE INDEX idx_unified_events_start_date ON unified_events(start_date);
CREATE INDEX idx_unified_events_city ON unified_events(city);
CREATE INDEX idx_unified_events_zip_code ON unified_events(zip_code);
CREATE INDEX idx_unified_events_latitude ON unified_events(latitude);
CREATE INDEX idx_unified_events_longitude ON unified_events(longitude);
CREATE INDEX idx_unified_events_category ON unified_events(primary_category);
CREATE INDEX idx_unified_events_indoor ON unified_events(is_indoor);
CREATE INDEX idx_unified_events_free ON unified_events(is_free);
CREATE INDEX idx_unified_events_active ON unified_events(is_active);

-- Original Events
CREATE INDEX idx_events_title ON events(title);
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_events_city ON events(city);
CREATE INDEX idx_events_zip_code ON events(zip_code);
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_active ON events(is_active);

-- User Profiles
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
```

## 🔗 **Relationships**

### Key Relationships
```sql
-- Unified Events can reference parent events (recurring)
ALTER TABLE unified_events 
ADD CONSTRAINT fk_parent_event 
FOREIGN KEY (parent_event_id) REFERENCES unified_events(id);

-- Event Categories can be hierarchical
ALTER TABLE event_categories 
ADD CONSTRAINT fk_parent_category 
FOREIGN KEY (parent_category_id) REFERENCES event_categories(id);
```

## 📈 **Data Types Summary**

| Field Type | Usage | Examples |
|------------|-------|----------|
| `UUID` | Primary keys | `id`, `parent_event_id` |
| `VARCHAR(n)` | Text fields | `title`, `city`, `state` |
| `TEXT` | Long text | `description`, `summary` |
| `JSON` | Arrays/Objects | `tags`, `secondary_categories` |
| `DATETIME` | Timestamps | `start_time`, `created_at` |
| `BOOLEAN` | True/False | `is_active`, `is_free` |
| `FLOAT` | Numbers | `latitude`, `price_min` |
| `INTEGER` | Whole numbers | `capacity`, `age_range_min` |
| `ENUM` | Predefined values | `source`, `event_type` |

## 🚀 **Database Migration**

### Create Tables
```python
# Run this to create all tables
from app.core.database import engine
from app.models.event import Base as EventBase
from app.models.unified_event import Base as UnifiedBase

# Create original tables
EventBase.metadata.create_all(bind=engine)

# Create unified tables
UnifiedBase.metadata.create_all(bind=engine)
```

### SQLite vs PostgreSQL
- **Development**: Uses SQLite (`sqlite:///./activityguide.db`)
- **Production**: Should use PostgreSQL for better performance
- **UUIDs**: PostgreSQL native support, SQLite uses text representation

## 📊 **Sample Data**

### Event Categories
```sql
INSERT INTO event_categories (name, display_name, description) VALUES
('family', 'Family Activities', 'Activities suitable for families'),
('kids', 'Kids Activities', 'Activities for children'),
('sports', 'Sports', 'Athletic activities and sports'),
('arts', 'Arts & Crafts', 'Creative and artistic activities'),
('education', 'Education', 'Learning and educational programs'),
('outdoor', 'Outdoor Recreation', 'Outdoor activities and nature'),
('indoor', 'Indoor Activities', 'Activities that take place indoors'),
('free', 'Free Events', 'No cost activities'),
('low_cost', 'Low Cost', 'Affordable activities');
```

## 🔍 **Query Examples**

### Search Events by Location
```sql
SELECT * FROM unified_events 
WHERE zip_code = '48104' 
AND is_active = TRUE 
ORDER BY start_time ASC;
```

### Find Free Family Events
```sql
SELECT * FROM unified_events 
WHERE is_free = TRUE 
AND (age_categories LIKE '%family%' OR age_categories LIKE '%all_ages%')
AND is_active = TRUE;
```

### Events by Source
```sql
SELECT source, COUNT(*) as event_count 
FROM unified_events 
WHERE is_active = TRUE 
GROUP BY source;
```

## 🛠️ **Maintenance**

### Cleanup Old Events
```sql
-- Mark old events as inactive
UPDATE unified_events 
SET is_active = FALSE 
WHERE last_synced < datetime('now', '-30 days');
```

### Data Quality Check
```sql
-- Find events with low data quality
SELECT id, title, data_quality_score 
FROM unified_events 
WHERE data_quality_score < 0.5 
ORDER BY data_quality_score ASC;
```

This schema supports comprehensive event management with multi-source integration, user personalization, and advanced search capabilities! 🎯
