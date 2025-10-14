"""
Explore alternative Eventbrite API endpoints for kids activities
"""

import asyncio
import sys
import httpx
sys.path.insert(0, '.')

from app.core.config import settings


async def test_eventbrite_endpoints():
    """Test various Eventbrite API endpoints"""
    
    token = settings.EVENTBRITE_API_KEY
    base_url = "https://www.eventbriteapi.com/v3"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print('=' * 80)
    print('EXPLORING EVENTBRITE API ENDPOINTS FOR KIDS ACTIVITIES')
    print('=' * 80)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Get categories
        print('[TEST 1] Getting Eventbrite Categories...')
        print('-' * 80)
        try:
            response = await client.get(
                f"{base_url}/categories/",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                categories = data.get("categories", [])
                print(f"[SUCCESS] Found {len(categories)} categories")
                print("\nFamily/Kids related categories:")
                for cat in categories:
                    name = cat.get("name", "")
                    if any(keyword in name.lower() for keyword in ["family", "kid", "child", "education"]):
                        print(f"  - {name} (ID: {cat.get('id')})")
            else:
                print(f"[ERROR] Status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        print()
        
        # Test 2: Get subcategories
        print('[TEST 2] Getting Family & Education Subcategories...')
        print('-' * 80)
        try:
            # Try to get subcategories for Family & Education category
            response = await client.get(
                f"{base_url}/subcategories/",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                subcats = data.get("subcategories", [])
                print(f"[SUCCESS] Found {len(subcats)} subcategories")
                print("\nKids/Family subcategories:")
                for subcat in subcats[:20]:  # Show first 20
                    name = subcat.get("name", "")
                    if any(keyword in name.lower() for keyword in ["family", "kid", "child", "education", "youth", "teen"]):
                        print(f"  - {name} (ID: {subcat.get('id')})")
            else:
                print(f"[ERROR] Status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        print()
        
        # Test 3: Browse events (public endpoint)
        print('[TEST 3] Browsing Public Events...')
        print('-' * 80)
        try:
            # Try different browse endpoints
            browse_endpoints = [
                "/events/",
                "/destination/events/",
            ]
            
            for endpoint in browse_endpoints:
                try:
                    response = await client.get(
                        f"{base_url}{endpoint}",
                        headers=headers,
                        params={"expand": "venue,category"}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        events = data.get("events", [])
                        print(f"[SUCCESS] {endpoint} - Found {len(events)} events")
                        if events:
                            for i, event in enumerate(events[:3], 1):
                                print(f"  {i}. {event.get('name', {}).get('text', 'No title')}")
                        break
                    else:
                        print(f"[INFO] {endpoint} - Status: {response.status_code}")
                except Exception as e:
                    print(f"[INFO] {endpoint} - {str(e)[:50]}")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        print()
        
        # Test 4: Event search by category
        print('[TEST 4] Searching Events by Category ID...')
        print('-' * 80)
        try:
            # Family & Education category ID (typically 116)
            params = {
                "categories": "116",  # Family & Education
                "location.address": "Ann Arbor, MI",
                "location.within": "25mi",
                "expand": "venue,category"
            }
            
            response = await client.get(
                f"{base_url}/events/search/",
                headers=headers,
                params=params
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                print(f"[SUCCESS] Found {len(events)} family events")
                for i, event in enumerate(events[:5], 1):
                    print(f"  {i}. {event.get('name', {}).get('text', 'No title')}")
            else:
                print(f"[INFO] Search not available (Status: {response.status_code})")
        except Exception as e:
            print(f"[INFO] {e}")
        
        print()
        
        # Test 5: Venue search
        print('[TEST 5] Searching Venues...')
        print('-' * 80)
        try:
            params = {
                "location.address": "Ann Arbor, MI",
                "location.within": "25mi"
            }
            
            response = await client.get(
                f"{base_url}/venues/",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                venues = data.get("venues", [])
                print(f"[SUCCESS] Found {len(venues)} venues")
                for i, venue in enumerate(venues[:5], 1):
                    print(f"  {i}. {venue.get('name', 'No name')}")
            else:
                print(f"[INFO] Status: {response.status_code}")
        except Exception as e:
            print(f"[INFO] {e}")
        
        print()
        
        # Test 6: User's followed events
        print('[TEST 6] Getting User Followed Events...')
        print('-' * 80)
        try:
            response = await client.get(
                f"{base_url}/users/me/events/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                print(f"[INFO] User has {len(events)} followed events")
            else:
                print(f"[INFO] Status: {response.status_code}")
        except Exception as e:
            print(f"[INFO] {e}")
    
    print()
    print('=' * 80)
    print('RECOMMENDATIONS')
    print('=' * 80)
    print("""
Since /events/search/ is deprecated, here are alternative approaches:

1. CATEGORY-BASED SEARCH:
   - Get Family & Education category ID (116)
   - Use it to filter events you create or manage

2. VENUE-BASED APPROACH:
   - Find venues in your area that host kids activities
   - Get events from those venues

3. ORGANIZATION APPROACH:
   - Partner with organizations that create kids events
   - Access their events through organization API

4. HYBRID APPROACH:
   - Use Eventbrite for events you CREATE/MANAGE
   - Use other APIs for public event discovery:
     * Meetup.com - Great for community kids activities
     * Google Places - Find venues/locations
     * Facebook Events - Wide coverage
     * Yelp - Classes and programs

5. EVENTBRITE WEBHOOKS:
   - Subscribe to event updates
   - Get notified when new events are created
    """)
    print('=' * 80)


if __name__ == '__main__':
    asyncio.run(test_eventbrite_endpoints())
