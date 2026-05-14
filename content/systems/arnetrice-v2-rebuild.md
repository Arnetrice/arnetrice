---
slug: arnetrice-v2-rebuild
id: SYS-000
title: "Arnetrice.com V2 — operational systems identity platform"
role: Architect, builder, sole maintainer
timeframe: 2026-05 → present
channel: SYS
state: live
summary: >
  Rebuilt the Arnetrice identity site from scratch as a modern operational
  systems platform — FastAPI, Jinja, HTMX, Tailwind, deployed to Railway,
  with the build process itself acting as the credibility signal.
stack:
  - FastAPI
  - Jinja2
  - HTMX
  - Alpine.js
  - Tailwind v4
  - Python 3.12
  - Railway
  - Docker (multi-stage)
published: 2026-05-14
featured: true
order: 0
---

## Challenge

The V1 of arnetrice.com mixed two surfaces in one site — an identity
brand for an operations systems architect, and a SaaS-flavored services
catalog for a related offering. The result read as a freelancer-portfolio
hybrid, undermining both.

The strategic brief was unambiguous: this needed to become an operations
systems architect identity platform. Not a résumé site, not a portfolio,
not a corporate brochure. The site itself had to communicate operational
maturity by being one — credibility derived from the artifact, not the
copy.

Three prior visual pivots had failed before this rebuild: a
blueprint/schematic direction rejected as documentation-coded, a dark
HUD/console direction rejected as "old skool," and a light gradient
direction that landed visually but rested on a Django-templated stack
that needed to be wiped to start clean.

## Architecture

**Stack discipline over framework fashion.** FastAPI as the runtime,
Jinja2 for server-rendered templates, HTMX for fragment-level
interactivity where it earns its keep, Alpine.js for tiny client state,
Tailwind v4 for the design system. No JS framework, no SPA. Stack
chosen for consistency with the operational Python background already
on display in the case studies it will host.

**Multi-stage deployment.** A Dockerfile splits the build: stage one
(`node:20-alpine`) compiles Tailwind tokens to CSS, stage two
(`python:3.12-slim`) installs Python deps and runs `uvicorn`. Deployed
to Railway with the build SHA piped through to the footer as operational
meta, alongside `/healthz` returning a JSON status payload.

**Content as code.** Case studies, insights, and capability topics live
as Markdown with YAML frontmatter under `/content/`, parsed at startup
via Pydantic schemas, cached in memory, served by typed loaders. No
CMS, no database for content. Adding a case study is one markdown
commit; the schema enforces the shape; the loader fails loudly if
frontmatter is wrong. Version control is the publishing pipeline.

**Operations Console design direction.** Light cool surface (`#F7F8FA`),
indigo + amber operational accents, Inter Display + Inter + Geist Mono
typography, dashboard-influenced operational metadata as the brand's
signature texture. The mono ID pattern (`SYS-001`, `ABT-001`), pulsing
status dots, deploy SHAs in the footer, the channel-code status strip
(`SYS · WKF · GOV · VIS`) — none of these are decoration. They *are*
the brand at the component level.

**Architecture-first, then build fast.** Every structural decision was
settled on paper before code: stack, folder layout, design tokens,
section composition, phased plan. Implementation then moved quickly
because the shape was already resolved. The build itself is a working
demonstration of the methodology the about page describes.

## Outcome

A modern operational systems platform that ships with the design
discipline it claims. The site now reads as what the strategic brief
asked for — *"someone who understands systems, operations, workflow,
infrastructure, and execution"* — not because of the copy, but because
of how it's built.

Phase 0 shipped the foundation, design tokens, base layout, and
rendered hero on Railway. Phase 1 added the full homepage (operating
principles, featured systems, capability matrix, insights teaser,
quiet contact) and the about narrative. Phase 2 — the case study you
are reading — adds the systems portfolio: typed content loader, index
and detail templates, prose styles for rendered markdown, and the
inaugural case (this one).

Each subsequent system shipped will follow the same shape — challenge,
architecture, outcome — and arrive as a single markdown commit. The
infrastructure is now content-ready.
