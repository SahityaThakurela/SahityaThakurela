"""Render animated, self-contained SVG cards for Sahitya Thakurela's GitHub profile.

The generated SVGs are embedded through Markdown <img> tags, so they contain their
own styles and subsetted WOFF fonts. Set STATIC=1 to render the final frame without
motion (useful for screenshots and visual QA).

Fonts: Instrument Serif, Inter and JetBrains Mono from Google Fonts (SIL OFL).
If font downloads are unavailable, locally installed DejaVu/Lato fonts are used.
"""
from __future__ import annotations

import cairosvg
import io
import base64
import calendar
import datetime as dt
import html
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "contributions.json"
CARDS_DIR = ROOT / "cards"
CACHE_DIR = ROOT / ".cache" / "fonts"
STATIC = os.getenv("STATIC", "0").strip().lower() in {"1", "true", "yes", "on"}
USERNAME = "SahityaThakurela"
AVATAR_URL = "https://avatars.githubusercontent.com/u/135995348?v=4"
PORTRAIT_FILE = ROOT / "Warm Studio Portrait in Black Hoodie.png"

PAPER = "#F5F3EE"
PAPER_2 = "#ECE9E1"
INK = "#191A1F"
MUTED = "#777873"
LINE = "#DEDAD0"
BLUE = "#3858F5"
BLUE_2 = "#8195FF"
BLUE_3 = "#C5CEFF"
WARM = "#D6A66B"

FONT_SOURCES = {
    "serif": (
        "Instrument Serif",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Regular.ttf",
        ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
    ),
    "sans": (
        "Inter",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
        ["/usr/share/fonts/truetype/lato/Lato-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    ),
    "mono": (
        "JetBrains Mono",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
        ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"],
    ),
}

def safe_text(value: Any) -> str:
    return html.escape(str(value), quote=True)

def download(url: str, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "SahityaProfileCards/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            destination.write_bytes(response.read())
        return True
    except Exception as exc:
        print(f"[font/avatar] Could not download {url}: {exc}", file=sys.stderr)
        return False

def locate_font(kind: str) -> tuple[str, Path | None]:
    family, url, fallbacks = FONT_SOURCES[kind]
    cached = CACHE_DIR / f"{kind}.ttf"
    if cached.exists() and cached.stat().st_size > 1024:
        return family, cached
    if download(url, cached) and cached.exists() and cached.stat().st_size > 1024:
        return family, cached
    for fallback in fallbacks:
        path = Path(fallback)
        if path.exists():
            return family, path
    return family, None

def subset_font(kind: str, family: str, source: Path | None) -> str:
    """Return a CSS @font-face block with base64 WOFF, or a safe system fallback."""
    if source is None:
        return ""
    output = CACHE_DIR / f"{kind}-subset.woff"
    pyftsubset = shutil.which("pyftsubset")
