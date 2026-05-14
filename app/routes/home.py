from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.content.loader import get_insights
from app.deps import templates, base_context


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    ctx = base_context(request)
    ctx["hero"] = {
        "id": "ARC-001",
        "status": "OPERATIONAL",
        "headline_lead": "Building operational systems that create",
        "headline_accent": "visibility, structure,",
        "headline_tail": "and scalable workflow.",
        "subtitle_chips": [
            "OPS SYS ARCH",
            "AI BUILDER",
            "WORKFLOW INFRA",
        ],
    }
    ctx["recent_insights"] = [d for d in get_insights() if d.insight.state == "live"][:3]
    return templates.TemplateResponse("pages/home.html", ctx)
