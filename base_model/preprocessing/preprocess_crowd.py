"""
Stream 4 — Crowd Density Map Preprocessing
Dataset : Crowd Counting Dataset
Output  : crowd_X.npy  shape (N, 512, 512, 3)   RGB image
          crowd_y.npy  shape (N,)                crowd count (regression target)

The model (CSRNet) takes an image and predicts a density map.
crowd_y holds the ground-truth head count read from crowds_counting.csv
or inferred from the subfolder name (0-1000, 1000-2000, etc.)
"""

import os
import sys
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    CROWD_DIR, CROWD_X, CROWD_Y,
    CROWD_SIZE, IMAGE_EXTS
)

# Density range folders → midpoint count used as label
RANGE_MIDPOINTS = {
    "0-1000":    500,
    "1000-2000": 1500,
    "2000-3000": 2500,
    "3000-4000": 3500,
    "4000-5000": 4500,
}


# ─────────────────────────────────────────────
# Helper: load image → (CROWD_SIZE, CROWD_SIZE, 3)
# ─────────────────────────────────────────────
def load_crowd_image(path: str) -> np.ndarray:
    img = Image.open(path).convert("RGB")
    img = img.resize((CROWD_SIZE, CROWD_SIZE), Image.BILINEAR)
    return np.array(img, dtype=np.float32) / 255.0


# ─────────────────────────────────────────────
# Strategy A: CSV-based loading
# crowds_counting.csv must have columns:
#   image_path, count
# ─────────────────────────────────────────────
def load_from_csv(csv_path: str, X: list, y: list) -> bool:
    if not os.path.exists(csv_path):
        return False

    df = pd.read_csv(csv_path)
    required = {'image_path', 'count'}
    if not required.issubset(df.columns):
        print(f"  [WARN] CSV missing columns. Found: {list(df.columns)}")
        print(f"         Expected at least: image_path, count")
        return False

    print(f"  Loading {len(df)} images from CSV")
    skipped = 0
    for _, row in tqdm(df.iterrows(), total=len(df), desc="  CSV"):
        img_path = os.path.join(CROWD_DIR, str(row['image_path']))
        if not os.path.exists(img_path):
            skipped += 1
            continue
        X.append(load_crowd_image(img_path))
        y.append(float(row['count']))

    if skipped:
        print(f"  [WARN] Skipped {skipped} missing images")
    return True


# ─────────────────────────────────────────────
# Strategy B: Folder-range-based loading
# Uses subfolder names like "0-1000", "1000-2000"
# as approximate crowd count labels
# ─────────────────────────────────────────────
def load_from_folders(X: list, y: list) -> bool:
    images_root = os.path.join(CROWD_DIR, "images")
    if not os.path.exists(images_root):
        return False

    subfolders = [d for d in os.listdir(images_root)
                  if os.path.isdir(os.path.join(images_root, d))]

    if not subfolders:
        return False

    print(f"  Found subfolders: {subfolders}")
    for subfolder in sorted(subfolders):
        count_label = RANGE_MIDPOINTS.get(subfolder, 0)
        folder_path = os.path.join(images_root, subfolder)
        imgs = [f for f in os.listdir(folder_path)
                if f.lower().endswith(IMAGE_EXTS)]
        print(f"  {subfolder:<12} → label={count_label}  {len(imgs)} images")

        for img_file in tqdm(imgs, desc=f"  {subfolder}", leave=False):
            path = os.path.join(folder_path, img_file)
            X.append(load_crowd_image(path))
            y.append(float(count_label))

    return True


# ─────────────────────────────────────────────
# Strategy C: Flat image folder fallback
# All images in CROWD_DIR root, no count info
# ─────────────────────────────────────────────
def load_flat_fallback(X: list, y: list) -> bool:
    imgs = [f for f in os.listdir(CROWD_DIR)
            if f.lower().endswith(IMAGE_EXTS)]
    if not imgs:
        return False

    print(f"  [Fallback] Loading {len(imgs)} images flat from {CROWD_DIR}")
    for img_file in tqdm(imgs, desc="  Flat"):
        path = os.path.join(CROWD_DIR, img_file)
        X.append(load_crowd_image(path))
        y.append(0.0)   # unknown count

    return True


# ─────────────────────────────────────────────
# Main preprocessing function
# ─────────────────────────────────────────────
def run():
    print("\n" + "=" * 55)
    print("  STREAM 4 — Crowd Density Preprocessing")
    print("=" * 55)

    if not os.path.exists(CROWD_DIR):
        print(f"\n[ERROR] CROWD_DIR not found: {CROWD_DIR}")
        return

    X, y = [], []
    csv_path = os.path.join(CROWD_DIR, "crowds_counting.csv")

    # Try loading strategies in order of preference
    if load_from_csv(csv_path, X, y):
        print("  Used strategy: CSV")
    elif load_from_folders(X, y):
        print("  Used strategy: range subfolders")
    elif load_flat_fallback(X, y):
        print("  Used strategy: flat folder")
    else:
        print("\n[ERROR] No crowd images found. Check CROWD_DIR in config.py")
        return

    if not X:
        print("\n[ERROR] No images loaded.")
        return

    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y, dtype=np.float32)

    print(f"\n  Saving {CROWD_X}  shape={X_arr.shape}")
    np.save(CROWD_X, X_arr)
    np.save(CROWD_Y, y_arr)

    print(f"  Done. Total={len(y_arr)}")
    print(f"  Count range: min={y_arr.min():.0f}  max={y_arr.max():.0f}  mean={y_arr.mean():.0f}")
    print(f"  File size ≈ {X_arr.nbytes / 1e9:.2f} GB")


if __name__ == "__main__":
    run()