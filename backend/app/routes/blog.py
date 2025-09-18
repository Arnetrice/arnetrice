from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/blog", tags=["blog"])

@router.post("/", response_model=schemas.BlogPost)
def create_blog_post(blog_post: schemas.BlogPostCreate, db: Session = Depends(get_db)):
    """
    Create a new blog post
    """
    return crud.create_blog_post(db=db, blog_post=blog_post)

@router.get("/", response_model=List[schemas.BlogPost])
def get_blog_posts(skip: int = 0, limit: int = 100, published_only: bool = True, db: Session = Depends(get_db)):
    """
    Get all blog posts
    """
    blog_posts = crud.get_blog_posts(db, skip=skip, limit=limit, published_only=published_only)
    return blog_posts

@router.get("/{blog_id}", response_model=schemas.BlogPost)
def get_blog_post(blog_id: int, db: Session = Depends(get_db)):
    """
    Get a specific blog post by ID
    """
    blog_post = crud.get_blog_post(db, blog_id=blog_id)
    if blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return blog_post

@router.get("/slug/{slug}", response_model=schemas.BlogPost)
def get_blog_post_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Get a specific blog post by slug
    """
    blog_post = crud.get_blog_post_by_slug(db, slug=slug)
    if blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return blog_post

@router.put("/{blog_id}", response_model=schemas.BlogPost)
def update_blog_post(blog_id: int, blog_post: schemas.BlogPostUpdate, db: Session = Depends(get_db)):
    """
    Update a blog post
    """
    updated_post = crud.update_blog_post(db, blog_id=blog_id, blog_post=blog_post)
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return updated_post

@router.delete("/{blog_id}")
def delete_blog_post(blog_id: int, db: Session = Depends(get_db)):
    """
    Delete a blog post
    """
    success = crud.delete_blog_post(db, blog_id=blog_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return {"message": "Blog post deleted successfully"}

