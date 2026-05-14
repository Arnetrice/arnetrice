from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.content.loader import get_architecture, get_topic
from app.deps import base_context, templates


router = APIRouter()


@router.get("/architecture", response_class=HTMLResponse)
async def architecture_index(request: Request):
    ctx = base_context(request)
    ctx["topics"] = get_architecture()
    return templates.TemplateResponse("pages/architecture_index.html", ctx)


@router.get("/architecture/{slug}", response_class=HTMLResponse)
async def architecture_topic(request: Request, slug: str):
    doc = get_topic(slug)
    if doc is None or doc.topic.state != "live":
        raise HTTPException(status_code=404)
    ctx = base_context(request)
    ctx["doc"] = doc
    return templates.TemplateResponse("pages/architecture_topic.html", ctx)
