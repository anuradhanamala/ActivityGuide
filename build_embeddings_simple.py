"""
Simple direct approach to build vector embeddings with ChromaDB
"""

import sys
import os
sys.path.insert(0, '.')

# Disable ChromaDB telemetry to prevent console warnings
os.environ['CHROMA_TELEMETRY'] = 'false'
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

import chromadb
from sentence_transformers import SentenceTransformer
from app.core.database import get_db
from app.models.unified_event import UnifiedEvent
from typing import List


def infer_contextual_traits(event: UnifiedEvent) -> List[str]:
    """
    Infer contextual traits from activity type and description
    to enable better semantic matching for personality-based queries
    """
    traits = []
    
    title_lower = (event.title or '').lower()
    desc_lower = (event.description or '').lower()
    category = (event.primary_category or '').lower()
    tags_lower = ' '.join(str(tag).lower() for tag in (event.tags or []))
    combined = f"{title_lower} {desc_lower} {category} {tags_lower}"
    
    # Personality match traits
    if any(kw in combined for kw in ['theater', 'drama', 'performance', 'stage']):
        traits.extend(['confidence-building', 'self-expression', 'social-skills'])
    
    if any(kw in combined for kw in ['martial arts', 'karate', 'taekwondo', 'judo']):
        traits.extend(['discipline', 'confidence-building', 'structured', 'self-defense'])
    
    if any(kw in combined for kw in ['dance', 'ballet', 'hip hop']):
        traits.extend(['creative', 'expressive', 'coordination', 'artistic'])
    
    if any(kw in combined for kw in ['art', 'paint', 'draw', 'craft', 'creative']):
        traits.extend(['creative', 'quiet-activity', 'hands-on', 'artistic', 'imagination'])
    
    # For "energetic kids" queries
    if any(kw in combined for kw in ['sports', 'basketball', 'soccer', 'football', 'baseball']):
        traits.extend(['high-energy', 'physical', 'team-building', 'active', 'competitive'])
    
    if any(kw in combined for kw in ['gym', 'fitness', 'athletic', 'exercise']):
        traits.extend(['physical', 'active', 'strength', 'high-energy'])
    
    if any(kw in combined for kw in ['swim', 'pool', 'aquatic', 'water']):
        traits.extend(['physical', 'active', 'refreshing', 'summer-activity'])
    
    if any(kw in combined for kw in ['playground', 'park', 'outdoor']):
        traits.extend(['outdoor', 'active', 'free-play', 'exploratory'])
    
    # For "anxious/calm" queries
    if any(kw in combined for kw in ['museum', 'exhibit', 'gallery', 'educational']):
        traits.extend(['calm', 'educational', 'quiet', 'learning', 'curious-minds'])
    
    if any(kw in combined for kw in ['library', 'reading', 'story', 'book']):
        traits.extend(['calm', 'quiet', 'educational', 'literacy', 'peaceful'])
    
    if any(kw in combined for kw in ['yoga', 'meditation', 'mindfulness']):
        traits.extend(['calm', 'mindful', 'relaxing', 'stress-relief'])
    
    # For "social" queries
    if any(kw in combined for kw in ['group', 'class', 'club', 'team']):
        traits.extend(['social', 'group-activity', 'peer-interaction'])
    
    if any(kw in combined for kw in ['camp', 'workshop', 'program']):
        traits.extend(['structured', 'supervised', 'skill-building'])
    
    # Learning and development
    if any(kw in combined for kw in ['science', 'stem', 'coding', 'robotics', 'tech']):
        traits.extend(['educational', 'stem', 'problem-solving', 'analytical', 'curious-minds'])
    
    if any(kw in combined for kw in ['music', 'instrument', 'band', 'orchestra']):
        traits.extend(['creative', 'artistic', 'coordination', 'auditory-learning'])
    
    # Age-specific traits
    if event.age_range_min and event.age_range_min <= 5:
        traits.extend(['toddler-friendly', 'early-childhood'])
    elif event.age_range_min and event.age_range_min <= 8:
        traits.extend(['elementary-age', 'developing-skills'])
    elif event.age_range_min and event.age_range_min >= 12:
        traits.extend(['teen-appropriate', 'adolescent'])
    
    # Group size inference
    if any(kw in combined for kw in ['one-on-one', 'private', 'individual']):
        traits.append('individualized')
    elif any(kw in combined for kw in ['small group', 'intimate']):
        traits.append('small-group')
    
    return list(set(traits))  # Remove duplicates


def create_enriched_document_text(event: UnifiedEvent) -> str:
    """
    Create rich text representation with contextual enrichment
    """
    parts = []
    
    # Title
    parts.append(f"Title: {event.title}")
    
    # Tags
    if event.tags:
        tags_str = ', '.join(str(t) for t in event.tags if t)
        parts.append(f"Tags: {tags_str}")
    
    # Description
    if event.description:
        parts.append(f"Description: {event.description}")
    
    if event.summary:
        parts.append(f"Summary: {event.summary}")
    
    # Type and category
    parts.append(f"Type: {event.event_type.value}")
    parts.append(f"Category: {event.primary_category or 'general'}")
    
    # Age information
    if event.age_range_min and event.age_range_max:
        parts.append(f"Suitable for ages {event.age_range_min} to {event.age_range_max}")
    elif event.age_range_min:
        parts.append(f"For ages {event.age_range_min} and up")
    
    # Location context
    parts.append(f"Location: {event.city or 'Unknown'}, {event.state or 'MI'}")
    if event.location_name:
        parts.append(f"Venue: {event.location_name}")
    
    # Activity characteristics
    if event.is_free:
        parts.append("Free activity")
    
    if event.is_indoor:
        parts.append("Indoor activity")
    elif event.is_outdoor:
        parts.append("Outdoor activity")
    
    # CONTEXTUAL ENRICHMENT - The key improvement!
    contextual_traits = infer_contextual_traits(event)
    if contextual_traits:
        parts.append(f"Characteristics: {', '.join(contextual_traits)}")
    
    return " | ".join(parts)


