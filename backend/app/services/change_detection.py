"""
Change Detection Service
Detects changes in funding programs and classifies them using LLM.
"""

import hashlib
import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ChangeType(Enum):
    """Types of detected changes."""
    NEW_PROGRAM = "new_program"
    UPDATED_PROGRAM = "updated_program"
    EXPIRED_PROGRAM = "expired_program"
    DEADLINE_CHANGED = "deadline_changed"
    AMOUNT_CHANGED = "amount_changed"
    CONDITIONS_CHANGED = "conditions_changed"
    NO_CHANGE = "no_change"


@dataclass
class Change:
    """Represents a detected change."""
    change_type: ChangeType
    program_id: Optional[str]
    program_name: str
    old_hash: Optional[str]
    new_hash: str
    changed_fields: List[str]
    confidence: float
    description: str
    requires_review: bool
    detected_at: datetime
    source_url: str
    

class ChangeDetectionService:
    """
    Service for detecting and classifying changes in funding programs.
    
    Features:
    - Hash-based change detection
    - Diff analysis for changed content
    - LLM-based classification of changes
    - Priority scoring for review queue
    """
    
    # LLM prompt for change classification
    CLASSIFICATION_PROMPT = """Analysiere die folgenden Änderungen an einem Förderprogramm und klassifiziere sie.

Alter Inhalt:
{old_content}

Neuer Inhalt:
{new_content}

Klassifiziere die Änderungen in eine der folgenden Kategorien:
1. NEW_PROGRAM - Komplett neues Förderprogramm
2. UPDATED_PROGRAM - Bestehende aktualisiert (allgemeine Änderungen)
3. EXPIRED_PROGRAM - Programm wurde eingestellt/beendet
4. DEADLINE_CHANGED - Antragsfrist geändert
5. AMOUNT_CHANGED - Förderhöhe/Quote geändert
6. CONDITIONS_CHANGED - Fördervoraussetzungen geändert
7. NO_CHANGE - Keine relevante Änderung (nur kosmetisch)

Antworte im JSON-Format:
{{
    "change_type": "KATEGORIE",
    "confidence": 0.0-1.0,
    "changed_fields": ["Feld1", "Feld2"],
    "description": "Kurze Beschreibung der Änderung",
    "requires_review": true/false,
    "priority": "high/medium/low"
}}"""

    def __init__(self, db_session=None, api_key: str = None):
        """
        Initialize change detection service.
        
        Args:
            db_session: Database session for storing change history
            api_key: OpenAI API key for LLM classification
        """
        self.db_session = db_session
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        
        # In-memory cache for hashes (would be database in production)
        self._hash_cache: Dict[str, Dict] = {}
    
    def calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content."""
        # Normalize content (remove extra whitespace, lowercase)
        normalized = ' '.join(content.lower().split())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def calculate_content_hash(self, program_data: Dict) -> str:
        """Calculate hash of program data fields."""
        # Select relevant fields for comparison
        relevant_fields = [
            'name', 'beschreibung', 'foerderhoehe_min', 'foerderhoehe_max',
            'foerderquote', 'deadline', 'voraussetzungen', 'zielgruppe'
        ]
        
        content_parts = []
        for field in relevant_fields:
            value = program_data.get(field)
            if value is not None:
                content_parts.append(f"{field}:{json.dumps(value, sort_keys=True)}")
        
        return self.calculate_hash('|'.join(content_parts))
    
    def detect_change(
        self, 
        source_url: str, 
        new_content: str, 
        program_data: Dict = None
    ) -> Optional[Change]:
        """
        Detect if content has changed from last scrape.
        
        Args:
            source_url: URL of the scraped page
            new_content: New HTML/text content
            program_data: Optional parsed program data
            
        Returns:
            Change object if change detected, None otherwise
        """
        new_hash = self.calculate_hash(new_content)
        
        # Get previous state
        previous = self._hash_cache.get(source_url)
        
        if previous is None:
            # First time seeing this URL - might be new program
            change = Change(
                change_type=ChangeType.NEW_PROGRAM,
                program_id=None,
                program_name=program_data.get('name', 'Unknown') if program_data else 'Unknown',
                old_hash=None,
                new_hash=new_hash,
                changed_fields=['all'],
                confidence=0.8,
                description="Neuer Eintrag gefunden",
                requires_review=True,
                detected_at=datetime.utcnow(),
                source_url=source_url
            )
            
            # Store for future comparisons
            self._hash_cache[source_url] = {
                'hash': new_hash,
                'content': new_content[:5000],  # Store truncated content
                'last_seen': datetime.utcnow()
            }
            
            return change
        
        old_hash = previous.get('hash')
        
        if old_hash == new_hash:
            # No change
            return None
        
        # Change detected - classify it
        old_content = previous.get('content', '')
        change = self._classify_change(
            source_url=source_url,
            old_content=old_content,
            new_content=new_content,
            old_hash=old_hash,
            new_hash=new_hash,
            program_data=program_data
        )
        
        # Update cache
        self._hash_cache[source_url] = {
            'hash': new_hash,
            'content': new_content[:5000],
            'last_seen': datetime.utcnow()
        }
        
        return change
    
    def _classify_change(
        self,
        source_url: str,
        old_content: str,
        new_content: str,
        old_hash: str,
        new_hash: str,
        program_data: Dict = None
    ) -> Change:
        """Classify the type of change using LLM or rules."""
        
        program_name = program_data.get('name', 'Unknown') if program_data else 'Unknown'
        
        # First, try rule-based classification
        rule_result = self._rule_based_classification(old_content, new_content)
        
        if rule_result:
            return Change(
                change_type=rule_result['change_type'],
                program_id=program_data.get('id') if program_data else None,
                program_name=program_name,
                old_hash=old_hash,
                new_hash=new_hash,
                changed_fields=rule_result['changed_fields'],
                confidence=rule_result['confidence'],
                description=rule_result['description'],
                requires_review=rule_result['requires_review'],
                detected_at=datetime.utcnow(),
                source_url=source_url
            )
        
        # Use LLM for complex cases
        if self.client:
            llm_result = self._llm_classification(old_content, new_content)
            if llm_result:
                return Change(
                    change_type=ChangeType[llm_result['change_type']],
                    program_id=program_data.get('id') if program_data else None,
                    program_name=program_name,
                    old_hash=old_hash,
                    new_hash=new_hash,
                    changed_fields=llm_result.get('changed_fields', []),
                    confidence=llm_result.get('confidence', 0.7),
                    description=llm_result.get('description', 'Änderung erkannt'),
                    requires_review=llm_result.get('requires_review', True),
                    detected_at=datetime.utcnow(),
                    source_url=source_url
                )
        
        # Fallback: generic update
        return Change(
            change_type=ChangeType.UPDATED_PROGRAM,
            program_id=program_data.get('id') if program_data else None,
            program_name=program_name,
            old_hash=old_hash,
            new_hash=new_hash,
            changed_fields=['unknown'],
            confidence=0.5,
            description="Inhalt wurde geändert",
            requires_review=True,
            detected_at=datetime.utcnow(),
            source_url=source_url
        )
    
    def _rule_based_classification(
        self, 
        old_content: str, 
        new_content: str
    ) -> Optional[Dict]:
        """Rule-based change classification."""
        old_lower = old_content.lower()
        new_lower = new_content.lower()
        
        # Check for program expiration
        expiration_keywords = ['eingestellt', 'beendet', 'ausgelaufen', 'nicht mehr verfügbar', 'geschlossen']
        for keyword in expiration_keywords:
            if keyword in new_lower and keyword not in old_lower:
                return {
                    'change_type': ChangeType.EXPIRED_PROGRAM,
                    'changed_fields': ['status'],
                    'confidence': 0.9,
                    'description': f'Programm möglicherweise beendet: "{keyword}" gefunden',
                    'requires_review': True
                }
        
        # Check for deadline changes
        deadline_patterns = [
            r'antragsfrist[:\s]+(\d{1,2}\.\d{1,2}\.\d{4})',
            r'deadline[:\s]+(\d{1,2}\.\d{1,2}\.\d{4})',
            r'bis zum[:\s]+(\d{1,2}\.\d{1,2}\.\d{4})',
        ]
        
        for pattern in deadline_patterns:
            old_match = re.search(pattern, old_lower)
            new_match = re.search(pattern, new_lower)
            
            if old_match and new_match and old_match.group(1) != new_match.group(1):
                return {
                    'change_type': ChangeType.DEADLINE_CHANGED,
                    'changed_fields': ['deadline'],
                    'confidence': 0.95,
                    'description': f'Antragsfrist geändert: {old_match.group(1)} → {new_match.group(1)}',
                    'requires_review': True
                }
        
        # Check for amount changes
        amount_patterns = [
            r'bis zu[:\s]+([\d.,]+)\s*(euro|€)',
            r'maximal[:\s]+([\d.,]+)\s*(euro|€)',
            r'([\d.,]+)\s*(euro|€)\s*förderung',
        ]
        
        old_amounts = []
        new_amounts = []
        
        for pattern in amount_patterns:
            old_amounts.extend(re.findall(pattern, old_lower))
            new_amounts.extend(re.findall(pattern, new_lower))
        
        if old_amounts and new_amounts:
            # Compare amounts
            old_set = set(a[0].replace('.', '').replace(',', '') for a in old_amounts)
            new_set = set(a[0].replace('.', '').replace(',', '') for a in new_amounts)
            
            if old_set != new_set:
                return {
                    'change_type': ChangeType.AMOUNT_CHANGED,
                    'changed_fields': ['foerderhoehe'],
                    'confidence': 0.85,
                    'description': 'Förderhöhe wurde geändert',
                    'requires_review': True
                }
        
        # Check for percentage changes
        percent_pattern = r'(\d{1,3})\s*%'
        old_percents = set(re.findall(percent_pattern, old_lower))
        new_percents = set(re.findall(percent_pattern, new_lower))
        
        if old_percents != new_percents:
            return {
                'change_type': ChangeType.CONDITIONS_CHANGED,
                'changed_fields': ['foerderquote'],
                'confidence': 0.8,
                'description': 'Prozentsätze wurden geändert',
                'requires_review': True
            }
        
        # If content is very different, might be major update
        old_words = set(old_lower.split())
        new_words = set(new_lower.split())
        
        if old_words and new_words:
            similarity = len(old_words & new_words) / len(old_words | new_words)
            
            if similarity < 0.5:
                return {
                    'change_type': ChangeType.UPDATED_PROGRAM,
                    'changed_fields': ['content'],
                    'confidence': 0.7,
                    'description': 'Umfangreiche Änderungen im Inhalt',
                    'requires_review': True
                }
        
        return None
    
    def _llm_classification(self, old_content: str, new_content: str) -> Optional[Dict]:
        """Use LLM to classify changes."""
        try:
            prompt = self.CLASSIFICATION_PROMPT.format(
                old_content=old_content[:2000],
                new_content=new_content[:2000]
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"LLM classification error: {e}")
            return None
    
    def get_pending_reviews(self) -> List[Change]:
        """Get all changes that require review."""
        # In production, this would query the database
        return []
    
    def approve_change(self, change: Change, approved_by: str):
        """Approve a detected change."""
        logger.info(f"Change approved: {change.program_name} by {approved_by}")
        # In production: update database, trigger notifications
    
    def reject_change(self, change: Change, rejected_by: str, reason: str):
        """Reject a detected change (false positive)."""
        logger.info(f"Change rejected: {change.program_name} - {reason}")
        # In production: update database, adjust detection rules
    
    def to_dict(self, change: Change) -> Dict:
        """Convert Change to dictionary."""
        return {
            'change_type': change.change_type.value,
            'program_id': change.program_id,
            'program_name': change.program_name,
            'old_hash': change.old_hash,
            'new_hash': change.new_hash,
            'changed_fields': change.changed_fields,
            'confidence': change.confidence,
            'description': change.description,
            'requires_review': change.requires_review,
            'detected_at': change.detected_at.isoformat(),
            'source_url': change.source_url
        }


# Convenience function for use in scrapers
def detect_changes(
    source_url: str,
    new_content: str,
    program_data: Dict = None,
    api_key: str = None
) -> Optional[Dict]:
    """
    Convenience function to detect changes.
    
    Args:
        source_url: URL of scraped page
        new_content: New content from scrape
        program_data: Optional parsed program data
        api_key: OpenAI API key
        
    Returns:
        Change dict if change detected, None otherwise
    """
    service = ChangeDetectionService(api_key=api_key)
    change = service.detect_change(source_url, new_content, program_data)
    
    if change:
        return service.to_dict(change)
    return None


if __name__ == "__main__":
    # Test the change detection
    service = ChangeDetectionService()
    
    # Simulate first scrape
    old_content = """
    ZIM Förderprogramm
    Bis zu 550.000 Euro Zuschuss
    Antragsfrist: 31.12.2025
    Für KMU mit weniger als 500 Mitarbeitern
    """
    
    # Simulate second scrape with changes
    new_content = """
    ZIM Förderprogramm
    Bis zu 600.000 Euro Zuschuss
    Antragsfrist: 30.06.2026
    Für KMU mit weniger als 500 Mitarbeitern
    """
    
    print("Testing Change Detection...")
    
    # First detection (new program)
    change1 = service.detect_change(
        "https://example.com/zim",
        old_content,
        {"name": "ZIM", "id": "zim-001"}
    )
    print(f"\nFirst scrape: {change1.change_type.value if change1 else 'None'}")
    
    # Second detection (changes)
    change2 = service.detect_change(
        "https://example.com/zim",
        new_content,
        {"name": "ZIM", "id": "zim-001"}
    )
    
    if change2:
        print(f"\nChange detected:")
        print(f"  Type: {change2.change_type.value}")
        print(f"  Fields: {change2.changed_fields}")
        print(f"  Description: {change2.description}")
        print(f"  Confidence: {change2.confidence}")
        print(f"  Requires Review: {change2.requires_review}")
