#!/usr/bin/env python3
"""Build-time renderer for the gta6-meme-x-01 meme (NOT run by the grader).

Renders meme.png, 1200x675: Vice City sunset, huge Anton "PAID" (GTA WASTED
parody), the make.fun ghost badge large on the left, GTA 6 price joke below,
make.fun strip at the bottom. No em-dashes anywhere in any text.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 675
HERE = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."


def _asset(name):
    """Assets live under assets/ in the repo; fall back to the script dir."""
    for p in (f"{HERE}/assets/{name}", f"{HERE}/{name}"):
        if os.path.exists(p):
            return p
    return f"{HERE}/assets/{name}"


ANTON = _asset("Anton-Regular.ttf")
GHOST = _asset("mark-1024.png")
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Sunset gradient stops (y fraction, RGB): deep magenta -> hot pink -> orange -> dark ground
STOPS = [
    (0.00, (122, 16, 92)),
    (0.30, (196, 24, 110)),
    (0.55, (255, 64, 120)),
    (0.72, (255, 122, 40)),
    (0.86, (255, 166, 66)),
    (1.00, (46, 10, 52)),
]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(w, h):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        f = y / (h - 1)
        for i in range(len(STOPS) - 1):
            f0, c0 = STOPS[i]
            f1, c1 = STOPS[i + 1]
            if f0 <= f <= f1:
                t = 0 if f1 == f0 else (f - f0) / (f1 - f0)
                col = lerp(c0, c1, t)
                break
        else:
            col = STOPS[-1][1]
        for x in range(w):
            px[x, y] = col
    return img


def fit_font(path, size, text, max_w, draw):
    """Shrink font until text fits max_w; returns (font, width)."""
    while size > 10:
        f = ImageFont.truetype(path, size)
        w = draw.textlength(text, font=f)
        if w <= max_w:
            return f, w
        size -= 1
    f = ImageFont.truetype(path, size)
    return f, draw.textlength(text, font=f)


def _bezier(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def _bezier3(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0]
             + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0])
        y = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1]
             + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1])
        pts.append((x, y))
    return pts


def draw_palm(d, x, base_y, h, lean, col):
    """Palm silhouette: curved trunk + sickle-shaped drooping leaf blades.
    Each blade sweeps up-out first, then bends down steeply, so the fan
    keeps open gaps instead of merging into a dome outline."""
    top_x = x + lean
    top_y = base_y - h
    # trunk: gentle curve
    pts = []
    for i in range(9):
        t = i / 8
        pts.append((x + lean * t * t, base_y - h * t))
    d.line(pts, fill=col, width=10, joint="curve")
    # blades: cubic beziers, tapered polygons
    for ang in (-165, -135, -105, -75, -45, -15):
        r = h * 0.58
        ca = math.cos(math.radians(ang))
        p1 = (top_x + ca * 0.40 * r, top_y - 0.45 * r)
        p2 = (top_x + ca * 0.90 * r, top_y + 0.05 * r)
        tip = (top_x + ca * r, top_y + 0.35 * r)
        centre = _bezier3((top_x, top_y), p1, p2, tip, 24)
        left, right = [], []
        for i, (px, py) in enumerate(centre):
            t = i / (len(centre) - 1)
            nx, ny = centre[min(i + 1, len(centre) - 1)]
            ox, oy = centre[max(i - 1, 0)]
            dx, dy = nx - ox, ny - oy
            ln = math.hypot(dx, dy) or 1
            wdt = 5.5 * (1 - t) + 0.5
            left.append((px - dy / ln * wdt, py + dx / ln * wdt))
            right.append((px + dy / ln * wdt, py - dx / ln * wdt))
        d.polygon(left + right[::-1], fill=col)
    # coconuts
    d.ellipse([top_x - 8, top_y + 2, top_x + 8, top_y + 14], fill=col)


def main():
    img = gradient(W, H)
    d = ImageDraw.Draw(img)

    # Sun: soft glow + pale disc, centre-right behind PAID
    sun_cx, sun_cy, sun_r = 640, 200, 150
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r, a in ((260, 26), (220, 40), (185, 60)):
        gd.ellipse([sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r], fill=(255, 220, 140, a))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
              fill=(255, 233, 168))
    # sun stripes (retro sunset cut lines) across the lower half of the disc
    for yy, hh in ((285, 7), (308, 9), (333, 11)):
        d.rectangle([sun_cx - sun_r, yy, sun_cx + sun_r, yy + hh], fill=(255, 122, 40))

    # Birds, upper right: smooth gull curves
    for bx, by, s in ((1020, 120, 16), (1075, 95, 12), (960, 88, 10)):
        d.line(_bezier((bx - s, by), (bx - s * 0.5, by - s * 0.7), (bx, by)),
               fill=(30, 8, 40), width=3, joint="curve")
        d.line(_bezier((bx, by), (bx + s * 0.5, by - s * 0.7), (bx + s, by)),
               fill=(30, 8, 40), width=3, joint="curve")

    # Skyline + palm silhouettes along the bottom (behind ghost and text)
    SIL = (26, 7, 38)
    ground_y = 632
    buildings = [
        (0, 96, 150), (95, 62, 190), (180, 110, 130), (285, 74, 210),
        (395, 120, 120), (505, 84, 190), (585, 128, 110), (700, 70, 200),
        (765, 104, 140), (860, 66, 200), (920, 118, 130), (1030, 78, 190),
        (1100, 112, 150),
    ]
    for bx, bw, bh in buildings:
        d.rectangle([bx, ground_y - bh, bx + bw, ground_y], fill=SIL)
    # antennas on two towers
    d.line([(445, ground_y - 120), (445, ground_y - 158)], fill=SIL, width=5)
    d.ellipse([441, ground_y - 164, 449, ground_y - 156], fill=(255, 90, 60))
    d.line([(1085, ground_y - 78), (1085, ground_y - 108)], fill=SIL, width=5)
    # lit windows: a few small warm dots
    import random
    random.seed(7)
    for bx, bw, bh in buildings:
        for _ in range(bw // 30):
            wx = bx + random.randint(8, max(9, bw - 12))
            wy = ground_y - random.randint(14, max(15, bh - 10))
            d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 190, 90))
    # palms: one tall on the right, one shorter mid-right
    draw_palm(d, 1000, ground_y, 250, 30, SIL)
    draw_palm(d, 700, ground_y, 180, -26, SIL)

    # Ghost: soft white glow behind, then the badge pasted with its alpha
    ghost = Image.open(GHOST).convert("RGBA")
    GH = 320
    ghost = ghost.resize((GH, GH), Image.LANCZOS)
    gx, gy = 26, 82
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse([gx - 26, gy - 26, gx + GH + 26, gy + GH + 26], fill=(255, 255, 255, 90))
    halo = halo.filter(ImageFilter.GaussianBlur(22))
    base = img.convert("RGBA")
    base = Image.alpha_composite(base, halo)
    base.paste(ghost, (gx, gy), ghost)
    img = base.convert("RGB")
    d = ImageDraw.Draw(img)

    # Top line (Anton has no middle-dot glyph, so use a plain hyphen)
    top_text = "GRAND THEFT AUTO VI - MAY 26, 2026"
    top_font, _ = fit_font(ANTON, 44, top_text, 900, d)
    d.text((600, 34), top_text, font=top_font, fill=(255, 255, 255),
           anchor="ma", stroke_width=2, stroke_fill=(20, 5, 30))

    # PAID: huge Anton, white fill ~92% alpha, thick black outline, GTA WASTED style
    paid_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(paid_layer)
    paid_font = ImageFont.truetype(ANTON, 235)
    pd.text((600, 258), "PAID", font=paid_font, fill=(255, 255, 255, 235),
            anchor="mm", stroke_width=14, stroke_fill=(0, 0, 0, 235))
    img = Image.alpha_composite(img.convert("RGBA"), paid_layer).convert("RGB")
    d = ImageDraw.Draw(img)

    # Line below PAID
    sub = "GTA 6 costs $100. My agent already earned it on make.fun."
    sub_font, _ = fit_font(BOLD, 32, sub, 1060, d)
    d.text((600, 442), sub, font=sub_font, fill=(255, 255, 255),
           anchor="mm", stroke_width=2, stroke_fill=(15, 4, 25))

    # Bottom strip
    d.rectangle([0, 632, W, H], fill=(18, 4, 24))
    d.rectangle([0, 632, W, 635], fill=(255, 45, 149))
    strip = "make.fun: humans and their AI agents earn real money"
    strip_font, _ = fit_font(BOLD, 24, strip, 1060, d)
    d.text((600, 654), strip, font=strip_font, fill=(255, 255, 255), anchor="mm")

    img.save(f"{HERE}/meme.png")
    print(f"saved {HERE}/meme.png {img.size}")


if __name__ == "__main__":
    main()
