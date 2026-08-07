#!/usr/bin/env python3
"""Regenerate all SunDesk mipmap icons with adaptive-icon safe-zone padding.

The source new_launcher.png has a diamond whose tips nearly touch the canvas
edges. On API 26+ the adaptive icon masks the outer ~33% of the 108dp
foreground, clipping those tips. This script extracts the diamond (removes
white bg), scales it to fit inside the safe zone, and re-writes all 20 files.
"""
from __future__ import annotations
import os
from PIL import Image

REPO = os.path.join("flutter", "android", "app", "src", "main", "res")
SRC = os.path.join(REPO, "drawable", "new_launcher.png")

DENS = {"mdpi": 1.0, "hdpi": 1.5, "xhdpi": 2.0, "xxhdpi": 3.0, "xxxhdpi": 4.0}
# name -> (dp base, fraction of canvas to fill, background)
FG   = {"ic_launcher_foreground": (108, 0.58, (0, 0, 0, 0))}
LEG  = {"ic_launcher": (48, 0.72, (255, 255, 255, 255)),
        "ic_launcher_round": (48, 0.72, (255, 255, 255, 255))}
NOTI = {"ic_stat_logo": (24, 0.72, (255, 255, 255, 255))}


def content_bbox(img: Image.Image) -> tuple:
    """Bounding box of all non-white (RGB < 250) pixels."""
    w, h = img.size
    px = img.load()
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r < 250 or g < 250 or b < 250:
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def main() -> int:
    src = Image.open(SRC).convert("RGBA")
    cmin, rmin, cmax, rmax = content_bbox(src)
    diamond = src.crop((cmin, rmin, cmax + 1, rmax + 1))
    print(f"diamond bbox ({cmin},{rmin})-({cmax},{rmax})  size {diamond.size}")

    written = 0
    for dname, mult in DENS.items():
        out_dir = os.path.join(REPO, f"mipmap-{dname}")
        for group in (FG, LEG, NOTI):
            for name, (dp, frac, bg) in group.items():
                size = int(round(dp * mult))
                canvas = Image.new("RGBA", (size, size), bg)
                max_side = int(size * frac)
                d = diamond.copy()
                d.thumbnail((max_side, max_side), Image.LANCZOS)
                ox = (size - d.width) // 2
                oy = (size - d.height) // 2
                canvas.paste(d, (ox, oy))
                out = os.path.join(out_dir, f"{name}.png")
                canvas.save(out)
                written += 1
                print(f"  {dname:6s} {name:30s} {size:3d}px  diamond {d.size}")
    print(f"done: {written} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
