"""OG image routes — branded PNG renders for social sharing."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.content.loader import get_insight, get_system, get_topic
from app.services.og import cached, render_content_og, render_default_og


router = APIRouter()

# Long browser cache + longer shared/CDN cache. Content keyed by URL;
# server restart re-renders (in-memory cache only).
PNG_HEADERS = {
    "Content-Type": "image/png",
    "Cache-Control": "public, max-age=86400, s-maxage=604800, immutable",
}


def _png(data: bytes) -> Response:
    return Response(content=data, headers=PNG_HEADERS)


@router.get("/og/default.png", include_in_schema=False)
async def og_default():
    return _png(cached("default", render_default_og))


@router.get("/og/system/{slug}.png", include_in_schema=False)
async def og_system(slug: str):
    doc = get_system(slug)
    if doc is None or doc.case.state != "live":
        raise HTTPException(status_code=404)
    data = cached(
        f"system/{slug}",
        lambda: render_content_og(
            id_text=doc.case.id,
            channel=doc.case.channel,
            state=doc.case.state,
            title=doc.case.title,
            summary=doc.case.summary,
        ),
    )
    return _png(data)


@router.get("/og/topic/{slug}.png", include_in_schema=False)
async def og_topic(slug: str):
    doc = get_topic(slug)
    if doc is None or doc.topic.state != "live":
        raise HTTPException(status_code=404)
    data = cached(
        f"topic/{slug}",
        lambda: render_content_og(
            id_text=doc.topic.id,
            channel=doc.topic.channel,
            state=doc.topic.state,
            title=doc.topic.title,
            summary=doc.topic.summary,
        ),
    )
    return _png(data)


@router.get("/og/insight/{slug}.png", include_in_schema=False)
async def og_insight(slug: str):
    doc = get_insight(slug)
    if doc is None or doc.insight.state != "live":
        raise HTTPException(status_code=404)
    data = cached(
        f"insight/{slug}",
        lambda: render_content_og(
            id_text=doc.insight.id,
            channel=doc.insight.channel,
            state=doc.insight.state,
            title=doc.insight.title,
            summary=doc.insight.summary,
        ),
    )
    return _png(data)
