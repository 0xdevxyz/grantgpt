"""
GPT-4 Program Extractor
Extracts structured funding program data from HTML/text using GPT-4.
"""

import json
import re
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

# Try to import OpenAI - will be available in production
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available - extraction will use fallback methods")


# Prompts for GPT-4 extraction
PROGRAM_DETECTION_PROMPT = """Analysiere den folgenden Text und bestimme, ob es sich um die Beschreibung eines Förderprogramms handelt.

Ein Förderprogramm ist eine staatliche oder institutionelle Initiative, die Unternehmen, Privatpersonen oder Organisationen finanzielle Unterstützung bietet (Zuschüsse, Kredite, Bürgschaften).

Text:
{content}

Antworte im folgenden Format:
IST_FOERDERPROGRAMM: JA oder NEIN
BEGRUENDUNG: Kurze Begründung (1-2 Sätze)
CONFIDENCE: Zahl zwischen 0.0 und 1.0"""


PROGRAM_EXTRACTION_PROMPT = """Extrahiere alle relevanten Informationen aus dem folgenden Text über ein Förderprogramm.

Quelle-URL: {source_url}

Text:
{content}

Gib die Daten als valides JSON zurück mit folgender Struktur (setze null wenn Information nicht vorhanden):

{{
    "name": "Vollständiger Programmname",
    "anbieter": "Fördergeber (z.B. BAFA, KfW, SAB)",
    "ebene": "bund" | "land" | "kommunal" | "eu",
    "beschreibung": "Ausführliche Beschreibung des Programms (max 500 Wörter)",
    "foerderhoehe_min": Minimale Förderhöhe in Euro (Zahl oder null),
    "foerderhoehe_max": Maximale Förderhöhe in Euro (Zahl oder null),
    "foerderquote": Förderquote als Dezimalzahl (z.B. 0.5 für 50%),
    "foerderart": "zuschuss" | "kredit" | "darlehen" | "buergschaft" | "beteiligung",
    "zielgruppe": {{
        "rechtsform": ["GmbH", "UG", "AG", ...],
        "mitarbeiter_min": Mindestmitarbeiter oder null,
        "mitarbeiter_max": Höchstmitarbeiter oder null,
        "umsatz_min": Mindestumsatz in Euro oder null,
        "umsatz_max": Höchstumsatz in Euro oder null,
        "branchen": ["Branche1", "Branche2", ...],
        "regionen": ["Region1", "Region2", ...]
    }},
    "foerdergegenstand": ["Innovation", "Digitalisierung", ...],
    "laufzeit_start": "YYYY-MM-DD" oder null,
    "laufzeit_ende": "YYYY-MM-DD" oder null,
    "deadline": "YYYY-MM-DD" oder null,
    "antragsverfahren": "einstufig" | "zweistufig" | null,
    "voraussetzungen": ["Voraussetzung 1", "Voraussetzung 2", ...],
    "ausschlusskriterien": ["Ausschluss 1", ...],
    "besonderheiten": "Besondere Hinweise" oder null,
    "kontakt_url": "URL zur offiziellen Programmseite",
    "kontakt_email": "E-Mail für Anfragen" oder null,
    "kontakt_telefon": "Telefon für Anfragen" oder null
}}

Antworte NUR mit dem JSON, ohne zusätzlichen Text oder Erklärungen."""


