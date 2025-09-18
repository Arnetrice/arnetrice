from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import os

# Create FastAPI app
app = FastAPI(
    title="Arnetrice.com",
    description="Data-driven solutions provider",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Arnetrice.com is running"}

# Serve static files for frontend
current_dir = os.getcwd()
frontend_path = os.path.join(current_dir, "frontend")
print(f"Current directory: {current_dir}")
print(f"Frontend path: {frontend_path}")
print(f"Frontend exists: {os.path.exists(frontend_path)}")

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
    
    # Set up Jinja2 templates
    templates = Jinja2Templates(directory=os.path.join(frontend_path, "templates"))
    
    @app.get("/")
    async def home(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/about")
    async def about(request: Request):
        return templates.TemplateResponse("about.html", {"request": request})
    
    @app.get("/services")
    async def services(request: Request):
        return templates.TemplateResponse("services.html", {"request": request})
    
    @app.get("/portfolio")
    async def portfolio(request: Request):
        return templates.TemplateResponse("portfolio.html", {"request": request})
    
    @app.get("/blog")
    async def blog(request: Request):
        return templates.TemplateResponse("blog.html", {"request": request})
    
    @app.get("/contact")
    async def contact(request: Request):
        return templates.TemplateResponse("contact.html", {"request": request})
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str, request: Request):
        # Serve index.html for all other routes (SPA behavior)
        if not full_path.startswith("api") and not full_path.startswith("docs") and not full_path.startswith("static"):
            return templates.TemplateResponse("index.html", {"request": request})
        raise HTTPException(status_code=404, detail="Not found")
else:
    # API-only mode if frontend doesn't exist
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Arnetrice.com API",
            "version": "1.0.0",
            "docs": "/docs"
        }

