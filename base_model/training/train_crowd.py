"""
train_crowd.py — Train Crowd Density Model
Loads crowd_X.npy + crowd_y.npy
Regression task — predicts crowd count from image
Note: only 20 images available, so we heavily augment
"""

import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    CROWD_X, CROWD_Y, WEIGHTS_DIR,
    EPOCHS, LEARNING_RATE
)
import src.model_crowd as model_def

CROWD_IMG_SIZE = 256


def augment_crowd(X, y, n_augments=20):
    """
    Heavy augmentation since we only have 20 crowd images.
    Creates n_augments versions of each image.
    """
    X_aug, y_aug = [], []
    rng = np.random.default_rng(42)

    for img, count in zip(X, y):
        for _ in range(n_augments):
            aug = img.copy()

            # Random horizontal flip
            if rng.random() > 0.5:
                aug = aug[:, ::-1, :]

            # Random brightness
            factor = rng.uniform(0.7, 1.3)
            aug = np.clip(aug * factor, 0, 1)

            # Random crop and resize
            h, w = aug.shape[:2]
            crop = rng.integers(10, 30)
            aug = aug[crop:h-crop, crop:w-crop, :]
            aug = tf.image.resize(aug, [CROWD_IMG_SIZE, CROWD_IMG_SIZE]).numpy()

            # Random noise
            noise = rng.normal(0, 0.02, aug.shape).astype(np.float32)
            aug = np.clip(aug + noise, 0, 1)

            X_aug.append(aug)
            y_aug.append(count)

    return np.array(X_aug, dtype=np.float32), np.array(y_aug, dtype=np.float32)


def get_callbacks(name):
    return [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(WEIGHTS_DIR, f"{name}_model.keras"),
            monitor="val_mae", mode="min",
            save_best_only=True, verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_mae", patience=10,
            restore_best_weights=True, verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=4, min_lr=1e-7, verbose=1
        ),
    ]


def run():
    print("\n" + "=" * 55)
    print("  TRAINING — Crowd Density Model")
    print("=" * 55)

    # ── Load data ──────────────────────────────────────────────────────────
    print("\n  Loading data...")
    X = np.load(CROWD_X)
    y = np.load(CROWD_Y)

    # Resize to model input size
    if X.shape[1] != CROWD_IMG_SIZE:
        print(f"  Resizing from {X.shape[1]} to {CROWD_IMG_SIZE}...")
        X = tf.image.resize(X, [CROWD_IMG_SIZE, CROWD_IMG_SIZE]).numpy()

    print(f"  X={X.shape}  y={y.shape}")
    print(f"  Count range: min={y.min():.0f}  max={y.max():.0f}  mean={y.mean():.0f}")

    # ── Augment (only 20 images, need more) ───────────────────────────────
    print(f"\n  Augmenting {len(X)} images × 20 = {len(X)*20} samples...")
    X_aug, y_aug = augment_crowd(X, y, n_augments=20)
    print(f"  After augmentation: {X_aug.shape}")

    # ── Train/val split ────────────────────────────────────────────────────
    X_train, X_val, y_train, y_val = train_test_split(
        X_aug, y_aug, test_size=0.2, random_state=42
    )
    print(f"  Train={len(y_train)}  Val={len(y_val)}")

    # Normalise counts to 0-1 for stable training
    y_max = y_train.max()
    y_train_norm = y_train / y_max
    y_val_norm   = y_val   / y_max

    # ── Build model ────────────────────────────────────────────────────────
    model = model_def.build(img_size=CROWD_IMG_SIZE)
    model = model_def.compile(model, lr=LEARNING_RATE)
    model.summary()

    # ── Train ──────────────────────────────────────────────────────────────
    print("\n  Training...")
    model.fit(
        X_train, y_train_norm,
        validation_data=(X_val, y_val_norm),
        epochs=EPOCHS,
        batch_size=8,
        callbacks=get_callbacks("crowd"),
        verbose=1
    )

    # ── Evaluate ───────────────────────────────────────────────────────────
    print("\n  Final evaluation:")
    results = model.evaluate(X_val, y_val_norm, verbose=0)
    for name, val in zip(model.metrics_names, results):
        print(f"    {name}: {val:.4f}")

    print(f"\n  Best model saved → {WEIGHTS_DIR}/crowd_model.keras")
    print(f"  Note: predictions are normalised (divide by {y_max:.0f} to get count)")


if __name__ == "__main__":
    run()