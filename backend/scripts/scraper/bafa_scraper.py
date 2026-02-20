"""
BAFA Scraper
Scrapes funding programs from the Bundesamt für Wirtschaft und Ausfuhrkontrolle (BAFA)
https://www.bafa.de
"""

from typing import List, Dict, Optional
from urllib.parse import urljoin
import re
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BAFAScraper(BaseScraper):
    """
    Scraper for BAFA (Bundesamt für Wirtschaft und Ausfuhrkontrolle)
    
    BAFA offers various funding programs including:
    - Energieberatung (Energy consulting)
    - Elektromobilität (E-mobility)
    - Digitalisierung
    - Außenwirtschaft (Foreign trade)
    """
    
    SOURCE_NAME = "bafa"
    BASE_URL = "https://www.bafa.de"
    TIER = 1  # Daily scraping
    
    # Known BAFA funding program pages
    PROGRAM_URLS = [
        # Energie
        "/DE/Energie/Energieberatung/energieberatung_node.html",
        "/DE/Energie/Effiziente_Gebaeude/effiziente_gebaeude_node.html",
        "/DE/Energie/Heizen_mit_Erneuerbaren_Energien/heizen_mit_erneuerbaren_energien_node.html",
        # Wirtschaft & Mittelstand
        "/DE/Wirtschaft_und_Mittelstand/wirtschaft_und_mittelstand_node.html",
        # Elektromobilität
        "/DE/Energie/Energieeffizienz/Elektromobilitaet/elektromobilitaet_node.html",
    ]
    
    # Direct program pages with details
    KNOWN_PROGRAMS = [
        {
            "url": "/DE/Energie/Energieberatung/Energieberatung_Wohngebaeude/energieberatung_wohngebaeude_node.html",
            "name": "Energieberatung für Wohngebäude (EBW)",
            "category": "energie"
        },
        {
            "url": "/DE/Energie/Energieberatung/Energieberatung_Nichtwohngebaeude/energieberatung_nichtwohngebaeude_node.html",
            "name": "Energieberatung für Nichtwohngebäude (EBN)",
            "category": "energie"
        },
        {
            "url": "/DE/Energie/Effiziente_Gebaeude/Sanierung_Wohngebaeude/sanierung_wohngebaeude_node.html",
            "name": "Bundesförderung für effiziente Gebäude - Sanierung Wohngebäude (BEG WG)",
            "category": "energie"
        },
        {
            "url": "/DE/Energie/Effiziente_Gebaeude/Sanierung_Nichtwohngebaeude/sanierung_nichtwohngebaeude_node.html",
            "name": "Bundesförderung für effiziente Gebäude - Sanierung Nichtwohngebäude (BEG NWG)",
            "category": "energie"
        },
        {
            "url": "/DE/Energie/Heizen_mit_Erneuerbaren_Energien/heizen_mit_erneuerbaren_energien_node.html",
            "name": "Heizen mit Erneuerbaren Energien",
            "category": "energie"
        },
        {
            "url": "/DE/Wirtschaft_und_Mittelstand/Beratung_Finanzierung/Unternehmensberatung/unternehmensberatung_node.html",
            "name": "Förderung unternehmerischen Know-hows",
            "category": "beratung"
        },
    ]
    
    def scrape_programs(self) -> List[Dict]:
        """Scrape all BAFA funding programs."""
        programs = []
        seen_urls = set()
        
        # First, add known programs
        for prog in self.KNOWN_PROGRAMS:
            full_url = urljoin(self.BASE_URL, prog["url"])
            if full_url not in seen_urls:
                programs.append({
                    "name": prog["name"],
                    "url": full_url,
                    "category": prog.get("category", "allgemein"),
                    "source_url": full_url
                })
                seen_urls.add(full_url)
        
        # Then scrape overview pages for more programs
        for program_path in self.PROGRAM_URLS:
            url = urljoin(self.BASE_URL, program_path)
            logger.info(f"Scanning: {url}")
            
            soup = self.get_page(url)
            if not soup:
                continue
            
            # Find program links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Filter for funding-related links
                if self._is_funding_link(href, text):
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in seen_urls and 'bafa.de' in full_url:
                        programs.append({
                            "name": text,
                            "url": full_url,
                            "source_url": url
                        })
                        seen_urls.add(full_url)
            
            self.wait(1)
        
        logger.info(f"Found {len(programs)} BAFA programs")
        return programs
    
    def _is_funding_link(self, href: str, text: str) -> bool:
        """Check if a link is likely a funding program link."""
        # Skip navigation and utility links
        skip_patterns = [
            'javascript:', '#', 'mailto:', 'tel:',
            '/SharedDocs/', '/Service/', '/Presse/',
            'facebook', 'twitter', 'youtube',
            '.pdf', '.jpg', '.png'
        ]
        for pattern in skip_patterns:
            if pattern in href.lower():
                return False
        
        # Look for funding-related keywords
        funding_keywords = [
            'förder', 'zuschuss', 'programm', 'antrag',
            'beratung', 'effizienz', 'energie', 'beg ',
            'sanierung', 'elektro', 'mobilität'
        ]
        text_lower = text.lower()
        for keyword in funding_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def scrape_program_details(self, program: Dict) -> Dict:
        """Scrape detailed information for a BAFA program."""
        url = program.get('url', '')
        if not url:
            return program
        
        soup = self.get_page(url)
        if not soup:
            return program
        
        # Calculate hash for change detection
        page_content = soup.get_text()
        program['raw_html_hash'] = self.calculate_hash(page_content)
        
        # Extract description
        description = ""
        content_areas = soup.find_all(['div', 'article'], class_=re.compile(r'(content|text|article|main)', re.I))
        for area in content_areas:
            paragraphs = area.find_all('p', limit=5)
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:
                    description += text + " "
        
        if not description:
            # Fallback: get first significant paragraphs
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 100:
                    description = text
                    break
        
        program['beschreibung'] = description[:2000].strip()
        
        # Extract funding details from text
        full_text = page_content.lower()
        
        # Try to find funding amounts
        amount_patterns = [
            r'bis\s+zu\s+([\d.,]+)\s*(euro|€|eur)',
            r'maximal\s+([\d.,]+)\s*(euro|€|eur)',
            r'höchstens\s+([\d.,]+)\s*(euro|€|eur)',
            r'([\d.,]+)\s*(euro|€|eur)\s*zuschuss',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, full_text)
            if match:
                amount_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    program['foerderhoehe_max'] = float(amount_str)
                except ValueError:
                    pass
                break
        
        # Try to find percentage
        percent_patterns = [
            r'([\d]+)\s*%\s*(der|des|förder)',
            r'förderquote\D*([\d]+)\s*%',
            r'zuschuss\D*([\d]+)\s*%',
        ]
        for pattern in percent_patterns:
            match = re.search(pattern, full_text)
            if match:
                try:
                    percent = int(match.group(1))
                    if percent <= 100:
                        program['foerderquote'] = percent / 100
                except ValueError:
                    pass
                break
        
        # Set BAFA-specific fields
        program['anbieter'] = 'BAFA - Bundesamt für Wirtschaft und Ausfuhrkontrolle'
        program['ebene'] = 'bund'
        program['foerderart'] = 'zuschuss'
        
        # Determine target group
        program['zielgruppe'] = {
            'rechtsform': ['GmbH', 'UG', 'AG', 'Einzelunternehmen', 'KG', 'OHG', 'Privatperson'],
            'regionen': ['bundesweit']
        }
        
        # Determine funding purpose
        foerdergegenstand = []
        if 'energie' in full_text:
            foerdergegenstand.append('Energieeffizienz')
        if 'beratung' in full_text:
            foerdergegenstand.append('Beratung')
        if 'sanierung' in full_text:
            foerdergegenstand.append('Sanierung')
        if 'elektro' in full_text or 'mobilität' in full_text:
            foerdergegenstand.append('Elektromobilität')
        if 'gebäude' in full_text:
            foerdergegenstand.append('Gebäude')
        
        program['foerdergegenstand'] = foerdergegenstand if foerdergegenstand else ['Energie']
        
        return program


def main():
    """Run BAFA scraper."""
    scraper = BAFAScraper()
    programs = scraper.run(save_path="/opt/projects/saas-project-8/backend/data/grants/bafa.json")
    
    print(f"\n📊 Results:")
    print(f"Total programs: {len(programs)}")
    
    if programs:
        print("\n📋 Sample programs:")
        for p in programs[:3]:
            print(f"  - {p['name'][:60]}")
            print(f"    URL: {p['url_offiziell'][:60]}...")
            if p.get('foerderhoehe_max'):
                print(f"    Max: {p['foerderhoehe_max']}€")


if __name__ == "__main__":
    main()
