from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

@router.post("/", response_model=schemas.Portfolio)
def create_portfolio_item(portfolio: schemas.PortfolioCreate, db: Session = Depends(get_db)):
    """
    Create a new portfolio item
    """
    return crud.create_portfolio_item(db=db, portfolio=portfolio)

@router.get("/", response_model=List[schemas.Portfolio])
def get_portfolio_items(skip: int = 0, limit: int = 100, featured_only: bool = False, db: Session = Depends(get_db)):
    """
    Get all portfolio items
    """
    portfolio_items = crud.get_portfolio_items(db, skip=skip, limit=limit, featured_only=featured_only)
    return portfolio_items

@router.get("/{portfolio_id}", response_model=schemas.Portfolio)
def get_portfolio_item(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Get a specific portfolio item by ID
    """
    portfolio_item = crud.get_portfolio_item(db, portfolio_id=portfolio_id)
    if portfolio_item is None:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return portfolio_item

@router.put("/{portfolio_id}", response_model=schemas.Portfolio)
def update_portfolio_item(portfolio_id: int, portfolio: schemas.PortfolioUpdate, db: Session = Depends(get_db)):
    """
    Update a portfolio item
    """
    updated_item = crud.update_portfolio_item(db, portfolio_id=portfolio_id, portfolio=portfolio)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return updated_item

@router.delete("/{portfolio_id}")
def delete_portfolio_item(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Delete a portfolio item
    """
    success = crud.delete_portfolio_item(db, portfolio_id=portfolio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return {"message": "Portfolio item deleted successfully"}

