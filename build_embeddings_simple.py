"""
Simple direct approach to build vector embeddings with ChromaDB
"""

import sys
sys.path.insert(0, '.')

import chromadb
from sentence_transformers import SentenceTransformer
from app.core.database import get_db
from app.models.unified_event import UnifiedEvent


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
    print('[STEP 5] Creating embeddings...')
    print(f'   Processing {len(events)} events...')
    print()
    
    documents = []
    metadatas = []
    ids = []
    
    for i, event in enumerate(events, 1):
        # Create rich text for embedding
        text = f"""
{event.title}
{event.description or ''}
Type: {event.event_type.value}
Category: {event.primary_category or 'general'}
Location: {event.city}, {event.state}
Tags: {', '.join(event.tags or [])}
Ages: {event.age_range_min}-{event.age_range_max}
{'FREE' if event.is_free else 'Paid'}
"""
        
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
