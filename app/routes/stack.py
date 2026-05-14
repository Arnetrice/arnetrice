from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.deps import base_context, templates


router = APIRouter()


@router.get("/stack", response_class=HTMLResponse)
async def stack_page(request: Request):
    return templates.TemplateResponse("pages/stack.html", base_context(request))
