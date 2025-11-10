"""
Seed script to load grant data into database and Qdrant
"""
import json
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.embeddings import embedding_service
from app.services.qdrant_service import qdrant_service


async def load_grants_from_file(filepath: str):
    """Load grants from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


async def seed_grants():
    """Main seed function"""
    print("🌱 Seeding grant data...")
    
    # Ensure Qdrant collection exists
    print("Creating Qdrant collection...")
    qdrant_service.ensure_collection()
    
    # Load grant files
    data_dir = Path(__file__).parent.parent / "data" / "grants"
    grant_files = [
        data_dir / "federal.json",
        data_dir / "state.json",
        data_dir / "eu.json"
    ]
    
    all_grants = []
    for filepath in grant_files:
        if filepath.exists():
            grants = await load_grants_from_file(filepath)
            all_grants.extend(grants)
            print(f"✓ Loaded {len(grants)} grants from {filepath.name}")
    
    print(f"\n📊 Total grants to embed: {len(all_grants)}")
    
    # Embed and store each grant
    embedded_count = 0
    failed_count = 0
    
    for i, grant in enumerate(all_grants, 1):
        try:
            print(f"\n[{i}/{len(all_grants)}] Processing: {grant['name']}")
            
            # Build embedding text
            embedding_text = _build_embedding_text(grant)
            print(f"  Generating embedding...")
            
            # Generate embedding
            vector = await embedding_service.embed_text(embedding_text)
            print(f"  ✓ Embedding generated ({len(vector)} dimensions)")
            
            # Prepare payload for Qdrant
            payload = {
                "external_id": grant["id"],
                "name": grant["name"],
                "type": grant["type"],
                "category": grant["category"],
                "max_funding": grant["max_funding"],
                "description": grant["description"],
                "deadline": grant.get("deadline"),
                "is_continuous": grant.get("is_continuous", False),
                "historical_success_rate": grant.get("historical_success_rate"),
                "website_url": grant.get("website_url"),
            }
            
            # Store in Qdrant
            print(f"  Storing in Qdrant...")
            qdrant_service.upsert_grant(
                grant_id=grant["id"],
                vector=vector,
                payload=payload
            )
            
            embedded_count += 1
            print(f"  ✅ Successfully embedded and stored!")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Seeding completed!")
    print(f"  Embedded: {embedded_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total: {len(all_grants)}")
    print(f"{'='*50}")


def _build_embedding_text(grant: dict) -> str:
    """Build comprehensive text for embedding"""
    parts = [
        f"Name: {grant['name']}",
        f"Type: {grant['type']}",
        f"Category: {grant['category']}",
        f"Max Funding: {grant['max_funding']} EUR",
        f"Description: {grant['description']}"
    ]
    
    if "guidelines" in grant:
        parts.append(f"Guidelines: {grant['guidelines']}")
    
    if "eligibility" in grant:
        parts.append(f"Eligibility: {', '.join(grant['eligibility'])}")
    
    return " ".join(parts)


if __name__ == "__main__":
    asyncio.run(seed_grants())

