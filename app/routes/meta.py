"""Operational meta routes — healthcheck, robots, sitemap."""
from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from app.config import get_settings
from app.content.loader import get_architecture, get_insights, get_systems
from app.deps import templates
from app.version import SITE_VERSION, PROCESS_STARTED_AT, BUILD_TIMESTAMP


router = APIRouter()


@router.get("/healthz", include_in_schema=False)
async def healthz():
    settings = get_settings()
    return JSONResponse(
        {
            "status": "ok",
            "service": "arnetrice",
            "version": SITE_VERSION,
            "commit": settings.commit_short,
            "deployment": settings.railway_deployment_id,
            "build_timestamp": BUILD_TIMESTAMP,
            "started_at": PROCESS_STARTED_AT,
            "env": settings.app_env,
        }
    )


@router.get("/robots.txt", include_in_schema=False)
async def robots():
    settings = get_settings()
    if settings.is_production:
        body = (
            "User-agent: *\nAllow: /\n"
            f"Sitemap: {settings.site_url.rstrip('/')}/sitemap.xml\n"
        )
    else:
        body = "User-agent: *\nDisallow: /\n"
    return PlainTextResponse(body)


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap(request: Request):
    settings = get_settings()
    today = date.today().isoformat()

    urls: list[dict] = [
        {"path": "/", "lastmod": today, "changefreq": "weekly", "priority": "1.0"},
        {"path": "/about", "lastmod": today, "changefreq": "monthly", "priority": "0.8"},
        {"path": "/systems", "lastmod": today, "changefreq": "weekly", "priority": "0.9"},
        {"path": "/architecture", "lastmod": today, "changefreq": "weekly", "priority": "0.9"},
        {"path": "/insights", "lastmod": today, "changefreq": "weekly", "priority": "0.9"},
        {"path": "/stack", "lastmod": today, "changefreq": "monthly", "priority": "0.6"},
        {"path": "/contact", "lastmod": today, "changefreq": "yearly", "priority": "0.5"},
    ]
    for doc in get_systems():
        if doc.case.state == "live":
            urls.append({
                "path": doc.url,
                "lastmod": doc.case.published.isoformat() if doc.case.published else today,
                "changefreq": "monthly",
                "priority": "0.7",
            })
    for doc in get_architecture():
        if doc.topic.state == "live":
            urls.append({
                "path": doc.url,
                "lastmod": doc.topic.published.isoformat() if doc.topic.published else today,
                "changefreq": "monthly",
                "priority": "0.7",
            })
    for doc in get_insights():
        if doc.insight.state == "live":
            urls.append({
                "path": doc.url,
                "lastmod": doc.insight.published.isoformat(),
                "changefreq": "yearly",
                "priority": "0.6",
            })

    ctx = {
        "request": request,
        "urls": urls,
        "site_url": settings.site_url.rstrip("/"),
    }
    body = templates.get_template("seo/sitemap.xml").render(ctx)
    return Response(content=body, media_type="application/xml; charset=utf-8")
