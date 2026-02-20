from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime, date
import re

from app.services.embeddings import EmbeddingService
from app.services.qdrant_service import QdrantService


def is_deadline_valid(deadline_str: Optional[str]) -> bool:
    """
    Check if a deadline is still valid (not expired).
    Returns True if:
    - deadline is None, empty, or "Laufend" (continuous)
    - deadline date is in the future
    Returns False if deadline has passed.
    """
    if not deadline_str:
        return True
    
    deadline_lower = str(deadline_str).lower().strip()
    
    # Continuous programs are always valid
    if deadline_lower in ['laufend', 'fortlaufend', 'keine', 'unbefristet', 'offen', '']:
        return True
    
    today = date.today()
    
    # Try to parse various date formats
    date_patterns = [
        # ISO format: 2025-06-30, 2025-06-30T23:59:59Z
        (r'(\d{4})-(\d{2})-(\d{2})', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
        # German format: 30.06.2025, 1.7.2025
        (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', lambda m: date(int(m.group(3)), int(m.group(2)), int(m.group(1)))),
        # Short German: 30.06.25
        (r'(\d{1,2})\.(\d{1,2})\.(\d{2})$', lambda m: date(2000 + int(m.group(3)), int(m.group(2)), int(m.group(1)))),
        # Month Year: Juni 2025, 06/2025
        (r'(\d{1,2})/(\d{4})', lambda m: date(int(m.group(2)), int(m.group(1)), 28)),
        # Just year: 2025, 2026
        (r'^(\d{4})$', lambda m: date(int(m.group(1)), 12, 31)),
    ]
    
    for pattern, date_converter in date_patterns:
        match = re.search(pattern, deadline_str)
        if match:
            try:
                deadline_date = date_converter(match)
                return deadline_date >= today
            except (ValueError, IndexError):
                continue
    
    # If we can't parse the date, assume it's valid (don't exclude it)
    return True

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
    
    # Search in Qdrant - request more results to compensate for deadline filtering
    results = qdrant_service.search_similar_grants(
        query_vector=query_embedding,
        limit=30,  # Request more, filter later
        score_threshold=0.3
    )
    
    # Convert Qdrant results to Grant format
    grants = []
    for result in results:
        # Skip if we already have 10 valid grants
        if len(grants) >= 10:
            break
        payload = result['payload']
        
        # Extract funding amount - handle both formats
        max_funding = 0.0
        if 'max_funding' in payload and payload['max_funding']:
            max_funding = float(payload['max_funding'])
        else:
            funding_str = payload.get('funding_amount', 'Nicht angegeben')
            if funding_str and 'bis' in str(funding_str).lower():
                try:
                    numbers = re.findall(r'\d+(?:\.\d+)?', str(funding_str).replace('.', '').replace(',', '.'))
                    if numbers:
                        max_funding = float(numbers[-1])
                except:
                    pass
        
        # Handle both name formats: some use 'name', others use 'title'
        grant_name = payload.get('name') or payload.get('title') or 'Unbekannt'
        
        # Determine type
        grant_type = payload.get('type', 'federal')
        if grant_type not in ['federal', 'state', 'eu', 'municipal']:
            funder = payload.get('funder', '').lower()
            if 'bund' in funder or 'bmw' in funder or 'bafa' in funder or 'kfw' in funder:
                grant_type = 'federal'
            elif any(state in funder.lower() for state in ['bayern', 'sachsen', 'nrw', 'hamburg', 'berlin', 'baden', 'hessen']):
                grant_type = 'state'
            else:
                grant_type = 'state'
        
        # Determine category
        grant_category = payload.get('category', 'digitalization')
        if grant_category not in ['innovation', 'digitalization', 'green_tech', 'export', 'training', 'regional']:
            what_funded = payload.get('what_is_funded', '').lower()
            if 'innovation' in what_funded or 'forschung' in what_funded:
                grant_category = 'innovation'
            elif 'digital' in what_funded or 'it' in what_funded:
                grant_category = 'digitalization'
            elif 'klima' in what_funded or 'umwelt' in what_funded or 'energie' in what_funded:
                grant_category = 'green_tech'
            else:
                grant_category = 'digitalization'
        
        # Handle deadline
        deadline = payload.get('deadline')
        if deadline == 'Laufend' or payload.get('is_continuous'):
            deadline = 'Laufend'
        
        # Skip expired programs
        if not is_deadline_valid(deadline):
            continue
        
        grant = {
            "id": payload.get('url') or payload.get('website_url') or payload.get('external_id') or str(result['id']),
            "name": grant_name,
            "type": grant_type,
            "category": grant_category,
            "max_funding": max_funding,
            "deadline": deadline,
            "description": (payload.get('description') or '')[:500],
            "eligibility": [
                payload.get('who_is_funded') or 'Nicht angegeben',
                f"Fördergeber: {payload.get('funder') or 'Nicht angegeben'}",
                f"Region: {payload.get('region') or 'Deutschland'}"
            ],
            "success_rate": payload.get('historical_success_rate') or 0.60,
            "match_score": result['score']
        }
        grants.append(grant)
    
    return grants


@router.get("/{grant_id}", response_model=GrantDetail)
async def get_grant_detail(grant_id: str):
    """Get detailed information about a specific grant"""
    # Try to fetch from Qdrant by ID or URL
    try:
        # Search by URL (which we use as ID in many cases)
        results = qdrant_service.search_grants_by_filter(
            filter_conditions={"url": grant_id},
            limit=1
        )
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail="Grant not found"
            )
        
        result = results[0]
        payload = result['payload']
        
        # Build detailed response
        grant_detail = {
            "id": grant_id,
            "name": payload.get('name') or payload.get('title') or 'Unbekannt',
            "type": payload.get('type', 'federal'),
            "category": payload.get('category', 'digitalization'),
            "max_funding": float(payload.get('max_funding', 0)),
            "deadline": payload.get('deadline', 'Laufend'),
            "description": payload.get('description', ''),
            "eligibility": [
                payload.get('who_is_funded') or 'Nicht angegeben',
                f"Fördergeber: {payload.get('funder') or 'Nicht angegeben'}",
                f"Region: {payload.get('region') or 'Deutschland'}"
            ],
            "success_rate": payload.get('historical_success_rate', 0.60),
            "requirements": payload.get('requirements', []) if isinstance(payload.get('requirements'), list) else [payload.get('requirements', 'Siehe Website')],
            "application_process": payload.get('application_process', 'Siehe offizielle Website für Details'),
            "duration": payload.get('duration', 'Nicht angegeben'),
            "contact": {
                "website": payload.get('url') or payload.get('website_url', ''),
                "email": payload.get('contact_email', ''),
                "phone": payload.get('contact_phone', ''),
                "funder": payload.get('funder', 'Nicht angegeben')
            }
        }
        
        return grant_detail
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching grant details: {str(e)}"
        )


