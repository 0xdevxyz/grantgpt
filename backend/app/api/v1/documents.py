from fastapi import APIRouter, HTTPException, Response, Depends, BackgroundTasks, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
import os

from app.core.database import get_db
from app.models.document import Document as DocumentModel, DocumentFormat, DocumentType
from app.models.application import Application as ApplicationModel
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.tasks.application_tasks import generate_document_task
from app.core.config import settings

router = APIRouter()


# Schemas
class DocumentGenerate(BaseModel):
    format: DocumentFormat = DocumentFormat.PDF
    document_type: Optional[DocumentType] = DocumentType.FULL_APPLICATION


class DocumentResponse(BaseModel):
    id: UUID
    application_id: UUID
    document_type: DocumentType
    format: DocumentFormat
    filename: str
    file_size: Optional[int]
    generated_by_ai: bool
    version: int
    created_at: datetime
    download_url: str
    
    class Config:
        from_attributes = True


@router.post("/applications/{application_id}/generate", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_document(
    application_id: UUID,
    params: DocumentGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a document for an application
    
    Uses AI to generate and format the document in the requested format.
    Generates asynchronously in background.
    """
    # Check if application exists and belongs to user
    application = db.query(ApplicationModel).filter(
        and_(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if document already exists
    existing_doc = db.query(DocumentModel).filter(
        and_(
            DocumentModel.application_id == application_id,
            DocumentModel.document_type == params.document_type,
            DocumentModel.format == params.format,
            DocumentModel.is_latest == True
        )
    ).first()
    
    if existing_doc:
        # Return existing document
        existing_doc.download_url = f"/api/v1/documents/{existing_doc.id}/download"
        return existing_doc
    
    # Create document record
    filename = f"antrag_{application.project_title[:30]}_{params.format.value}.{params.format.value}"
    file_path = f"storage/documents/{application_id}/{filename}"
    
    document = DocumentModel(
        application_id=application_id,
        document_type=params.document_type,
        format=params.format,
        filename=filename,
        file_path=file_path,
        generated_by_ai=True,
        version=1
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Trigger background generation
    background_tasks.add_task(
        generate_document_task.delay,
        str(application_id),
        str(document.id),
        params.format.value
    )
    
    document.download_url = f"/api/v1/documents/{document.id}/download"
    return document


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_info(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get metadata about a document"""
    document = db.query(DocumentModel).join(ApplicationModel).filter(
        and_(
            DocumentModel.id == document_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document.download_url = f"/api/v1/documents/{document.id}/download"
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a generated document"""
    document = db.query(DocumentModel).join(ApplicationModel).filter(
        and_(
            DocumentModel.id == document_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if file exists
    file_path = os.path.join(os.getcwd(), document.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found. It may still be generating."
        )
    
    # Return file
    media_type = "application/pdf" if document.format == DocumentFormat.PDF else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=document.filename,
        headers={"Content-Disposition": f"attachment; filename={document.filename}"}
    )


@router.get("/applications/{application_id}/documents", response_model=List[DocumentResponse])
async def list_application_documents(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for an application"""
    # Check if application exists and belongs to user
    application = db.query(ApplicationModel).filter(
        and_(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    documents = db.query(DocumentModel).filter(
        DocumentModel.application_id == application_id
    ).order_by(DocumentModel.created_at.desc()).all()
    
    for doc in documents:
        doc.download_url = f"/api/v1/documents/{doc.id}/download"
    
    return documents


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(DocumentModel).join(ApplicationModel).filter(
        and_(
            DocumentModel.id == document_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from storage
    file_path = os.path.join(os.getcwd(), document.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return None


