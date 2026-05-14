"""Shared FastAPI dependencies and Jinja context helpers."""
from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import PROJECT_ROOT, get_settings
from app.version import SITE_VERSION


templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

STATIC_DIR = PROJECT_ROOT / "static"


def _asset_version(path: str) -> str:
    """Cache-bust token for static assets.

    - Production: short build SHA (stable per deploy, max cache efficiency).
    - Development: file mtime (token changes on each Tailwind rebuild,
      forcing the browser to refetch instead of serving a heuristically
      cached stale copy).
    """
    settings = get_settings()
    if settings.is_production:
        return settings.commit_short
    full_path = STATIC_DIR / path
    try:
        return str(int(full_path.stat().st_mtime))
    except (FileNotFoundError, OSError):
        return "dev"


def make_asset_url(request: Request):
    """Returns a closure that builds versioned static URLs.

    Template usage: ``{{ asset_url('dist/output.css') }}``
    """
    def asset_url(path: str) -> str:
        base = str(request.url_for("static", path=path))
        return f"{base}?v={_asset_version(path)}"
    return asset_url


def base_context(request: Request) -> dict:
    """Context every page receives. Keep this lean."""
    settings = get_settings()
    return {
        "request": request,
        "site_version": SITE_VERSION,
        "commit_short": settings.commit_short,
        "is_production": settings.is_production,
        "site_url_clean": settings.site_url_clean,
        "asset_url": make_asset_url(request),
        "nav_primary": [
            {"label": "Systems", "href": "/systems", "state": "live"},
            {"label": "Architecture", "href": "/architecture", "state": "live"},
            {"label": "Insights", "href": "/insights", "state": "live"},
            {"label": "About", "href": "/about", "state": "live"},
        ],
        "nav_utility": [
            {"label": "Stack", "href": "/stack", "state": "live"},
            {"label": "Contact", "href": "/contact", "state": "live"},
        ],
        "status_channels": [
            {"id": "SYS", "label": "Systems", "state": "ok"},
            {"id": "WKF", "label": "Workflow", "state": "ok"},
            {"id": "GOV", "label": "Governance", "state": "ok"},
            {"id": "VIS", "label": "Visibility", "state": "ok"},
        ],
    }
