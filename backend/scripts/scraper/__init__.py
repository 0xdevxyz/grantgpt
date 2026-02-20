"""
FörderScout Scrapers Package
Collection of scrapers for German, Austrian, and Swiss funding programs.
"""

from .base_scraper import BaseScraper
from .foerderdatenbank_scraper import FoerderdatenbankScraper
from .bafa_scraper import BAFAScraper
from .kfw_scraper import KfWScraper
from .sab_scraper import SABScraper
from .bmwk_scraper import BMWKScraper
from .godigital_scraper import GoDigitalScraper
from .program_extractor import ProgramExtractor

# All available scrapers
ALL_SCRAPERS = {
    'foerderdatenbank': FoerderdatenbankScraper,
    'bafa': BAFAScraper,
    'kfw': KfWScraper,
    'sab': SABScraper,
    'bmwk': BMWKScraper,
    'godigital': GoDigitalScraper,
}

# Tier 1 scrapers (daily)
TIER1_SCRAPERS = ['bafa', 'kfw', 'sab', 'bmwk', 'godigital', 'foerderdatenbank']

# Tier 2 scrapers (weekly) - to be added
TIER2_SCRAPERS = []

__all__ = [
    'BaseScraper',
    'FoerderdatenbankScraper',
    'BAFAScraper',
    'KfWScraper',
    'SABScraper',
    'BMWKScraper',
    'GoDigitalScraper',
    'ProgramExtractor',
    'ALL_SCRAPERS',
    'TIER1_SCRAPERS',
    'TIER2_SCRAPERS',
]
