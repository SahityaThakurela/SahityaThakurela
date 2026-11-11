        x = chart_left + i * (bar_width + gap)
        y = chart_top + chart_height - h
        fill = BLUE if max_val and month["count"] == max_val else (BLUE_2 if month["count"] > 0 else PAPER_2)
        parts.append(f'<rect class="enter" x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{max(3,h):.1f}" rx="7" fill="{fill}" style="animation-delay:{1.2+i*.035:.2f}s"/>')
        if month["count"] and (month["count"] == max_val or i in (0, 11)):
            parts.append(f'<text x="{x+bar_width/2:.1f}" y="{max(197,y-10):.1f}" text-anchor="middle" class="mono" font-size="12" fill="{INK}">{month["count"]}</text>')
        parts.append(f'<text x="{x+bar_width/2:.1f}" y="{chart_top+chart_height+29}" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">{safe_text(month["name"])}</text>')
    if not stats["ready"]:
        parts.append(f'<text x="600" y="250" text-anchor="middle" class="mono" font-size="14" letter-spacing="1.1" fill="{MUTED}">WAITING FOR FIRST DAILY CONTRIBUTION SYNC</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def render_repo(font_css: str, title: str, index: str, description: str, tags: list[str], url: str, accent: str, delay: float) -> str:
    W, H = 1200, 250
    parts = [svg_open(W, H, font_css, delay), card_base(W, H)]
    parts.append(label(54, 53, f"FEATURED BUILD  /  {index}", accent))
    parts.append(f'<text x="54" y="122" class="serif enter" font-size="65" fill="{INK}">{safe_text(title)}</text>')
    parts.append(f'<text x="56" y="164" font-size="20" fill="#55565C">{safe_text(description)}</text>')

    x = 56
    for tag in tags:
        width = max(74, 16 + len(tag) * 9)
        parts.append(f'<rect x="{x}" y="188" width="{width}" height="34" rx="17" fill="{PAPER_2}"/>')
        parts.append(f'<text x="{x+width/2}" y="210" text-anchor="middle" class="mono" font-size="12" fill="#56575F">{safe_text(tag)}</text>')
        x += width + 10
        if x > 790:
            break
    parts.append(f'<circle cx="1087" cy="125" r="53" fill="{BLUE if index == "01" else PAPER_2}"/>')
    arrow = "#FFFFFF" if index == "01" else BLUE
    parts.append(f'<path d="M1068 125 H1104 M1090 110 L1105 125 L1090 140" fill="none" stroke="{arrow}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append(f'<text x="1087" y="212" text-anchor="middle" class="mono" font-size="12" fill="{MUTED}">OPEN REPO</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def render_graph(font_css: str, days: list[dict[str, Any]]) -> str:
    W, H = 1200, 300
    parts = [svg_open(W, H, font_css, 2.1), card_base(W, H)]
    parts.append('<text x="52" y="62" class="serif" font-size="45" fill="%s">A year in <tspan fill="%s" font-style="italic">blue.</tspan></text>' % (INK, BLUE))
    parts.append(label(760, 58, "Daily contributions  /  52 weeks", MUTED))
    x0, y0, cell, gap = 116, 108, 13, 5
    today = dt.datetime.now(dt.timezone.utc).date()
    end = today
    start = end - dt.timedelta(days=364)
    grid_start = start - dt.timedelta(days=(start.weekday() + 1) % 7)
    by_date = {d["date"]: d for d in days if d["date"] <= end}
    cols = ((end - grid_start).days // 7) + 1
    cell_colors = [PAPER_2, "#DCE2FF", "#AEBBFF", "#7188FF", BLUE]
    for day in range((end - grid_start).days + 1):
        date = grid_start + dt.timedelta(days=day)
        if date < start:
            continue
        col = day // 7
        row = (date.weekday() + 1) % 7
        item = by_date.get(date, {"count": 0, "level": 0})
        level = max(0, min(4, int(item.get("level", 0))))

        if item.get("count", 0) > 0 and level == 0:
            level = min(4, 1 + int(item["count"] >= 3) + int(item["count"] >= 6) + int(item["count"] >= 10))
        x, y = x0 + col*(cell+gap), y0 + row*(cell+gap)
        parts.append(f'<rect class="enter" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{cell_colors[level]}" style="animation-delay:{2.12+day*.0009:.2f}s"/>')
    if not days:
        parts.append(f'<text x="600" y="214" text-anchor="middle" class="mono" font-size="14" letter-spacing="1.1" fill="{MUTED}">WAITING FOR FIRST DAILY CONTRIBUTION SYNC</text>')
    months_seen = set()
    for day in range((end - grid_start).days + 1):
        date = grid_start + dt.timedelta(days=day)
        if date < start or date.day > 7:
            continue
        key = (date.year, date.month)
        if key in months_seen:
            continue
        months_seen.add(key)
        col = day // 7
        parts.append(f'<text x="{x0+col*(cell+gap)}" y="94" class="mono" font-size="12" fill="{MUTED}">{calendar.month_abbr[date.month]}</text>')
    parts.append(label(118, 265, "LESS", MUTED))
    for i, color in enumerate(cell_colors):
        parts.append(f'<rect x="{1015+i*23}" y="251" width="15" height="15" rx="3" fill="{color}"/>')
    parts.append(label(1140, 265, "MORE", MUTED))
    parts.append('</svg>')
    return "\n".join(parts)

def main() -> None:
    global STATIC
    
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    font_css = build_font_css()
    days, _totals = load_contributions()
    stats = contribution_stats(days)

    files = {
        "hero.svg": render_hero(font_css),
        "build.svg": render_tile(font_css, "Build", "01 / Projects", "Products with a purpose", "SEE MY WORK", BLUE, "build", 0.35),
        "explore.svg": render_tile(font_css, "Explore", "02 / Engineering", "150+ DSA problems solved in C++", "BROWSE GITHUB", WARM, "explore", 0.48),
        "connect.svg": render_tile(font_css, "Connect", "03 / Community", "Open to ideas and collaboration", "SAY HELLO", BLUE, "connect", 0.61),
        "activity.svg": render_activity(font_css, stats),
        "repo-nivaran.svg": render_repo(font_css, "Nivaran", "01", "A civic-tech platform for reporting issues and coordinating resolution.", ["TypeScript", "React Native", "PostgreSQL", "Prisma", "pgvector"], "https://github.com/SahityaThakurela/Nivaran", BLUE, 1.35),
        "repo-jan-vaani.svg": render_repo(font_css, "Jan Vaani", "02", "A voice-first AI helpline for discovering welfare schemes in Hindi and English.", ["FastAPI", "Gemini", "Qdrant", "RAG", "React"], "https://github.com/SahityaThakurela/Jan-Vaani", BLUE_2, 1.55),
        "repo-flixparty.svg": render_repo(font_css, "FlixParty", "03", "A synchronized watch party with WebRTC video, voice chat and playback sync.", ["WebRTC", "TypeScript", "P2P", "Chrome Extension"], "https://github.com/SahityaThakurela/FlixParty", WARM, 1.75),
        "contributions.svg": render_graph(font_css, days),
    }
    for filename, content in files.items():
        (CARDS_DIR / filename).write_text(content + "\n", encoding="utf-8")

        # Generate a static PNG version of the hero for GitHub README.
    original_static = STATIC
    
    try:
        STATIC = True
        static_hero = render_hero(font_css)
    finally:
        STATIC = original_static
    
    cairosvg.svg2png(
        bytestring=(static_hero + "\n").encode("utf-8"),
        write_to=str(CARDS_DIR / "hero.png"),
        output_width=2400,
        output_height=840,
    )
    
    print("Generated hero.png successfully.")
    mode = "static preview" if STATIC else "animated cards"
    print(f"Rendered {len(files)} {mode} in {CARDS_DIR}")
    if not stats["ready"]:
        print("Contribution data is empty; activity and graph cards show a sync-pending state.")

if __name__ == "__main__":
    main()


















# """Render animated, self-contained SVG cards for Sahitya Thakurela's GitHub profile.

# The generated SVGs are embedded through Markdown <img> tags, so they contain their
# own styles and subsetted WOFF fonts. Set STATIC=1 to render the final frame without
# motion (useful for screenshots and visual QA).

# Fonts: Instrument Serif, Inter and JetBrains Mono from Google Fonts (SIL OFL).
# If font downloads are unavailable, locally installed DejaVu/Lato fonts are used.
# """
# from __future__ import annotations

# import cairosvg
# import io
# import base64
# import calendar
# import datetime as dt
# import html
# import json
# import os
# import shutil
# import subprocess
# import sys
# import urllib.request
# from pathlib import Path
# from typing import Any

# ROOT = Path(__file__).resolve().parents[1]
# DATA_FILE = ROOT / "data" / "contributions.json"
# CARDS_DIR = ROOT / "cards"
# CACHE_DIR = ROOT / ".cache" / "fonts"
# STATIC = os.getenv("STATIC", "0").strip().lower() in {"1", "true", "yes", "on"}
# USERNAME = "SahityaThakurela"
# AVATAR_URL = "https://avatars.githubusercontent.com/u/135995348?v=4"
# PORTRAIT_FILE = ROOT / "Warm Studio Portrait in Black Hoodie.png"

# PAPER = "#F5F3EE"
# PAPER_2 = "#ECE9E1"
# INK = "#191A1F"
# MUTED = "#777873"
# LINE = "#DEDAD0"
# BLUE = "#3858F5"
# BLUE_2 = "#8195FF"
# BLUE_3 = "#C5CEFF"
# WARM = "#D6A66B"

# FONT_SOURCES = {
#     "serif": (
#         "Instrument Serif",
#         "https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Regular.ttf",
#         ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
#     ),
#     "sans": (
#         "Inter",
#         "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
#         ["/usr/share/fonts/truetype/lato/Lato-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
#     ),
#     "mono": (
#         "JetBrains Mono",
#         "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
#         ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"],
#     ),
# }

# def safe_text(value: Any) -> str:
#     return html.escape(str(value), quote=True)

# def download(url: str, destination: Path) -> bool:
#     destination.parent.mkdir(parents=True, exist_ok=True)
#     request = urllib.request.Request(url, headers={"User-Agent": "SahityaProfileCards/1.0"})
#     try:
#         with urllib.request.urlopen(request, timeout=20) as response:
#             destination.write_bytes(response.read())
#         return True
#     except Exception as exc:
#         print(f"[font/avatar] Could not download {url}: {exc}", file=sys.stderr)
#         return False

# def locate_font(kind: str) -> tuple[str, Path | None]:
#     family, url, fallbacks = FONT_SOURCES[kind]
#     cached = CACHE_DIR / f"{kind}.ttf"
#     if cached.exists() and cached.stat().st_size > 1024:
#         return family, cached
#     if download(url, cached) and cached.exists() and cached.stat().st_size > 1024:
#         return family, cached
#     for fallback in fallbacks:
#         path = Path(fallback)
#         if path.exists():
#             return family, path
#     return family, None

# def subset_font(kind: str, family: str, source: Path | None) -> str:
#     """Return a CSS @font-face block with base64 WOFF, or a safe system fallback."""
#     if source is None:
#         return ""
#     output = CACHE_DIR / f"{kind}-subset.woff"
#     pyftsubset = shutil.which("pyftsubset")
#     if not pyftsubset:
#         print("[font] pyftsubset not found; using system fallback fonts", file=sys.stderr)
#         return ""

#     subset_chars = (
#         "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
#         " .,!?;:'\"()[]{}+-=*/\\_@#$%&<>|~^`·•→←↑↓—–…"
#     )
#     command = [
#         pyftsubset, str(source), f"--text={subset_chars}",
#         "--flavor=woff", f"--output-file={output}",
#         "--layout-features=kern,liga", "--no-hinting",
#     ]
#     try:
#         subprocess.run(command, check=True, capture_output=True, text=True)
#         encoded = base64.b64encode(output.read_bytes()).decode("ascii")
#         return (
#             f"@font-face{{font-family:'{family}';src:url(data:font/woff;base64,{encoded}) format('woff');"
#             "font-style:normal;font-weight:100 900;font-display:swap;}"
#         )
#     except Exception as exc:
#         print(f"[font] Could not subset {source}: {exc}", file=sys.stderr)
#         return ""

# def build_font_css() -> str:
#     blocks = []
#     for kind in ("serif", "sans", "mono"):
#         family, path = locate_font(kind)
#         css = subset_font(kind, family, path)
#         if css:
#             blocks.append(css)
#     return "\n".join(blocks)

# def css_block(font_css: str, delay: float = 0.0) -> str:
#     if STATIC:
#         animation_css = ""
#     else:
#         animation_css = f"""
#         .enter {{ opacity:0; transform:translateY(18px); animation:rise .85s cubic-bezier(.2,.75,.2,1) {delay:.2f}s forwards; }}
#         .soft {{ opacity:0; animation:fade .8s ease {delay + .2:.2f}s forwards; }}
#         .shimmer {{ animation:shimmer 5.5s ease-in-out {delay + 1.8:.2f}s infinite; }}
#         @keyframes rise {{ to {{ opacity:1; transform:translateY(0); }} }}
#         @keyframes fade {{ to {{ opacity:1; }} }}
#         @keyframes shimmer {{ 0%,70%,100% {{ opacity:.18; }} 82% {{ opacity:.75; }} }}
#         .smil {{ display:inline; }}
#         @media (prefers-reduced-motion: reduce) {{
#           .enter,.soft,.shimmer {{ animation:none !important; opacity:1 !important; transform:none !important; }}
#           .smil {{ display:none !important; }}
#         }}
#         """
#     return f"""
#     <style>
#       {font_css}
#       text {{ font-family:'Inter','Lato','DejaVu Sans',sans-serif; }}
#       .serif {{ font-family:'Instrument Serif','DejaVu Serif',serif; }}
#       .mono {{ font-family:'JetBrains Mono','DejaVu Sans Mono',monospace; }}
#       {animation_css}
#     </style>
#     """

# def svg_open(width: int, height: int, font_css: str, delay: float = 0.0) -> str:
#     return (
#         f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
#         f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
#         f'{css_block(font_css, delay)}'
#     )

# def card_base(width: int, height: int, radius: int = 28) -> str:
#     return (
#         f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="{radius}" '
#         f'fill="{PAPER}" stroke="{LINE}" stroke-width="2"/>'
#     )

# def label(x: int, y: int, text: str, fill: str = MUTED) -> str:
#     return f'<text x="{x}" y="{y}" class="mono" font-size="15" letter-spacing="2.2" fill="{fill}">{safe_text(text.upper())}</text>'

# def load_contributions() -> tuple[list[dict[str, Any]], dict[str, Any]]:
#     if not DATA_FILE.exists():
#         return [], {}
#     try:
#         payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
#         raw = payload.get("contributions", [])
#         if isinstance(raw, dict):

#             flattened = []
#             for months in raw.values():
#                 if isinstance(months, dict):
#                     for days in months.values():
#                         if isinstance(days, dict):
#                             flattened.extend(d for d in days.values() if isinstance(d, dict))
#             raw = flattened
#         clean = []
#         for item in raw:
#             if not isinstance(item, dict) or not item.get("date"):
#                 continue
#             try:
#                 date = dt.date.fromisoformat(str(item["date"]))
#             except ValueError:
#                 continue
#             clean.append({"date": date, "count": max(0, int(item.get("count") or 0)), "level": max(0, min(4, int(item.get("level") or 0)))})
#         clean.sort(key=lambda x: x["date"])
#         return clean, payload.get("total", {}) if isinstance(payload.get("total", {}), dict) else {}
#     except Exception as exc:
#         print(f"[data] Could not read {DATA_FILE}: {exc}", file=sys.stderr)
#         return [], {}

# def contribution_stats(days: list[dict[str, Any]]) -> dict[str, Any]:
#     if not days:
#         return {"ready": False, "streak": None, "active": None, "busiest": None, "total": None, "monthly": []}
#     today = dt.datetime.now(dt.timezone.utc).date()
#     recent = [d for d in days if today - dt.timedelta(days=364) <= d["date"] <= today]
#     by_date = {d["date"]: d["count"] for d in recent}
#     active = sum(1 for n in by_date.values() if n > 0)
#     total = sum(by_date.values())
#     active_days = [d for d in recent if d["count"] > 0]
#     busiest = max(active_days, key=lambda x: x["count"], default=None)

#     cursor = today if by_date.get(today, 0) > 0 else today - dt.timedelta(days=1)
#     streak = 0
#     while by_date.get(cursor, 0) > 0:
#         streak += 1
#         cursor -= dt.timedelta(days=1)

#     first_month = (today.replace(day=1) - dt.timedelta(days=335)).replace(day=1)
#     month_keys = []
#     y, m = first_month.year, first_month.month
#     for _ in range(12):
#         month_keys.append((y, m))
#         if m == 12:
#             y, m = y + 1, 1
#         else:
#             m += 1
#     monthly = []
#     for year, month in month_keys:
#         count = sum(d["count"] for d in recent if d["date"].year == year and d["date"].month == month)
#         monthly.append({"key": f"{year}-{month:02d}", "name": calendar.month_abbr[month], "count": count})
#     return {"ready": True, "streak": streak, "active": active, "busiest": busiest, "total": total, "monthly": monthly, "recent": recent}


# def engraved_portrait_data_uri() -> str:
#     """Create a transparent, engraved-style portrait embedded in the hero SVG."""
#     from PIL import (
#         Image,
#         ImageChops,
#         ImageEnhance,
#         ImageFilter,
#         ImageOps,
#     )

#     if not PORTRAIT_FILE.exists():
#         raise FileNotFoundError(
#             f"Portrait image not found: {PORTRAIT_FILE}"
#         )

#     with Image.open(PORTRAIT_FILE) as original:
#         source = ImageOps.exif_transpose(original).convert("RGB")

#     # Crop to a square and resize for the SVG portrait area.
#     width, height = source.size
#     side = min(width, height)

#     left = (width - side) // 2
#     top = (height - side) // 2

#     source = source.crop((
#         left,
#         top,
#         left + side,
#         top + side
#     ))

#     source = ImageOps.fit(
#         source,
#         (520, 520),
#         method=Image.Resampling.LANCZOS
#     )

#     # Convert the photograph into a pencil-sketch effect.
#     gray = ImageOps.autocontrast(
#         ImageOps.grayscale(source)
#     )

    
#     inverted = ImageOps.invert(gray)
    
#     blurred = inverted.filter(
#         ImageFilter.GaussianBlur(radius=10)
#     )
    
#     # Manual color-dodge calculation.
#     # Uses standard Python arithmetic, no ImageChops.dodge/divide.
#     gray_pixels = list(gray.getdata())
#     blurred_pixels = list(blurred.getdata())
    
#     sketch_pixels = []
    
#     for base, blur in zip(gray_pixels, blurred_pixels):
#         denominator = max(1, 255 - blur)
    
#         value = min(
#             255,
#             int(base * 255 / denominator)
#         )
    
#         sketch_pixels.append(value)
    
#     sketch = Image.new("L", gray.size)
#     sketch.putdata(sketch_pixels)
    
#     sketch = ImageOps.autocontrast(sketch)



#     # Blend original tonal details with engraved lines.
#     engraved = Image.blend(gray, sketch, 0.45)

#     engraved = ImageEnhance.Contrast(
#         engraved
#     ).enhance(1.25)

#     # Warm monochrome ink matching the cream banner.
#     colored = ImageOps.colorize(
#         engraved,
#         black="#383630",
#         white="#F5F3EE"
#     )

#     # Remove the white studio background.
#     # Darker foreground pixels remain fully opaque.
#     gray_original = ImageOps.grayscale(source)

#     alpha = Image.eval(
#         gray_original,
#         lambda pixel: (
#             255
#             if pixel <= 225
#             else max(0, min(255, int((255 - pixel) * 8.5)))
#         )
#     )

#     portrait = colored.convert("RGBA")
#     portrait.putalpha(alpha)

#     # Export PNG into memory and encode it for SVG embedding.
#     output = io.BytesIO()

#     portrait.save(
#         output,
#         format="PNG",
#         optimize=True
#     )

#     encoded = base64.b64encode(
#         output.getvalue()
#     ).decode("ascii")

#     return encoded


# def render_hero(font_css: str) -> str:
#     W, H = 1200, 420
#     parts = [svg_open(W, H, font_css, 0.0), card_base(W, H)]
#     parts.append('<circle cx="62" cy="58" r="6" fill="%s"><animate attributeName="r" values="5;7;5" dur="2.6s" repeatCount="indefinite" class="smil"/></circle>' % BLUE if not STATIC else f'<circle cx="62" cy="58" r="6" fill="{BLUE}"/>')
#     parts.append(label(84, 64, "Software tinkerer  /  full-stack developer", INK))
#     parts.append('<text x="62" y="195" class="serif enter" font-size="112" letter-spacing="-2" fill="%s">Sahitya</text>' % INK)
#     parts.append('<text x="62" y="305" class="serif enter" font-size="112" letter-spacing="-2" fill="%s" style="animation-delay:.18s">Thakurela</text>' % INK)
#     parts.append('<rect class="shimmer" x="63" y="337" width="54" height="5" rx="2.5" fill="%s"/>' % BLUE)
#     parts.append('<text x="63" y="382" font-size="24" fill="#42434A">Full-stack developer. My side projects have side projects.</text>')
#     parts.append('<text x="63" y="405" class="mono" font-size="13" letter-spacing="1.3" fill="%s">B.TECH CSE @ JSS ACADEMY  ·  GDG WEB DEVELOPER  ·  NOIDA, INDIA</text>' % MUTED)

        
#     # Warm circular background behind the portrait.
#     parts.append(
#         f'<circle cx="965" cy="212" r="157" fill="{PAPER_2}"/>'
#     )
    
#     parts.append(
#         f'<circle cx="965" cy="212" r="157" '
#         f'fill="none" stroke="{LINE}" stroke-width="1.5"/>'
#     )
    
#     # Generate the real engraved portrait.
#     portrait_data = engraved_portrait_data_uri()
    
#     # Embed the portrait directly into the SVG.
#     parts.append(
#         f'<image '
#         f'x="805" y="52" '
#         f'width="320" height="320" '
#         f'preserveAspectRatio="xMidYMid meet" '
#         f'xlink:href="data:image/png;base64,{portrait_data}"/>'
#     )
    
#     # Small footer below the portrait.
#     parts.append(
#         f'<text x="965" y="398" '
#         f'class="mono" font-size="12" '
#         f'text-anchor="middle" letter-spacing="2" '
#         f'fill="{MUTED}">ST / 2026</text>'
#     )

#     return "\n".join(parts)

# def render_tile(font_css: str, title: str, eyebrow: str, subtitle: str, number: str, accent: str, kind: str, delay: float) -> str:
#     W, H = 390, 198
#     parts = [svg_open(W, H, font_css, delay), card_base(W, H, 24)]
#     parts.append(label(28, 38, eyebrow, MUTED))
#     parts.append(f'<text x="28" y="102" class="serif enter" font-size="48" fill="{INK}">{safe_text(title)}</text>')
#     parts.append(f'<text x="28" y="139" font-size="17" fill="#5F605F">{safe_text(subtitle)}</text>')
#     parts.append(f'<text x="28" y="177" class="mono" font-size="13" letter-spacing="1.1" fill="{accent}">{safe_text(number)}  ↗</text>')

#     if kind == "build":
#         parts.append(f'<path d="M316 62 L356 62 L356 102 L316 102 Z M326 72 L346 72 L346 92 L326 92 Z" fill="none" stroke="{accent}" stroke-width="4"/>')
#         parts.append(f'<path d="M316 122 L356 122" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>')
#     elif kind == "explore":
#         parts.append(f'<circle cx="335" cy="82" r="30" fill="none" stroke="{accent}" stroke-width="4"/>')
#         parts.append(f'<path d="M335 52 L335 112 M305 82 L365 82" stroke="{accent}" stroke-width="2" opacity=".65"/>')
#         parts.append(f'<circle cx="335" cy="82" r="7" fill="{accent}"/>')
#     else:
#         parts.append(f'<path d="M306 72 C318 48 352 48 364 72 C352 96 318 96 306 72 Z" fill="none" stroke="{accent}" stroke-width="4"/>')
#         parts.append(f'<path d="M335 55 L335 90 M319 72 L351 72" stroke="{accent}" stroke-width="2"/>')
#     parts.append('</svg>')
#     return "\n".join(parts)

# def render_activity(font_css: str, stats: dict[str, Any]) -> str:
#     W, H = 1200, 420
#     parts = [svg_open(W, H, font_css, 1.05), card_base(W, H)]
#     parts.append('<text x="52" y="64" class="serif" font-size="45" fill="%s">A little progress, <tspan fill="%s" font-style="italic">every month.</tspan></text>' % (INK, BLUE))
#     parts.append(label(730, 61, "Contribution rhythm  /  last 12 months", MUTED))
#     stats_items = [
#         ("CURRENT STREAK", f"{stats['streak']} days" if stats["ready"] else "—"),
#         ("ACTIVE DAYS", str(stats["active"]) if stats["ready"] else "—"),
#         ("BUSIEST DAY", f"{stats['busiest']['date'].strftime('%b %d')} · {stats['busiest']['count']}" if stats["ready"] and stats["busiest"] else "—"),
#     ]
#     for i, (head, value) in enumerate(stats_items):
#         x = 54 + i * 265
#         parts.append(label(x, 110, head, MUTED))
#         parts.append(f'<text x="{x}" y="158" class="serif" font-size="43" fill="{INK}">{safe_text(value)}</text>')
#         if i < 2:
#             parts.append(f'<line x1="{x+226}" y1="94" x2="{x+226}" y2="169" stroke="{LINE}"/>')
#     chart_left, chart_top, chart_height = 76, 222, 150
#     chart_width, gap = 1048, 18
#     monthly = stats.get("monthly", [])
#     max_val = max((m["count"] for m in monthly), default=0)
#     bar_width = (chart_width - gap * 11) / 12
#     parts.append(f'<line x1="{chart_left}" y1="{chart_top+chart_height}" x2="{chart_left+chart_width}" y2="{chart_top+chart_height}" stroke="{LINE}" stroke-width="2"/>')
#     for i, month in enumerate(monthly):
#         h = (month["count"] / max_val * chart_height) if max_val else 0
#         x = chart_left + i * (bar_width + gap)
#         y = chart_top + chart_height - h
#         fill = BLUE if max_val and month["count"] == max_val else (BLUE_2 if month["count"] > 0 else PAPER_2)
#         parts.append(f'<rect class="enter" x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{max(3,h):.1f}" rx="7" fill="{fill}" style="animation-delay:{1.2+i*.035:.2f}s"/>')
#         if month["count"] and (month["count"] == max_val or i in (0, 11)):
#             parts.append(f'<text x="{x+bar_width/2:.1f}" y="{max(197,y-10):.1f}" text-anchor="middle" class="mono" font-size="12" fill="{INK}">{month["count"]}</text>')
#         parts.append(f'<text x="{x+bar_width/2:.1f}" y="{chart_top+chart_height+29}" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">{safe_text(month["name"])}</text>')
#     if not stats["ready"]:
#         parts.append(f'<text x="600" y="250" text-anchor="middle" class="mono" font-size="14" letter-spacing="1.1" fill="{MUTED}">WAITING FOR FIRST DAILY CONTRIBUTION SYNC</text>')
#     parts.append('</svg>')
#     return "\n".join(parts)

# def render_repo(font_css: str, title: str, index: str, description: str, tags: list[str], url: str, accent: str, delay: float) -> str:
#     W, H = 1200, 250
#     parts = [svg_open(W, H, font_css, delay), card_base(W, H)]
#     parts.append(label(54, 53, f"FEATURED BUILD  /  {index}", accent))
#     parts.append(f'<text x="54" y="122" class="serif enter" font-size="65" fill="{INK}">{safe_text(title)}</text>')
#     parts.append(f'<text x="56" y="164" font-size="20" fill="#55565C">{safe_text(description)}</text>')

#     x = 56
#     for tag in tags:
#         width = max(74, 16 + len(tag) * 9)
#         parts.append(f'<rect x="{x}" y="188" width="{width}" height="34" rx="17" fill="{PAPER_2}"/>')
#         parts.append(f'<text x="{x+width/2}" y="210" text-anchor="middle" class="mono" font-size="12" fill="#56575F">{safe_text(tag)}</text>')
#         x += width + 10
#         if x > 790:
#             break
#     parts.append(f'<circle cx="1087" cy="125" r="53" fill="{BLUE if index == "01" else PAPER_2}"/>')
#     arrow = "#FFFFFF" if index == "01" else BLUE
#     parts.append(f'<path d="M1068 125 H1104 M1090 110 L1105 125 L1090 140" fill="none" stroke="{arrow}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
#     parts.append(f'<text x="1087" y="212" text-anchor="middle" class="mono" font-size="12" fill="{MUTED}">OPEN REPO</text>')
#     parts.append('</svg>')
#     return "\n".join(parts)

# def render_graph(font_css: str, days: list[dict[str, Any]]) -> str:
#     W, H = 1200, 300
#     parts = [svg_open(W, H, font_css, 2.1), card_base(W, H)]
#     parts.append('<text x="52" y="62" class="serif" font-size="45" fill="%s">A year in <tspan fill="%s" font-style="italic">blue.</tspan></text>' % (INK, BLUE))
#     parts.append(label(760, 58, "Daily contributions  /  52 weeks", MUTED))
#     x0, y0, cell, gap = 116, 108, 13, 5
#     today = dt.datetime.now(dt.timezone.utc).date()
#     end = today
#     start = end - dt.timedelta(days=364)
#     grid_start = start - dt.timedelta(days=(start.weekday() + 1) % 7)
#     by_date = {d["date"]: d for d in days if d["date"] <= end}
#     cols = ((end - grid_start).days // 7) + 1
#     cell_colors = [PAPER_2, "#DCE2FF", "#AEBBFF", "#7188FF", BLUE]
#     for day in range((end - grid_start).days + 1):
#         date = grid_start + dt.timedelta(days=day)
#         if date < start:
#             continue
#         col = day // 7
#         row = (date.weekday() + 1) % 7
#         item = by_date.get(date, {"count": 0, "level": 0})
#         level = max(0, min(4, int(item.get("level", 0))))

#         if item.get("count", 0) > 0 and level == 0:
#             level = min(4, 1 + int(item["count"] >= 3) + int(item["count"] >= 6) + int(item["count"] >= 10))
#         x, y = x0 + col*(cell+gap), y0 + row*(cell+gap)
#         parts.append(f'<rect class="enter" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{cell_colors[level]}" style="animation-delay:{2.12+day*.0009:.2f}s"/>')
#     if not days:
#         parts.append(f'<text x="600" y="214" text-anchor="middle" class="mono" font-size="14" letter-spacing="1.1" fill="{MUTED}">WAITING FOR FIRST DAILY CONTRIBUTION SYNC</text>')
#     months_seen = set()
#     for day in range((end - grid_start).days + 1):
#         date = grid_start + dt.timedelta(days=day)
#         if date < start or date.day > 7:
#             continue
#         key = (date.year, date.month)
#         if key in months_seen:
#             continue
#         months_seen.add(key)
#         col = day // 7
#         parts.append(f'<text x="{x0+col*(cell+gap)}" y="94" class="mono" font-size="12" fill="{MUTED}">{calendar.month_abbr[date.month]}</text>')
#     parts.append(label(118, 265, "LESS", MUTED))
#     for i, color in enumerate(cell_colors):
#         parts.append(f'<rect x="{1015+i*23}" y="251" width="15" height="15" rx="3" fill="{color}"/>')
#     parts.append(label(1140, 265, "MORE", MUTED))
#     parts.append('</svg>')
#     return "\n".join(parts)

# def main() -> None:
#     global STATIC
    
#     CARDS_DIR.mkdir(parents=True, exist_ok=True)
#     CACHE_DIR.mkdir(parents=True, exist_ok=True)
#     font_css = build_font_css()
#     days, _totals = load_contributions()
#     stats = contribution_stats(days)

#     files = {
#         "hero.svg": render_hero(font_css),
#         "build.svg": render_tile(font_css, "Build", "01 / Projects", "Products with a purpose", "SEE MY WORK", BLUE, "build", 0.35),
#         "explore.svg": render_tile(font_css, "Explore", "02 / Engineering", "150+ DSA problems solved in C++", "BROWSE GITHUB", WARM, "explore", 0.48),
#         "connect.svg": render_tile(font_css, "Connect", "03 / Community", "Open to ideas and collaboration", "SAY HELLO", BLUE, "connect", 0.61),
#         "activity.svg": render_activity(font_css, stats),
#         "repo-nivaran.svg": render_repo(font_css, "Nivaran", "01", "A civic-tech platform for reporting issues and coordinating resolution.", ["TypeScript", "React Native", "PostgreSQL", "Prisma", "pgvector"], "https://github.com/SahityaThakurela/Nivaran", BLUE, 1.35),
#         "repo-jan-vaani.svg": render_repo(font_css, "Jan Vaani", "02", "A voice-first AI helpline for discovering welfare schemes in Hindi and English.", ["FastAPI", "Gemini", "Qdrant", "RAG", "React"], "https://github.com/SahityaThakurela/Jan-Vaani", BLUE_2, 1.55),
#         "repo-flixparty.svg": render_repo(font_css, "FlixParty", "03", "A synchronized watch party with WebRTC video, voice chat and playback sync.", ["WebRTC", "TypeScript", "P2P", "Chrome Extension"], "https://github.com/SahityaThakurela/FlixParty", WARM, 1.75),
#         "contributions.svg": render_graph(font_css, days),
#     }
#     for filename, content in files.items():
#         (CARDS_DIR / filename).write_text(content + "\n", encoding="utf-8")

#         # Generate a static PNG version of the hero for GitHub README.
#     original_static = STATIC
    
#     try:
#         STATIC = True
#         static_hero = render_hero(font_css)
#     finally:
#         STATIC = original_static
    
#     cairosvg.svg2png(
#         bytestring=(static_hero + "\n").encode("utf-8"),
#         write_to=str(CARDS_DIR / "hero.png"),
#         output_width=2400,
#         output_height=840,
#     )
    
#     print("Generated hero.png successfully.")
#     mode = "static preview" if STATIC else "animated cards"
#     print(f"Rendered {len(files)} {mode} in {CARDS_DIR}")
#     if not stats["ready"]:
#         print("Contribution data is empty; activity and graph cards show a sync-pending state.")

# if __name__ == "__main__":
#     main()
