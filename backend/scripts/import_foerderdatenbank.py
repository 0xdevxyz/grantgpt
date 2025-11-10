"""
Import scraped Förderdatenbank programs into Qdrant
"""

import json
import sys
import os
import asyncio

# Add app directory to path
sys.path.insert(0, '/app')

from app.services.embeddings import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.core.config import settings


async def main():
    print("🚀 Starting Förd erdatenbank Import")
    print("=" * 70)
    
    # Initialize services
    print("📦 Initializing services...")
    embedding_service = EmbeddingService()
    qdrant_service = QdrantService()
    
    # Create collection if not exists
    print("🗄️  Setting up Qdrant collection...")
    qdrant_service.ensure_collection()
    
    # Load data
    data_file = "/app/data/grants/foerderdatenbank.json"
    print(f"📂 Loading programs from {data_file}...")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        programs = json.load(f)
    
    print(f"✅ Loaded {len(programs)} programs")
    
    # Process and import each program
    print("\n📝 Generating embeddings and importing to Qdrant...")
    success_count = 0
    error_count = 0
    
    for i, program in enumerate(programs, 1):
        try:
            print(f"[{i}/{len(programs)}] Processing: {program['title'][:60]}...")
            
            # Create text for embedding
            text_for_embedding = f"""
            {program['title']}
            
            {program.get('description', '')}
            
            Wer wird gefördert: {program.get('who_is_funded', '')}
            Was wird gefördert: {program.get('what_is_funded', '')}
            Fördergeber: {program.get('funder', '')}
            Förderart: {program.get('funding_type', '')}
            Region: {program.get('region', '')}
            """.strip()
            
            # Generate embedding
            embedding = await embedding_service.embed_text(text_for_embedding)
            
            # Prepare payload for Qdrant
            payload = {
                "title": program['title'],
                "description": program.get('description', ''),
                "url": program.get('url', ''),
                "who_is_funded": program.get('who_is_funded', ''),
                "what_is_funded": program.get('what_is_funded', ''),
                "funder": program.get('funder', 'Bund'),
                "funding_type": program.get('funding_type', 'Zuschuss'),
                "region": program.get('region', 'Deutschland'),
                "deadline": program.get('deadline', 'Laufend'),
                "funding_amount": program.get('funding_amount', 'Nicht angegeben'),
                "source": "foerderdatenbank.de",
                "category": "bundesförderung"
            }
            
            # Create a unique ID from the URL
            grant_id = f"foerderdatenbank_{i}"
            
            # Upsert to Qdrant
            qdrant_service.upsert_grant(grant_id, embedding, payload)
            
            success_count += 1
            print(f"  ✅ Imported successfully")
            
        except Exception as e:
            error_count += 1
            print(f"  ❌ Error: {e}")
            continue
    
    print("\n" + "=" * 70)
    print(f"✅ Import complete!")
    print(f"📊 Successfully imported: {success_count}/{len(programs)}")
    if error_count > 0:
        print(f"⚠️  Errors: {error_count}")
    print("=" * 70)
    
    # Test search
    print("\n🔍 Testing search...")
    test_query = "Ich suche Förderung für mein innovatives Startup im Bereich KI"
    print(f"Query: {test_query}")
    
    query_embedding = await embedding_service.embed_text(test_query)
    results = qdrant_service.search_similar_grants(query_embedding, limit=3, score_threshold=0.0)
    
    print(f"\n📋 Top 3 matches:")
    for i, result in enumerate(results, 1):
        payload = result['payload']
        print(f"\n{i}. {payload.get('title', 'N/A')}")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Who: {payload.get('who_is_funded', 'N/A')}")
        print(f"   What: {payload.get('what_is_funded', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())

