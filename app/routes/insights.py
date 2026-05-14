from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, Response

from app.config import get_settings
from app.content.loader import get_insight, get_insights
from app.content.models import Channel
from app.deps import base_context, templates


router = APIRouter()


# Order matters — exact paths before parameterized.

@router.get("/insights", response_class=HTMLResponse)
async def insights_index(
    request: Request,
    channel: str | None = Query(default=None),
):
    all_insights = get_insights()
    selected = (channel or "ALL").upper()
    if selected == "ALL":
        filtered = [d for d in all_insights if d.insight.state == "live"]
    else:
        filtered = [
            d for d in all_insights
            if d.insight.state == "live" and d.insight.channel == selected
        ]
    ctx = base_context(request)
    ctx["insights"] = filtered
    ctx["total_count"] = len([d for d in all_insights if d.insight.state == "live"])
    ctx["active_channel"] = selected
    return templates.TemplateResponse("pages/insights_index.html", ctx)


@router.get("/insights/rss.xml", include_in_schema=False)
async def insights_rss(request: Request):
    settings = get_settings()
    insights = [d for d in get_insights() if d.insight.state == "live"]
    ctx = {
        "request": request,
        "insights": insights,
        "site_url": settings.site_url.rstrip("/"),
        "build_date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"),
    }
    body = templates.get_template("rss/insights.xml").render(ctx)
    return Response(content=body, media_type="application/rss+xml; charset=utf-8")


@router.get("/insights/_list", response_class=HTMLResponse, include_in_schema=False)
async def insights_list_fragment(
    request: Request,
    channel: str | None = Query(default=None),
):
    """HTMX fragment endpoint. Returns just the list grid for client-side filter swap."""
    all_insights = get_insights()
    selected = (channel or "ALL").upper()
    if selected == "ALL":
        filtered = [d for d in all_insights if d.insight.state == "live"]
    else:
        filtered = [
            d for d in all_insights
            if d.insight.state == "live" and d.insight.channel == selected
        ]
    ctx = base_context(request)
    ctx["insights"] = filtered
    ctx["active_channel"] = selected
    return templates.TemplateResponse("_partials/insights_list.html", ctx)


@router.get("/insights/{slug}", response_class=HTMLResponse)
async def insight_detail(request: Request, slug: str):
    doc = get_insight(slug)
    if doc is None or doc.insight.state != "live":
        raise HTTPException(status_code=404)
    ctx = base_context(request)
    ctx["doc"] = doc
    return templates.TemplateResponse("pages/insight_detail.html", ctx)
