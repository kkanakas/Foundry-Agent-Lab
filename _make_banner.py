"""
Generate the blog banner image for the Foundry Agent Lab blog post.
Output: blog-foundry-agent-lab-banner.png  (1300 x 500 px)
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# ── Canvas ──────────────────────────────────────────────────────────────────
W, H = 1300, 500
img = Image.new("RGB", (W, H), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# ── Background gradient (dark navy → rich blue) ──────────────────────────────
for y in range(H):
    t = y / H
    r = int(10 + t * 5)
    g = int(12 + t * 20)
    b = int(40 + t * 60)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# ── Diagonal accent band ─────────────────────────────────────────────────────
accent_poly = [
    (W * 0.55, 0),
    (W, 0),
    (W, H),
    (W * 0.62, H),
]
draw.polygon(accent_poly, fill=(0, 60, 120))

# ── Circuit / node-graph decoration (right side) ─────────────────────────────
NODE_COLOR = (0, 120, 212)        # Microsoft blue
LINE_COLOR = (0, 90, 170)
BRIGHT_NODE = (0, 168, 255)

nodes = [
    (900, 80),
    (1000, 160),
    (870, 230),
    (1050, 290),
    (950, 380),
    (1150, 200),
    (1200, 340),
    (1100, 100),
    (820, 340),
    (1000, 440),
]

edges = [
    (0, 1), (1, 2), (1, 3), (2, 4), (3, 5),
    (5, 6), (3, 6), (0, 7), (7, 5), (2, 8),
    (4, 9), (6, 9), (8, 4),
]

for a, b in edges:
    x1, y1 = nodes[a]
    x2, y2 = nodes[b]
    draw.line([(x1, y1), (x2, y2)], fill=LINE_COLOR, width=2)

for i, (nx, ny) in enumerate(nodes):
    r = 8 if i % 3 == 0 else 5
    color = BRIGHT_NODE if i % 3 == 0 else NODE_COLOR
    draw.ellipse([(nx - r, ny - r), (nx + r, ny + r)], fill=color)

# ── Horizontal rule beneath title area ───────────────────────────────────────
draw.rectangle([(60, 320), (660, 323)], fill=(0, 120, 212))

# ── Font loading — fall back gracefully ──────────────────────────────────────
FONT_PATHS_BOLD = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
]
FONT_PATHS_REG = [
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
]


def load_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


font_title_large = load_font(FONT_PATHS_BOLD, 52)
font_title_small = load_font(FONT_PATHS_BOLD, 42)
font_sub = load_font(FONT_PATHS_REG, 26)
font_tag = load_font(FONT_PATHS_REG, 22)
font_eyebrow = load_font(FONT_PATHS_REG, 20)

# ── Text: eyebrow ─────────────────────────────────────────────────────────────
draw.text((60, 80), "MICROSOFT FOUNDRY  ·  AGENT LAB", font=font_eyebrow,
          fill=(0, 168, 255))

# ── Text: main title (two lines) ─────────────────────────────────────────────
title_line1 = "Building AI Agents"
title_line2 = "with Microsoft Foundry"

draw.text((60, 120), title_line1, font=font_title_large, fill=(255, 255, 255))
draw.text((60, 185), title_line2, font=font_title_large, fill=(255, 255, 255))

# ── Text: subtitle ───────────────────────────────────────────────────────────
sub = "A progressive lab from Hello World to Self-Hosted"
draw.text((60, 265), sub, font=font_sub, fill=(180, 210, 255))

# ── Tag pills ────────────────────────────────────────────────────────────────
tags = ["#MicrosoftFoundry", "#AIAgents", "#ModelRouter", "#Python"]
pill_x = 60
pill_y = 345

for tag in tags:
    bbox = draw.textbbox((0, 0), tag, font=font_tag)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x, pad_y = 14, 7
    pill_w = tw + pad_x * 2
    pill_h = th + pad_y * 2
    # Rounded rect via ellipse corners
    draw.rounded_rectangle(
        [(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)],
        radius=14,
        fill=(0, 50, 100),
        outline=(0, 120, 212),
    )
    draw.text((pill_x + pad_x, pill_y + pad_y), tag, font=font_tag,
              fill=(0, 168, 255))
    pill_x += pill_w + 12

# ── Demo count badge ─────────────────────────────────────────────────────────
badge_x, badge_y = 60, 415
draw.rounded_rectangle(
    [(badge_x, badge_y), (badge_x + 230, badge_y + 50)],
    radius=10,
    fill=(0, 120, 212),
)
draw.text((badge_x + 16, badge_y + 12), "9 Progressive Demos  →", font=font_tag,
          fill=(255, 255, 255))

# ── Bottom accent line ────────────────────────────────────────────────────────
draw.rectangle([(0, H - 6), (W, H)], fill=(0, 120, 212))

# ── Save ─────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "blog-foundry-agent-lab-banner.png")
img.save(out, "PNG")
print(f"Banner saved → {out}  ({W}×{H} px)")
