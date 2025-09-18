"""
Blog-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlogPostBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    author: Optional[str] = "Arnetrice Smith"
    tags: Optional[str] = None
    featured_image: Optional[str] = None

class BlogPostCreate(BlogPostBase):
    slug: str

class BlogPostUpdate(BlogPostBase):
    is_published: Optional[bool] = True

class BlogPost(BlogPostBase):
    id: int
    slug: str
    published_at: datetime
    is_published: bool
    
    class Config:
        from_attributes = True

