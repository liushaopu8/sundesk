#!/usr/bin/env python3
"""Generate all mipmap icons from drawable/ic_launcher.png source.

Produces:
- mipmap-*/ic_launcher.png (legacy launcher, white bg)
- mipmap-*/ic_launcher_round.png (round launcher, white bg)
- mipmap-*/ic_stat_logo.png (notification icon, white bg)

All from the same 512x512 source with white background.
"""
from __future__ import annotations
import os
from PIL import Image

REPO = os.path.join("flutter", "android", "app", "src", "main", "res")
SRC = os.path.join(REPO, "drawable", "ic_launcher.png")
DENS = {"mdpi": 1.0, "hdpi": 1.5, "xhdpi": 2.0, "xxhdpi": 3.0, "xxxhdpi": 4.0}

# (name, dp base) pairs
ICONS = {
    "ic_launcher": 48,
    "ic_launcher_round": 48,
    "ic_stat_logo": 24,
}


def main() -> int:
    src = Image.open(SRC).convert("RGBA")
    print(f"source: {src.size[0]}x{src.size[1]}")

    written = 0
    for dname, mult in DENS.items():
        out_dir = os.path.join(REPO, f"mipmap-{dname}")
        for name, dp in ICONS.items():
            size = int(round(dp * mult))
            resized = src.resize((size, size), Image.LANCZOS)
            out = os.path.join(out_dir, f"{name}.png")
            resized.save(out)
            written += 1
            print(f"  {dname:6s} {name:30s} {size:3d}px")

    print(f"done: {written} files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
