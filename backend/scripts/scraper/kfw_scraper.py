"""
KfW Scraper
Scrapes funding programs from Kreditanstalt für Wiederaufbau (KfW)
https://www.kfw.de
"""

from typing import List, Dict, Optional
from urllib.parse import urljoin
import re
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class KfWScraper(BaseScraper):
    """
    Scraper for KfW (Kreditanstalt für Wiederaufbau)
    
    KfW offers various funding programs including:
    - Gründung & Nachfolge (Startups)
    - Unternehmen erweitern & festigen
    - Innovation & Digitalisierung
    - Energieeffizienz & Erneuerbare Energien
    """
    
    SOURCE_NAME = "kfw"
    BASE_URL = "https://www.kfw.de"
    TIER = 1  # Daily scraping
    
    # KfW Program overview pages
    OVERVIEW_URLS = [
        "/inlandsfoerderung/Unternehmen/index.html",
        "/inlandsfoerderung/Unternehmen/Gr%C3%BCndung-Nachfolge/index.html",
        "/inlandsfoerderung/Unternehmen/Energie-Umwelt/index.html",
        "/inlandsfoerderung/Unternehmen/Innovation/index.html",
    ]
    
    # Known KfW programs with details
    KNOWN_PROGRAMS = [
        {
            "name": "ERP-Gründerkredit - StartGeld (067)",
            "url": "/inlandsfoerderung/Unternehmen/Gr%C3%BCndung-Nachfolge/ERP-Gr%C3%BCnderkredit-Startgeld/index.html",
            "product_number": "067",
            "foerderhoehe_max": 125000,
            "foerderart": "kredit",
            "category": "gruendung"
        },
        {
            "name": "ERP-Gründerkredit - Universell (073, 074, 075, 076)",
            "url": "/inlandsfoerderung/Unternehmen/Gr%C3%BCndung-Nachfolge/ERP-Gr%C3%BCnderkredit-Universell/index.html",
            "product_number": "073-076",
            "foerderhoehe_max": 25000000,
            "foerderart": "kredit",
            "category": "gruendung"
        },
        {
            "name": "ERP-Kapital für Gründung (058)",
            "url": "/inlandsfoerderung/Unternehmen/Gr%C3%BCndung-Nachfolge/ERP-Kapital-f%C3%BCr-Gr%C3%BCndung/index.html",
            "product_number": "058",
            "foerderhoehe_max": 500000,
            "foerderart": "kredit",
            "category": "gruendung"
        },
        {
            "name": "ERP-Digitalisierungs- und Innovationskredit (380, 390, 391)",
            "url": "/inlandsfoerderung/Unternehmen/Innovation/ERP-Digitalisierungs-Innovationskredit/index.html",
            "product_number": "380,390,391",
            "foerderhoehe_max": 25000000,
            "foerderart": "kredit",
            "category": "innovation"
        },
        {
            "name": "KfW-Unternehmerkredit (037, 047)",
            "url": "/inlandsfoerderung/Unternehmen/Erweitern-Festigen/KfW-Unternehmerkredit/index.html",
            "product_number": "037,047",
            "foerderhoehe_max": 25000000,
            "foerderart": "kredit",
            "category": "wachstum"
        },
        {
            "name": "Bundesförderung für effiziente Gebäude (261, 263)",
            "url": "/inlandsfoerderung/Unternehmen/Energie-Umwelt/F%C3%B6rderprodukte-f%C3%BCr-Bestandsgeb%C3%A4ude-%28Unternehmen%29/index.html",
            "product_number": "261,263",
            "foerderhoehe_max": 150000,
            "foerderart": "kredit",
            "category": "energie"
        },
        {
            "name": "Erneuerbare Energien - Standard (270)",
            "url": "/inlandsfoerderung/Unternehmen/Energie-Umwelt/Erneuerbare-Energien-Standard/index.html",
            "product_number": "270",
            "foerderhoehe_max": 150000000,
            "foerderart": "kredit",
            "category": "energie"
        },
        {
            "name": "Klimaschutzoffensive für Unternehmen (293)",
            "url": "/inlandsfoerderung/Unternehmen/Energie-Umwelt/Klimaschutzoffensive-f%C3%BCr-Unternehmen/index.html",
            "product_number": "293",
            "foerderhoehe_max": 25000000,
            "foerderart": "kredit",
            "category": "energie"
        },
    ]
    
    def scrape_programs(self) -> List[Dict]:
        """Scrape all KfW funding programs."""
        programs = []
        seen_urls = set()
        
        # Add known programs first
        for prog in self.KNOWN_PROGRAMS:
            full_url = urljoin(self.BASE_URL, prog["url"])
            if full_url not in seen_urls:
                programs.append({
                    "name": prog["name"],
                    "url": full_url,
                    "source_url": full_url,
                    "product_number": prog.get("product_number", ""),
                    "foerderhoehe_max": prog.get("foerderhoehe_max"),
                    "foerderart": prog.get("foerderart", "kredit"),
                    "category": prog.get("category", "allgemein")
                })
                seen_urls.add(full_url)
        
        # Scrape overview pages for additional programs
        for overview_url in self.OVERVIEW_URLS:
            url = urljoin(self.BASE_URL, overview_url)
            logger.info(f"Scanning KfW overview: {url}")
            
            soup = self.get_page(url)
            if not soup:
                continue
            
            # Find program links (KfW uses specific CSS classes)
            product_links = soup.find_all('a', href=re.compile(r'/inlandsfoerderung/'))
            for link in product_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if self._is_product_link(href, text):
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in seen_urls:
                        programs.append({
                            "name": text,
                            "url": full_url,
                            "source_url": url
                        })
                        seen_urls.add(full_url)
            
            self.wait(1)
        
        logger.info(f"Found {len(programs)} KfW programs")
        return programs
    
    def _is_product_link(self, href: str, text: str) -> bool:
        """Check if link is a KfW product page."""
        # Skip utility links
        skip_patterns = [
            '/Service/', '/kontakt/', '/downloads/',
            '.pdf', 'javascript:', '#', 'mailto:'
        ]
        for pattern in skip_patterns:
            if pattern.lower() in href.lower():
                return False
        
        # Product pages typically contain these in URL or text
        product_indicators = [
            'kredit', 'ERP', 'Förder', 'Start',
            'Gründer', 'Unternehmer', 'Energie'
        ]
        
        combined = (href + " " + text).lower()
        for indicator in product_indicators:
            if indicator.lower() in combined:
                return True
        
        # Check for product number pattern (3-digit number)
        if re.search(r'\(\d{3}\)', text):
            return True
        
        return False
    
    def scrape_program_details(self, program: Dict) -> Dict:
        """Scrape detailed information for a KfW program."""
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
        
        # Try intro/teaser section first
        intro_sections = soup.find_all(['div', 'section'], class_=re.compile(r'(intro|teaser|lead|summary)', re.I))
        for section in intro_sections:
            text = section.get_text(strip=True)
            if len(text) > 50:
                description = text[:1000]
                break
        
        # Fallback to main content
        if not description:
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                paragraphs = main_content.find_all('p', limit=5)
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 50:
                        description += text + " "
        
        program['beschreibung'] = description[:2000].strip()
        
        # Extract structured data from tables or lists
        full_text = page_content.lower()
        
        # Try to find credit amount
        if not program.get('foerderhoehe_max'):
            amount_patterns = [
                r'bis\s+zu\s+([\d.,]+)\s*(mio|million)',
                r'maximal\s+([\d.,]+)\s*(euro|€)',
                r'kredithöhe\D*([\d.,]+)',
                r'([\d.,]+)\s*(euro|€)\s*kredit',
            ]
            for pattern in amount_patterns:
                match = re.search(pattern, full_text)
                if match:
                    amount_str = match.group(1).replace('.', '').replace(',', '.')
                    try:
                        amount = float(amount_str)
                        # Check if millions
                        if 'mio' in match.group(0) or 'million' in match.group(0):
                            amount *= 1000000
                        program['foerderhoehe_max'] = amount
                    except ValueError:
                        pass
                    break
        
        # Extract interest rate info
        zins_match = re.search(r'([\d,]+)\s*%\s*(p\.?\s*a\.?|zinssatz|zins)', full_text)
        if zins_match:
            program['zinssatz'] = zins_match.group(1).replace(',', '.')
        
        # Set KfW-specific fields
        program['anbieter'] = 'KfW - Kreditanstalt für Wiederaufbau'
        program['ebene'] = 'bund'
        
        # Default to kredit if not set
        if not program.get('foerderart'):
            program['foerderart'] = 'kredit'
        
        # Target group
        program['zielgruppe'] = {
            'rechtsform': ['GmbH', 'UG', 'AG', 'GmbH & Co. KG', 'Einzelunternehmen', 'KG', 'OHG'],
            'regionen': ['bundesweit']
        }
        
        # Determine funding purpose from category or content
        foerdergegenstand = []
        if program.get('category') == 'gruendung' or 'gründ' in full_text:
            foerdergegenstand.append('Existenzgründung')
        if program.get('category') == 'innovation' or 'innovation' in full_text or 'digital' in full_text:
            foerdergegenstand.append('Innovation')
            foerdergegenstand.append('Digitalisierung')
        if program.get('category') == 'energie' or 'energie' in full_text or 'klima' in full_text:
            foerdergegenstand.append('Energieeffizienz')
            foerdergegenstand.append('Klimaschutz')
        if program.get('category') == 'wachstum' or 'wachstum' in full_text or 'erweit' in full_text:
            foerdergegenstand.append('Unternehmenswachstum')
        
        program['foerdergegenstand'] = foerdergegenstand if foerdergegenstand else ['Unternehmensfinanzierung']
        
        return program


def main():
    """Run KfW scraper."""
    scraper = KfWScraper()
    programs = scraper.run(save_path="/opt/projects/saas-project-8/backend/data/grants/kfw.json")
    
    print(f"\n📊 Results:")
    print(f"Total programs: {len(programs)}")
    
    if programs:
        print("\n📋 Sample programs:")
        for p in programs[:3]:
            print(f"  - {p['name'][:60]}")
            print(f"    URL: {p['url_offiziell'][:60]}...")
            if p.get('foerderhoehe_max'):
                print(f"    Max: {p['foerderhoehe_max']:,.0f}€")


if __name__ == "__main__":
    main()
