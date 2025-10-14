"""
Full Yelp sync - Import all Yelp businesses into unified_events table
"""

import asyncio
import sys
sys.path.insert(0, '.')

from app.services.api_clients import YelpClient
from app.core.database import get_db
from app.models.unified_event import UnifiedEvent, EventSource
from datetime import datetime


async def sync_all_yelp_data():
    """Sync all Yelp businesses for specified ZIP codes"""
    
    print('=' * 80)
    print('FULL YELP SYNC TO unified_events TABLE')
    print('=' * 80)
    print()
    
    zip_codes = ["48083", "48084", "48085"]  # Troy, MI
    
    yelp_client = YelpClient()
    db = next(get_db())
    
    total_fetched = 0
    total_saved = 0
    total_updated = 0
    errors = []
    
    try:
        for zip_code in zip_codes:
            print(f'Fetching Yelp businesses for ZIP: {zip_code}...')
            
            try:
                # Fetch businesses
                businesses = await yelp_client.search_businesses(
                    location=zip_code,
                    categories=["museums", "playgrounds", "amusementparks", 
                               "kids_activities", "gymnastics", "martialarts",
                               "dancestudio", "musicschools", "trampoline"]
                )
                
                print(f'  Found {len(businesses)} businesses')
                total_fetched += len(businesses)
                
                # Save each business
                for biz in businesses:
                    try:
                        # Remove invalid fields for UnifiedEvent
                        biz_copy = biz.copy()
                        if 'category' in biz_copy:
                            del biz_copy['category']
                        if 'source_id' in biz_copy:
                            del biz_copy['source_id']
                        
                        # Check if already exists
                        existing = db.query(UnifiedEvent).filter(
                            UnifiedEvent.external_id == biz_copy.get('external_id'),
                            UnifiedEvent.source == EventSource.YELP
                        ).first()
                        
                        if existing:
                            # Update existing
                            for key, value in biz_copy.items():
                                if hasattr(existing, key) and value is not None:
                                    setattr(existing, key, value)
                            existing.updated_at = datetime.now()
                            existing.last_synced = datetime.now()
                            total_updated += 1
                        else:
                            # Create new
                            new_event = UnifiedEvent(**biz_copy)
                            new_event.created_at = datetime.now()
                            new_event.last_synced = datetime.now()
                            db.add(new_event)
                            total_saved += 1
                        
                        db.commit()
                        
                    except Exception as e:
                        print(f'  Error saving {biz.get("title")}: {e}')
                        errors.append(str(e))
                        db.rollback()
                        continue
                
            except Exception as e:
                print(f'  Error fetching for {zip_code}: {e}')
                errors.append(str(e))
                continue
        
        print()
        print('=' * 80)
        print('SYNC RESULTS')
        print('=' * 80)
        print(f'Total businesses fetched: {total_fetched}')
        print(f'New events created: {total_saved}')
        print(f'Events updated: {total_updated}')
        print(f'Errors: {len(errors)}')
        print()
        
        # Verify database
        yelp_count = db.query(UnifiedEvent).filter(
            UnifiedEvent.source == EventSource.YELP
        ).count()
        
        print(f'Total Yelp events in database: {yelp_count}')
        print()
        
        if yelp_count > 0:
            print('Sample Yelp events in database:')
            print('-' * 80)
            events = db.query(UnifiedEvent).filter(
                UnifiedEvent.source == EventSource.YELP
            ).limit(10).all()
            
            for i, e in enumerate(events, 1):
                print(f'{i}. {e.title}')
                print(f'   Location: {e.city}, {e.state} {e.zip_code}')
                print(f'   Category: {e.primary_category}')
                tags_display = ', '.join(e.tags[:3]) if e.tags else 'None'
                print(f'   Tags: {tags_display}')
                print()
        
        print('=' * 80)
        print('[SUCCESS] Yelp sync completed!')
        print('=' * 80)
        
    except Exception as e:
        print(f'[ERROR] Sync failed: {e}')
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == '__main__':
    asyncio.run(sync_all_yelp_data())
