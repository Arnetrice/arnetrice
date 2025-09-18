# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Arnetrice.com is a professional business website built with FastAPI backend and static frontend. It's designed as a data-driven solutions provider platform with contact forms, blog system, and portfolio showcase.

## Development Commands

### Running the Application
```bash
# Primary method - runs FastAPI with frontend serving
python run.py

# Alternative - direct uvicorn command from backend directory
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage reporting
pytest --cov=app
```

### Database Setup
```bash
# Create PostgreSQL database (if not exists)
createdb arnetrice_db

# Run Alembic migrations (if available)
alembic upgrade head
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env
```

## Architecture

### Backend Structure
- **FastAPI Application**: `backend/app/main.py` - Main application with route includes and static file serving
- **Configuration**: `backend/app/config.py` - Environment-based settings with flexible database URL support
- **Database Models**: `backend/app/models.py` - SQLAlchemy models for Contact, BlogPost, and Portfolio
- **API Routes**: `backend/app/routes/` - Modular route organization (contact, blog, portfolio)
- **Database Layer**: `backend/app/crud.py` - Database operations and `backend/app/database.py` - Connection setup

### Frontend Structure
- **Templates**: `frontend/templates/` - Jinja2 HTML templates with base.html inheritance
- **Static Assets**: `frontend/static/` - CSS (styles.css) and JavaScript (main.js, contact.js, portfolio.js)
- **Hybrid Serving**: FastAPI serves both API endpoints and frontend templates

### Key Architectural Patterns
- **Template-based Frontend**: Uses Jinja2 templates served by FastAPI, not a separate SPA
- **Modular API Routes**: Each feature (contact, blog, portfolio) has dedicated route files
- **Flexible Database Config**: Supports both single DATABASE_URL and separate DB variables
- **Static + Dynamic Content**: Frontend templates can call API endpoints for dynamic data

### Database Schema
- **contacts**: Contact form submissions with read status tracking
- **blog_posts**: Blog content with slug-based URLs, publishing status, and SEO fields
- **portfolio**: Project showcases with client info, technologies, and external links

## Configuration

### Required Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (or use separate DB_* variables)
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: Email configuration for contact forms
- `SECRET_KEY`: Application secret key
- `DEBUG`: Debug mode flag

### Development vs Production
- Development: Uses `reload=True` in uvicorn, serves from local filesystem
- Production: Expects configured PostgreSQL and SMTP for full functionality
- Frontend path resolution: Uses `os.getcwd()` relative paths for template/static file serving

## Email System
Contact forms trigger email notifications through `backend/app/utils/email.py`. Requires SMTP configuration with Gmail app passwords recommended for development.

## Testing Strategy
Tests are in `backend/tests/`. Basic functionality tests exist with graceful handling of database connection failures (returns 500 vs crashing).