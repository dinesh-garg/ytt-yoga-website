#!/usr/bin/env python3
"""
normalize_yoga_imgs.py
──────────────────────
Resizes all yoga pose PNGs to a uniform canvas so they display
at consistent visual size in the website.

Strategy:
  - Target canvas: TARGET_W × TARGET_H pixels
  - Each image is scaled to fit INSIDE the canvas (letterbox/pillarbox),
    preserving its aspect ratio.
  - The scaled image is centred on a transparent canvas.
  - Output files OVERWRITE the originals (originals are backed up first).

Usage:
  pip install Pillow
  python normalize_yoga_imgs.py

  # Optional: change TARGET_W / TARGET_H below, or pass as args:
  python normalize_yoga_imgs.py --width 800 --height 1000 --dir /path/to/yoga_imgs
"""

import argparse
import shutil
from pathlib import Path
from PIL import Image

# ── defaults ────────────────────────────────────────────────────────────────
DEFAULT_DIR    = Path("/Users/dgarg/Documents/GitHub/ytt-yoga-website/yoga_imgs")
TARGET_W       = 800   # px  ← tweak if you want a different size
TARGET_H       = 1000  # px  ← portrait works well for standing poses
BACKUP_SUFFIX  = "_orig"   # set to None to skip backup
# ────────────────────────────────────────────────────────────────────────────


def normalize(img_path: Path, target_w: int, target_h: int, backup: bool) -> None:
    with Image.open(img_path) as im:
        orig_w, orig_h = im.size
        orig_mode = im.mode

        # ── scale to fit inside the target canvas ────────────────────────
        scale = min(target_w / orig_w, target_h / orig_h)
        new_w = round(orig_w * scale)
        new_h = round(orig_h * scale)

        # Use LANCZOS for downscaling quality
        resized = im.resize((new_w, new_h), Image.LANCZOS)

        # ── create transparent canvas ─────────────────────────────────────
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))

        # Centre the resized image
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2

        if resized.mode == "RGBA":
            canvas.paste(resized, (paste_x, paste_y), mask=resized)
        else:
            canvas.paste(resized, (paste_x, paste_y))

        # ── backup original ───────────────────────────────────────────────
        if backup:
            backup_path = img_path.with_stem(img_path.stem + BACKUP_SUFFIX)
            if not backup_path.exists():
                shutil.copy2(img_path, backup_path)
                print(f"  ↳ backed up → {backup_path.name}")

        # ── save (overwrite original) ─────────────────────────────────────
        # PNG supports RGBA natively
        canvas.save(img_path, "PNG", optimize=False)

        print(f"  ✓ {img_path.name}  ({orig_w}×{orig_h} → {new_w}×{new_h} on {target_w}×{target_h})")


def main():
    parser = argparse.ArgumentParser(description="Normalize yoga pose images to uniform canvas size.")
    parser.add_argument("--dir",    default=str(DEFAULT_DIR), help="Path to yoga_imgs folder")
    parser.add_argument("--width",  type=int, default=TARGET_W, help="Canvas width in px  (default 800)")
    parser.add_argument("--height", type=int, default=TARGET_H, help="Canvas height in px (default 1000)")
    parser.add_argument("--no-backup", action="store_true", help="Skip backing up originals")
    args = parser.parse_args()

    imgs_dir = Path(args.dir)
    if not imgs_dir.is_dir():
        print(f"ERROR: directory not found: {imgs_dir}")
        return

    png_files = sorted(imgs_dir.glob("*.png"))
    # Exclude any backup files from a previous run
    png_files = [p for p in png_files if BACKUP_SUFFIX not in p.stem]

    if not png_files:
        print("No .png files found.")
        return

    print(f"\nNormalizing {len(png_files)} images → {args.width}×{args.height}px canvas")
    print(f"Directory  : {imgs_dir}")
    print(f"Backup     : {'no' if args.no_backup else 'yes (suffix: ' + BACKUP_SUFFIX + ')'}\n")

    for p in png_files:
        normalize(p, args.width, args.height, backup=not args.no_backup)

    print(f"\nDone. All images are now {args.width}×{args.height}px.")
    print("(Your HTML already uses object-fit:contain, so no HTML changes needed.)\n")


if __name__ == "__main__":
    main()
