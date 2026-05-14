"""OG image generation — branded social-preview PNGs.

Renders 1200×630 images that mirror the live site's Operations Console
design language: faint hairline grid, channel status strip, mono ID +
channel + state badges, display-weight title, brand footer.

Graceful degradation: if TTF font files aren't present in static/fonts/,
falls back to Pillow's bitmap font with a single startup warning.
"""
from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

from app.config import PROJECT_ROOT


logger = logging.getLogger("arnetrice.og")

WIDTH, HEIGHT = 1200, 630
PAD_X, PAD_Y = 80, 50

# Brand palette — mirrors static/css/input.css design tokens.
SURFACE       = (247, 248, 250)   # --color-surface
SURFACE_ELEV  = (255, 255, 255)   # --color-surface-elev
SURFACE_TINT  = (238, 241, 245)   # --color-surface-tint
INK_STRONG    = (11, 18, 32)      # --color-ink-strong
INK           = (17, 24, 39)      # --color-ink
INK_MUTED     = (75, 85, 99)      # --color-ink-muted
INK_FAINT     = (156, 163, 175)   # --color-ink-faint
HAIRLINE      = (229, 231, 235)   # --color-hairline
ACCENT        = (67, 56, 202)     # --color-accent (indigo)
AMBER         = (217, 119, 6)     # --color-amber
SIGNAL_OK     = (16, 185, 129)    # --color-signal-ok

FONTS_DIR = PROJECT_ROOT / "static" / "fonts"

_font_cache: dict[tuple[str, int], object] = {}
_fonts_warned = False

# Filename candidates per family — first match wins. Bring-your-own-font.
FONT_CANDIDATES = {
    "display": [
        "Inter-Variable.ttf",
        "InterVariable.ttf",
        "Inter-VariableFont.ttf",
        "Inter-Regular.ttf",
        "Inter.ttf",
    ],
    "mono": [
        "GeistMono-Variable.ttf",
        "GeistMonoVariable.ttf",
        "GeistMono-VariableFont.ttf",
        "GeistMono-Regular.ttf",
        "GeistMono.ttf",
    ],
}


def _font(family: str, size: int):
    global _fonts_warned
    key = (family, size)
    if key in _font_cache:
        return _font_cache[key]

    for name in FONT_CANDIDATES.get(family, []):
        path = FONTS_DIR / name
        if path.exists():
            font = ImageFont.truetype(str(path), size=size)
            _font_cache[key] = font
            return font

    if not _fonts_warned:
        logger.warning(
            "OG fonts missing in %s — bitmap fallback in use. "
            "Add Inter-Variable.ttf and GeistMono-Variable.ttf for branded output.",
            FONTS_DIR,
        )
        _fonts_warned = True
    fallback = ImageFont.load_default()
    _font_cache[key] = fallback
    return fallback


