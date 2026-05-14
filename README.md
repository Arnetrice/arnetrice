# Arnetrice.com — V2

Operations Systems Architect identity platform.
FastAPI + Jinja + HTMX + Tailwind, deployed to Railway.

## Phase status

- [x] **Phase 0** — Foundation: scaffold, design tokens, base layout, rendered hero
- [ ] **Phase 1** — Home + About (full homepage sections, mobile nav, motion)
- [ ] **Phase 2** — Systems portfolio (case studies)
- [ ] **Phase 3** — Architecture deep dives
- [ ] **Phase 4** — Insights (writing pipeline)
- [ ] **Phase 5** — Polish (a11y, perf, SEO, analytics)

See `docs/Claude/rebrand-v2-plan.md` for the strategic brief.

## Local development

Two processes run side by side: Python app and Tailwind CSS watcher.

### One-time setup

```powershell
# Python deps
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Tailwind deps (Node 20+)
npm install
```

### Run

```powershell
# Terminal 1: Tailwind watcher
npm run watch:css

# Terminal 2: FastAPI dev server
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Visit `http://localhost:8000`.

## Production build

```powershell
# Build CSS once
npm run build:css

# Run app (Railway sets $PORT)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Deploy (Railway)

Railway uses the multi-stage `Dockerfile`:

1. Stage 1 (`node:20-alpine`) builds minified CSS from `static/css/input.css`.
2. Stage 2 (`python:3.12-slim`) installs Python deps and runs `uvicorn`.

Build metadata (`RAILWAY_GIT_COMMIT_SHA`) is read at startup and surfaced
in the footer meta row.

Healthcheck: `GET /healthz` returns operational status + version JSON.

## Project structure

```
app/             FastAPI application — routes, config, content loader
templates/       Jinja templates — base, macros (components), sections, pages
content/         Markdown source for case studies, insights, architecture topics
static/          CSS source + Tailwind build output, JS, fonts, images
docs/Claude/     Strategic brief (source of truth)
tests/           pytest + httpx route tests
```

## Design system

Operations Console direction — see `static/css/input.css` for the design
token block. Single source of truth for surface, ink, accent, type, motion.

Mono is Geist Mono (validated swap from the rejected IBM Plex / JetBrains
typefaces). Display is Inter Display, body is Inter.
