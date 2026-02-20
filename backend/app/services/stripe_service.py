"""
Stripe Payment Service
Handles Success-Fee billing using Stripe Connect.
"""

import os
import logging
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import Stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe not installed - payment features disabled")


class PaymentStatus(Enum):
    """Payment status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class SuccessFeePayment:
    """Represents a success fee payment."""
    id: str
    user_id: str
    application_id: str
    grant_name: str
    approved_amount: float
    fee_percentage: float
    fee_amount: float
    status: PaymentStatus
    stripe_payment_intent_id: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]


class StripeService:
    """
    Stripe service for handling Success-Fee payments.
    
    Features:
    - Customer management
    - Payment intent creation for success fees
    - Invoice generation
    - Webhook handling
    """
    
    # Fee percentages by subscription tier
    FEE_PERCENTAGES = {
        "tier_1": 0.25,  # 25% for basic tier
        "tier_2": 0.20,  # 20% for hybrid tier
        "tier_3": 0.15,  # 15% for enterprise tier
    }
    
    # Minimum fee amounts
    MIN_FEE_AMOUNT = 500  # 500 EUR minimum
    MAX_FEE_AMOUNT = 50000  # 50,000 EUR maximum
    
    def __init__(self, api_key: str = None, webhook_secret: str = None):
        """
        Initialize Stripe service.
        
        Args:
            api_key: Stripe API key
            webhook_secret: Stripe webhook signing secret
        """
        self.api_key = api_key or os.getenv('STRIPE_API_KEY')
        self.webhook_secret = webhook_secret or os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if STRIPE_AVAILABLE and self.api_key:
            stripe.api_key = self.api_key
            logger.info("Stripe service initialized")
        else:
            logger.warning("Stripe service running in mock mode")
    
    def calculate_success_fee(
        self,
        approved_amount: float,
        subscription_tier: str = "tier_1"
    ) -> Dict:
        """
        Calculate success fee based on approved funding amount.
        
        Args:
            approved_amount: Amount of funding approved (EUR)
            subscription_tier: User's subscription tier
            
        Returns:
            Dict with fee calculation details
        """
        fee_percentage = self.FEE_PERCENTAGES.get(subscription_tier, 0.25)
        raw_fee = approved_amount * fee_percentage
        
        # Apply min/max limits
        fee_amount = max(self.MIN_FEE_AMOUNT, min(raw_fee, self.MAX_FEE_AMOUNT))
        
        return {
            "approved_amount": approved_amount,
            "fee_percentage": fee_percentage,
            "fee_percentage_display": f"{fee_percentage * 100:.0f}%",
            "raw_fee": raw_fee,
            "fee_amount": fee_amount,
            "min_applied": raw_fee < self.MIN_FEE_AMOUNT,
            "max_applied": raw_fee > self.MAX_FEE_AMOUNT,
            "currency": "eur"
        }
    
    async def create_customer(
        self,
        user_id: str,
        email: str,
        company_name: str,
        metadata: Dict = None
    ) -> Optional[str]:
        """
        Create or get existing Stripe customer.
        
        Args:
            user_id: Internal user ID
            email: Customer email
            company_name: Company name
            metadata: Additional metadata
            
        Returns:
            Stripe customer ID
        """
        if not STRIPE_AVAILABLE or not self.api_key:
            logger.warning("Stripe not available - returning mock customer")
            return f"cus_mock_{user_id}"
        
        try:
            # Check for existing customer
            existing = stripe.Customer.list(email=email, limit=1)
            if existing.data:
                return existing.data[0].id
            
            # Create new customer
            customer = stripe.Customer.create(
                email=email,
                name=company_name,
                metadata={
                    "user_id": user_id,
                    **(metadata or {})
                }
            )
            
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {e}")
            return None
    
    async def create_success_fee_payment(
        self,
        customer_id: str,
        application_id: str,
        grant_name: str,
        approved_amount: float,
        subscription_tier: str = "tier_1",
        metadata: Dict = None
    ) -> Optional[Dict]:
        """
        Create a payment intent for success fee.
        
        Args:
            customer_id: Stripe customer ID
            application_id: Application ID
            grant_name: Name of the grant
            approved_amount: Approved funding amount
            subscription_tier: User's subscription tier
            metadata: Additional metadata
            
        Returns:
            Payment intent details or None
        """
        fee_calc = self.calculate_success_fee(approved_amount, subscription_tier)
        fee_amount_cents = int(fee_calc["fee_amount"] * 100)
        
        if not STRIPE_AVAILABLE or not self.api_key:
            logger.warning("Stripe not available - returning mock payment")
            return {
                "payment_intent_id": f"pi_mock_{application_id}",
                "client_secret": f"secret_mock_{application_id}",
                "amount": fee_calc["fee_amount"],
                "currency": "eur",
                "status": "requires_payment_method"
            }
        
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=fee_amount_cents,
                currency="eur",
                customer=customer_id,
                description=f"Success Fee: {grant_name}",
                metadata={
                    "application_id": application_id,
                    "grant_name": grant_name,
                    "approved_amount": str(approved_amount),
                    "fee_percentage": str(fee_calc["fee_percentage"]),
                    "type": "success_fee",
                    **(metadata or {})
                },
                automatic_payment_methods={"enabled": True}
            )
            
            logger.info(f"Created payment intent: {payment_intent.id}")
            
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": fee_calc["fee_amount"],
                "amount_cents": fee_amount_cents,
                "currency": "eur",
                "status": payment_intent.status,
                "fee_details": fee_calc
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            return None
    
    async def create_invoice(
        self,
        customer_id: str,
        application_id: str,
        grant_name: str,
        approved_amount: float,
        subscription_tier: str = "tier_1",
        due_days: int = 30
    ) -> Optional[Dict]:
        """
        Create an invoice for success fee.
        
        Args:
            customer_id: Stripe customer ID
            application_id: Application ID
            grant_name: Name of the grant
            approved_amount: Approved funding amount
            subscription_tier: User's subscription tier
            due_days: Days until invoice is due
            
        Returns:
            Invoice details or None
        """
        fee_calc = self.calculate_success_fee(approved_amount, subscription_tier)
        fee_amount_cents = int(fee_calc["fee_amount"] * 100)
        
        if not STRIPE_AVAILABLE or not self.api_key:
            logger.warning("Stripe not available - returning mock invoice")
            return {
                "invoice_id": f"inv_mock_{application_id}",
                "invoice_url": f"https://example.com/invoice/{application_id}",
                "amount": fee_calc["fee_amount"],
                "status": "draft"
            }
        
        try:
            # Create invoice item
            invoice_item = stripe.InvoiceItem.create(
                customer=customer_id,
                amount=fee_amount_cents,
                currency="eur",
                description=f"Success Fee für {grant_name} (Förderhöhe: {approved_amount:,.2f}€)",
                metadata={
                    "application_id": application_id,
                    "type": "success_fee"
                }
            )
            
            # Create invoice
            invoice = stripe.Invoice.create(
                customer=customer_id,
                collection_method="send_invoice",
                days_until_due=due_days,
                auto_advance=True,
                metadata={
                    "application_id": application_id,
                    "grant_name": grant_name,
                    "type": "success_fee"
                }
            )
            
            # Finalize invoice
            invoice = stripe.Invoice.finalize_invoice(invoice.id)
            
            logger.info(f"Created invoice: {invoice.id}")
            
            return {
                "invoice_id": invoice.id,
                "invoice_number": invoice.number,
                "invoice_url": invoice.hosted_invoice_url,
                "invoice_pdf": invoice.invoice_pdf,
                "amount": fee_calc["fee_amount"],
                "status": invoice.status,
                "due_date": invoice.due_date,
                "fee_details": fee_calc
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating invoice: {e}")
            return None
    
    async def get_payment_status(self, payment_intent_id: str) -> Optional[Dict]:
        """
        Get status of a payment intent.
        
        Args:
            payment_intent_id: Stripe payment intent ID
            
        Returns:
            Payment status details
        """
        if not STRIPE_AVAILABLE or not self.api_key:
            return {"status": "mock", "id": payment_intent_id}
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount / 100,
                "currency": payment_intent.currency,
                "created": payment_intent.created,
                "metadata": payment_intent.metadata
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment: {e}")
            return None
    
    def verify_webhook(self, payload: bytes, signature: str) -> Optional[Dict]:
        """
        Verify and parse Stripe webhook event.
        
        Args:
            payload: Raw request body
            signature: Stripe signature header
            
        Returns:
            Parsed event or None if invalid
        """
        if not STRIPE_AVAILABLE or not self.webhook_secret:
            logger.warning("Webhook verification not available")
            return None
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
            
        except (stripe.error.SignatureVerificationError, ValueError) as e:
            logger.error(f"Webhook verification failed: {e}")
            return None
    
    async def handle_webhook_event(self, event: Dict) -> Dict:
        """
        Handle Stripe webhook event.
        
        Args:
            event: Parsed Stripe event
            
        Returns:
            Processing result
        """
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        handlers = {
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "payment_intent.payment_failed": self._handle_payment_failed,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return await handler(data)
        
        logger.info(f"Unhandled webhook event: {event_type}")
        return {"handled": False, "event_type": event_type}
    
    async def _handle_payment_succeeded(self, data: Dict) -> Dict:
        """Handle successful payment."""
        application_id = data.get("metadata", {}).get("application_id")
        logger.info(f"Payment succeeded for application: {application_id}")
        
        # TODO: Update application status in database
        # TODO: Send confirmation email
        
        return {
            "handled": True,
            "event_type": "payment_intent.succeeded",
            "application_id": application_id,
            "amount": data.get("amount", 0) / 100
        }
    
    async def _handle_payment_failed(self, data: Dict) -> Dict:
        """Handle failed payment."""
        application_id = data.get("metadata", {}).get("application_id")
        logger.warning(f"Payment failed for application: {application_id}")
        
        # TODO: Update application status
        # TODO: Send notification email
        
        return {
            "handled": True,
            "event_type": "payment_intent.payment_failed",
            "application_id": application_id,
            "error": data.get("last_payment_error", {}).get("message")
        }
    
    async def _handle_invoice_paid(self, data: Dict) -> Dict:
        """Handle paid invoice."""
        application_id = data.get("metadata", {}).get("application_id")
        logger.info(f"Invoice paid for application: {application_id}")
        
        return {
            "handled": True,
            "event_type": "invoice.paid",
            "application_id": application_id,
            "invoice_id": data.get("id"),
            "amount": data.get("amount_paid", 0) / 100
        }
    
    async def _handle_invoice_payment_failed(self, data: Dict) -> Dict:
        """Handle failed invoice payment."""
        application_id = data.get("metadata", {}).get("application_id")
        logger.warning(f"Invoice payment failed for application: {application_id}")
        
        return {
            "handled": True,
            "event_type": "invoice.payment_failed",
            "application_id": application_id,
            "invoice_id": data.get("id")
        }


# Global service instance
stripe_service = StripeService()
