from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.content.loader import get_system, get_systems
from app.deps import base_context, templates


router = APIRouter()


@router.get("/systems", response_class=HTMLResponse)
async def systems_index(request: Request):
    ctx = base_context(request)
    ctx["systems"] = get_systems()
    return templates.TemplateResponse("pages/systems_index.html", ctx)


@router.get("/systems/{slug}", response_class=HTMLResponse)
async def system_detail(request: Request, slug: str):
    doc = get_system(slug)
    if doc is None or doc.case.state != "live":
        raise HTTPException(status_code=404)
    ctx = base_context(request)
    ctx["doc"] = doc
    return templates.TemplateResponse("pages/system_detail.html", ctx)
