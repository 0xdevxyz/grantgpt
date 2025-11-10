"""
Web Scraper für die Förderdatenbank des Bundes
https://www.foerderdatenbank.de/

Dieser Scraper sammelt Förderprogramme und bereitet sie für GrantGPT auf.
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Any
from datetime import datetime


class FoerderdatenbankScraper:
    """
    Scraper für die offizielle Förderdatenbank des Bundes
    
    WICHTIG: 
    - Robots.txt beachten
    - Rate-Limiting einhalten (max 1 Request/Sekunde)
    - User-Agent setzen
    """
    
    def __init__(self):
        self.base_url = "https://www.foerderdatenbank.de"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GrantGPT-Bot/1.0 (Fördermittel-Aggregator; info@grantgpt.de)"
        })
    
    def search_programs(
        self, 
        query: str = "", 
        region: str = "bundesweit",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Suche nach Förderprogrammen
        
        Args:
            query: Suchbegriff (z.B. "Innovation", "Digitalisierung")
            region: Region (z.B. "bundesweit", "Bayern", "NRW")
            limit: Max. Anzahl Ergebnisse
            
        Returns:
            Liste von Förderprogrammen
        """
        programs = []
        
        # TODO: Echte API-Calls implementieren
        # Die Förderdatenbank hat vermutlich eine Such-API oder HTML-Struktur
        
        print(f"Scraping Förderdatenbank für: {query} in {region}")
        
        # Beispiel-Struktur für gescrapte Programme
        example_program = {
            "id": "foerderdatenbank-12345",
            "source": "foerderdatenbank.de",
            "name": "Beispiel-Förderprogramm",
            "type": "federal",  # oder "state", "eu"
            "category": "innovation",
            "description": "Beschreibung des Programms...",
            "max_funding": 500000,
            "min_funding": 50000,
            "min_own_contribution_percent": 15,
            "eligibility": [
                "KMU mit Sitz in Deutschland",
                "Innovative Technologie",
            ],
            "requirements": [
                "Detaillierter Projektantrag",
                "Finanzplan",
            ],
            "deadline": "2025-12-31T23:59:59Z",
            "is_continuous": False,
            "website_url": "https://www.foerderdatenbank.de/...",
            "contact_info": {
                "organization": "Förderorganisation",
                "email": "info@beispiel.de",
                "phone": "+49 ...",
            },
            "scraped_at": datetime.now().isoformat(),
        }
        
        # Rate Limiting
        time.sleep(1)
        
        return programs
    
    def scrape_all_programs(self, output_file: str = "all_grants.json"):
        """
        Scrapt alle verfügbaren Förderprogramme
        
        STRATEGIE:
        1. Alle Kategorien durchgehen (Innovation, Digitalisierung, etc.)
        2. Alle Regionen (Bund, Länder, EU)
        3. Duplikate entfernen
        4. In JSON speichern
        """
        all_programs = []
        
        categories = [
            "innovation",
            "digitalisierung", 
            "forschung",
            "gruendung",
            "export",
            "umwelt",
            "energie",
        ]
        
        regions = [
            "bundesweit",
            "baden-wuerttemberg",
            "bayern",
            "berlin",
            "brandenburg",
            "bremen",
            "hamburg",
            "hessen",
            "niedersachsen",
            "nrw",
            "rheinland-pfalz",
            "saarland",
            "sachsen",
            "sachsen-anhalt",
            "schleswig-holstein",
            "thueringen",
            "eu",
        ]
        
        print(f"Scraping {len(categories)} Kategorien x {len(regions)} Regionen...")
        
        for category in categories:
            for region in regions:
                print(f"\n→ {category} in {region}")
                programs = self.search_programs(
                    query=category, 
                    region=region,
                    limit=50
                )
                all_programs.extend(programs)
                
                # Rate Limiting: 1 Request/Sekunde
                time.sleep(1)
        
        # Duplikate entfernen (basierend auf ID)
        unique_programs = {p["id"]: p for p in all_programs}.values()
        
        print(f"\n✅ {len(unique_programs)} einzigartige Programme gefunden")
        
        # Speichern
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(list(unique_programs), f, indent=2, ensure_ascii=False)
        
        print(f"💾 Gespeichert: {output_file}")
        
        return list(unique_programs)


def main():
    """
    Hauptfunktion zum Scrapen und Importieren
    """
    scraper = FoerderdatenbankScraper()
    
    print("=" * 60)
    print("Förderdatenbank.de Scraper")
    print("=" * 60)
    
    # Alle Programme scrapen
    programs = scraper.scrape_all_programs(
        output_file="/app/data/grants/foerderdatenbank_all.json"
    )
    
    print(f"\n🎉 Fertig! {len(programs)} Programme bereit für Import in GrantGPT")
    
    # TODO: Automatisch in Qdrant embedden
    # from app.services.embeddings import embedding_service
    # from app.services.qdrant_service import qdrant_service


if __name__ == "__main__":
    main()

