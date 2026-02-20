#!/usr/bin/env python3
import json
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embeddings import EmbeddingService
from app.services.qdrant_service import QdrantService

async def main():
    # Load grants
    grants_file = "/opt/projects/saas-project-8/backend/data/grants/all_programs_unique.json"
    with open(grants_file, 'r') as f:
        grants = json.load(f)
    
    print(f"Loaded {len(grants)} grants")
    
    # Initialize services
    embedding_service = EmbeddingService()
    qdrant_service = QdrantService()
    
    # Ensure collection
    qdrant_service.ensure_collection()
    
    # Process each grant
    for i, grant in enumerate(grants, 1):
        print(f"[{i}/{len(grants)}] Processing: {grant.get('name', 'Unknown')[:50]}...")
        
        # Create description for embedding
        desc_parts = []
        if grant.get('name'):
            desc_parts.append(grant['name'])
        if grant.get('description'):
            desc_parts.append(grant['description'])
        if grant.get('what_is_funded'):
            desc_parts.append(f"Was wird gefördert: {grant['what_is_funded']}")
        
        description = " ".join(desc_parts)
        
        # Generate embedding
        embedding = await embedding_service.embed_text(description)
        
        # Normalize grant data
        grant_id = grant.get('url') or grant.get('external_id') or f"grant-{i}"
        
        payload = {
            "name": grant.get('name', 'Unbekannt'),
            "description": grant.get('description', ''),
            "funder": grant.get('funder', 'Bund'),
            "type": grant.get('type', 'federal'),
            "category": grant.get('category', 'innovation'),
            "url": grant.get('url', ''),
            "max_funding": grant.get('max_funding', 0),
            "deadline": grant.get('deadline', 'Laufend'),
            "who_is_funded": grant.get('who_is_funded', 'KMU'),
            "what_is_funded": grant.get('what_is_funded', ''),
            "region": grant.get('region', 'Deutschland'),
        }
        
        # Upload to Qdrant
        qdrant_service.upsert_grant(grant_id, embedding, payload)
    
    print(f"\n✅ Successfully seeded {len(grants)} grants to Qdrant!")
    
    # Get stats
    stats = qdrant_service.get_collection_stats()
    print(f"Collection stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
