from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..utils.email import send_contact_notification, send_contact_confirmation

router = APIRouter(prefix="/api/contact", tags=["contact"])

@router.post("/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    """
    Submit a new contact form
    """
    try:
        # Save to database
        db_contact = crud.create_contact(db=db, contact=contact)
        
        # Send notification email to Arnetrice
        send_contact_notification(contact)
        
        # Send confirmation email to the person
        send_contact_confirmation(contact)
        
        return db_contact
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing contact form: {str(e)}")

@router.get("/", response_model=List[schemas.Contact])
def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all contact submissions (admin only)
    """
    contacts = crud.get_contacts(db, skip=skip, limit=limit)
    return contacts

@router.get("/{contact_id}", response_model=schemas.Contact)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Get a specific contact submission by ID
    """
    contact = crud.get_contact(db, contact_id=contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}/read", response_model=schemas.Contact)
def mark_contact_read(contact_id: int, db: Session = Depends(get_db)):
    """
    Mark a contact submission as read
    """
    contact = crud.mark_contact_read(db, contact_id=contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

