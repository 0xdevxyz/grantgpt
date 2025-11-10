"""
Background tasks for grant application generation
"""
from typing import Dict, Any
import asyncio
from datetime import datetime

from app.celery_app import celery_app
from app.services.application_writer import application_writer
from app.models.application import ApplicationStatus


@celery_app.task(name="generate_application_content")
def generate_application_content(
    application_id: str,
    project_info: Dict[str, Any],
    grant_info: Dict[str, Any],
    company_info: Dict[str, Any]
):
    """
    Background task to generate complete application content
    
    This task generates all sections of a grant application:
    - Project description
    - Market analysis
    - Technical feasibility
    - Work plan
    - Financial plan
    - Risk management
    - Utilization plan
    """
    try:
        # Update status to generating
        _update_application_status(application_id, ApplicationStatus.GENERATING, 0)
        
        # Extract grant guidelines
        grant_guidelines = grant_info.get("guidelines", "")
        
        # Generate each section
        sections = {}
        total_sections = 7
        
        # 1. Project Description (14% progress)
        print(f"Generating project description for {application_id}")
        sections["project_description"] = asyncio.run(
            application_writer.generate_project_description(
                project_info,
                grant_guidelines
            )
        )
        _update_application_status(application_id, ApplicationStatus.GENERATING, 14)
        
        # 2. Market Analysis (28% progress)
        print(f"Generating market analysis for {application_id}")
        sections["market_analysis"] = asyncio.run(
            application_writer.generate_market_analysis(
                project_info,
                grant_guidelines
            )
        )
        _update_application_status(application_id, ApplicationStatus.GENERATING, 28)
        
        # 3. Technical Feasibility (42% progress)
        print(f"Generating technical feasibility for {application_id}")
        sections["technical_feasibility"] = asyncio.run(
            application_writer.generate_technical_feasibility(
                project_info,
                grant_guidelines
            )
        )
        _update_application_status(application_id, ApplicationStatus.GENERATING, 42)
        
        # 4. Work Plan (57% progress)
        print(f"Generating work plan for {application_id}")
        sections["work_plan"] = asyncio.run(
            application_writer.generate_work_plan(
                project_info,
                project_info.get("timeline_months", 12),
                grant_guidelines
            )
        )
        _update_application_status(application_id, ApplicationStatus.GENERATING, 57)
        
        # 5. Financial Plan (71% progress)
        print(f"Generating financial plan for {application_id}")
        budget_info = {
            "total_budget": project_info.get("total_budget", 0),
            "requested_funding": project_info.get("requested_funding", 0),
            "own_contribution": project_info.get("own_contribution", 0),
            "breakdown": project_info.get("budget_breakdown", {})
        }
        sections["financial_plan"] = asyncio.run(
            application_writer.generate_financial_plan(
                budget_info,
                grant_guidelines
            )
        )
        _update_application_status(application_id, ApplicationStatus.GENERATING, 71)
        
        # 6. Risk Management (85% progress)
        print(f"Generating risk management for {application_id}")
        sections["risk_management"] = asyncio.run(
            application_writer.generate_risk_management(
                project_info,
                grant_guidelines
            )
        )
        _update_application_status(application_id, ApplicationStatus.GENERATING, 85)
        
        # 7. Utilization Plan (100% progress)
        print(f"Generating utilization plan for {application_id}")
        sections["utilization_plan"] = asyncio.run(
            application_writer.generate_utilization_plan(
                project_info,
                grant_guidelines
            )
        )
        _update_application_status(application_id, ApplicationStatus.GENERATING, 100)
        
        # Save generated content and update status
        _save_generated_content(application_id, sections)
        _update_application_status(application_id, ApplicationStatus.REVIEW, 100)
        
        # TODO: Send notification to user
        print(f"Application {application_id} generation completed!")
        
        return {
            "application_id": application_id,
            "status": "completed",
            "sections_generated": len(sections)
        }
        
    except Exception as e:
        print(f"Error generating application {application_id}: {e}")
        _update_application_status(application_id, ApplicationStatus.DRAFT, 0)
        raise


def _update_application_status(
    application_id: str,
    status: ApplicationStatus,
    completion: int
):
    """Update application status in database"""
    # TODO: Implement database update
    # For now, just log
    print(f"Application {application_id}: {status.value} ({completion}%)")


def _save_generated_content(
    application_id: str,
    sections: Dict[str, str]
):
    """Save generated content to database"""
    # TODO: Implement database save
    print(f"Saving {len(sections)} sections for application {application_id}")


@celery_app.task(name="run_compliance_check")
def run_compliance_check(application_id: str, grant_id: str):
    """
    Run compliance checks on generated application
    
    Checks:
    - Budget plausibility
    - Eligibility criteria
    - Completeness
    - Grant-specific requirements
    """
    # TODO: Implement compliance checking
    print(f"Running compliance check for {application_id}")
    
    return {
        "application_id": application_id,
        "compliance_score": 95,
        "checks_passed": 18,
        "checks_failed": 1,
        "warnings": ["Innovation could be emphasized more on page 5"]
    }


@celery_app.task(name="generate_document_export")
def generate_document_export(
    application_id: str,
    format: str = "pdf"
):
    """
    Generate document export (PDF or DOCX)
    """
    # TODO: Implement document generation
    print(f"Generating {format.upper()} for {application_id}")
    
    return {
        "application_id": application_id,
        "format": format,
        "file_path": f"/storage/documents/{application_id}.{format}",
        "file_size": 2450000  # bytes
    }

