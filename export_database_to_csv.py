"""Export database events to CSV file"""
import csv
from app.core.database import get_db
from app.models.unified_event import UnifiedEvent
from datetime import datetime

print("=" * 70)
print("Exporting Database to CSV")
print("=" * 70)
print()

# Get all events from database
db = next(get_db())
events = db.query(UnifiedEvent).all()

print(f"Found {len(events)} events in database")
print()

# Create CSV file
csv_filename = f"activityguide_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Define CSV columns
fieldnames = [
    'id', 'title', 'description', 'summary',
    'event_type', 'primary_category', 'secondary_categories',
    'location_name', 'address', 'city', 'state', 'zip_code',
    'latitude', 'longitude',
    'age_range_min', 'age_range_max',
    'price_min', 'price_max', 'is_free',
    'is_indoor', 'is_outdoor', 'is_virtual',
    'start_time', 'end_time', 'is_recurring', 'recurrence_pattern',
    'source', 'source_url', 'website_url',
    'contact_email', 'contact_phone',
    'image_url', 'source_rating', 'source_review_count',
    'tags',
    'data_quality_score', 'priority_score',
    'is_active', 'is_verified',
    'created_at', 'updated_at', 'last_synced'
]

print(f"Creating CSV file: {csv_filename}")
print()

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write header
    writer.writeheader()
    
    # Write events
    for i, event in enumerate(events, 1):
        row = {
            'id': str(event.id),
            'title': event.title,
            'description': event.description,
            'summary': event.summary,
            'event_type': event.event_type.value if event.event_type else '',
            'primary_category': event.primary_category,
            'secondary_categories': ', '.join(event.secondary_categories) if event.secondary_categories else '',
            'location_name': event.location_name,
            'address': event.address,
            'city': event.city,
            'state': event.state,
            'zip_code': event.zip_code,
            'latitude': event.latitude,
            'longitude': event.longitude,
            'age_range_min': event.age_range_min,
            'age_range_max': event.age_range_max,
            'price_min': event.price_min,
            'price_max': event.price_max,
            'is_free': event.is_free,
            'is_indoor': event.is_indoor,
            'is_outdoor': event.is_outdoor,
            'is_virtual': event.is_virtual,
            'start_time': event.start_time.isoformat() if event.start_time else '',
            'end_time': event.end_time.isoformat() if event.end_time else '',
            'is_recurring': event.is_recurring,
            'recurrence_pattern': str(event.recurrence_pattern) if event.recurrence_pattern else '',
            'source': event.source.value if event.source else '',
            'source_url': event.source_url,
            'website_url': event.website_url,
            'contact_email': event.contact_email,
            'contact_phone': event.contact_phone,
            'image_url': event.image_url,
            'source_rating': event.source_rating,
            'source_review_count': event.source_review_count,
            'tags': ', '.join(str(t) for t in event.tags) if event.tags else '',
            'data_quality_score': event.data_quality_score,
            'priority_score': event.priority_score,
            'is_active': event.is_active,
            'is_verified': event.is_verified,
            'created_at': event.created_at.isoformat() if event.created_at else '',
            'updated_at': event.updated_at.isoformat() if event.updated_at else '',
            'last_synced': event.last_synced.isoformat() if event.last_synced else ''
        }
        
        writer.writerow(row)
        
        if i % 50 == 0:
            print(f"Exported {i}/{len(events)} events...")

print()
print(f"✅ Export complete!")
print(f"   File: {csv_filename}")
print(f"   Total rows: {len(events)}")
print(f"   Total columns: {len(fieldnames)}")
print()

# Show sample data
print("=" * 70)
print("Sample Data (first 5 events):")
print("=" * 70)
for i, event in enumerate(events[:5], 1):
    print(f"{i}. {event.title}")
    print(f"   City: {event.city}, {event.state}")
    print(f"   Source: {event.source.value}")
    print(f"   Category: {event.primary_category}")
    print()

db.close()

print("=" * 70)
print(f"CSV file ready: {csv_filename}")
print("You can open it in Excel or any spreadsheet application")
print("=" * 70)

