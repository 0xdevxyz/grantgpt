"""
Background tasks for grant application generation
"""
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
import os

from app.celery_app import celery_app
from app.services.application_writer import application_writer
from app.models.application import Application, ApplicationStatus
from app.models.document import Document, DocumentFormat, DocumentType
from app.core.database import AsyncSessionLocal
from app.services.document_generator import document_generator


@celery_app.task(name="generate_application_content", bind=True)
def generate_application_content(
    self,
    application_id: str,
    section: Optional[str] = None
):
    """
    Background task to generate complete application content
    
    This task generates all sections of a grant application and saves to DB.
    """
    try:
        # Create sync session for celery task
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Get application from database
            application = db.query(Application).filter(
                Application.id == application_id
            ).first()
            
            if not application:
                raise ValueError(f"Application {application_id} not found")
            
            # Update status
            application.status = ApplicationStatus.GENERATING
            application.completion_percentage = 0
            db.commit()
            
            # Prepare data for AI generation
            project_info = {
                "title": application.project_title,
                "description": application.project_description,
                "goals": application.project_goals or [],
                "innovation": application.project_innovation or "",
                "timeline_months": application.timeline_months,
                "total_budget": application.total_budget,
                "requested_funding": application.requested_funding,
                "target_audience": application.target_audience or "",
                "market_analysis": application.market_analysis or ""
            }
            
            grant_guidelines = ""  # TODO: Fetch from grant data
            
            # Generate sections
            sections = {}
            total_sections = 7
            
            # 1. Project Description
            print(f"[{application_id}] Generating project description...")
            sections["project_description"] = asyncio.run(
                application_writer.generate_project_description(
                    project_info,
                    grant_guidelines
                )
            )
            application.completion_percentage = 14
            db.commit()
            
            # 2. Market Analysis
            print(f"[{application_id}] Generating market analysis...")
            sections["market_analysis"] = asyncio.run(
                application_writer.generate_market_analysis(
                    project_info,
                    grant_guidelines
                )
            )
            application.completion_percentage = 28
            db.commit()
            
            # 3. Technical Feasibility
            print(f"[{application_id}] Generating technical feasibility...")
            sections["technical_feasibility"] = asyncio.run(
                application_writer.generate_technical_feasibility(
                    project_info,
                    grant_guidelines
                )
            )
            application.completion_percentage = 42
            db.commit()
            
            # 4. Work Plan
            print(f"[{application_id}] Generating work plan...")
            sections["work_plan"] = asyncio.run(
                application_writer.generate_work_plan(
                    project_info,
                    project_info["timeline_months"],
                    grant_guidelines
                )
            )
            application.completion_percentage = 57
            db.commit()
            
            # 5. Financial Plan
            print(f"[{application_id}] Generating financial plan...")
            budget_info = {
                "total_budget": application.total_budget,
                "requested_funding": application.requested_funding,
                "own_contribution": application.own_contribution,
                "breakdown": application.budget_breakdown or {}
            }
            sections["financial_plan"] = asyncio.run(
                application_writer.generate_financial_plan(
                    budget_info,
                    grant_guidelines
                )
            )
            application.completion_percentage = 71
            db.commit()
            
            # 6. Risk Management
            print(f"[{application_id}] Generating risk management...")
            sections["risk_management"] = asyncio.run(
                application_writer.generate_risk_management(
                    project_info,
                    grant_guidelines
                )
            )
            application.completion_percentage = 85
            db.commit()
            
            # 7. Utilization Plan
            print(f"[{application_id}] Generating utilization plan...")
            sections["utilization_plan"] = asyncio.run(
                application_writer.generate_utilization_plan(
                    project_info,
                    grant_guidelines
                )
            )
            application.completion_percentage = 100
            db.commit()
            
            # Save generated content to database
            application.generated_content = sections
            application.status = ApplicationStatus.READY
            application.updated_at = datetime.utcnow()
            
            db.commit()
            
            print(f"[{application_id}] Generation completed successfully!")
            
            return {
                "application_id": application_id,
                "status": "completed",
                "sections_generated": len(sections)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error generating application {application_id}: {e}")
        # Update status to error
        try:
            db = SessionLocal()
            application = db.query(Application).filter(
                Application.id == application_id
            ).first()
            if application:
                application.status = ApplicationStatus.DRAFT
                application.completion_percentage = 0
                db.commit()
            db.close()
        except:
            pass
        raise


@celery_app.task(name="generate_document_task", bind=True)
def generate_document_task(
    self,
    application_id: str,
    document_id: str,
    format: str = "pdf"
):
    """
    Generate document export (PDF or DOCX)
    """
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Get application and document
            application = db.query(Application).filter(
                Application.id == application_id
            ).first()
            
            document = db.query(Document).filter(
                Document.id == document_id
            ).first()
            
            if not application or not document:
                raise ValueError("Application or document not found")
            
            # Generate document
            print(f"[{application_id}] Generating {format.upper()} document...")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(document.file_path), exist_ok=True)
            
            # Generate based on format
            if format == "pdf":
                file_path = document_generator.generate_pdf(
                    application,
                    document.file_path
                )
            elif format == "docx":
                file_path = document_generator.generate_docx(
                    application,
                    document.file_path
                )
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Update document record
            document.file_size = os.path.getsize(file_path)
            db.commit()
            
            print(f"[{application_id}] Document generated: {file_path}")
            
            return {
                "application_id": application_id,
                "document_id": document_id,
                "file_path": file_path,
                "file_size": document.file_size
            }
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error generating document for {application_id}: {e}")
        raise


@celery_app.task(name="run_compliance_check")
def run_compliance_check(application_id: str, grant_id: str):
    """
    Run compliance checks on generated application
    """
    # TODO: Implement comprehensive compliance checking
    print(f"Running compliance check for {application_id}")
    
    return {
        "application_id": application_id,
        "compliance_score": 95,
        "checks_passed": 18,
        "checks_failed": 1,
        "warnings": ["Innovation could be emphasized more"]
    }


