# Fonts — for OG image generation

The dynamic OG image generator (`app/services/og.py`) reads TTF files from
this directory to render branded social-preview images. **Without these
files, OG images render with a bitmap fallback font** — the route still
works, but the result looks unbranded.

## What to download

Both fonts are free, open source (SIL Open Font License).

**1. Inter Variable** (display + body)
   - Source: https://github.com/rsms/inter/releases (latest release)
   - File: `Inter-Variable.ttf` (from the variable font folder)
   - Save here as: `Inter-Variable.ttf`

**2. Geist Mono Variable** (mono labels, IDs, status)
   - Source: https://github.com/vercel/geist-font/releases (latest release)
   - File: `GeistMono-VariableFont_wght.ttf` or `GeistMono-Variable.ttf`
   - Save here as: `GeistMono-Variable.ttf`

## Lookup order

The generator tries these filenames in order — first match wins:

- Display: `Inter-Variable.ttf`, `InterVariable.ttf`, `Inter-VariableFont.ttf`, `Inter-Regular.ttf`, `Inter.ttf`
- Mono: `GeistMono-Variable.ttf`, `GeistMonoVariable.ttf`, `GeistMono-VariableFont.ttf`, `GeistMono-Regular.ttf`, `GeistMono.ttf`

## After adding the files

No rebuild needed. The OG generator picks up the files on the next image
render. Existing cached images are invalidated on the next server restart
(in-memory cache only).
