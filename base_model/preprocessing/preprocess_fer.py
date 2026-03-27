"""
Stream 3 — Facial Expression Preprocessing
Dataset : FER-2013
Output  : fer_X.npy  shape (N, 64, 64, 3)   RGB normalised
          fer_y.npy  shape (N,)  0=Calm  1=Aggressive
          (angry / disgust / fear → 1,  happy / neutral / sad / surprise → 0)

Note: FER images are 48x48 pixels. We resize to 64x64 (not 224x224)
      to keep RAM usage low while still giving the model enough detail.
"""

import os
import sys
import numpy as np
from PIL import Image, ImageEnhance
from tqdm import tqdm
import random

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    FER_DIR, FER_X, FER_Y,
    AGGRESSIVE_EMOTIONS, IMAGE_EXTS
)

FER_IMG_SIZE = 64    # smaller size keeps RAM under control


# ─────────────────────────────────────────────
# Helper: augment an image (mild, for training)
# ─────────────────────────────────────────────
def augment(img: Image.Image) -> Image.Image:
    """
    Applies random horizontal flip, brightness, and rotation.
    Only used on training images.
    """
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # Random brightness ±20%
    factor = random.uniform(0.8, 1.2)
    img = ImageEnhance.Brightness(img).enhance(factor)

    # Random rotation ±15°
    angle = random.uniform(-15, 15)
    img = img.rotate(angle, fillcolor=(128, 128, 128))

    return img


# ─────────────────────────────────────────────
# Helper: load one image → numpy array
# ─────────────────────────────────────────────
def load_image(path: str, augment_img: bool = False) -> np.ndarray:
    img = Image.open(path).convert("RGB")
    if augment_img:
        img = augment(img)
    img = img.resize((FER_IMG_SIZE, FER_IMG_SIZE), Image.BILINEAR)
    return np.array(img, dtype=np.float32) / 255.0


def count_images(split_dir: str) -> int:
    total = 0
    if not os.path.exists(split_dir):
        return 0
    for emotion in os.listdir(split_dir):
        emo_path = os.path.join(split_dir, emotion)
        if os.path.isdir(emo_path):
            total += len([f for f in os.listdir(emo_path)
                          if f.lower().endswith(IMAGE_EXTS)])
    return total


def run():
    print("\n" + "=" * 55)
    print("  STREAM 3 — Facial Expression Preprocessing (FER-2013)")
    print("=" * 55)

    train_dir = os.path.join(FER_DIR, "train")
    test_dir  = os.path.join(FER_DIR, "test")

    total = count_images(train_dir) + count_images(test_dir)
    if total == 0:
        print("\n[ERROR] No images found. Check FER_DIR in config.py")
        return

    print(f"  Total images: {total}  →  size per image: {FER_IMG_SIZE}x{FER_IMG_SIZE}")

    # Pre-allocate memory-mapped arrays
    X_map = np.lib.format.open_memmap(
        FER_X, mode='w+', dtype=np.float32,
        shape=(total, FER_IMG_SIZE, FER_IMG_SIZE, 3)
    )
    y_map = np.lib.format.open_memmap(
        FER_Y, mode='w+', dtype=np.int8, shape=(total,)
    )

    idx = 0
    for split, split_dir, do_aug in [("train", train_dir, True),
                                      ("test",  test_dir,  False)]:
        if not os.path.exists(split_dir):
            print(f"  [SKIP] {split_dir}")
            continue

        print(f"\n  [{split}]")
        for emotion in sorted(os.listdir(split_dir)):
            emo_path = os.path.join(split_dir, emotion)
            if not os.path.isdir(emo_path):
                continue
            label  = AGGRESSIVE_EMOTIONS.get(emotion.lower(), 0)
            images = [f for f in os.listdir(emo_path)
                      if f.lower().endswith(IMAGE_EXTS)]
            print(f"    {emotion:<10} label={label}  {len(images)} images")

            for img_file in tqdm(images, desc=f"    {emotion}", leave=False):
                arr = load_image(os.path.join(emo_path, img_file), do_aug)
                X_map[idx] = arr
                y_map[idx] = label
                idx += 1

            X_map.flush()
            y_map.flush()

    print(f"\n  Saved fer_X.npy  shape={X_map.shape}")
    aggressive = int(y_map[:idx].sum())
    print(f"  Done. Total={idx}  Aggressive={aggressive}  Calm={idx - aggressive}")
    size_mb = (idx * FER_IMG_SIZE * FER_IMG_SIZE * 3 * 4) / 1e6
    print(f"  File size ≈ {size_mb:.0f} MB")


if __name__ == "__main__":
    run()