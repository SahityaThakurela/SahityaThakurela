#!/usr/bin/env python3
"""Render a GitHub-safe PNG hero banner from the source portrait."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Warm Studio Portrait in Black Hoodie.png"
OUTPUT = ROOT / "cards" / "hero.png"
W, H = 1200, 420
PAPER = "#F5F3EE"
INK = "#191A1F"
MUTED = "#777873"
BLUE = "#3858F5"

def font(paths, size):
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()

serif = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
], 100)
sans = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
], 23)
mono = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
], 14)

def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Portrait source not found: {SOURCE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=28, outline="#DEDAD0", width=2)

    draw.ellipse((56, 52, 68, 64), fill=BLUE)
    draw.text((84, 43), "SOFTWARE TINKERER  /  FULL-STACK DEVELOPER", font=mono, fill=INK)
    draw.text((60, 105), "Sahitya", font=serif, fill=INK, stroke_width=0)
    draw.text((60, 210), "Thakurela", font=serif, fill=INK, stroke_width=0)
    draw.rounded_rectangle((62, 330, 120, 336), radius=3, fill=BLUE)
    draw.text((62, 350), "Full-stack developer. My side projects have side projects.", font=sans, fill="#42434A")
    draw.text((62, 393), "B.TECH CSE @ JSS ACADEMY  ·  GDG WEB DEVELOPER  ·  NOIDA, INDIA", font=mono, fill=MUTED)

    size = 320
    portrait = Image.open(SOURCE).convert("RGB")
    portrait = ImageOps.fit(portrait, (size, size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.43))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)

    # Subtle circular shadow and outline.
    shadow = Image.new("RGBA", (size + 36, size + 36), (0, 0, 0, 0))
    shadow_mask = Image.new("L", shadow.size, 0)
    ImageDraw.Draw(shadow_mask).ellipse((18, 18, size + 17, size + 17), fill=90)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(10))
    shadow.putalpha(shadow_mask)
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.alpha_composite(shadow, (W - 395, 25))

    portrait_rgba = portrait.convert("RGBA")
    portrait_rgba.putalpha(mask)
    canvas_rgba.alpha_composite(portrait_rgba, (W - 377, 43))
    final = ImageDraw.Draw(canvas_rgba)
    final.ellipse((W - 378, 42, W - 57, 363), outline="#DEDAD0", width=2)
    canvas_rgba.convert("RGB").save(OUTPUT, format="PNG", optimize=True)
    print(f"Rendered {OUTPUT}")

if __name__ == "__main__":
    main()
