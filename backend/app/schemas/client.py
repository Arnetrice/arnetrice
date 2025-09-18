"""
Client submission-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ClientSubmissionBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    plan: str
    payment_frequency: Optional[str] = "monthly"
    add_ons: Optional[str] = None
    needs_requirements: Optional[str] = None
    save_card: Optional[bool] = False
    accept_policies: bool

class ClientSubmissionCreate(ClientSubmissionBase):
    pass

class ClientSubmissionUpdate(BaseModel):
    stripe_session_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    payment_status: Optional[str] = None
    subscription_status: Optional[str] = None
    amount: Optional[Decimal] = None
    setup_fee_amount: Optional[Decimal] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    is_processed: Optional[bool] = None

class ClientSubmission(ClientSubmissionBase):
    id: int
    stripe_session_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    payment_status: str
    subscription_status: str
    amount: Optional[Decimal] = None
    setup_fee_amount: Optional[Decimal] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_processed: bool
    
    class Config:
        from_attributes = True

