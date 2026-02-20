"""
go-digital Scraper
Scrapes detailed information about the go-digital funding program
https://www.bmwk.de and partner sites
"""

from typing import List, Dict, Optional
from urllib.parse import urljoin
import re
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class GoDigitalScraper(BaseScraper):
    """
    Specialized scraper for go-digital program details.
    
    go-digital is a major BMWK program for SME digitalization with three modules:
    - Module 1: Digitalisierte Geschäftsprozesse
    - Module 2: Digitale Markterschließung
    - Module 3: IT-Sicherheit
    """
    
    SOURCE_NAME = "godigital"
    BASE_URL = "https://www.bmwk.de"
    TIER = 1  # Daily scraping
    
    # Official go-digital pages
    PROGRAM_PAGES = [
        "/Redaktion/DE/Artikel/Digitale-Welt/foerderprogramm-go-digital.html",
    ]
    
    # go-digital modules with details
    GODIGITAL_MODULES = [
        {
            "name": "go-digital - Modul: Digitalisierte Geschäftsprozesse",
            "module_number": 1,
            "beschreibung": "Beratung zur Einführung und Optimierung digitaler Geschäftsprozesse. Schwerpunkte: ERP-Systeme, Dokumentenmanagement, Workflow-Automatisierung, Cloud-Lösungen.",
            "foerderhoehe_max": 16500,
            "foerderquote": 0.5,
            "max_tage": 30,
            "tagessatz": 1100
        },
        {
            "name": "go-digital - Modul: Digitale Markterschließung",
            "module_number": 2,
            "beschreibung": "Beratung zur Erschließung digitaler Vertriebskanäle. Schwerpunkte: Online-Marketing, E-Commerce, Social Media Marketing, Webshop-Aufbau.",
            "foerderhoehe_max": 16500,
            "foerderquote": 0.5,
            "max_tage": 30,
            "tagessatz": 1100
        },
        {
            "name": "go-digital - Modul: IT-Sicherheit",
            "module_number": 3,
            "beschreibung": "Beratung zur Verbesserung der IT-Sicherheit. Schwerpunkte: Risikoanalyse, Sicherheitskonzepte, Datenschutz, Notfallmanagement, Mitarbeiterschulungen.",
            "foerderhoehe_max": 16500,
            "foerderquote": 0.5,
            "max_tage": 30,
            "tagessatz": 1100
        },
    ]
    
    # Comprehensive program details
    GODIGITAL_DETAILS = {
        "name": "go-digital",
        "anbieter": "BMWK - Bundesministerium für Wirtschaft und Klimaschutz",
        "durchfuehrung": "Euronorm GmbH",
        "ebene": "bund",
        "foerderart": "zuschuss",
        "foerderhoehe_min": 0,
        "foerderhoehe_max": 16500,
        "foerderquote": 0.5,
        "foerdergegenstand": ["Digitalisierung", "Beratung", "IT-Sicherheit", "E-Commerce"],
        "zielgruppe": {
            "rechtsform": ["GmbH", "UG", "AG", "GmbH & Co. KG", "Einzelunternehmen", "KG", "OHG", "eG", "Freiberufler"],
            "mitarbeiter_max": 100,
            "umsatz_max": 20000000,
            "branchen": ["Handwerk", "Handel", "Dienstleistung", "Produktion"],
            "regionen": ["bundesweit"],
            "ausschluss": [
                "Unternehmen der Primärproduktion landwirtschaftlicher Erzeugnisse",
                "Unternehmen der Fischerei und Aquakultur",
                "Unternehmensberatungen"
            ]
        },
        "voraussetzungen": [
            "Firmensitz und Geschäftsbetrieb in Deutschland",
            "Weniger als 100 Mitarbeiter",
            "Jahresumsatz oder Bilanzsumme max. 20 Mio. €",
            "Gewerbliche oder freiberufliche Tätigkeit",
            "Beratung durch autorisiertes Beratungsunternehmen"
        ],
        "antragstellung": {
            "verfahren": "Antragstellung durch autorisiertes Beratungsunternehmen",
            "online": True,
            "url": "https://foerderportal.bund.de"
        },
        "url_offiziell": "https://www.bmwk.de/Redaktion/DE/Artikel/Digitale-Welt/foerderprogramm-go-digital.html",
        "url_antrag": "https://foerderportal.bund.de",
        "hotline": "030 2125-3888",
        "email": "foerderprogramm@euronorm.de"
    }
    
    def scrape_programs(self) -> List[Dict]:
        """
        Return go-digital program and its modules as separate entries.
        Since go-digital is a well-documented program, we provide curated data.
        """
        programs = []
        
        # Add main go-digital program
        main_program = self.GODIGITAL_DETAILS.copy()
        main_program['url'] = main_program['url_offiziell']
        main_program['source_url'] = main_program['url_offiziell']
        main_program['beschreibung'] = (
            "go-digital unterstützt kleine und mittlere Unternehmen (KMU) sowie Handwerksbetriebe bei der "
            "Digitalisierung durch geförderte Beratungsleistungen. Das Programm fördert 50% der Beratungskosten "
            "bis maximal 16.500 € in drei Modulen: Digitalisierte Geschäftsprozesse, Digitale Markterschließung "
            "und IT-Sicherheit. Die Beratung erfolgt durch vom BMWK autorisierte Beratungsunternehmen."
        )
        programs.append(main_program)
        
        # Add each module as separate entry for better matching
        for module in self.GODIGITAL_MODULES:
            module_program = {
                "name": module["name"],
                "anbieter": "BMWK - Bundesministerium für Wirtschaft und Klimaschutz",
                "ebene": "bund",
                "foerderart": "zuschuss",
                "foerderhoehe_max": module["foerderhoehe_max"],
                "foerderquote": module["foerderquote"],
                "beschreibung": module["beschreibung"],
                "foerdergegenstand": self._get_module_purposes(module["module_number"]),
                "zielgruppe": self.GODIGITAL_DETAILS["zielgruppe"].copy(),
                "url": self.GODIGITAL_DETAILS["url_offiziell"],
                "source_url": self.GODIGITAL_DETAILS["url_offiziell"],
                "voraussetzungen": self.GODIGITAL_DETAILS["voraussetzungen"],
                "max_beratertage": module["max_tage"],
                "tagessatz": module["tagessatz"],
                "parent_program": "go-digital"
            }
            programs.append(module_program)
        
        logger.info(f"Created {len(programs)} go-digital program entries")
        return programs
    
    def _get_module_purposes(self, module_number: int) -> List[str]:
        """Return specific funding purposes for each module."""
        purposes = {
            1: ["Digitalisierung", "Geschäftsprozesse", "ERP", "Workflow"],
            2: ["Digitalisierung", "E-Commerce", "Online-Marketing", "Vertrieb"],
            3: ["IT-Sicherheit", "Datenschutz", "Cybersecurity"]
        }
        return purposes.get(module_number, ["Digitalisierung"])
    
    def scrape_program_details(self, program: Dict) -> Dict:
        """
        For go-digital, we already have detailed data.
        Just fetch the page for hash calculation if needed.
        """
        url = program.get('url', '')
        
        # Calculate hash from current data for change detection
        content_for_hash = f"{program.get('name', '')}{program.get('beschreibung', '')}{program.get('foerderhoehe_max', '')}"
        program['raw_html_hash'] = self.calculate_hash(content_for_hash)
        
        # Optionally fetch page for latest content
        if url:
            soup = self.get_page(url)
            if soup:
                # Update hash with actual page content
                page_content = soup.get_text()
                program['raw_html_hash'] = self.calculate_hash(page_content)
                
                # Check for any updates in the official description
                article = soup.find('article') or soup.find('div', class_=re.compile('content'))
                if article:
                    latest_text = article.get_text(strip=True)[:500]
                    # Compare with stored description
                    if 'eingestellt' in latest_text.lower() or 'beendet' in latest_text.lower():
                        program['status'] = 'expired'
                        logger.warning(f"Program may be expired: {program['name']}")
        
        return program


def main():
    """Run go-digital scraper."""
    scraper = GoDigitalScraper()
    programs = scraper.run(save_path="/opt/projects/saas-project-8/backend/data/grants/godigital.json")
    
    print(f"\n📊 go-digital Results:")
    print(f"Total entries: {len(programs)}")
    
    if programs:
        print("\n📋 Programs:")
        for p in programs:
            print(f"\n  📌 {p['name']}")
            print(f"     Max: {p.get('foerderhoehe_max', 'N/A'):,}€")
            print(f"     Quote: {p.get('foerderquote', 0)*100:.0f}%")
            if p.get('beschreibung'):
                print(f"     {p['beschreibung'][:100]}...")


if __name__ == "__main__":
    main()
