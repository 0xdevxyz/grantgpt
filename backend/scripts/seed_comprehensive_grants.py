"""
Comprehensive Grant Seeding Script
Imports all funding programs into Qdrant with embeddings.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import dependencies
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed - embeddings will be skipped")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("Qdrant client not installed - database operations will be skipped")


# Configuration
DATA_DIR = "/opt/projects/saas-project-8/backend/data/grants"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "grants"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072


def load_grant_files() -> List[Dict]:
    """Load all grant data from JSON files."""
    all_grants = []
    
    files_to_load = [
        "comprehensive_programs.json",
        "federal.json",
        "state.json",
        "eu.json",
        "foerderdatenbank.json",
        # Scraper outputs
        "bafa.json",
        "kfw.json",
        "sab.json",
        "bmwk.json",
        "godigital.json",
    ]
    
    for filename in files_to_load:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    grants = json.load(f)
                    if isinstance(grants, list):
                        logger.info(f"Loaded {len(grants)} grants from {filename}")
                        all_grants.extend(grants)
                    else:
                        logger.warning(f"Unexpected format in {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
    
    return all_grants


def normalize_grant(grant: Dict) -> Dict:
    """Normalize grant data to consistent schema."""
    
    # Handle different field names
    name = grant.get('name') or grant.get('title') or 'Unknown Program'
    
    # Determine description
    description = (
        grant.get('beschreibung') or 
        grant.get('description') or 
        grant.get('guidelines') or 
        ''
    )
    
    # Determine funding amount
    max_funding = (
        grant.get('foerderhoehe_max') or 
        grant.get('max_funding') or 
        grant.get('funding_amount') or 
        None
    )
    
    min_funding = (
        grant.get('foerderhoehe_min') or 
        grant.get('min_funding') or 
        None
    )
    
    # Determine provider
    provider = (
        grant.get('anbieter') or 
        grant.get('funder') or 
        grant.get('contact_info', {}).get('organization') or 
        ''
    )
    
    # Determine level
    level = grant.get('ebene') or grant.get('type') or 'bund'
    if level in ['federal', 'bundesweit']:
        level = 'bund'
    elif level == 'state':
        level = 'land'
    
    # Determine funding type
    funding_type = grant.get('foerderart') or 'zuschuss'
    
    # Determine category/purposes
    purposes = grant.get('foerdergegenstand') or []
    if not purposes:
        category = grant.get('category', '')
        if category:
            purposes = [category.replace('_', ' ').title()]
    
    # Target group
    target_group = grant.get('zielgruppe') or {}
    if not target_group:
        eligibility = grant.get('eligibility', [])
        if eligibility:
            target_group = {
                'voraussetzungen': eligibility,
                'regionen': ['bundesweit'] if level == 'bund' else []
            }
    
    # Generate ID if not present
    grant_id = grant.get('id') or str(uuid.uuid4())
    
    normalized = {
        'id': grant_id,
        'name': name,
        'anbieter': provider,
        'ebene': level,
        'beschreibung': description[:2000],  # Limit description length
        'foerderhoehe_min': min_funding,
        'foerderhoehe_max': max_funding,
        'foerderquote': grant.get('foerderquote') or grant.get('min_own_contribution_percent'),
        'foerderart': funding_type,
        'zielgruppe': target_group,
        'foerdergegenstand': purposes,
        'laufzeit_start': grant.get('laufzeit_start'),
        'laufzeit_ende': grant.get('laufzeit_ende'),
        'deadline': grant.get('deadline'),
        'url_offiziell': grant.get('url_offiziell') or grant.get('website_url') or grant.get('url') or '',
        'status': grant.get('status') or 'active',
        'source': grant.get('source') or 'manual',
        'imported_at': datetime.utcnow().isoformat(),
    }
    
    return normalized


def deduplicate_grants(grants: List[Dict]) -> List[Dict]:
    """Remove duplicate grants based on name similarity."""
    seen_names = {}
    unique_grants = []
    
    for grant in grants:
        name = grant.get('name', '').lower().strip()
        
        # Skip if we've seen very similar name
        is_duplicate = False
        for seen_name in seen_names:
            # Simple similarity check
            if name == seen_name or (len(name) > 10 and name in seen_name) or (len(seen_name) > 10 and seen_name in name):
                is_duplicate = True
                break
        
        if not is_duplicate:
            seen_names[name] = True
            unique_grants.append(grant)
    
    logger.info(f"Deduplication: {len(grants)} -> {len(unique_grants)} grants")
    return unique_grants


def create_embedding_text(grant: Dict) -> str:
    """Create text for embedding from grant data."""
    parts = [
        grant.get('name', ''),
        grant.get('beschreibung', ''),
        grant.get('anbieter', ''),
        ' '.join(grant.get('foerdergegenstand', [])),
    ]
    
    zielgruppe = grant.get('zielgruppe', {})
    if isinstance(zielgruppe, dict):
        parts.append(' '.join(zielgruppe.get('branchen', [])))
        parts.append(' '.join(zielgruppe.get('regionen', [])))
    
    return ' '.join(filter(None, parts))


def create_embeddings(grants: List[Dict], api_key: str = None) -> List[Dict]:
    """Create embeddings for all grants."""
    if not OPENAI_AVAILABLE:
        logger.warning("OpenAI not available - skipping embeddings")
        return grants
    
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.warning("No OpenAI API key - skipping embeddings")
        return grants
    
    client = OpenAI(api_key=api_key)
    
    logger.info(f"Creating embeddings for {len(grants)} grants...")
    
    # Process in batches
    batch_size = 100
    for i in range(0, len(grants), batch_size):
        batch = grants[i:i+batch_size]
        texts = [create_embedding_text(g) for g in batch]
        
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts
            )
            
            for j, embedding_data in enumerate(response.data):
                grants[i+j]['embedding'] = embedding_data.embedding
            
            logger.info(f"Created embeddings for batch {i//batch_size + 1}/{(len(grants)-1)//batch_size + 1}")
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            break
    
    return grants


def setup_qdrant_collection(client: 'QdrantClient'):
    """Setup Qdrant collection for grants."""
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME in collection_names:
        logger.info(f"Collection '{COLLECTION_NAME}' exists, recreating...")
        client.delete_collection(COLLECTION_NAME)
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
    )
    logger.info(f"Created collection '{COLLECTION_NAME}'")


def upload_to_qdrant(grants: List[Dict], host: str = None, port: int = None):
    """Upload grants with embeddings to Qdrant."""
    if not QDRANT_AVAILABLE:
        logger.warning("Qdrant client not available - skipping upload")
        return
    
    host = host or QDRANT_HOST
    port = port or QDRANT_PORT
    
    try:
        client = QdrantClient(host=host, port=port)
        logger.info(f"Connected to Qdrant at {host}:{port}")
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return
    
    # Setup collection
    setup_qdrant_collection(client)
    
    # Filter grants with embeddings
    grants_with_embeddings = [g for g in grants if g.get('embedding')]
    
    if not grants_with_embeddings:
        logger.warning("No grants with embeddings to upload")
        return
    
    logger.info(f"Uploading {len(grants_with_embeddings)} grants to Qdrant...")
    
    # Create points
    points = []
    for i, grant in enumerate(grants_with_embeddings):
        # Create payload without embedding
        payload = {k: v for k, v in grant.items() if k != 'embedding'}
        
        point = PointStruct(
            id=i,
            vector=grant['embedding'],
            payload=payload
        )
        points.append(point)
    
    # Upload in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch
        )
        logger.info(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
    
    logger.info(f"Successfully uploaded {len(points)} grants to Qdrant")


def save_combined_json(grants: List[Dict]):
    """Save all normalized grants to combined JSON file."""
    output_path = os.path.join(DATA_DIR, "all_grants_normalized.json")
    
    # Remove embeddings for JSON file (too large)
    grants_for_json = [{k: v for k, v in g.items() if k != 'embedding'} for g in grants]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(grants_for_json, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"Saved {len(grants_for_json)} grants to {output_path}")


def main():
    """Main seeding function."""
    print("\n" + "="*70)
    print("🚀 FörderScout - Comprehensive Grant Seeding")
    print("="*70)
    
    # Load all grant files
    raw_grants = load_grant_files()
    logger.info(f"Loaded {len(raw_grants)} total grants from files")
    
    if not raw_grants:
        logger.error("No grants loaded - check data files")
        return
    
    # Normalize
    normalized_grants = [normalize_grant(g) for g in raw_grants]
    
    # Deduplicate
    unique_grants = deduplicate_grants(normalized_grants)
    
    # Create embeddings
    grants_with_embeddings = create_embeddings(unique_grants)
    
    # Count with embeddings
    with_embeddings = sum(1 for g in grants_with_embeddings if g.get('embedding'))
    logger.info(f"Grants with embeddings: {with_embeddings}/{len(grants_with_embeddings)}")
    
    # Save combined JSON
    save_combined_json(grants_with_embeddings)
    
    # Upload to Qdrant
    upload_to_qdrant(grants_with_embeddings)
    
    # Summary
    print("\n" + "="*70)
    print("📊 SEEDING SUMMARY")
    print("="*70)
    print(f"  Total grants loaded:     {len(raw_grants)}")
    print(f"  After normalization:     {len(normalized_grants)}")
    print(f"  After deduplication:     {len(unique_grants)}")
    print(f"  With embeddings:         {with_embeddings}")
    print("="*70)
    
    # Stats by level
    by_level = {}
    for g in unique_grants:
        level = g.get('ebene', 'unknown')
        by_level[level] = by_level.get(level, 0) + 1
    
    print("\n📈 By Level:")
    for level, count in sorted(by_level.items()):
        print(f"  {level:15}: {count}")
    
    # Stats by type
    by_type = {}
    for g in unique_grants:
        ftype = g.get('foerderart', 'unknown')
        by_type[ftype] = by_type.get(ftype, 0) + 1
    
    print("\n📈 By Type:")
    for ftype, count in sorted(by_type.items()):
        print(f"  {ftype:15}: {count}")
    
    print("\n✅ Seeding complete!")


if __name__ == "__main__":
    main()
