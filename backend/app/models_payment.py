from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric, Enum, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class PaymentProvider(enum.Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class SubscriptionStatus(enum.Enum):
    INACTIVE = "inactive"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"
    PAUSED = "paused"

class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, nullable=True)

    # Basic Information
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(200), nullable=True)

    # Billing Address
    billing_address_line1 = Column(String(200), nullable=True)
    billing_address_line2 = Column(String(200), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(100), nullable=True)
    billing_postal_code = Column(String(20), nullable=True)
    billing_country = Column(String(2), nullable=True)

    # Tax Information
    tax_id = Column(String(100), nullable=True)
    tax_exempt = Column(Boolean, default=False)
    tax_rate = Column(Numeric(5, 4), default=0)

    # Customer Status
    status = Column(String(50), default="active")
    credit_limit = Column(Numeric(10, 2), nullable=True)
    balance = Column(Numeric(10, 2), default=0)

    # Stripe/PayPal IDs
    stripe_customer_id = Column(String(200), nullable=True, unique=True)
    paypal_customer_id = Column(String(200), nullable=True, unique=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    payment_methods = relationship("PaymentMethod", back_populates="customer")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    # Pricing
    base_price = Column(Numeric(10, 2), nullable=False)
    setup_fee = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="USD")

    # Product Type
    is_subscription = Column(Boolean, default=False)
    is_addon = Column(Boolean, default=False)
    billing_cycle = Column(String(20), nullable=True)

    # External IDs
    stripe_product_id = Column(String(200), nullable=True)
    stripe_price_id_monthly = Column(String(200), nullable=True)
    stripe_price_id_annual = Column(String(200), nullable=True)
    stripe_setup_price_id = Column(String(200), nullable=True)
    paypal_plan_id = Column(String(200), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # Metadata
    features = Column(JSON, nullable=True)
    limitations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription_items = relationship("SubscriptionItem", back_populates="product")
    invoice_items = relationship("InvoiceItem", back_populates="product")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # External IDs
    stripe_subscription_id = Column(String(200), nullable=True, unique=True)
    paypal_subscription_id = Column(String(200), nullable=True, unique=True)

    # Subscription Details
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE)
    billing_cycle = Column(String(20), nullable=False)

    # Dates
    start_date = Column(DateTime, nullable=False)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)

    # Pricing
    total_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)

    # Metadata
    custom_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")
    items = relationship("SubscriptionItem", back_populates="subscription", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="subscription")

class SubscriptionItem(Base):
    __tablename__ = "subscription_items"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Item Details
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)

    # External IDs
    stripe_item_id = Column(String(200), nullable=True)
    paypal_item_id = Column(String(200), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="items")
    product = relationship("Product", back_populates="subscription_items")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    # Payment Details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    provider = Column(Enum(PaymentProvider), nullable=False)

    # External IDs
    stripe_payment_intent_id = Column(String(200), nullable=True)
    stripe_charge_id = Column(String(200), nullable=True)
    paypal_transaction_id = Column(String(200), nullable=True)

    # Payment Method
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    payment_method_type = Column(String(50), nullable=True)

    # Transaction Details
    processed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(String(500), nullable=True)

    # Refund Information
    refunded_amount = Column(Numeric(10, 2), default=0)
    refund_reason = Column(String(500), nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # Metadata
    description = Column(String(500), nullable=True)
    custom_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")
    payment_method = relationship("PaymentMethod")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Method Details
    type = Column(String(50), nullable=False)
    is_default = Column(Boolean, default=False)

    # Card Information (if applicable)
    card_brand = Column(String(50), nullable=True)
    card_last4 = Column(String(4), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)

    # Bank Information (if applicable)
    bank_name = Column(String(100), nullable=True)
    bank_last4 = Column(String(4), nullable=True)

    # External IDs
    stripe_payment_method_id = Column(String(200), nullable=True)
    paypal_billing_agreement_id = Column(String(200), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    verified_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="payment_methods")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    # Invoice Details
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)

    # Amounts
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0)
    balance_due = Column(Numeric(10, 2), nullable=False)

    # External IDs
    stripe_invoice_id = Column(String(200), nullable=True)
    paypal_invoice_id = Column(String(200), nullable=True)

    # Communication
    sent_at = Column(DateTime, nullable=True)
    reminder_sent_at = Column(DateTime, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    custom_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    # Item Details
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(Enum(PaymentProvider), nullable=False)
    event_id = Column(String(200), unique=True, nullable=False)
    event_type = Column(String(100), nullable=False)

    # Processing Status
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    failed = Column(Boolean, default=False)
    failure_reason = Column(String(500), nullable=True)
    retry_count = Column(Integer, default=0)

    # Event Data
    payload = Column(JSON, nullable=False)
    response = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_webhook_provider_type', 'provider', 'event_type'),
        Index('idx_webhook_processed', 'processed', 'created_at'),
    )

class PaymentAuditLog(Base):
    __tablename__ = "payment_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)

    # Change Details
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)

    # User Information
    user_id = Column(Integer, nullable=True)
    user_email = Column(String(200), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_created', 'created_at'),
    )