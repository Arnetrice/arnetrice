from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Set up templates path
current_dir = os.getcwd()
frontend_path = os.path.join(current_dir, "frontend")
templates = Jinja2Templates(directory=os.path.join(frontend_path, "templates"))

@router.get("/")
async def home(request: Request):
    print(f"HOME route called! Request URL: {request.url}")
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/services")
async def services(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})

@router.get("/portfolio")
async def portfolio_page(request: Request):
    return templates.TemplateResponse("portfolio.html", {"request": request})

@router.get("/blog")
async def blog_page(request: Request):
    return templates.TemplateResponse("blog.html", {"request": request})

@router.get("/contact")
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@router.get("/faq")
async def faq(request: Request):
    print(f"FAQ route called! Request URL: {request.url}")
    response = templates.TemplateResponse("faq_blog.html", {"request": request})
    print(f"FAQ template response created: {response}")
    return response

# Keep the test routes for debugging if needed
@router.get("/faq-test")
async def faq_test(request: Request):
    print(f"FAQ TEST route called! Request URL: {request.url}")
    response = templates.TemplateResponse("faq_blog.html", {"request": request})
    print(f"FAQ TEST template response created: {response}")
    return response

@router.get("/test-faq-unique-path")
async def faq_unique_test(request: Request):
    return templates.TemplateResponse("faq_blog.html", {"request": request})

# Policy Pages
@router.get("/terms-of-service")
async def terms_of_service(request: Request):
    return templates.TemplateResponse("terms-of-service.html", {"request": request})

@router.get("/privacy-policy")
async def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy-policy.html", {"request": request})

@router.get("/billing-policy")
async def billing_policy(request: Request):
    return templates.TemplateResponse("billing-policy.html", {"request": request})