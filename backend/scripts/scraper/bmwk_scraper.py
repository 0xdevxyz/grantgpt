"""
BMWK Scraper
Scrapes funding programs from Bundesministerium für Wirtschaft und Klimaschutz
https://www.bmwk.de
"""

from typing import List, Dict, Optional
from urllib.parse import urljoin
import re
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BMWKScraper(BaseScraper):
    """
    Scraper for BMWK (Bundesministerium für Wirtschaft und Klimaschutz)
    
    BMWK offers/coordinates various funding programs including:
    - go-digital
    - go-inno
    - EXIST
    - ZIM
    - INVEST
    """
    
    SOURCE_NAME = "bmwk"
    BASE_URL = "https://www.bmwk.de"
    TIER = 1  # Daily scraping
    
    # BMWK funding overview pages
    OVERVIEW_URLS = [
        "/Redaktion/DE/Dossier/foerderprogramme.html",
        "/Navigation/DE/Themen/Mittelstand/Mittelstandsfinanzierung/mittelstandsfinanzierung.html",
        "/Navigation/DE/Themen/Digitale-Welt/digitale-welt.html",
    ]
    
    # Known BMWK programs with details
    KNOWN_PROGRAMS = [
        {
            "name": "go-digital",
            "url": "/Redaktion/DE/Artikel/Digitale-Welt/foerderprogramm-go-digital.html",
            "foerderhoehe_max": 16500,
            "foerderquote": 0.5,
            "foerderart": "zuschuss",
            "category": "digitalisierung",
            "beschreibung": "Förderprogramm für kleine und mittlere Unternehmen zur Digitalisierung. Unterstützt werden Beratungsleistungen in den Modulen Digitalisierte Geschäftsprozesse, Digitale Markterschließung und IT-Sicherheit."
        },
        {
            "name": "go-inno",
            "url": "/Redaktion/DE/Artikel/Mittelstand/go-inno.html",
            "foerderhoehe_max": 20000,
            "foerderquote": 0.5,
            "foerderart": "zuschuss",
            "category": "innovation",
            "beschreibung": "Beratungsförderung für innovative KMU. Unterstützt werden Beratungsleistungen zur Vorbereitung und Durchführung von Produkt- und technischen Verfahrensinnovationen."
        },
        {
            "name": "ZIM - Zentrales Innovationsprogramm Mittelstand",
            "url": "/Redaktion/DE/Artikel/Mittelstand/zim.html",
            "foerderhoehe_max": 550000,
            "foerderquote": 0.45,
            "foerderart": "zuschuss",
            "category": "innovation",
            "beschreibung": "Das ZIM ist das größte Innovationsförderprogramm für den Mittelstand. Es fördert Forschungs- und Entwicklungsprojekte von KMU und deren Kooperationen mit Forschungseinrichtungen."
        },
        {
            "name": "EXIST-Gründerstipendium",
            "url": "/Redaktion/DE/Artikel/Mittelstand/exist-gruenderstipendium.html",
            "foerderhoehe_max": 3000,  # pro Monat
            "foerderquote": 1.0,
            "foerderart": "zuschuss",
            "category": "gruendung",
            "beschreibung": "Unterstützt Studierende, Absolventen und Wissenschaftler bei der Vorbereitung innovativer technologieorientierter Gründungsvorhaben."
        },
        {
            "name": "EXIST-Forschungstransfer",
            "url": "/Redaktion/DE/Artikel/Mittelstand/exist-forschungstransfer.html",
            "foerderhoehe_max": 250000,
            "foerderquote": 1.0,
            "foerderart": "zuschuss",
            "category": "gruendung",
            "beschreibung": "Fördert herausragende forschungsbasierte Gründungsvorhaben. Unterstützt Entwicklungsarbeiten und die Vorbereitung einer Unternehmensgründung."
        },
        {
            "name": "INVEST - Zuschuss für Wagniskapital",
            "url": "/Redaktion/DE/Artikel/Mittelstand/invest-zuschuss-fuer-wagniskapital.html",
            "foerderhoehe_max": 100000,
            "foerderquote": 0.25,
            "foerderart": "zuschuss",
            "category": "finanzierung",
            "beschreibung": "Fördert Business Angels und andere Privatinvestoren, die in innovative Startups investieren. 25% Zuschuss auf Investments bis 400.000€."
        },
        {
            "name": "ERP-Digitalisierungs- und Innovationskredit",
            "url": "/Redaktion/DE/Artikel/Mittelstand/erp-digitalisierungs-und-innovationskredit.html",
            "foerderhoehe_max": 25000000,
            "foerderart": "kredit",
            "category": "innovation",
            "beschreibung": "Zinsgünstiger Kredit für Digitalisierungs- und Innovationsvorhaben mittelständischer Unternehmen."
        },
        {
            "name": "ERP-Gründerkredit StartGeld",
            "url": "/Redaktion/DE/Artikel/Mittelstand/erp-gruenderkredit-startgeld.html",
            "foerderhoehe_max": 125000,
            "foerderart": "kredit",
            "category": "gruendung",
            "beschreibung": "Günstiger Kredit für Existenzgründer und junge Unternehmen bis 5 Jahre nach Gründung."
        },
        {
            "name": "Mikromezzaninfonds Deutschland",
            "url": "/Redaktion/DE/Artikel/Mittelstand/mikromezzaninfonds-deutschland.html",
            "foerderhoehe_max": 75000,
            "foerderart": "beteiligung",
            "category": "finanzierung",
            "beschreibung": "Stille Beteiligungen für Kleinstunternehmen, Existenzgründer und Sozialunternehmen."
        },
        {
            "name": "Innovationsprämie Klima",
            "url": "/Redaktion/DE/Artikel/Mittelstand/innovationspraemie-klima.html",
            "foerderhoehe_max": 35000,
            "foerderquote": 0.5,
            "foerderart": "zuschuss",
            "category": "klimaschutz",
            "beschreibung": "Unterstützt kleine Unternehmen bei der Entwicklung und Umsetzung von klimaschonenden Produkten und Dienstleistungen."
        },
    ]
    
    def scrape_programs(self) -> List[Dict]:
        """Scrape all BMWK funding programs."""
        programs = []
        seen_urls = set()
        
        # Add known programs first (with detailed data)
        for prog in self.KNOWN_PROGRAMS:
            full_url = urljoin(self.BASE_URL, prog["url"])
            if full_url not in seen_urls:
                program_data = {
                    "name": prog["name"],
                    "url": full_url,
                    "source_url": full_url,
                    "foerderart": prog.get("foerderart", "zuschuss"),
                    "category": prog.get("category", "allgemein"),
                    "beschreibung": prog.get("beschreibung", "")
                }
                if "foerderhoehe_max" in prog:
                    program_data["foerderhoehe_max"] = prog["foerderhoehe_max"]
                if "foerderquote" in prog:
                    program_data["foerderquote"] = prog["foerderquote"]
                
                programs.append(program_data)
                seen_urls.add(full_url)
        
        # Scrape overview pages for additional programs
        for overview_path in self.OVERVIEW_URLS:
            url = urljoin(self.BASE_URL, overview_path)
            logger.info(f"Scanning BMWK overview: {url}")
            
            soup = self.get_page(url)
            if not soup:
                continue
            
            # Find program links
            links = soup.find_all('a', href=True)
            for link in links:
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
        
        logger.info(f"Found {len(programs)} BMWK programs")
        return programs
    
    def _is_program_link(self, href: str, text: str) -> bool:
        """Check if link is a BMWK program page."""
        # Skip utility links
        skip_patterns = [
            '/Service/', '/Presse/', '/Ministerium/',
            '/SharedDocs/', 'facebook', 'twitter', 'youtube',
            '.pdf', '.jpg', '.png', 'javascript:', '#', 'mailto:'
        ]
        for pattern in skip_patterns:
            if pattern.lower() in href.lower():
                return False
        
        # Must be on BMWK domain or relative
        if href.startswith('http') and 'bmwk.de' not in href:
            return False
        
        # Look for funding-related keywords
        combined = (href + " " + text).lower()
        funding_keywords = [
            'förder', 'programm', 'zuschuss', 'kredit',
            'zim', 'exist', 'invest', 'go-digital', 'go-inno',
            'erp', 'innovation', 'gründer', 'startup'
        ]
        
        for keyword in funding_keywords:
            if keyword in combined:
                return True
        
        return False
    
    def scrape_program_details(self, program: Dict) -> Dict:
        """Scrape detailed information for a BMWK program."""
        url = program.get('url', '')
        if not url:
            return program
        
        # Skip if we already have detailed description
        if len(program.get('beschreibung', '')) > 100:
            program['raw_html_hash'] = self.calculate_hash(program.get('beschreibung', ''))
            program['anbieter'] = 'BMWK - Bundesministerium für Wirtschaft und Klimaschutz'
            program['ebene'] = 'bund'
            return program
        
        soup = self.get_page(url)
        if not soup:
            return program
        
        # Calculate hash for change detection
        page_content = soup.get_text()
        program['raw_html_hash'] = self.calculate_hash(page_content)
        
        # Extract description from article content
        description = ""
        
        # BMWK uses article structure
        article = soup.find('article') or soup.find('div', class_='article-content')
        if article:
            paragraphs = article.find_all('p', limit=7)
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:
                    description += text + " "
        
        # Fallback
        if not description:
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 100 and 'Cookie' not in text:
                    description += text + " "
                    if len(description) > 500:
                        break
        
        program['beschreibung'] = description[:2000].strip()
        
        # Extract funding details from text
        full_text = page_content.lower()
        
        # Try to find funding amounts if not already set
        if not program.get('foerderhoehe_max'):
            amount_patterns = [
                r'bis\s+zu\s+([\d.,]+)\s*(euro|€)',
                r'maximal\s+([\d.,]+)\s*(euro|€)',
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
        
        # Set BMWK-specific fields
        program['anbieter'] = 'BMWK - Bundesministerium für Wirtschaft und Klimaschutz'
        program['ebene'] = 'bund'
        
        # Determine funding type if not set
        if not program.get('foerderart'):
            if 'kredit' in full_text or 'darlehen' in full_text:
                program['foerderart'] = 'kredit'
            elif 'beteiligung' in full_text:
                program['foerderart'] = 'beteiligung'
            else:
                program['foerderart'] = 'zuschuss'
        
        # Target group
        zielgruppe = {
            'rechtsform': ['GmbH', 'UG', 'AG', 'GmbH & Co. KG', 'Einzelunternehmen'],
            'regionen': ['bundesweit']
        }
        
        # KMU focus
        if 'kmu' in full_text or 'mittelstand' in full_text:
            zielgruppe['mitarbeiter_max'] = 250
        if 'kleinstunternehmen' in full_text:
            zielgruppe['mitarbeiter_max'] = 10
        
        program['zielgruppe'] = zielgruppe
        
        # Determine funding purpose
        foerdergegenstand = []
        category = program.get('category', '')
        
        if category == 'digitalisierung' or 'digital' in full_text:
            foerdergegenstand.append('Digitalisierung')
        if category == 'innovation' or 'innovation' in full_text:
            foerdergegenstand.append('Innovation')
        if category == 'gruendung' or 'gründ' in full_text or 'exist' in full_text.lower():
            foerdergegenstand.append('Existenzgründung')
        if category == 'finanzierung' or 'finanzierung' in full_text:
            foerdergegenstand.append('Unternehmensfinanzierung')
        if category == 'klimaschutz' or 'klima' in full_text:
            foerdergegenstand.append('Klimaschutz')
        if 'forschung' in full_text or 'entwicklung' in full_text:
            foerdergegenstand.append('Forschung & Entwicklung')
        if 'beratung' in full_text:
            foerdergegenstand.append('Beratung')
        
        program['foerdergegenstand'] = foerdergegenstand if foerdergegenstand else ['Wirtschaftsförderung']
        
        return program


def main():
    """Run BMWK scraper."""
    scraper = BMWKScraper()
    programs = scraper.run(save_path="/opt/projects/saas-project-8/backend/data/grants/bmwk.json")
    
    print(f"\n📊 Results:")
    print(f"Total programs: {len(programs)}")
    
    if programs:
        print("\n📋 Sample programs:")
        for p in programs[:5]:
            print(f"  - {p['name'][:60]}")
            if p.get('foerderhoehe_max'):
                print(f"    Max: {p['foerderhoehe_max']:,.0f}€")
            if p.get('foerderquote'):
                print(f"    Quote: {p['foerderquote']*100:.0f}%")


if __name__ == "__main__":
    main()