@router.get("/", response_model=List[Grant])
async def list_grants(
    type: Optional[GrantType] = None,
    category: Optional[GrantCategory] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100)
):
    """List all available grants with optional filters"""
    try:
        # Build filter conditions
        filter_conditions = {}
        
        if type:
            filter_conditions['type'] = type.value
        
        if category:
            filter_conditions['category'] = category.value
        
        # Fetch from Qdrant
        results = qdrant_service.scroll_grants(
            filter_conditions=filter_conditions if filter_conditions else None,
            limit=limit,
            offset=skip
        )
        
        # Convert to Grant format
        grants = []
        for result in results:
            payload = result['payload']
            
            # Skip expired grants
            deadline = payload.get('deadline', 'Laufend')
            if not is_deadline_valid(deadline):
                continue
            
            max_funding = float(payload.get('max_funding', 0))
            if max_funding == 0:
                funding_str = payload.get('funding_amount', '')
                if 'bis' in str(funding_str).lower():
                    try:
                        numbers = re.findall(r'\d+(?:\.\d+)?', str(funding_str).replace('.', '').replace(',', '.'))
                        if numbers:
                            max_funding = float(numbers[-1])
                    except:
                        pass
            
            grant = {
                "id": payload.get('url') or payload.get('external_id') or str(result['id']),
                "name": payload.get('name') or payload.get('title') or 'Unbekannt',
                "type": payload.get('type', 'federal'),
                "category": payload.get('category', 'digitalization'),
                "max_funding": max_funding,
                "deadline": deadline,
                "description": (payload.get('description') or '')[:500],
                "eligibility": [
                    payload.get('who_is_funded') or 'Nicht angegeben',
                    f"Fördergeber: {payload.get('funder') or 'Nicht angegeben'}"
                ],
                "success_rate": payload.get('historical_success_rate', 0.60),
                "match_score": None
            }
            grants.append(grant)
        
        return grants
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing grants: {str(e)}"
        )

