"""Arnetrice.com — V2 application entry."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import PROJECT_ROOT, get_settings
from app.deps import templates, base_context
from app.content.loader import warm_caches
from app.routes import about, architecture, contact, home, insights, meta, og, stack, systems


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: warm content caches from /content/*.md."""
    warm_caches()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Arnetrice",
        description="Operations Systems Architect identity platform.",
        version="2.0.0",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None,
        openapi_url=None if settings.is_production else "/openapi.json",
        lifespan=lifespan,
    )

    app.mount(
        "/static",
        StaticFiles(directory=str(PROJECT_ROOT / "static")),
        name="static",
    )

    app.include_router(meta.router)
    app.include_router(home.router)
    app.include_router(about.router)
    app.include_router(systems.router)
    app.include_router(architecture.router)
    app.include_router(insights.router)
    app.include_router(stack.router)
    app.include_router(contact.router)
    app.include_router(og.router)

    @app.exception_handler(404)
    async def not_found(request: Request, exc):
        return templates.TemplateResponse(
            "errors/404.html",
            base_context(request),
            status_code=404,
        )

    return app


app = create_app()