def build_embeddings():
    """Build vector embeddings using direct ChromaDB approach"""
    
    print('=' * 80)
    print('BUILDING VECTOR EMBEDDINGS - DIRECT APPROACH')
    print('=' * 80)
    print()
    
    # Initialize ChromaDB
    print('[STEP 1] Initializing ChromaDB...')
    client = chromadb.PersistentClient(path="./chroma_db")
    print('[OK] ChromaDB client created')
    print(f'   Storage: ./chroma_db')
    print()
    
    # Get or create collection
    print('[STEP 2] Creating collection...')
    try:
        # Delete existing if any
        try:
            client.delete_collection("activity_events")
            print('   Deleted old collection')
        except:
            pass
        
        collection = client.create_collection(
            name="activity_events",
            metadata={"description": "Activity events for semantic search"}
        )
        print(f'[OK] Collection created: {collection.name}')
    except Exception as e:
        print(f'❌ Error creating collection: {e}')
        return
    
    print()
    
    # Load embedding model
    print('[STEP 3] Loading embedding model...')
    print('   Model: all-MiniLM-L6-v2 (HuggingFace)')
    print('   This runs locally - no API calls!')
    print('   First time may download model (~80MB)...')
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print('[OK] Model loaded')
    print()
    
    # Get events from database
    print('[STEP 4] Loading events from database...')
    db = next(get_db())
    events = db.query(UnifiedEvent).filter(
        UnifiedEvent.is_active == True
    ).all()
    
    print(f'[OK] Found {len(events)} events to embed')
    print()
    
    if len(events) == 0:
        print('❌ No events in database!')
        print('   Run sync first: python sync_yelp_full.py')
        return
    
    # Create embeddings
    print('[STEP 5] Creating embeddings with contextual enrichment...')
    print(f'   Processing {len(events)} events...')
    print()
    
    documents = []
    metadatas = []
    ids = []
    
    for i, event in enumerate(events, 1):
        # Use contextual enrichment function
        # This adds personality traits, developmental context, etc.
        text = create_enriched_document_text(event)
        
        # Metadata
        metadata = {
            "id": str(event.id),
            "title": event.title,
            "source": event.source.value,
            "city": event.city or "",
            "state": event.state or "",
            "category": event.primary_category or "",
            "is_free": str(event.is_free or False),
            "age_min": str(event.age_range_min or 0),
            "age_max": str(event.age_range_max or 18)
        }
        
        documents.append(text)
        metadatas.append(metadata)
        ids.append(str(event.id))
        
        if i % 10 == 0:
            print(f'   Prepared {i}/{len(events)} events...')
    
    print(f'[OK] All {len(events)} events prepared')
    print()
    
    # Generate embeddings and add to ChromaDB
    print('[STEP 6] Generating embeddings and storing in ChromaDB...')
    print('   This may take 1-2 minutes...')
    print()
    
    # Process in batches
    batch_size = 10
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        
        # Generate embeddings
        embeddings = model.encode(batch_docs).tolist()
        
        # Add to ChromaDB
        collection.add(
            documents=batch_docs,
            embeddings=embeddings,
            metadatas=batch_metas,
            ids=batch_ids
        )
        
        print(f'   Indexed {min(i+batch_size, len(documents))}/{len(documents)} events')
    
    print()
    print('[OK] All embeddings created and stored!')
    print()
    
    # Verify
    print('[STEP 7] Verifying index...')
    count = collection.count()
    print(f'[OK] Total embeddings in ChromaDB: {count}')
    print()
    
    # Test a query
    print('[STEP 8] Testing semantic search...')
    test_query = "confidence building activities"
    print(f'   Query: "{test_query}"')
    
    query_embedding = model.encode([test_query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )
    
    print(f'   Found {len(results["ids"][0])} results:')
    for i, (doc_id, metadata) in enumerate(zip(results["ids"][0], results["metadatas"][0]), 1):
        print(f'   {i}. {metadata["title"]} ({metadata["category"]})')
    
    print()
    print('=' * 80)
    print('SUCCESS! VECTOR INDEX READY')
    print('=' * 80)
    print()
    print(f'[OK] {count} events indexed with vector embeddings')
    print(f'[OK] Storage: ./chroma_db (SQLite)')
    print(f'[OK] Model: all-MiniLM-L6-v2 (384 dimensions)')
    print(f'[OK] Semantic search working!')
    print()
    print('You can now use:')
    print('  - POST /api/v1/rag/semantic-search')
    print('  - POST /api/v1/rag/hybrid-recommend')
    print('  - GET /api/v1/rag/similar/{id}')
    print()
    print('Test with:')
    print('  python test_semantic_search.py')
    print()
    print('=' * 80)
    
    db.close()


if __name__ == '__main__':
    build_embeddings()
