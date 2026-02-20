"""
SAB Scraper
Scrapes funding programs from Sächsische Aufbaubank (SAB)
https://www.sab.sachsen.de
"""

from typing import List, Dict, Optional
from urllib.parse import urljoin
import re
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SABScraper(BaseScraper):
    """
    Scraper for SAB (Sächsische Aufbaubank)
    
    SAB is the development bank of Saxony and offers various funding programs:
    - Existenzgründung & Unternehmensentwicklung
    - Innovation & Technologie
    - Umwelt & Energie
    - Infrastruktur
    """
    
    SOURCE_NAME = "sab_sachsen"
    BASE_URL = "https://www.sab.sachsen.de"
    TIER = 1  # Daily scraping
    
    # SAB program overview pages
    OVERVIEW_URLS = [
        "/f%C3%B6rderprogramme/sie-m%C3%B6chten/ein-unternehmen-gr%C3%BCnden-oder-entwickeln",
        "/f%C3%B6rderprogramme/sie-m%C3%B6chten/innovationen-vorantreiben",
        "/f%C3%B6rderprogramme/sie-m%C3%B6chten/in-forschung-und-entwicklung-investieren",
        "/f%C3%B6rderprogramme/sie-m%C3%B6chten/digitalisieren-und-arbeit-4-0-vorantreiben",
    ]
    
    # Known SAB programs
    KNOWN_PROGRAMS = [
        {
            "name": "Innovationsgutschein",
            "url": "/f%C3%B6rderprogramme/alle-programme/innovationsgutschein",
            "foerderhoehe_min": 5000,
            "foerderhoehe_max": 15000,
            "foerderquote": 0.8,
            "foerderart": "zuschuss",
            "category": "innovation"
        },
        {
            "name": "GRW - Gewerbliche Wirtschaft",
            "url": "/f%C3%B6rderprogramme/alle-programme/grw-gewerbliche-wirtschaft",
            "foerderhoehe_max": 2000000,
            "foerderquote": 0.35,
            "foerderart": "zuschuss",
            "category": "investition"
        },
        {
            "name": "Mittelstandsrichtlinie - Beratung",
            "url": "/f%C3%B6rderprogramme/alle-programme/mittelstandsrichtlinie-beratung",
            "foerderhoehe_max": 20000,
            "foerderquote": 0.5,
            "foerderart": "zuschuss",
            "category": "beratung"
        },
        {
            "name": "Mittelstandsrichtlinie - Markterschließung",
            "url": "/f%C3%B6rderprogramme/alle-programme/mittelstandsrichtlinie-markterschlie%C3%9Fung",
            "foerderhoehe_max": 15000,
            "foerderquote": 0.5,
            "foerderart": "zuschuss",
            "category": "export"
        },
        {
            "name": "Technologieförderung - InnoTeam",
            "url": "/f%C3%B6rderprogramme/alle-programme/technologief%C3%B6rderung-innoteam",
            "foerderhoehe_max": 400000,
            "foerderquote": 0.5,
            "foerderart": "zuschuss",
            "category": "innovation"
        },
        {
            "name": "Technologieförderung - Einzelprojekte",
            "url": "/f%C3%B6rderprogramme/alle-programme/technologief%C3%B6rderung-einzelprojekte",
            "foerderhoehe_max": 1000000,
            "foerderquote": 0.5,
            "foerderart": "zuschuss",
            "category": "innovation"
        },
        {
            "name": "Gründerberatung",
            "url": "/f%C3%B6rderprogramme/alle-programme/gr%C3%BCnderberatung",
            "foerderhoehe_max": 4000,
            "foerderquote": 0.8,
            "foerderart": "zuschuss",
            "category": "gruendung"
        },
        {
            "name": "Mikrokredit Sachsen",
            "url": "/f%C3%B6rderprogramme/alle-programme/mikrokredit-sachsen",
            "foerderhoehe_max": 20000,
            "foerderart": "kredit",
            "category": "gruendung"
        },
        {
            "name": "Sachsen-Kredit",
            "url": "/f%C3%B6rderprogramme/alle-programme/sachsen-kredit",
            "foerderhoehe_max": 2000000,
            "foerderart": "kredit",
            "category": "investition"
        },
        {
            "name": "Energie und Klima (EFRE)",
            "url": "/f%C3%B6rderprogramme/alle-programme/energie-und-klima-efre",
            "foerderhoehe_max": 500000,
            "foerderquote": 0.5,
            "foerderart": "zuschuss",
            "category": "energie"
        },
    ]
    
    def scrape_programs(self) -> List[Dict]:
        """Scrape all SAB funding programs."""
        programs = []
        seen_urls = set()
        
        # Add known programs first
        for prog in self.KNOWN_PROGRAMS:
            full_url = urljoin(self.BASE_URL, prog["url"])
            if full_url not in seen_urls:
                program_data = {
                    "name": prog["name"],
                    "url": full_url,
                    "source_url": full_url,
                    "foerderart": prog.get("foerderart", "zuschuss"),
                    "category": prog.get("category", "allgemein")
                }
                # Add optional fields if present
                if "foerderhoehe_min" in prog:
                    program_data["foerderhoehe_min"] = prog["foerderhoehe_min"]
                if "foerderhoehe_max" in prog:
                    program_data["foerderhoehe_max"] = prog["foerderhoehe_max"]
                if "foerderquote" in prog:
                    program_data["foerderquote"] = prog["foerderquote"]
                
                programs.append(program_data)
                seen_urls.add(full_url)
        
        # Scrape overview pages for additional programs
        for overview_path in self.OVERVIEW_URLS:
            url = urljoin(self.BASE_URL, overview_path)
            logger.info(f"Scanning SAB overview: {url}")
            
            soup = self.get_page(url)
            if not soup:
                continue
            
            # Find program links
            program_links = soup.find_all('a', href=re.compile(r'/f.*rderprogramme/'))
            for link in program_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if self._is_program_link(href, text):
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in seen_urls:
                        programs.append({
                            "name": text,
                            "url": full_url,
                            "source_url": url
                        })
                        seen_urls.add(full_url)
            
            self.wait(1)
        
        logger.info(f"Found {len(programs)} SAB programs")
        return programs
    
    def _is_program_link(self, href: str, text: str) -> bool:
        """Check if link is a SAB program page."""
        # Skip utility links
        skip_patterns = [
            '/service/', '/kontakt/', '/aktuelles/',
            '.pdf', 'javascript:', '#', 'mailto:',
            '/datenschutz', '/impressum'
        ]
        for pattern in skip_patterns:
            if pattern.lower() in href.lower():
                return False
        
        # Must be in Förderprogramme section
        if '/f%C3%B6rderprogramme/' not in href and '/förderprogramme/' not in href.lower():
            return False
        
        # Skip overview pages
        if '/sie-m%C3%B6chten/' in href:
            return False
        
        # Must have some meaningful text
        if len(text) < 5:
            return False
        
        return True
    
    def scrape_program_details(self, program: Dict) -> Dict:
        """Scrape detailed information for a SAB program."""
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
        
        # SAB uses specific content areas
        content_areas = soup.find_all(['div', 'section'], class_=re.compile(r'(content|text|body|main)', re.I))
        for area in content_areas:
            paragraphs = area.find_all('p', limit=5)
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50 and 'Cookie' not in text:
                    description += text + " "
        
        if not description:
            # Fallback
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 80 and 'Cookie' not in text:
                    description = text
                    break
        
        program['beschreibung'] = description[:2000].strip()
        
        # Extract funding details from structured data or text
        full_text = page_content.lower()
        
        # Try to find funding amounts if not already set
        if not program.get('foerderhoehe_max'):
            amount_patterns = [
                r'bis\s+zu\s+([\d.,]+)\s*(euro|€)',
                r'maximal\s+([\d.,]+)\s*(euro|€)',
                r'höchstens\s+([\d.,]+)\s*(euro|€)',
                r'([\d.,]+)\s*(euro|€)\s*(förderung|zuschuss)',
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
        
        # Try to find percentage if not set
        if not program.get('foerderquote'):
            percent_patterns = [
                r'([\d]+)\s*%\s*(förder|zuschuss|der)',
                r'förderquote\D*([\d]+)\s*%',
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
        
        # Set SAB-specific fields
        program['anbieter'] = 'SAB - Sächsische Aufbaubank'
        program['ebene'] = 'land'
        
        # Default to zuschuss if not set
        if not program.get('foerderart'):
            if 'kredit' in full_text or 'darlehen' in full_text:
                program['foerderart'] = 'kredit'
            else:
                program['foerderart'] = 'zuschuss'
        
        # Target group - Sachsen only
        zielgruppe = {
            'rechtsform': ['GmbH', 'UG', 'AG', 'GmbH & Co. KG', 'Einzelunternehmen'],
            'regionen': ['Sachsen']
        }
        
        # Try to extract company size requirements
        if 'kmu' in full_text or 'kleine und mittlere' in full_text:
            zielgruppe['mitarbeiter_max'] = 250
        if 'kleinstunternehmen' in full_text:
            zielgruppe['mitarbeiter_max'] = 10
        
        program['zielgruppe'] = zielgruppe
        
        # Determine funding purpose
        foerdergegenstand = []
        category = program.get('category', '')
        
        if category == 'innovation' or 'innovation' in full_text:
            foerdergegenstand.append('Innovation')
        if category == 'gruendung' or 'gründ' in full_text:
            foerdergegenstand.append('Existenzgründung')
        if category == 'investition' or 'investition' in full_text:
            foerdergegenstand.append('Investition')
        if category == 'beratung' or 'beratung' in full_text:
            foerdergegenstand.append('Beratung')
        if category == 'energie' or 'energie' in full_text or 'klima' in full_text:
            foerdergegenstand.append('Energieeffizienz')
        if category == 'export' or 'export' in full_text or 'markt' in full_text:
            foerdergegenstand.append('Internationalisierung')
        if 'digital' in full_text:
            foerdergegenstand.append('Digitalisierung')
        if 'forschung' in full_text or 'entwicklung' in full_text:
            foerdergegenstand.append('Forschung & Entwicklung')
        
        program['foerdergegenstand'] = foerdergegenstand if foerdergegenstand else ['Wirtschaftsförderung']
        
        return program


def main():
    """Run SAB scraper."""
    scraper = SABScraper()
    programs = scraper.run(save_path="/opt/projects/saas-project-8/backend/data/grants/sab.json")
    
    print(f"\n📊 Results:")
    print(f"Total programs: {len(programs)}")
    
    if programs:
        print("\n📋 Sample programs:")
        for p in programs[:3]:
            print(f"  - {p['name'][:60]}")
            print(f"    URL: {p['url_offiziell'][:60]}...")
            if p.get('foerderhoehe_max'):
                print(f"    Max: {p['foerderhoehe_max']:,.0f}€")
            if p.get('foerderquote'):
                print(f"    Quote: {p['foerderquote']*100:.0f}%")


if __name__ == "__main__":
    main()
