"""
Build vector embeddings index for all events in database
Run this once to create the ChromaDB vector store
"""

import asyncio
import sys
sys.path.insert(0, '.')

from app.services.vector_rag import vector_rag_service


async def build_index():
    """Build vector index for semantic search"""
    
    print('=' * 80)
    print('BUILDING VECTOR EMBEDDINGS INDEX WITH CHROMADB')
    print('=' * 80)
    print()
    
    print('[INFO] This will create vector embeddings for all events in your database')
    print('[INFO] Using: HuggingFace sentence-transformers (FREE, runs locally)')
    print('[INFO] Model: all-MiniLM-L6-v2 (fast, good quality)')
    print('[INFO] Storage: ChromaDB + SQLite')
    print()
    print('-' * 80)
    print('[STEP 1] Checking current index status...')
    print('-' * 80)
    
    # Check current status
    stats = vector_rag_service.get_index_stats()
    
    if 'error' in stats:
        print(f'[ERROR] {stats["error"]}')
        return
    
    print(f'Collection: {stats["collection_name"]}')
    print(f'Current embeddings: {stats["total_embeddings"]}')
    print(f'Storage location: {stats["persist_directory"]}')
    print(f'Status: {stats["status"]}')
    print()
    
    if stats["total_embeddings"] > 0:
        print('[INFO] Vector index already exists!')
        print()
        choice = input('Rebuild index? This will delete existing embeddings. (y/N): ')
        force_rebuild = choice.lower() == 'y'
    else:
        print('[INFO] No existing index found. Creating new index...')
        force_rebuild = False
    
    print()
    print('-' * 80)
    print('[STEP 2] Building vector index...')
    print('-' * 80)
    print()
    print('[INFO] This may take 1-5 minutes depending on number of events')
    print('[INFO] Creating embeddings using local model (no API calls)')
    print()
    
    # Build index
    result = await vector_rag_service.build_vector_index(force_rebuild=force_rebuild)
    
    if 'error' in result:
        print(f'[ERROR] {result["error"]}')
        return
    
    print('[SUCCESS] Vector index built!')
    print()
    print('Results:')
    print(f'  Events indexed: {result["events_indexed"]}')
    print(f'  Collection: {result["collection"]}')
    print(f'  Storage: {result["persist_directory"]}')
    print()
    
    # Verify
    print('-' * 80)
    print('[STEP 3] Verifying index...')
    print('-' * 80)
    
    final_stats = vector_rag_service.get_index_stats()
    print(f'Total embeddings: {final_stats["total_embeddings"]}')
    print(f'Embedding model: {final_stats["embedding_model"]}')
    print(f'Embedding dimension: {final_stats["embedding_dimension"]}')
    print(f'Status: {final_stats["status"]}')
    print()
    
    print('=' * 80)
    print('VECTOR INDEX READY FOR SEMANTIC SEARCH!')
    print('=' * 80)
    print()
    print('You can now use:')
    print('  - Semantic search (finds by meaning)')
    print('  - Concept-based queries ("confidence building")')
    print('  - Synonym matching (swim = aquatics)')
    print('  - "Find similar" features')
    print()
    print('Test with:')
    print('  python test_semantic_search.py')
    print()
    print('=' * 80)


if __name__ == '__main__':
    asyncio.run(build_index())
