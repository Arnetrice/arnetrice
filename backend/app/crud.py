from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas
from typing import List, Optional

# Contact CRUD operations
def create_contact(db: Session, contact: schemas.ContactCreate) -> models.Contact:
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Contact]:
    return db.query(models.Contact).order_by(desc(models.Contact.created_at)).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int) -> Optional[models.Contact]:
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def mark_contact_read(db: Session, contact_id: int) -> Optional[models.Contact]:
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact:
        contact.is_read = True
        db.commit()
        db.refresh(contact)
    return contact

# Blog CRUD operations
def create_blog_post(db: Session, blog_post: schemas.BlogPostCreate) -> models.BlogPost:
    db_blog_post = models.BlogPost(**blog_post.dict())
    db.add(db_blog_post)
    db.commit()
    db.refresh(db_blog_post)
    return db_blog_post

def get_blog_posts(db: Session, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[models.BlogPost]:
    query = db.query(models.BlogPost)
    if published_only:
        query = query.filter(models.BlogPost.is_published == True)
    return query.order_by(desc(models.BlogPost.published_at)).offset(skip).limit(limit).all()

def get_blog_post(db: Session, blog_id: int) -> Optional[models.BlogPost]:
    return db.query(models.BlogPost).filter(models.BlogPost.id == blog_id).first()

def get_blog_post_by_slug(db: Session, slug: str) -> Optional[models.BlogPost]:
    return db.query(models.BlogPost).filter(models.BlogPost.slug == slug).first()

def update_blog_post(db: Session, blog_id: int, blog_post: schemas.BlogPostUpdate) -> Optional[models.BlogPost]:
    db_blog_post = db.query(models.BlogPost).filter(models.BlogPost.id == blog_id).first()
    if db_blog_post:
        for key, value in blog_post.dict(exclude_unset=True).items():
            setattr(db_blog_post, key, value)
        db.commit()
        db.refresh(db_blog_post)
    return db_blog_post

def delete_blog_post(db: Session, blog_id: int) -> bool:
    db_blog_post = db.query(models.BlogPost).filter(models.BlogPost.id == blog_id).first()
    if db_blog_post:
        db.delete(db_blog_post)
        db.commit()
        return True
    return False

# Portfolio CRUD operations
def create_portfolio_item(db: Session, portfolio: schemas.PortfolioCreate) -> models.Portfolio:
    db_portfolio = models.Portfolio(**portfolio.dict())
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def get_portfolio_items(db: Session, skip: int = 0, limit: int = 100, featured_only: bool = False) -> List[models.Portfolio]:
    query = db.query(models.Portfolio)
    if featured_only:
        query = query.filter(models.Portfolio.featured == True)
    return query.order_by(desc(models.Portfolio.created_at)).offset(skip).limit(limit).all()

def get_portfolio_item(db: Session, portfolio_id: int) -> Optional[models.Portfolio]:
    return db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()

def update_portfolio_item(db: Session, portfolio_id: int, portfolio: schemas.PortfolioUpdate) -> Optional[models.Portfolio]:
    db_portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if db_portfolio:
        for key, value in portfolio.dict(exclude_unset=True).items():
            setattr(db_portfolio, key, value)
        db.commit()
        db.refresh(db_portfolio)
    return db_portfolio

def delete_portfolio_item(db: Session, portfolio_id: int) -> bool:
    db_portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if db_portfolio:
        db.delete(db_portfolio)
        db.commit()
        return True
    return False