def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int, max_lines: int) -> list[str]:
    """Greedy word-wrap, truncate with ellipsis when overflowing max_lines."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for w in words:
        candidate = " ".join(current + [w])
        if _text_size(draw, candidate, font)[0] <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(" ".join(current))
    # If we ran out of room, append ellipsis to the last line.
    consumed_words = sum(len(line.split()) for line in lines)
    if consumed_words < len(words):
        last = lines[-1].rstrip(",.;: ") + "…"
        lines[-1] = last
    return lines


def _draw_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, WIDTH + 1, 48):
        draw.line([(x, 0), (x, HEIGHT)], fill=HAIRLINE, width=1)
    for y in range(0, HEIGHT + 1, 48):
        draw.line([(0, y), (WIDTH, y)], fill=HAIRLINE, width=1)


def _draw_status_strip(draw: ImageDraw.ImageDraw) -> None:
    """SYS · WKF · GOV · VIS top strip — mirrors the live site."""
    font = _font("mono", 15)
    channels = [
        ("SYSTEMS",),
        ("WORKFLOW",),
        ("GOVERNANCE",),
        ("VISIBILITY",),
    ]
    x = PAD_X
    y = 22
    for (label,) in channels:
        draw.ellipse((x, y + 4, x + 9, y + 13), fill=SIGNAL_OK)
        x += 16
        draw.text((x, y), label, font=font, fill=INK_MUTED)
        w, _ = _text_size(draw, label, font)
        x += w + 32

    # Right-side LIVE indicator
    right_label = "LIVE"
    w, _ = _text_size(draw, right_label, font)
    draw.text((WIDTH - PAD_X - w, y), right_label, font=font, fill=SIGNAL_OK)


def _draw_brand_footer(draw: ImageDraw.ImageDraw) -> None:
    """Bottom hairline + indigo square + wordmark + role line."""
    draw.line([(0, HEIGHT - 96), (WIDTH, HEIGHT - 96)], fill=HAIRLINE, width=1)

    sq_x, sq_y = PAD_X, HEIGHT - 62
    draw.rounded_rectangle((sq_x, sq_y, sq_x + 18, sq_y + 18), radius=3, fill=ACCENT)

    display_font = _font("display", 26)
    wordmark = "Arnetrice"
    draw.text((sq_x + 30, sq_y - 6), wordmark, font=display_font, fill=INK_STRONG)
    w, _ = _text_size(draw, wordmark, display_font)

    mono_font = _font("mono", 14)
    draw.text(
        (sq_x + 30 + w + 16, sq_y + 1),
        "OPERATIONS SYSTEMS ARCHITECT",
        font=mono_font,
        fill=INK_FAINT,
    )

    # Right side: site URL
    url_text = "arnetrice.com"
    uw, _ = _text_size(draw, url_text, mono_font)
    draw.text((WIDTH - PAD_X - uw, sq_y + 1), url_text, font=mono_font, fill=INK_FAINT)


def _state_color(state: str) -> tuple[int, int, int]:
    return {"live": SIGNAL_OK, "draft": AMBER, "queued": INK_FAINT}.get(state.lower(), INK_FAINT)


def _draw_meta_row(draw: ImageDraw.ImageDraw, id_text: str, channel: str, state: str, y: int) -> None:
    """[ID]  [CHANNEL]  ● STATE row."""
    font = _font("mono", 18)
    pad_h, pad_v = 14, 10
    h_box = 40

    x = PAD_X

    # ID badge
    w, _ = _text_size(draw, id_text, font)
    draw.rounded_rectangle(
        (x, y, x + w + pad_h * 2, y + h_box),
        radius=8, fill=SURFACE_ELEV, outline=HAIRLINE, width=1,
    )
    draw.text((x + pad_h, y + pad_v - 3), id_text, font=font, fill=INK_MUTED)
    x += w + pad_h * 2 + 12

    # Channel badge
    cw, _ = _text_size(draw, channel, font)
    draw.rounded_rectangle(
        (x, y, x + cw + pad_h * 2, y + h_box),
        radius=8, fill=SURFACE_ELEV, outline=HAIRLINE, width=1,
    )
    draw.text((x + pad_h, y + pad_v - 3), channel, font=font, fill=INK_MUTED)
    x += cw + pad_h * 2 + 18

    # Status indicator
    color = _state_color(state)
    dot_y = y + h_box // 2
    draw.ellipse((x, dot_y - 5, x + 10, dot_y + 5), fill=color)
    state_label = state.upper()
    draw.text((x + 20, y + pad_v - 3), state_label, font=font, fill=color)


def _draw_title(draw: ImageDraw.ImageDraw, title: str, y: int, max_lines: int = 2) -> int:
    """Display-weight title with word-wrap. Returns y-coord after last line."""
    font = _font("display", 70)
    max_w = WIDTH - PAD_X * 2
    lines = _wrap(draw, title, font, max_w, max_lines)
    line_h = 82
    for i, line in enumerate(lines):
        draw.text((PAD_X, y + i * line_h), line, font=font, fill=INK_STRONG)
    return y + len(lines) * line_h


def _draw_summary(draw: ImageDraw.ImageDraw, summary: str, y: int, max_lines: int = 2) -> None:
    font = _font("display", 22)
    max_w = WIDTH - PAD_X * 2 - 120
    lines = _wrap(draw, summary, font, max_w, max_lines)
    line_h = 32
    for i, line in enumerate(lines):
        draw.text((PAD_X, y + i * line_h), line, font=font, fill=INK_MUTED)


# ---------- Renderers ----------

def render_content_og(*, id_text: str, channel: str, state: str, title: str, summary: str = "") -> bytes:
    img = Image.new("RGB", (WIDTH, HEIGHT), SURFACE)
    draw = ImageDraw.Draw(img)

    _draw_grid(draw)
    _draw_status_strip(draw)
    draw.line([(0, 56), (WIDTH, 56)], fill=HAIRLINE, width=1)

    _draw_meta_row(draw, id_text, channel, state, y=110)
    title_end_y = _draw_title(draw, title, y=200, max_lines=2)

    if summary and title_end_y < HEIGHT - 200:
        _draw_summary(draw, summary, y=title_end_y + 36, max_lines=2)

    _draw_brand_footer(draw)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def render_default_og() -> bytes:
    img = Image.new("RGB", (WIDTH, HEIGHT), SURFACE)
    draw = ImageDraw.Draw(img)

    _draw_grid(draw)
    _draw_status_strip(draw)
    draw.line([(0, 56), (WIDTH, 56)], fill=HAIRLINE, width=1)

    # Identity hero
    title_font = _font("display", 82)
    title_lines = ["Building operational", "systems."]
    line_h = 96
    y = 180
    for i, line in enumerate(title_lines):
        draw.text((PAD_X, y + i * line_h), line, font=title_font, fill=INK_STRONG)

    mono_font = _font("mono", 18)
    subtitle = "OPS SYS ARCH  ·  AI BUILDER  ·  WORKFLOW INFRA"
    draw.text(
        (PAD_X, y + len(title_lines) * line_h + 30),
        subtitle,
        font=mono_font,
        fill=INK_MUTED,
    )

    _draw_brand_footer(draw)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ---------- In-memory cache ----------
_cache: dict[str, bytes] = {}


def cached(key: str, fn: Callable[[], bytes]) -> bytes:
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]
