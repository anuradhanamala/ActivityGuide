"""
Create unified event tables in the database
"""

import sys
sys.path.insert(0, '.')

from app.core.database import engine
from app.models.unified_event import Base
from sqlalchemy import inspect


def create_tables():
    """Create all unified event tables"""
    
    print('=' * 70)
    print('CREATING UNIFIED EVENT TABLES')
    print('=' * 70)
    print()
    
    # Check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print('Existing tables:')
    for table in existing_tables:
        print(f'  - {table}')
    print()
    
    # Create new tables
    print('Creating unified event tables...')
    print('-' * 70)
    
    try:
        Base.metadata.create_all(bind=engine)
        
        print('[SUCCESS] Tables created successfully!')
        print()
        
        # Check new tables
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        
        print('All tables now:')
        for table in new_tables:
            if table not in existing_tables:
                print(f'  [NEW] {table}')
            else:
                print(f'  [OLD] {table}')
        
        print()
        print('=' * 70)
        print('Tables created for:')
        print('  - unified_events (main event storage)')
        print('  - event_providers (organizations & venues)')
        print('  - event_categories (standardized categories)')
        print('  - event_sync_logs (sync monitoring)')
        print('=' * 70)
        
    except Exception as e:
        print(f'[ERROR] Failed to create tables: {e}')
        print(f'Error type: {type(e).__name__}')


if __name__ == '__main__':
    create_tables()
