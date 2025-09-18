from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import os

from .config import settings
from .database import create_tables
from .routes import contact, blog, portfolio, pages, checkout

# Create FastAPI app
app = FastAPI(
    title="Arnetrice.com API",
    description="Data-driven solutions provider API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pages.router)
app.include_router(contact.router)
app.include_router(blog.router)
app.include_router(portfolio.router)
app.include_router(checkout.router)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Arnetrice.com API is running"}

# Debug endpoint to list all routes
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods) if hasattr(route, 'methods') else []
            })
    return {"routes": routes}

# Serve static files for frontend
# Use a more reliable path resolution method
current_dir = os.getcwd()
frontend_path = os.path.join(current_dir, "frontend")
print(f"Current directory: {current_dir}")
print(f"Frontend path: {frontend_path}")
print(f"Frontend exists: {os.path.exists(frontend_path)}")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
else:
    # API-only mode if frontend doesn't exist
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Arnetrice.com API",
            "version": "1.0.0",
            "docs": "/docs"
        }
