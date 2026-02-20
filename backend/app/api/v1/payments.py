"""
Payment API Routes
Handles success fee payments and billing.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_active_user
from app.services.stripe_service import stripe_service

router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class FeeCalculationRequest(BaseModel):
    """Request to calculate success fee."""
    approved_amount: float = Field(..., gt=0, description="Approved funding amount in EUR")


class FeeCalculationResponse(BaseModel):
    """Success fee calculation response."""
    approved_amount: float
    fee_percentage: float
    fee_percentage_display: str
    fee_amount: float
    currency: str = "EUR"
    min_applied: bool
    max_applied: bool


class CreatePaymentRequest(BaseModel):
    """Request to create a payment for success fee."""
    application_id: str
    grant_name: str
    approved_amount: float = Field(..., gt=0)


class PaymentResponse(BaseModel):
    """Payment creation response."""
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str
    status: str


class CreateInvoiceRequest(BaseModel):
    """Request to create an invoice for success fee."""
    application_id: str
    grant_name: str
    approved_amount: float = Field(..., gt=0)
    due_days: int = Field(default=30, ge=1, le=90)


class InvoiceResponse(BaseModel):
    """Invoice creation response."""
    invoice_id: str
    invoice_number: Optional[str]
    invoice_url: str
    invoice_pdf: Optional[str]
    amount: float
    status: str
    due_date: Optional[int]


class PaymentStatusResponse(BaseModel):
    """Payment status response."""
    id: str
    status: str
    amount: float
    currency: str


# =============================================================================
# API Routes
# =============================================================================

@router.post("/calculate-fee", response_model=FeeCalculationResponse)
async def calculate_success_fee(
    request: FeeCalculationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate success fee for a given approved amount.
    
    The fee is calculated based on:
    - User's subscription tier (determines percentage)
    - Approved funding amount
    - Minimum and maximum fee limits
    """
    fee_calc = stripe_service.calculate_success_fee(
        approved_amount=request.approved_amount,
        subscription_tier=current_user.subscription_tier.value
    )
    
    return FeeCalculationResponse(
        approved_amount=fee_calc["approved_amount"],
        fee_percentage=fee_calc["fee_percentage"],
        fee_percentage_display=fee_calc["fee_percentage_display"],
        fee_amount=fee_calc["fee_amount"],
        currency="EUR",
        min_applied=fee_calc["min_applied"],
        max_applied=fee_calc["max_applied"]
    )


@router.post("/create-payment", response_model=PaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment intent for success fee.
    
    This creates a Stripe PaymentIntent that can be used
    to collect the success fee when funding is approved.
    """
    # Get or create Stripe customer
    customer_id = await stripe_service.create_customer(
        user_id=str(current_user.id),
        email=current_user.email,
        company_name=current_user.company_name
    )
    
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment customer"
        )
    
    # Create payment intent
    payment = await stripe_service.create_success_fee_payment(
        customer_id=customer_id,
        application_id=request.application_id,
        grant_name=request.grant_name,
        approved_amount=request.approved_amount,
        subscription_tier=current_user.subscription_tier.value,
        metadata={
            "user_id": str(current_user.id),
            "company_name": current_user.company_name
        }
    )
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )
    
    return PaymentResponse(
        payment_intent_id=payment["payment_intent_id"],
        client_secret=payment["client_secret"],
        amount=payment["amount"],
        currency=payment["currency"],
        status=payment["status"]
    )


@router.post("/create-invoice", response_model=InvoiceResponse)
async def create_invoice(
    request: CreateInvoiceRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an invoice for success fee.
    
    This creates a Stripe Invoice that will be sent to the customer
    for payment of the success fee.
    """
    # Get or create Stripe customer
    customer_id = await stripe_service.create_customer(
        user_id=str(current_user.id),
        email=current_user.email,
        company_name=current_user.company_name
    )
    
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create invoice customer"
        )
    
    # Create invoice
    invoice = await stripe_service.create_invoice(
        customer_id=customer_id,
        application_id=request.application_id,
        grant_name=request.grant_name,
        approved_amount=request.approved_amount,
        subscription_tier=current_user.subscription_tier.value,
        due_days=request.due_days
    )
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create invoice"
        )
    
    return InvoiceResponse(
        invoice_id=invoice["invoice_id"],
        invoice_number=invoice.get("invoice_number"),
        invoice_url=invoice["invoice_url"],
        invoice_pdf=invoice.get("invoice_pdf"),
        amount=invoice["amount"],
        status=invoice["status"],
        due_date=invoice.get("due_date")
    )


@router.get("/payment/{payment_intent_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_intent_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get status of a payment intent.
    """
    status_info = await stripe_service.get_payment_status(payment_intent_id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentStatusResponse(
        id=status_info["id"],
        status=status_info["status"],
        amount=status_info["amount"],
        currency=status_info["currency"]
    )


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    
    This endpoint receives events from Stripe for
    payment status updates, invoice events, etc.
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature"
        )
    
    # Verify and parse event
    event = stripe_service.verify_webhook(payload, signature)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    
    # Handle event
    result = await stripe_service.handle_webhook_event(event)
    
    return {"received": True, "result": result}


@router.get("/fee-tiers")
async def get_fee_tiers():
    """
    Get available fee tiers and their percentages.
    
    Returns the fee structure for different subscription levels.
    """
    return {
        "tiers": [
            {
                "tier": "tier_1",
                "name": "Basic / Success-Fee",
                "fee_percentage": 25,
                "monthly_fee": 0,
                "description": "Keine monatlichen Kosten. 25% Success-Fee bei Bewilligung."
            },
            {
                "tier": "tier_2",
                "name": "Hybrid",
                "fee_percentage": 20,
                "monthly_fee": 199,
                "description": "199€/Monat + reduzierte 20% Success-Fee."
            },
            {
                "tier": "tier_3",
                "name": "Enterprise",
                "fee_percentage": 15,
                "monthly_fee": 499,
                "description": "499€/Monat + nur 15% Success-Fee. Priority Support."
            }
        ],
        "min_fee": 500,
        "max_fee": 50000,
        "currency": "EUR"
    }
