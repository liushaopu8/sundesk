#!/usr/bin/env python3
"""Regenerate ic_launcher_foreground PNGs.

The current foreground has a white outer area that creates a "grey" look
against the adaptive-icon white background. This script regenerates all
density PNGs with a pure transparent background and slightly larger
computer+phone icons.
"""
from __future__ import annotations
import os
from PIL import Image, ImageDraw

REPO = os.path.join("flutter", "android", "app", "src", "main", "res")
DENS = {"mdpi": 1.0, "hdpi": 1.5, "xhdpi": 2.0, "xxhdpi": 3.0, "xxxhdpi": 4.0}
# Adaptive icon foreground is 108dp base
BASE = 108
TRANSPARENT = (0, 0, 0, 0)
BLUE = (33, 150, 243, 255)       # #2196F3
WHITE = (255, 255, 255, 255)
TRANSPARENT_BLUE = (33, 150, 243, 0)  # for "screen" areas showing background


def draw_foreground(size: int) -> Image.Image:
    s = size / 108.0  # scale factor from 108dp base
    img = Image.new("RGBA", (size, size), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Blue rounded rectangle - the main icon background
    # Safe zone is inner 66% of 108dp = ~71dp, with some padding
    # Current design: blue rounded rect filling most of the canvas
    pad = int(8 * s)
    radius = int(18 * s)
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=radius,
        fill=BLUE,
    )

    # --- Computer monitor (left side, slightly bigger, shifted right) ---
    # Screen frame
    mx = int(26 * s)
    my = int(22 * s)
    mw = int(44 * s)
    mh = int(38 * s)
    mr = int(4 * s)
    draw.rounded_rectangle([mx, my, mx + mw, my + mh], radius=mr, fill=WHITE)
    # Screen inner (blue - shows "background" through screen)
    si_pad = int(4 * s)
    draw.rectangle(
        [mx + si_pad, my + si_pad, mx + mw - si_pad, my + mh - si_pad],
        fill=BLUE,
    )
    # Stand
    stand_w = int(6 * s)
    stand_h = int(8 * s)
    sx = mx + (mw - stand_w) // 2
    sy = my + mh
    draw.rectangle([sx, sy, sx + stand_w, sy + stand_h], fill=WHITE)
    # Base
    base_w = int(24 * s)
    base_h = int(4 * s)
    bx = mx + (mw - base_w) // 2
    by = sy + stand_h
    draw.rounded_rectangle(
        [bx, by, bx + base_w, by + base_h],
        radius=max(1, int(2 * s)),
        fill=WHITE,
    )

    # --- Phone (right side, slightly bigger, shifted right) ---
    px = int(66 * s)
    py = int(20 * s)
    pw = int(28 * s)
    ph = int(48 * s)
    pr = int(4 * s)
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=pr, fill=WHITE)
    # Phone screen (blue)
    ps_pad = int(3 * s)
    draw.rectangle(
        [px + ps_pad, py + int(8 * s), px + pw - ps_pad, py + ph - int(10 * s)],
        fill=BLUE,
    )
    # Speaker slot at top
    sw = int(10 * s)
    sh = int(2 * s)
    sx2 = px + (pw - sw) // 2
    draw.rounded_rectangle(
        [sx2, py + int(3 * s), sx2 + sw, py + int(3 * s) + sh],
        radius=max(1, int(1 * s)),
        fill=BLUE,
    )
    # Home button at bottom
    hb_size = int(4 * s)
    hb_x = px + (pw - hb_size) // 2
    hb_y = py + ph - int(7 * s)
    draw.ellipse(
        [hb_x, hb_y, hb_x + hb_size, hb_y + hb_size],
        fill=BLUE,
    )

    return img


def main() -> int:
    written = 0
    for dname, mult in DENS.items():
        out_dir = os.path.join(REPO, f"mipmap-{dname}")
        size = int(round(BASE * mult))
        icon = draw_foreground(size)
        out = os.path.join(out_dir, "ic_launcher_foreground.png")
        icon.save(out)
        written += 1
        print(f"  {dname:6s} ic_launcher_foreground.png  {size:3d}px")
    print(f"done: {written} files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
