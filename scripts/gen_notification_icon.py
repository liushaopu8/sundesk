#!/usr/bin/env python3
"""Generate ic_stat_logo notification icons at all densities.

Design: solid blue circle background (#2196F3) with simplified white
computer-monitor + phone icon. Clean and recognizable at small sizes.
"""
from __future__ import annotations
import os
from PIL import Image, ImageDraw

REPO = os.path.join("flutter", "android", "app", "src", "main", "res")
DENS = {"mdpi": 1.0, "hdpi": 1.5, "xhdpi": 2.0, "xxhdpi": 3.0, "xxxhdpi": 4.0}
BASE_SIZE = 24  # dp base for notification icons
BG_COLOR = (33, 150, 243, 255)  # #2196F3 blue circle
FG_COLOR = (255, 255, 255, 255)  # white icons
TRANSPARENT = (0, 0, 0, 0)


def draw_notification_icon(size: int) -> Image.Image:
    """Draw a clean notification icon at the given pixel size."""
    img = Image.new("RGBA", (size, size), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    s = size / 24.0

    # Blue circle background
    draw.ellipse([0, 0, size - 1, size - 1], fill=BG_COLOR)

    # --- Computer monitor (left) ---
    mx, my = int(3 * s), int(5 * s)
    mw, mh = int(10 * s), int(8 * s)
    r = max(1, int(1.2 * s))
    draw.rounded_rectangle([mx, my, mx + mw, my + mh], radius=r, fill=FG_COLOR)
    # Screen (blue)
    draw.rectangle([int(4 * s), int(6 * s), int(12 * s), int(11.5 * s)], fill=BG_COLOR)
    # Stand
    draw.rectangle([int(6.5 * s), int(13 * s), int(9.5 * s), int(14.5 * s)], fill=FG_COLOR)
    # Base
    draw.rounded_rectangle([int(5 * s), int(14.5 * s), int(11 * s), int(15.5 * s)],
                           radius=max(1, int(0.5 * s)), fill=FG_COLOR)

    # --- Phone (right) ---
    px, py = int(14 * s), int(4 * s)
    pw, ph = int(7 * s), int(11 * s)
    pr = max(1, int(1 * s))
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=pr, fill=FG_COLOR)
    # Screen (blue)
    draw.rectangle([int(14.8 * s), int(5 * s), int(20.3 * s), int(13 * s)], fill=BG_COLOR)
    # Speaker
    draw.rounded_rectangle([int(16 * s), int(5 * s), int(18.5 * s), int(5.6 * s)],
                           radius=max(1, int(0.3 * s)), fill=BG_COLOR)
    # Home button
    hb = max(1, int(1.2 * s))
    draw.ellipse([int(16.4 * s), int(13.5 * s), int(16.4 * s) + hb, int(13.5 * s) + hb], fill=BG_COLOR)

    return img


def main() -> int:
    written = 0
    for dname, mult in DENS.items():
        out_dir = os.path.join(REPO, f"mipmap-{dname}")
        size = int(round(BASE_SIZE * mult))
        icon = draw_notification_icon(size)
        out = os.path.join(out_dir, "ic_stat_logo.png")
        icon.save(out)
        written += 1
        print(f"  {dname:6s} ic_stat_logo.png  {size:3d}px")
    print(f"done: {written} files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
