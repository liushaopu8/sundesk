#!/usr/bin/env python3
"""Generate ic_launcher.png and new_floating_window.png with pure white backgrounds.

ic_launcher.png: Blue rounded rect + white computer/phone (matches adaptive icon foreground)
new_floating_window.png: White square + blue circle outline + dark line-art computer/phone
"""
from __future__ import annotations
import os
from PIL import Image, ImageDraw

REPO = os.path.join("flutter", "android", "app", "src", "main", "res")
SIZE = 512  # output resolution

WHITE = (255, 255, 255, 255)
BLUE = (33, 150, 243, 255)       # #2196F3
DARK = (51, 51, 51, 255)         # #333333


def draw_launcher(size: int) -> Image.Image:
    """Blue rounded rect + white computer/phone on white background."""
    s = size / 512.0
    img = Image.new("RGBA", (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    # Blue rounded rectangle (with padding from edge)
    pad = int(40 * s)
    radius = int(80 * s)
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=radius,
        fill=BLUE,
    )

    # --- Computer monitor ---
    mx = int(120 * s)
    my = int(105 * s)
    mw = int(195 * s)
    mh = int(165 * s)
    mr = int(18 * s)
    draw.rounded_rectangle([mx, my, mx + mw, my + mh], radius=mr, fill=WHITE)
    # Screen inner
    si = int(18 * s)
    draw.rectangle([mx + si, my + si, mx + mw - si, my + mh - si], fill=BLUE)
    # Stand
    stand_w = int(28 * s)
    stand_h = int(36 * s)
    sx = mx + (mw - stand_w) // 2
    sy = my + mh
    draw.rectangle([sx, sy, sx + stand_w, sy + stand_h], fill=WHITE)
    # Base
    base_w = int(105 * s)
    base_h = int(18 * s)
    bx = mx + (mw - base_w) // 2
    by = sy + stand_h
    draw.rounded_rectangle([bx, by, bx + base_w, by + base_h], radius=int(8 * s), fill=WHITE)

    # --- Phone ---
    px = int(285 * s)
    py = int(95 * s)
    pw = int(120 * s)
    ph = int(215 * s)
    pr = int(18 * s)
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=pr, fill=WHITE)
    # Phone screen
    ps = int(14 * s)
    draw.rectangle(
        [px + ps, py + int(36 * s), px + pw - ps, py + ph - int(42 * s)],
        fill=BLUE,
    )
    # Speaker slot
    sw = int(42 * s)
    sh = int(8 * s)
    sx2 = px + (pw - sw) // 2
    draw.rounded_rectangle([sx2, py + int(14 * s), sx2 + sw, py + int(14 * s) + sh], radius=int(4 * s), fill=BLUE)
    # Home button
    hb = int(18 * s)
    hb_x = px + (pw - hb) // 2
    hb_y = py + ph - int(30 * s)
    draw.ellipse([hb_x, hb_y, hb_x + hb, hb_y + hb], fill=BLUE)

    return img


def draw_floating_window(size: int) -> Image.Image:
    """White square + blue circle outline + dark line-art computer/phone."""
    s = size / 512.0
    img = Image.new("RGBA", (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    r = int(220 * s)
    lw = int(14 * s)

    # Blue circle outline
    draw.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        outline=BLUE,
        width=lw,
    )

    # --- Computer monitor (outline) ---
    line_w = int(13 * s)
    mx = int(130 * s)
    my = int(140 * s)
    mw = int(165 * s)
    mh = int(145 * s)
    draw.rounded_rectangle([mx, my, mx + mw, my + mh], radius=int(6 * s), outline=DARK, width=line_w)
    # Stand
    stand_cx = mx + mw // 2
    draw.line([(stand_cx, my + mh), (stand_cx, my + mh + int(35 * s))], fill=DARK, width=line_w)
    # Base
    base_half = int(38 * s)
    base_y = my + mh + int(35 * s)
    draw.line([(stand_cx - base_half, base_y), (stand_cx + base_half, base_y)], fill=DARK, width=line_w)

    # --- Phone (outline) ---
    px = int(245 * s)
    py = int(120 * s)
    pw = int(80 * s)
    ph = int(175 * s)
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=int(8 * s), outline=DARK, width=line_w)
    # Camera dot
    dot_r = int(6 * s)
    dot_cx = px + pw // 2
    dot_cy = py + ph - int(30 * s)
    draw.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=DARK,
    )

    return img


def main() -> int:
    out_launcher = os.path.join(REPO, "drawable", "ic_launcher.png")
    out_floating = os.path.join(REPO, "drawable", "new_floating_window.png")

    launcher = draw_launcher(SIZE)
    launcher.save(out_launcher)
    print(f"  wrote {out_launcher}  {SIZE}x{SIZE}")

    floating = draw_floating_window(SIZE)
    floating.save(out_floating)
    print(f"  wrote {out_floating}  {SIZE}x{SIZE}")

    print("done: 2 files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
