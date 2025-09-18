from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(String(300), nullable=True)
    author = Column(String(100), default="Arnetrice Smith")
    published_at = Column(DateTime, default=datetime.utcnow)
    is_published = Column(Boolean, default=True)
    tags = Column(String(200), nullable=True)
    featured_image = Column(String(300), nullable=True)

class Portfolio(Base):
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    client = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    technologies = Column(String(200), nullable=True)
    project_url = Column(String(300), nullable=True)
    github_url = Column(String(300), nullable=True)
    image_url = Column(String(300), nullable=True)
    featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClientSubmission(Base):
    __tablename__ = "client_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    plan = Column(String(50), nullable=False)  # starter, growth, enterprise
    payment_frequency = Column(String(20), default="monthly")  # monthly, annual
    add_ons = Column(String(500), nullable=True)  # JSON string of selected add-ons
    needs_requirements = Column(Text, nullable=True)  # For enterprise submissions
    
    # Stripe Integration Fields
    stripe_session_id = Column(String(200), nullable=True)
    stripe_customer_id = Column(String(200), nullable=True)
    stripe_subscription_id = Column(String(200), nullable=True)
    payment_status = Column(String(50), default="pending")  # pending, completed, failed, cancelled
    
    # Payment Details
    amount = Column(Numeric(10, 2), nullable=True)
    setup_fee_amount = Column(Numeric(10, 2), nullable=True, default=0)
    
    # Subscription Management
    subscription_status = Column(String(50), default="inactive")  # inactive, active, cancelled, past_due
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    
    # Customer Preferences
    save_card = Column(Boolean, default=False)
    accept_policies = Column(Boolean, nullable=False)
    
    # Processing Status
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processed = Column(Boolean, default=False)