class ProgramExtractor:
    """
    Extracts structured funding program data using GPT-4.
    
    Includes:
    - Program detection (is this a funding program?)
    - Structured data extraction
    - Data validation and cleaning
    - Embedding creation for vector search
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the extractor.
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("ProgramExtractor initialized with OpenAI")
        else:
            logger.warning("ProgramExtractor running without OpenAI - using fallback methods")
    
    def extract(self, content: str, source_url: str = "") -> Optional[Dict]:
        """
        Extract program data from content.
        
        Args:
            content: HTML or text content containing program information
            source_url: URL where content was scraped from
            
        Returns:
            Structured program data or None if extraction fails
        """
        # Clean content
        clean_content = self._clean_content(content)
        
        if len(clean_content) < 100:
            logger.warning("Content too short for extraction")
            return None
        
        # Step 1: Check if it's a funding program
        is_program, confidence = self.is_funding_program(clean_content)
        if not is_program:
            logger.info(f"Content is not a funding program (confidence: {confidence})")
            return None
        
        # Step 2: Extract structured data
        program_data = self.extract_program_data(clean_content, source_url)
        if not program_data:
            return None
        
        # Step 3: Validate and clean
        validated_data = self.validate_and_clean(program_data)
        
        # Step 4: Add metadata
        validated_data['source_url'] = source_url
        validated_data['extracted_at'] = datetime.utcnow().isoformat()
        validated_data['extraction_confidence'] = confidence
        validated_data['raw_content_hash'] = self._calculate_hash(clean_content)
        
        return validated_data
    
    def is_funding_program(self, content: str) -> tuple[bool, float]:
        """
        Detect if content describes a funding program.
        
        Returns:
            Tuple of (is_program, confidence)
        """
        # Quick heuristic check first
        funding_keywords = [
            'förder', 'zuschuss', 'kredit', 'darlehen', 'subvention',
            'finanzierung', 'unterstützung', 'programm', 'antrag',
            'beihilfe', 'grant', 'funding'
        ]
        
        content_lower = content.lower()
        keyword_count = sum(1 for kw in funding_keywords if kw in content_lower)
        
        if keyword_count == 0:
            return False, 0.1
        
        if keyword_count >= 3:
            # High confidence without API call
            return True, 0.8 + min(keyword_count * 0.02, 0.15)
        
        # Use GPT-4 for uncertain cases
        if self.client:
            try:
                prompt = PROGRAM_DETECTION_PROMPT.format(content=content[:2000])
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=200
                )
                
                answer = response.choices[0].message.content
                is_program = "IST_FOERDERPROGRAMM: JA" in answer.upper()
                
                # Extract confidence
                confidence_match = re.search(r'CONFIDENCE:\s*([\d.]+)', answer)
                confidence = float(confidence_match.group(1)) if confidence_match else 0.7
                
                return is_program, confidence
                
            except Exception as e:
                logger.error(f"Error in program detection: {e}")
        
        # Fallback based on keyword count
        return keyword_count >= 2, 0.5 + keyword_count * 0.1
    
    def extract_program_data(self, content: str, source_url: str) -> Optional[Dict]:
        """
        Extract structured program data using GPT-4.
        
        Args:
            content: Clean text content
            source_url: Source URL
            
        Returns:
            Extracted program data or None
        """
        if self.client:
            try:
                # Limit content length for API
                truncated_content = content[:8000]
                
                prompt = PROGRAM_EXTRACTION_PROMPT.format(
                    content=truncated_content,
                    source_url=source_url
                )
                
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                
                result = response.choices[0].message.content
                data = json.loads(result)
                return data
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                # Try to extract JSON from response
                response_text = response.choices[0].message.content
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"Error in GPT-4 extraction: {e}")
        
        # Fallback: rule-based extraction
        return self._fallback_extraction(content, source_url)
    
    def _fallback_extraction(self, content: str, source_url: str) -> Dict:
        """
        Rule-based fallback extraction when GPT-4 is not available.
        """
        content_lower = content.lower()
        
        # Extract name (first heading or title-like text)
        name = ""
        lines = content.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if 10 < len(line) < 200 and not line.startswith('http'):
                name = line
                break
        
        # Extract amounts
        amount_max = None
        amount_patterns = [
            r'bis\s+zu\s+([\d.,]+)\s*(euro|€|eur|mio)',
            r'maximal\s+([\d.,]+)\s*(euro|€|eur)',
            r'([\d.,]+)\s*(euro|€)\s*(förderung|zuschuss)',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, content_lower)
            if match:
                amount_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    amount_max = float(amount_str)
                    if 'mio' in match.group(0):
                        amount_max *= 1000000
                except:
                    pass
                break
        
        # Extract percentage
        foerderquote = None
        percent_match = re.search(r'([\d]+)\s*%', content_lower)
        if percent_match:
            try:
                percent = int(percent_match.group(1))
                if percent <= 100:
                    foerderquote = percent / 100
            except:
                pass
        
        # Determine funding type
        foerderart = 'zuschuss'
        if 'kredit' in content_lower or 'darlehen' in content_lower:
            foerderart = 'kredit'
        elif 'bürgschaft' in content_lower:
            foerderart = 'buergschaft'
        
        # Determine level
        ebene = 'bund'
        if any(land in content_lower for land in ['sachsen', 'bayern', 'nrw', 'landesförderung']):
            ebene = 'land'
        elif 'eu' in content_lower or 'europa' in content_lower:
            ebene = 'eu'
        
        # Extract description (first 500 chars of meaningful content)
        beschreibung = ' '.join(content.split()[:100])
        
        return {
            'name': name,
            'anbieter': '',
            'ebene': ebene,
            'beschreibung': beschreibung[:1000],
            'foerderhoehe_max': amount_max,
            'foerderquote': foerderquote,
            'foerderart': foerderart,
            'zielgruppe': {},
            'foerdergegenstand': [],
            'kontakt_url': source_url
        }
    
    def validate_and_clean(self, data: Dict) -> Dict:
        """
        Validate and clean extracted data.
        
        Args:
            data: Raw extracted data
            
        Returns:
            Validated and cleaned data
        """
        # Required fields
        if not data.get('name'):
            data['name'] = 'Unbekanntes Programm'
        
        # Validate numeric fields
        numeric_fields = ['foerderhoehe_min', 'foerderhoehe_max', 'foerderquote']
        for field in numeric_fields:
            if field in data and data[field] is not None:
                try:
                    data[field] = float(data[field])
                    # Sanity checks
                    if field == 'foerderquote' and data[field] > 1:
                        data[field] = data[field] / 100
                    if data[field] < 0:
                        data[field] = None
                except (ValueError, TypeError):
                    data[field] = None
        
        # Validate dates
        date_fields = ['laufzeit_start', 'laufzeit_ende', 'deadline']
        for field in date_fields:
            if data.get(field):
                if not re.match(r'\d{4}-\d{2}-\d{2}', str(data[field])):
                    data[field] = None
        
        # Ensure arrays
        array_fields = ['foerdergegenstand', 'voraussetzungen', 'ausschlusskriterien']
        for field in array_fields:
            if field not in data or not isinstance(data[field], list):
                data[field] = []
        
        # Validate zielgruppe
        if not isinstance(data.get('zielgruppe'), dict):
            data['zielgruppe'] = {}
        
        zielgruppe_defaults = {
            'rechtsform': [],
            'branchen': [],
            'regionen': []
        }
        for key, default in zielgruppe_defaults.items():
            if key not in data['zielgruppe']:
                data['zielgruppe'][key] = default
        
        # Validate ebene
        valid_ebene = ['bund', 'land', 'kommunal', 'eu']
        if data.get('ebene') not in valid_ebene:
            data['ebene'] = 'bund'
        
        # Validate foerderart
        valid_foerderart = ['zuschuss', 'kredit', 'darlehen', 'buergschaft', 'beteiligung']
        if data.get('foerderart') not in valid_foerderart:
            data['foerderart'] = 'zuschuss'
        
        return data
    
    def create_embedding(self, program_data: Dict) -> Optional[List[float]]:
        """
        Create vector embedding for semantic search.
        
        Args:
            program_data: Program data dictionary
            
        Returns:
            Embedding vector or None
        """
        if not self.client:
            return None
        
        # Combine relevant text fields
        text_parts = [
            program_data.get('name', ''),
            program_data.get('beschreibung', ''),
            program_data.get('anbieter', ''),
            ' '.join(program_data.get('foerdergegenstand', [])),
            ' '.join(program_data.get('zielgruppe', {}).get('branchen', [])),
            ' '.join(program_data.get('zielgruppe', {}).get('regionen', [])),
        ]
        
        combined_text = ' '.join(filter(None, text_parts))
        
        if not combined_text:
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=combined_text[:8000]
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return None
    
    def extract_batch(self, items: List[Dict], include_embeddings: bool = False) -> List[Dict]:
        """
        Extract multiple programs in batch.
        
        Args:
            items: List of dicts with 'content' and 'source_url' keys
            include_embeddings: Whether to create embeddings
            
        Returns:
            List of extracted program data
        """
        results = []
        
        for i, item in enumerate(items, 1):
            logger.info(f"Processing {i}/{len(items)}: {item.get('source_url', 'unknown')[:50]}...")
            
            content = item.get('content', '')
            source_url = item.get('source_url', '')
            
            program = self.extract(content, source_url)
            
            if program:
                if include_embeddings:
                    embedding = self.create_embedding(program)
                    if embedding:
                        program['embedding'] = embedding
                results.append(program)
        
        logger.info(f"Extracted {len(results)} programs from {len(items)} items")
        return results
    
    def _clean_content(self, content: str) -> str:
        """Remove HTML tags and clean text."""
        # Remove script and style elements
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Decode HTML entities
        import html
        content = html.unescape(content)
        
        # Clean whitespace
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        return content
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


def main():
    """Test the extractor with sample content."""
    sample_content = """
    go-digital - Förderprogramm für KMU Digitalisierung
    
    Das Bundesministerium für Wirtschaft und Klimaschutz (BMWK) unterstützt kleine und 
    mittlere Unternehmen (KMU) bei der Digitalisierung ihrer Geschäftsprozesse.
    
    Gefördert werden Beratungsleistungen in drei Modulen:
    - Modul 1: Digitalisierte Geschäftsprozesse (ERP, DMS, Cloud)
    - Modul 2: Digitale Markterschließung (Online-Marketing, E-Commerce)
    - Modul 3: IT-Sicherheit (Datenschutz, Cybersecurity)
    
    Förderhöhe: bis zu 16.500 Euro
    Förderquote: 50% der Beratungskosten
    
    Zielgruppe:
    - Unternehmen mit weniger als 100 Mitarbeitern
    - Jahresumsatz max. 20 Mio. Euro
    - Firmensitz in Deutschland
    
    Die Antragstellung erfolgt über autorisierte Beratungsunternehmen.
    
    Mehr Informationen: https://www.bmwk.de/go-digital
    """
    
    extractor = ProgramExtractor()
    
    print("\n" + "="*70)
    print("Testing ProgramExtractor")
    print("="*70)
    
    result = extractor.extract(sample_content, "https://www.bmwk.de/go-digital")
    
    if result:
        print("\n✅ Extraction successful!")
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print("\n❌ Extraction failed")


if __name__ == "__main__":
    main()
