"""
Base Scraper Class
Abstract base class for all funding program scrapers
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for funding program scrapers.
    All scrapers should inherit from this class.
    """
    
    # To be overridden by subclasses
    SOURCE_NAME = "base"
    BASE_URL = ""
    TIER = 1  # 1 = daily, 2 = weekly, 3 = monthly
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        self.scraped_at = datetime.utcnow().isoformat()
        
    @abstractmethod
    def scrape_programs(self) -> List[Dict]:
        """
        Main method to scrape all programs from this source.
        Must be implemented by subclasses.
        
        Returns:
            List of program dictionaries
        """
        pass
    
    @abstractmethod
    def scrape_program_details(self, program: Dict) -> Dict:
        """
        Scrape detailed information for a single program.
        Must be implemented by subclasses.
        
        Args:
            program: Basic program info with at least 'url' key
            
        Returns:
            Enriched program dictionary
        """
        pass
    
    def get_page(self, url: str, params: Dict = None, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch a page and return BeautifulSoup object.
        Includes retry logic and rate limiting.
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        logger.error(f"Failed to fetch {url} after {retries} attempts")
        return None
    
    def calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content for change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def normalize_program(self, raw_data: Dict) -> Dict:
        """
        Normalize program data to standard schema.
        
        Standard schema fields:
        - name: Program name
        - anbieter: Funding provider
        - ebene: 'bund', 'land', 'kommunal', 'eu'
        - beschreibung: Description
        - foerderhoehe_min: Minimum funding amount
        - foerderhoehe_max: Maximum funding amount
        - foerderquote: Funding percentage (0.0 - 1.0)
        - foerderart: 'zuschuss', 'darlehen', 'kredit', 'buergschaft'
        - zielgruppe: Target group info (dict)
        - foerdergegenstand: List of funding purposes
        - laufzeit_start: Program start date
        - laufzeit_ende: Program end date
        - deadline: Application deadline
        - url_offiziell: Official URL
        - source_url: Where it was scraped from
        - source: Source identifier
        - scraped_at: Timestamp
        - raw_html_hash: Hash for change detection
        """
        return {
            'name': raw_data.get('name', raw_data.get('title', '')),
            'anbieter': raw_data.get('anbieter', raw_data.get('funder', '')),
            'ebene': raw_data.get('ebene', 'bund'),
            'beschreibung': raw_data.get('beschreibung', raw_data.get('description', '')),
            'foerderhoehe_min': self._parse_amount(raw_data.get('foerderhoehe_min')),
            'foerderhoehe_max': self._parse_amount(raw_data.get('foerderhoehe_max')),
            'foerderquote': self._parse_percentage(raw_data.get('foerderquote')),
            'foerderart': raw_data.get('foerderart', 'zuschuss'),
            'zielgruppe': raw_data.get('zielgruppe', {}),
            'foerdergegenstand': raw_data.get('foerdergegenstand', []),
            'laufzeit_start': raw_data.get('laufzeit_start'),
            'laufzeit_ende': raw_data.get('laufzeit_ende'),
            'deadline': raw_data.get('deadline'),
            'url_offiziell': raw_data.get('url_offiziell', raw_data.get('url', '')),
            'source_url': raw_data.get('source_url', self.BASE_URL),
            'source': self.SOURCE_NAME,
            'scraped_at': self.scraped_at,
            'raw_html_hash': raw_data.get('raw_html_hash', ''),
            'confidence_score': raw_data.get('confidence_score', 0.8),
            'status': 'pending_review',
        }
    
    def _parse_amount(self, value: Any) -> Optional[float]:
        """Parse funding amount from various formats."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols and thousands separators
            cleaned = value.replace('€', '').replace('EUR', '').replace('.', '').replace(',', '.').strip()
            # Extract numbers
            import re
            numbers = re.findall(r'[\d.]+', cleaned)
            if numbers:
                try:
                    return float(numbers[0])
                except ValueError:
                    pass
        return None
    
    def _parse_percentage(self, value: Any) -> Optional[float]:
        """Parse percentage from various formats."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value if value <= 1 else value / 100
        if isinstance(value, str):
            cleaned = value.replace('%', '').replace(',', '.').strip()
            try:
                num = float(cleaned)
                return num if num <= 1 else num / 100
            except ValueError:
                pass
        return None
    
    def wait(self, seconds: float = 1.0):
        """Polite waiting between requests."""
        time.sleep(seconds)
    
    def save_to_json(self, programs: List[Dict], filename: str):
        """Save programs to JSON file."""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(programs, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Saved {len(programs)} programs to {filename}")
    
    def run(self, save_path: Optional[str] = None) -> List[Dict]:
        """
        Run the complete scraping process.
        
        Args:
            save_path: Optional path to save JSON output
            
        Returns:
            List of normalized program dictionaries
        """
        logger.info(f"🚀 Starting {self.SOURCE_NAME} scraper")
        logger.info(f"Base URL: {self.BASE_URL}")
        logger.info("=" * 70)
        
        # Scrape programs
        programs = self.scrape_programs()
        logger.info(f"Found {len(programs)} programs")
        
        # Scrape details for each
        enriched_programs = []
        for i, program in enumerate(programs, 1):
            logger.info(f"[{i}/{len(programs)}] Scraping details for: {program.get('name', program.get('title', 'Unknown'))[:50]}...")
            enriched = self.scrape_program_details(program)
            normalized = self.normalize_program(enriched)
            enriched_programs.append(normalized)
            self.wait(0.5)
        
        # Save if path provided
        if save_path:
            self.save_to_json(enriched_programs, save_path)
        
        logger.info("=" * 70)
        logger.info(f"✅ {self.SOURCE_NAME} scraping complete: {len(enriched_programs)} programs")
        
        return enriched_programs
