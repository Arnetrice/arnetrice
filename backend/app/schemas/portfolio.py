"""
Portfolio-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PortfolioBase(BaseModel):
    title: str
    description: str
    client: Optional[str] = None
    category: Optional[str] = None
    technologies: Optional[str] = None
    project_url: Optional[str] = None
    github_url: Optional[str] = None
    image_url: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(PortfolioBase):
    featured: Optional[bool] = False

class Portfolio(PortfolioBase):
    id: int
    featured: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

