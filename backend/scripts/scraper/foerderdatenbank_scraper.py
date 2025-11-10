"""
Förderdatenbank.de Scraper
Scrapes funding programs from the German federal funding database
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, quote


class FoerderdatenbankScraper:
    BASE_URL = "https://www.foerderdatenbank.de"
    SEARCH_URL = f"{BASE_URL}/SiteGlobals/FDB/Forms/Suche/Startseitensuche_Formular.html"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def search_programs(self, query: str = "", max_results: int = 100) -> List[Dict]:
        """
        Search for funding programs
        """
        programs = []
        page = 0
        
        while len(programs) < max_results:
            print(f"📄 Scraping page {page + 1}...")
            
            params = {
                'templateQueryString': query,
                'filterCategories': 'FundingProgram',
                'submit': 'Suchen',
                'pageNo': page
            }
            
            try:
                response = self.session.get(self.SEARCH_URL, params=params, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all program cards
                cards = soup.find_all('div', class_='card--fundingprogram')
                
                if not cards:
                    print("No more results found.")
                    break
                
                for card in cards:
                    if len(programs) >= max_results:
                        break
                        
                    program = self._parse_program_card(card)
                    if program:
                        programs.append(program)
                        print(f"✅ Found: {program['title'][:60]}...")
                
                page += 1
                time.sleep(1)  # Be polite
                
            except Exception as e:
                print(f"❌ Error scraping page {page}: {e}")
                break
        
        return programs
    
    def _parse_program_card(self, card) -> Optional[Dict]:
        """
        Parse a single program card from search results
        """
        try:
            # Find title and link
            title_elem = card.find('p', class_='card--title')
            if not title_elem:
                return None
            
            link_elem = title_elem.find('a')
            if not link_elem:
                return None
            
            title = link_elem.get_text(strip=True)
            href = link_elem.get('href', '')
            url = urljoin(self.BASE_URL, href)
            
            # Extract metadata
            metadata = {}
            dl = card.find('dl', class_='document-info-fundingprogram')
            if dl:
                dts = dl.find_all('dt')
                dds = dl.find_all('dd')
                for dt, dd in zip(dts, dds):
                    key = dt.get_text(strip=True).rstrip(':')
                    value = dd.get_text(strip=True)
                    metadata[key] = value
            
            program = {
                'title': title,
                'url': url,
                'who_is_funded': metadata.get('Wer wird gefördert?', ''),
                'what_is_funded': metadata.get('Was wird gefördert?', ''),
                'source': 'foerderdatenbank.de'
            }
            
            return program
            
        except Exception as e:
            print(f"⚠️  Error parsing card: {e}")
            return None
    
    def scrape_program_details(self, program: Dict) -> Dict:
        """
        Scrape detailed information from a program's detail page
        """
        try:
            print(f"🔍 Scraping details: {program['title'][:50]}...")
            response = self.session.get(program['url'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract description
            description = ""
            content_div = soup.find('div', class_='rich--text')
            if content_div:
                paragraphs = content_div.find_all('p')
                description = ' '.join(p.get_text(strip=True) for p in paragraphs[:3])
            
            # Extract structured data
            details = {}
            dl_elements = soup.find_all('dl')
            for dl in dl_elements:
                dts = dl.find_all('dt')
                dds = dl.find_all('dd')
                for dt, dd in zip(dts, dds):
                    key = dt.get_text(strip=True).rstrip(':')
                    value = dd.get_text(strip=True)
                    details[key] = value
            
            program['description'] = description[:1000] if description else program.get('what_is_funded', '')
            program['details'] = details
            program['funding_amount'] = self._extract_amount(details)
            program['deadline'] = details.get('Antragsfrist', 'Laufend')
            program['region'] = details.get('Fördergebiet', 'Deutschland')
            program['funder'] = details.get('Fördergeber', 'Bund')
            program['funding_type'] = details.get('Förderart', 'Zuschuss')
            
            time.sleep(0.5)  # Be polite
            return program
            
        except Exception as e:
            print(f"⚠️  Error scraping details for {program['title']}: {e}")
            return program
    
    def _extract_amount(self, details: Dict) -> str:
        """
        Try to extract funding amount from details
        """
        for key, value in details.items():
            if any(term in key.lower() for term in ['höhe', 'betrag', 'förderung']):
                return value
        return "Nicht angegeben"
    
    def scrape_all(self, queries: List[str], max_per_query: int = 50) -> List[Dict]:
        """
        Scrape programs for multiple queries
        """
        all_programs = []
        seen_urls = set()
        
        for query in queries:
            print(f"\n🔎 Searching for: '{query}'")
            programs = self.search_programs(query, max_per_query)
            
            # Remove duplicates
            for program in programs:
                if program['url'] not in seen_urls:
                    all_programs.append(program)
                    seen_urls.add(program['url'])
            
            print(f"✅ Found {len(programs)} programs for '{query}' ({len(all_programs)} total unique)")
        
        # Scrape details for each program
        print(f"\n📚 Scraping details for {len(all_programs)} programs...")
        for i, program in enumerate(all_programs, 1):
            print(f"[{i}/{len(all_programs)}] ", end='')
            all_programs[i-1] = self.scrape_program_details(program)
        
        return all_programs


def main():
    """
    Main scraper function
    """
    scraper = FoerderdatenbankScraper()
    
    # Search queries to cover different areas
    queries = [
        "",  # Empty = all programs
        "innovation",
        "digitalisierung",
        "forschung",
        "startup",
        "mittelstand",
    ]
    
    print("🚀 Starting Förderdatenbank.de Scraper")
    print("=" * 70)
    
    # Scrape programs
    programs = scraper.scrape_all(queries, max_per_query=20)
    
    # Save to JSON
    import os
    output_file = "/app/data/grants/foerderdatenbank.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(programs, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print(f"✅ Scraping complete!")
    print(f"📊 Total programs scraped: {len(programs)}")
    print(f"💾 Saved to: {output_file}")
    print("=" * 70)
    
    # Print sample
    if programs:
        print("\n📋 Sample program:")
        sample = programs[0]
        print(f"Title: {sample['title']}")
        print(f"URL: {sample['url']}")
        print(f"Who: {sample.get('who_is_funded', 'N/A')}")
        print(f"What: {sample.get('what_is_funded', 'N/A')}")
        print(f"Description: {sample.get('description', 'N/A')[:200]}...")


if __name__ == "__main__":
    main()

