"""
Payment-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"

class PlanType(str, Enum):
    STARTER = "starter"
    GROWTH = "growth" 
    ENTERPRISE = "enterprise"

class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"

class CheckoutRequest(BaseModel):
    """Request schema for creating checkout sessions"""
    # Customer information
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str = Field(..., min_length=7, max_length=25, description="Phone number (7-25 characters)")
    company: Optional[str] = Field(None, max_length=100)

    # Plan selection
    plan: PlanType
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    add_ons: List[str] = Field(default_factory=list)

    # Payment provider selection
    payment_provider: Optional[PaymentProvider] = PaymentProvider.STRIPE

    # Billing information (for reference, not processed directly)
    billing_info: Optional[Dict[str, Any]] = None

    # Bank transfer information (for ACH payments)
    bank_info: Optional[Dict[str, Any]] = None

    # Preferences
    save_card: bool = False
    accept_policies: bool = Field(..., description="Must accept terms and policies")

class CheckoutResponse(BaseModel):
    """Response schema for checkout session creation"""
    success: bool
    checkout_url: Optional[str] = None
    session_id: Optional[str] = None
    provider: Optional[str] = None
    error: Optional[str] = None

class WebhookEvent(BaseModel):
    """Schema for webhook event processing"""
    event_type: str
    processed: bool
    action: Optional[str] = None
    session_id: Optional[str] = None
    subscription_id: Optional[str] = None
    customer_email: Optional[str] = None
    plan_id: Optional[str] = None
    billing_cycle: Optional[str] = None
    add_ons: List[str] = Field(default_factory=list)
    amount_paid: Optional[float] = None
    error: Optional[str] = None