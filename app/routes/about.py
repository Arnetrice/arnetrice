from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.deps import templates, base_context


router = APIRouter()


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("pages/about.html", base_context(request))
