"""
Scraper Tasks for Celery
Background tasks for automated grant scraping and change detection.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

from app.celery_app import celery_app
from app.services.change_detection import ChangeDetectionService, ChangeType

# Add scripts path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = "/opt/projects/saas-project-8/backend/data/grants"


def get_scraper_class(scraper_name: str):
    """Dynamically import and return scraper class."""
    try:
        from scripts.scraper import ALL_SCRAPERS
        return ALL_SCRAPERS.get(scraper_name)
    except ImportError as e:
        logger.error(f"Failed to import scrapers: {e}")
        return None


@celery_app.task(name="run_scraper", bind=True, max_retries=3)
def run_scraper(self, scraper_name: str, save_to_file: bool = True) -> Dict:
    """
    Run a single scraper and detect changes.
    
    Args:
        scraper_name: Name of the scraper to run (e.g., 'bafa', 'kfw')
        save_to_file: Whether to save results to JSON file
        
    Returns:
        Dict with scraping results and detected changes
    """
    logger.info(f"🚀 Starting scraper task: {scraper_name}")
    
    try:
        scraper_class = get_scraper_class(scraper_name)
        if not scraper_class:
            raise ValueError(f"Unknown scraper: {scraper_name}")
        
        # Initialize scraper and change detection
        scraper = scraper_class()
        change_service = ChangeDetectionService()
        
        # Run scraper
        save_path = os.path.join(DATA_DIR, f"{scraper_name}.json") if save_to_file else None
        programs = scraper.run(save_path=save_path)
        
        # Detect changes
        changes = []
        for program in programs:
            # Check for changes using the program's URL as key
            url = program.get('url_offiziell') or program.get('source_url', '')
            if url:
                change = change_service.detect_change(
                    source_url=url,
                    new_content=json.dumps(program),
                    program_data=program
                )
                if change and change.change_type != ChangeType.NO_CHANGE:
                    changes.append(change_service.to_dict(change))
        
        result = {
            "scraper": scraper_name,
            "programs_found": len(programs),
            "changes_detected": len(changes),
            "changes": changes,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "success"
        }
        
        logger.info(f"✅ Scraper {scraper_name} completed: {len(programs)} programs, {len(changes)} changes")
        return result
        
    except Exception as e:
        logger.error(f"❌ Scraper {scraper_name} failed: {e}")
        
        # Retry if not last attempt
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
        return {
            "scraper": scraper_name,
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat()
        }


@celery_app.task(name="run_tier1_scrapers")
def run_tier1_scrapers() -> Dict:
    """
    Run all Tier-1 scrapers (daily).
    
    Tier-1 sources include:
    - BAFA
    - KfW  
    - SAB Sachsen
    - BMWK
    - go-digital
    - Förderdatenbank
    """
    logger.info("🚀 Starting Tier-1 scraper run (daily)")
    
    try:
        from scripts.scraper import TIER1_SCRAPERS
    except ImportError:
        TIER1_SCRAPERS = ['bafa', 'kfw', 'sab', 'bmwk', 'godigital', 'foerderdatenbank']
    
    results = {
        "tier": 1,
        "started_at": datetime.utcnow().isoformat(),
        "scrapers": {}
    }
    
    total_programs = 0
    total_changes = 0
    
    for scraper_name in TIER1_SCRAPERS:
        try:
            # Run each scraper as subtask
            result = run_scraper.delay(scraper_name, save_to_file=True)
            
            # For now, run synchronously for simplicity
            # In production, use: result = run_scraper(scraper_name, save_to_file=True)
            scraper_result = run_scraper(scraper_name, save_to_file=True)
            
            results["scrapers"][scraper_name] = {
                "status": scraper_result.get("status", "unknown"),
                "programs": scraper_result.get("programs_found", 0),
                "changes": scraper_result.get("changes_detected", 0)
            }
            
            total_programs += scraper_result.get("programs_found", 0)
            total_changes += scraper_result.get("changes_detected", 0)
            
        except Exception as e:
            logger.error(f"Error running {scraper_name}: {e}")
            results["scrapers"][scraper_name] = {
                "status": "failed",
                "error": str(e)
            }
    
    results["completed_at"] = datetime.utcnow().isoformat()
    results["total_programs"] = total_programs
    results["total_changes"] = total_changes
    
    logger.info(f"✅ Tier-1 run completed: {total_programs} programs, {total_changes} changes")
    
    return results


@celery_app.task(name="run_tier2_scrapers")
def run_tier2_scrapers() -> Dict:
    """
    Run all Tier-2 scrapers (weekly).
    
    Tier-2 sources include regional and secondary sources.
    """
    logger.info("🚀 Starting Tier-2 scraper run (weekly)")
    
    try:
        from scripts.scraper import TIER2_SCRAPERS
    except ImportError:
        TIER2_SCRAPERS = []  # To be expanded
    
    if not TIER2_SCRAPERS:
        logger.info("No Tier-2 scrapers configured yet")
        return {"tier": 2, "status": "no_scrapers", "message": "No Tier-2 scrapers configured"}
    
    results = {
        "tier": 2,
        "started_at": datetime.utcnow().isoformat(),
        "scrapers": {}
    }
    
    for scraper_name in TIER2_SCRAPERS:
        try:
            scraper_result = run_scraper(scraper_name, save_to_file=True)
            results["scrapers"][scraper_name] = {
                "status": scraper_result.get("status", "unknown"),
                "programs": scraper_result.get("programs_found", 0),
                "changes": scraper_result.get("changes_detected", 0)
            }
        except Exception as e:
            logger.error(f"Error running {scraper_name}: {e}")
            results["scrapers"][scraper_name] = {"status": "failed", "error": str(e)}
    
    results["completed_at"] = datetime.utcnow().isoformat()
    
    return results


@celery_app.task(name="process_changes")
def process_changes(changes: List[Dict]) -> Dict:
    """
    Process detected changes and queue for review.
    
    Args:
        changes: List of change dictionaries
        
    Returns:
        Processing results
    """
    logger.info(f"Processing {len(changes)} changes")
    
    # Group changes by type
    by_type = {}
    for change in changes:
        change_type = change.get("change_type", "unknown")
        if change_type not in by_type:
            by_type[change_type] = []
        by_type[change_type].append(change)
    
    # High priority: expired programs and deadline changes
    high_priority = (
        by_type.get("expired_program", []) + 
        by_type.get("deadline_changed", [])
    )
    
    # Medium priority: amount and condition changes
    medium_priority = (
        by_type.get("amount_changed", []) +
        by_type.get("conditions_changed", [])
    )
    
    # Low priority: new programs and general updates
    low_priority = (
        by_type.get("new_program", []) +
        by_type.get("updated_program", [])
    )
    
    results = {
        "total_changes": len(changes),
        "by_type": {k: len(v) for k, v in by_type.items()},
        "high_priority": len(high_priority),
        "medium_priority": len(medium_priority),
        "low_priority": len(low_priority),
        "processed_at": datetime.utcnow().isoformat()
    }
    
    # In production: store to database, send notifications
    # For now, just log
    if high_priority:
        logger.warning(f"⚠️ High priority changes detected: {len(high_priority)}")
        for change in high_priority:
            logger.warning(f"  - {change.get('program_name')}: {change.get('description')}")
    
    return results


@celery_app.task(name="update_embeddings")
def update_embeddings(program_ids: List[str] = None) -> Dict:
    """
    Update embeddings for changed programs.
    
    Args:
        program_ids: List of program IDs to update (all if None)
        
    Returns:
        Update results
    """
    logger.info("Updating embeddings for changed programs")
    
    # Import embedding services
    try:
        from app.tasks.grant_tasks import embed_grants
        from scripts.seed_comprehensive_grants import load_grant_files, normalize_grant
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return {"status": "failed", "error": str(e)}
    
    # Load current grants
    grants = load_grant_files()
    
    # Filter by IDs if specified
    if program_ids:
        grants = [g for g in grants if g.get('id') in program_ids]
    
    # Normalize and embed
    normalized = [normalize_grant(g) for g in grants]
    
    # Call embed task
    result = embed_grants(normalized)
    
    return {
        "status": "success",
        "updated": len(normalized),
        "embed_result": result
    }
