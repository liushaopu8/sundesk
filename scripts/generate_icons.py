#!/usr/bin/env python3
"""Regenerate all Android icons from the source ic_launcher.png (512×512).

Source: drawable/ic_launcher.png — blue rounded-rectangle with white
computer+phone icons on a white canvas background.

Generates for each density (mdpi / hdpi / xhdpi / xxhdpi / xxxhdpi):
  ic_launcher.png            — legacy app icon (resized source as-is)
  ic_launcher_round.png      — circle-cropped legacy icon (API ≤ 25)
  ic_launcher_foreground.png — adaptive-icon foreground (blue content on
                               transparent bg; white canvas removed via
                               corner flood-fill)
  ic_stat_logo.png           — notification small icon (white icons only
                               on transparent bg; system tints these)

Why these sizes (dp × density multiplier):
  ic_launcher / _round  = 48 dp  (legacy launcher fallback, API < 26)
  ic_launcher_foreground = 108 dp (adaptive icon layer; 72dp inner safe zone)
  ic_stat_logo           = 24 dp  (notification small icon in status bar)

Usage:
    python scripts/generate_icons.py
    python scripts/generate_icons.py /path/to/custom_source.png
"""

from __future__ import annotations

import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(
    REPO, "flutter", "android", "app", "src", "main", "res")
DEFAULT_SOURCE = os.path.join(RES_DIR, "drawable", "ic_launcher.png")

# dp base per icon type
ICON_DP = {
    "ic_launcher_foreground": 108,
    "ic_launcher": 48,
    "ic_launcher_round": 48,
    "ic_stat_logo": 24,
}

# density → multiplier
DENSITIES = {
    "mdpi": 1.0,
    "hdpi": 1.5,
    "xhdpi": 2.0,
    "xxhdpi": 3.0,
    "xxxhdpi": 4.0,
}

# Pixels with R,G,B all above this are considered "white-ish".
WHITE_THRESH = 200


# ---------------------------------------------------------------------------
# Canvas detection – flood-fill from image border
# ---------------------------------------------------------------------------

def _canvas_mask(arr: np.ndarray) -> np.ndarray:
    """BFS from border to find white canvas pixels.

    The source has a blue rounded-rectangle centred on a white canvas.
    White pixels connected to the image edge = canvas; white pixels
    surrounded by blue = the icon foreground (computer + phone).
    """
    h, w = arr.shape[:2]
    is_white = (
        (arr[:, :, 0] > WHITE_THRESH)
        & (arr[:, :, 1] > WHITE_THRESH)
        & (arr[:, :, 2] > WHITE_THRESH)
    )

    visited = np.zeros((h, w), dtype=bool)
    mask = np.zeros((h, w), dtype=bool)
    queue: deque = deque()

    # Seed from every border pixel that is white
    for y in range(h):
        for x in (0, w - 1):
            if is_white[y, x] and not visited[y, x]:
                visited[y, x] = True
                queue.append((y, x))
    for x in range(w):
        for y in (0, h - 1):
            if is_white[y, x] and not visited[y, x]:
                visited[y, x] = True
                queue.append((y, x))

    while queue:
        y, x = queue.popleft()
        if is_white[y, x]:
            mask[y, x] = True
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if (
                    0 <= ny < h
                    and 0 <= nx < w
                    and not visited[ny, nx]
                    and is_white[ny, nx]
                ):
                    visited[ny, nx] = True
                    queue.append((ny, nx))

    return mask


# ---------------------------------------------------------------------------
# Icon extraction
# ---------------------------------------------------------------------------

def _extract_foreground(source_arr: np.ndarray, cmask: np.ndarray) -> Image.Image:
    """Blue content + white icons on transparent background.

    Canvas (white corners) becomes transparent; the blue rounded-rectangle
    and white icon pixels inside it are kept as-is.
    """
    result = source_arr.copy()
    result[cmask, 3] = 0  # alpha → 0 for canvas
    return Image.fromarray(result)


def _extract_notification(source_arr: np.ndarray, cmask: np.ndarray) -> Image.Image:
    """White icon pixels only, on transparent background.

    Android tints notification small icons, so the source must be a single
    colour (white) on transparent.  We keep white-ish pixels that are NOT
    canvas (i.e. the computer + phone shapes inside the blue area).
    """
    h, w = source_arr.shape[:2]
    result = np.zeros((h, w, 4), dtype=np.uint8)

    is_white = (
        (source_arr[:, :, 0] > WHITE_THRESH)
        & (source_arr[:, :, 1] > WHITE_THRESH)
        & (source_arr[:, :, 2] > WHITE_THRESH)
    )
    icon = is_white & ~cmask  # white pixels inside the blue area
    result[icon] = [255, 255, 255, 255]
    return Image.fromarray(result)


def _circle_crop(img: Image.Image) -> Image.Image:
    """Apply a circular alpha mask (for ic_launcher_round on API ≤ 25)."""
    s = img.size
    mask = Image.new("L", s, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, s[0] - 1, s[1] - 1), fill=255)
    out = Image.new("RGBA", s, (0, 0, 0, 0))
    out.paste(img, mask=mask)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    source = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE
    if not os.path.isfile(source):
        print(f"error: source not found: {source}")
        return 1

    src = Image.open(source).convert("RGBA")
    src.load()
    arr = np.array(src)
    cmask = _canvas_mask(arr)

    print(f"source: {source}  ({src.size[0]}×{src.size[1]})")
    print(f"canvas pixels (white bg removed): {cmask.sum():,} / {cmask.size:,}")

    fg_full = _extract_foreground(arr, cmask)
    notif_full = _extract_notification(arr, cmask)

    written = 0
    for bucket, mult in DENSITIES.items():
        out_dir = os.path.join(RES_DIR, f"mipmap-{bucket}")
        print(f"\n{bucket}:")
        for name, dp in ICON_DP.items():
            side = int(round(dp * mult))

            if name == "ic_launcher":
                # Legacy — resized source as-is (blue rounded-rect + white bg)
                img = src.resize((side, side), Image.LANCZOS)
            elif name == "ic_launcher_round":
                # Legacy round — circle-cropped legacy icon
                legacy = src.resize((side, side), Image.LANCZOS)
                img = _circle_crop(legacy)
            elif name == "ic_launcher_foreground":
                # Adaptive icon foreground — content on transparent bg
                img = fg_full.resize((side, side), Image.LANCZOS)
            elif name == "ic_stat_logo":
                # Notification — white icons on transparent bg
                img = notif_full.resize((side, side), Image.LANCZOS)
            else:
                img = src.resize((side, side), Image.LANCZOS)

            out = os.path.join(out_dir, f"{name}.png")
            img.save(out, "PNG")
            written += 1
            print(f"  {name}.png  {side}×{side}")

    print(f"\ndone: {written} files written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
