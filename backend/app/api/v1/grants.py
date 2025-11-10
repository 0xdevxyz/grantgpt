from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

from app.services.embeddings import EmbeddingService
from app.services.qdrant_service import QdrantService

router = APIRouter()

# Initialize services
embedding_service = EmbeddingService()
qdrant_service = QdrantService()


# Enums
class GrantType(str, Enum):
    FEDERAL = "federal"
    STATE = "state"
    EU = "eu"
    MUNICIPAL = "municipal"


class GrantCategory(str, Enum):
    INNOVATION = "innovation"
    DIGITALIZATION = "digitalization"
    GREEN_TECH = "green_tech"
    EXPORT = "export"
    TRAINING = "training"
    REGIONAL = "regional"


# Schemas
class GrantSearch(BaseModel):
    company_size: Optional[int] = None
    industry: Optional[str] = None
    project_description: Optional[str] = None
    budget: Optional[float] = None
    location: Optional[str] = None


class Grant(BaseModel):
    id: str
    name: str
    type: GrantType
    category: GrantCategory
    max_funding: float
    deadline: Optional[str] = None
    description: str
    eligibility: List[str]
    success_rate: Optional[float] = None
    match_score: Optional[float] = None


class GrantDetail(Grant):
    requirements: List[str]
    application_process: str
    duration: str
    contact: dict


@router.post("/search", response_model=List[Grant])
async def search_grants(search_params: GrantSearch):
    """
    AI-powered grant matching
    
    Searches through 2000+ grant programs and returns best matches
    based on company profile and project description.
    """
    # Build search query from parameters
    query_parts = []
    
    if search_params.project_description:
        query_parts.append(search_params.project_description)
    
    if search_params.industry:
        query_parts.append(f"Branche: {search_params.industry}")
    
    if search_params.company_size:
        query_parts.append(f"Unternehmensgröße: {search_params.company_size} Mitarbeiter")
    
    if search_params.budget:
        query_parts.append(f"Budget: {search_params.budget} EUR")
    
    if search_params.location:
        query_parts.append(f"Standort: {search_params.location}")
    
    if not query_parts:
        raise HTTPException(status_code=400, detail="Bitte geben Sie eine Projektbeschreibung an")
    
    query_text = " ".join(query_parts)
    
    # Generate embedding for search query
    query_embedding = await embedding_service.embed_text(query_text)
    
    # Search in Qdrant
    results = qdrant_service.search_similar_grants(
        query_vector=query_embedding,
        limit=10,
        score_threshold=0.3
    )
    
    # Convert Qdrant results to Grant format
    grants = []
    for result in results:
        payload = result['payload']
        
        # Extract funding amount
        funding_str = payload.get('funding_amount', 'Nicht angegeben')
        max_funding = 0.0
        if 'bis' in funding_str.lower():
            try:
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', funding_str.replace('.', '').replace(',', '.'))
                if numbers:
                    max_funding = float(numbers[-1])  # Take the highest number
            except:
                max_funding = 0.0
        
        grant = {
            "id": payload.get('url', result['id']),
            "name": payload.get('title', 'Unbekannt'),
            "type": "federal" if "bund" in payload.get('funder', '').lower() else "state",
            "category": "innovation" if "innovation" in payload.get('what_is_funded', '').lower() else "digitalization",
            "max_funding": max_funding,
            "deadline": payload.get('deadline', 'Laufend'),
            "description": payload.get('description', '')[:500],
            "eligibility": [
                payload.get('who_is_funded', 'Nicht angegeben'),
                f"Fördergeber: {payload.get('funder', 'Nicht angegeben')}",
                f"Region: {payload.get('region', 'Deutschland')}"
            ],
            "success_rate": 0.60,  # Default, could be calculated later
            "match_score": result['score']
        }
        grants.append(grant)
    
    return grants


@router.get("/{grant_id}", response_model=GrantDetail)
async def get_grant_detail(grant_id: str):
    """Get detailed information about a specific grant"""
    # TODO: Fetch from database
    
    # Placeholder
    raise HTTPException(status_code=404, detail="Grant not found")


@router.get("/", response_model=List[Grant])
async def list_grants(
    type: Optional[GrantType] = None,
    category: Optional[GrantCategory] = None,
    limit: int = Query(20, le=100)
):
    """List all available grants with optional filters"""
    # TODO: Implement filtering and pagination
    
    return []

