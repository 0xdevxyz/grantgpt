"""
Background tasks for grant data management
"""
import asyncio
from typing import List, Dict, Any

from app.celery_app import celery_app
from app.services.embeddings import embedding_service
from app.services.qdrant_service import qdrant_service


@celery_app.task(name="embed_grants")
def embed_grants(grants_data: List[Dict[str, Any]]):
    """
    Embed multiple grants and store in Qdrant
    
    Args:
        grants_data: List of grant dictionaries
    """
    try:
        # Ensure Qdrant collection exists
        qdrant_service.ensure_collection()
        
        embedded_count = 0
        failed_count = 0
        
        for grant in grants_data:
            try:
                # Build text for embedding
                embedding_text = _build_embedding_text(grant)
                
                # Generate embedding
                vector = asyncio.run(
                    embedding_service.embed_text(embedding_text)
                )
                
                # Prepare payload
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
                }
                
                # Store in Qdrant
                qdrant_service.upsert_grant(
                    grant_id=grant["id"],
                    vector=vector,
                    payload=payload
                )
                
                embedded_count += 1
                print(f"Embedded grant: {grant['name']}")
                
            except Exception as e:
                print(f"Error embedding grant {grant.get('id', 'unknown')}: {e}")
                failed_count += 1
        
        return {
            "total": len(grants_data),
            "embedded": embedded_count,
            "failed": failed_count
        }
        
    except Exception as e:
        print(f"Error in embed_grants task: {e}")
        raise


def _build_embedding_text(grant: Dict[str, Any]) -> str:
    """Build comprehensive text for embedding"""
    parts = [
        f"Name: {grant['name']}",
        f"Type: {grant['type']}",
        f"Category: {grant['category']}",
        f"Description: {grant['description']}"
    ]
    
    if "guidelines" in grant:
        parts.append(f"Guidelines: {grant['guidelines'][:500]}")  # First 500 chars
    
    if "eligibility" in grant:
        parts.append(f"Eligibility: {', '.join(grant['eligibility'])}")
    
    return " ".join(parts)


@celery_app.task(name="update_grant_embeddings")
def update_grant_embeddings(grant_ids: List[str]):
    """
    Update embeddings for specific grants (e.g., after data changes)
    """
    # TODO: Fetch grants from database and re-embed
    print(f"Updating embeddings for {len(grant_ids)} grants")
    return {"updated": len(grant_ids)}


@celery_app.task(name="cleanup_expired_grants")
def cleanup_expired_grants():
    """
    Remove expired grants from Qdrant
    """
    # TODO: Find and remove grants with past deadlines
    print("Cleaning up expired grants")
    return {"removed": 0}

