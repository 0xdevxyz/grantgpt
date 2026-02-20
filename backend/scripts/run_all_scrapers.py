"""
FörderScout - Run All Scrapers
Main script to run all funding program scrapers and combine results.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scraper import ALL_SCRAPERS, TIER1_SCRAPERS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Output directory
OUTPUT_DIR = "/opt/projects/saas-project-8/backend/data/grants"


def run_scraper(scraper_name: str, save_individual: bool = True) -> List[Dict]:
    """
    Run a single scraper and return results.
    
    Args:
        scraper_name: Name of the scraper to run
        save_individual: Whether to save results to individual JSON file
        
    Returns:
        List of scraped programs
    """
    if scraper_name not in ALL_SCRAPERS:
        logger.error(f"Unknown scraper: {scraper_name}")
        return []
    
    scraper_class = ALL_SCRAPERS[scraper_name]
    scraper = scraper_class()
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Running {scraper_name.upper()} scraper")
    logger.info(f"{'='*70}")
    
    try:
        if save_individual:
            save_path = os.path.join(OUTPUT_DIR, f"{scraper_name}.json")
        else:
            save_path = None
        
        programs = scraper.run(save_path=save_path)
        logger.info(f"✅ {scraper_name}: {len(programs)} programs scraped")
        return programs
        
    except Exception as e:
        logger.error(f"❌ {scraper_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def run_all_scrapers(scrapers: List[str] = None, tier: int = None) -> List[Dict]:
    """
    Run multiple scrapers and combine results.
    
    Args:
        scrapers: List of scraper names to run (default: all)
        tier: Run only scrapers of this tier (1 or 2)
        
    Returns:
        Combined list of all scraped programs
    """
    if tier == 1:
        scrapers_to_run = TIER1_SCRAPERS
    elif tier == 2:
        from scripts.scraper import TIER2_SCRAPERS
        scrapers_to_run = TIER2_SCRAPERS
    elif scrapers:
        scrapers_to_run = scrapers
    else:
        scrapers_to_run = list(ALL_SCRAPERS.keys())
    
    all_programs = []
    stats = {}
    
    logger.info(f"\n🚀 FörderScout Scraper - Starting")
    logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📋 Scrapers to run: {', '.join(scrapers_to_run)}")
    
    for scraper_name in scrapers_to_run:
        programs = run_scraper(scraper_name, save_individual=True)
        all_programs.extend(programs)
        stats[scraper_name] = len(programs)
    
    # Save combined results
    combined_path = os.path.join(OUTPUT_DIR, "all_programs.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(all_programs, f, ensure_ascii=False, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 SCRAPING SUMMARY")
    print("="*70)
    for name, count in stats.items():
        print(f"  {name:20} : {count:5} programs")
    print("-"*70)
    print(f"  {'TOTAL':20} : {len(all_programs):5} programs")
    print("="*70)
    print(f"💾 Combined results saved to: {combined_path}")
    
    return all_programs


def deduplicate_programs(programs: List[Dict]) -> List[Dict]:
    """
    Remove duplicate programs based on URL.
    
    Args:
        programs: List of programs to deduplicate
        
    Returns:
        Deduplicated list
    """
    seen_urls = set()
    unique_programs = []
    
    for program in programs:
        url = program.get('url_offiziell', '') or program.get('url', '')
        if url and url not in seen_urls:
            unique_programs.append(program)
            seen_urls.add(url)
        elif not url:
            # Keep programs without URLs (based on name)
            name = program.get('name', '')
            if name and name not in seen_urls:
                unique_programs.append(program)
                seen_urls.add(name)
    
    logger.info(f"Deduplication: {len(programs)} → {len(unique_programs)} programs")
    return unique_programs


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='FörderScout - Funding Program Scraper')
    parser.add_argument(
        '--scrapers', '-s',
        nargs='+',
        choices=list(ALL_SCRAPERS.keys()),
        help='Specific scrapers to run'
    )
    parser.add_argument(
        '--tier', '-t',
        type=int,
        choices=[1, 2],
        help='Run scrapers by tier (1=daily, 2=weekly)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available scrapers'
    )
    parser.add_argument(
        '--deduplicate', '-d',
        action='store_true',
        help='Deduplicate combined results'
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📋 Available Scrapers:")
        print("-"*50)
        for name, scraper_class in ALL_SCRAPERS.items():
            scraper = scraper_class()
            print(f"  {name:20} - Tier {scraper.TIER} ({scraper.SOURCE_NAME})")
        print("-"*50)
        return
    
    # Run scrapers
    programs = run_all_scrapers(
        scrapers=args.scrapers,
        tier=args.tier
    )
    
    # Optionally deduplicate
    if args.deduplicate and programs:
        programs = deduplicate_programs(programs)
        
        # Save deduplicated results
        dedup_path = os.path.join(OUTPUT_DIR, "all_programs_unique.json")
        with open(dedup_path, 'w', encoding='utf-8') as f:
            json.dump(programs, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 Deduplicated results saved to: {dedup_path}")


if __name__ == "__main__":
    main()
