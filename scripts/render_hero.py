#!/usr/bin/env python3
"""Render a GitHub-safe PNG hero with a monochrome dot-matrix portrait."""
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
DOT = (48, 50, 58, 235)


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


def draw_dot_portrait(canvas):
    """Translate dark portrait detail into small dots; the light backdrop disappears."""
    size = (440, 370)
    portrait = Image.open(SOURCE).convert("RGB")
    portrait = ImageOps.fit(
        portrait, size, method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.43),
    )
    gray = ImageOps.autocontrast(ImageOps.grayscale(portrait), cutoff=1)
    gray = gray.filter(ImageFilter.GaussianBlur(0.35))

    # A subtle oval keeps the dot field visually contained without a photo frame.
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((8, 2, size[0] - 8, size[1] - 2), fill=255)
    pixels = gray.load()
    mask_pixels = mask.load()

    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    dots = ImageDraw.Draw(layer)
    spacing = 3
    for y in range(1, size[1] - 1, spacing):
        for x in range(1, size[0] - 1, spacing):
            if mask_pixels[x, y] < 128:
                continue
            darkness = 255 - pixels[x, y]
            # Near-white background pixels are omitted, leaving only the person.
            if darkness < 22:
                continue
            radius = 0.25 + (darkness / 255.0) * 1.45
            cx, cy = x, y
            dots.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=DOT,
            )

    # Fade the far edges slightly so the artwork blends into the paper.
    alpha = layer.getchannel("A")
    fade = Image.new("L", size, 255)
    fade_px = fade.load()
    for x in range(size[0]):
        edge = min(x / 34, (size[0] - 1 - x) / 34, 1)
        factor = max(0, min(1, edge))
        for y in range(size[1]):
            fade_px[x, y] = int(255 * factor)
    alpha = ImageChops.multiply(alpha, fade)
    layer.putalpha(alpha)

    canvas.alpha_composite(layer, (W - size[0] - 32, 25))


def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Portrait source not found: {SOURCE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (W, H), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=28, outline="#DEDAD0", width=2)

    draw.ellipse((56, 52, 68, 64), fill=BLUE)
    draw.text((84, 43), "SOFTWARE TINKERER  /  FULL-STACK DEVELOPER", font=mono, fill=INK)
    draw.text((60, 105), "Sahitya", font=serif, fill=INK)
    draw.text((60, 210), "Thakurela", font=serif, fill=INK)
    draw.rounded_rectangle((62, 330, 120, 336), radius=3, fill=BLUE)
    draw.text((62, 350), "Full-stack developer. My side projects have side projects.", font=sans, fill="#42434A")
    draw.text((62, 393), "B.TECH CSE @ JSS ACADEMY  ·  GDG WEB DEVELOPER  ·  NOIDA, INDIA", font=mono, fill=MUTED)

    draw_dot_portrait(canvas)
    canvas.convert("RGB").save(OUTPUT, format="PNG", optimize=True)
    print(f"Rendered dotted portrait hero: {OUTPUT}")


if __name__ == "__main__":
    from PIL import ImageChops
    main()
