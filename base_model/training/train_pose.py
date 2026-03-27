"""
train_pose.py — Train Body Pose Model
Loads pose_X.npy + pose_y.npy
Note: pose dataset has only label=0 (NonViolence) from CCTV Human Pose.
We augment with synthetic violent poses (mirrored + jittered sequences)
to create a balanced dataset.
"""

import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
import tensorflow as tf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    POSE_X, POSE_Y, WEIGHTS_DIR,
    BATCH_SIZE, EPOCHS, LEARNING_RATE
)
import src.model_pose as model_def


def augment_violent_poses(X_calm: np.ndarray,
                           n_samples: int) -> np.ndarray:
    """
    Synthesises 'violent' pose sequences by applying:
    - Large random jitter (simulates fast chaotic motion)
    - Random flipping
    - Speed-up (skip frames = faster motion)
    This is a simple heuristic — replace with real violent poses
    if you obtain a labelled skeleton violence dataset later.
    """
    rng = np.random.default_rng(42)
    indices = rng.integers(0, len(X_calm), size=n_samples)
    X_aug = X_calm[indices].copy()

    # Add large jitter to simulate erratic violent motion
    noise = rng.normal(0, 0.08, X_aug.shape).astype(np.float32)
    X_aug = np.clip(X_aug + noise, 0, 1)

    # Random horizontal flip (x coord = 1 - x)
    flip_mask = rng.random(n_samples) > 0.5
    X_aug[flip_mask, :, :, 0] = 1.0 - X_aug[flip_mask, :, :, 0]

    return X_aug


def get_callbacks(name):
    return [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(WEIGHTS_DIR, f"{name}_model.keras"),
            monitor="val_auc", mode="max",
            save_best_only=True, verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_auc", patience=8,
            restore_best_weights=True, verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=3, min_lr=1e-7, verbose=1
        ),
    ]


def run():
    print("\n" + "=" * 55)
    print("  TRAINING — Body Pose Model")
    print("=" * 55)

    # ── Load data ──────────────────────────────────────────────────────────
    print("\n  Loading data...")
    X = np.load(POSE_X)
    y = np.load(POSE_Y)
    print(f"  X={X.shape}  y={y.shape}")
    print(f"  Violent={y.sum()}  NonViolent={len(y)-y.sum()}")

    # ── Synthesise violent samples if none exist ───────────────────────────
    n_calm = int((y == 0).sum())
    n_violent = int((y == 1).sum())

    if n_violent < n_calm * 0.3:
        print(f"\n  [INFO] Few violent samples ({n_violent}). "
              f"Synthesising {n_calm} augmented violent sequences...")
        X_calm = X[y == 0]
        X_violent_aug = augment_violent_poses(X_calm, n_calm)
        y_violent_aug = np.ones(n_calm, dtype=np.int8)

        X = np.concatenate([X, X_violent_aug], axis=0)
        y = np.concatenate([y, y_violent_aug], axis=0)

        # Shuffle
        perm = np.random.permutation(len(y))
        X, y = X[perm], y[perm]
        print(f"  After augmentation: {len(y)} samples  "
              f"Violent={y.sum()}  NonViolent={len(y)-y.sum()}")

    # ── Train/val split ────────────────────────────────────────────────────
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train={len(y_train)}  Val={len(y_val)}")

    # ── Class weights ──────────────────────────────────────────────────────
    cw = class_weight.compute_class_weight(
        "balanced", classes=np.unique(y_train), y=y_train
    )
    class_weights = dict(enumerate(cw))

    # ── Build model ────────────────────────────────────────────────────────
    model = model_def.build(
        sequence_len=X.shape[1],
        num_keypoints=X.shape[2],
        coords=X.shape[3]
    )
    model = model_def.compile(model, lr=LEARNING_RATE)
    model.summary()

    # ── Train ──────────────────────────────────────────────────────────────
    print("\n  Training...")
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weights,
        callbacks=get_callbacks("pose"),
        verbose=1
    )

    # ── Evaluate ───────────────────────────────────────────────────────────
    print("\n  Final evaluation:")
    results = model.evaluate(X_val, y_val, verbose=0)
    for name, val in zip(model.metrics_names, results):
        print(f"    {name}: {val:.4f}")

    print(f"\n  Best model saved → {WEIGHTS_DIR}/pose_model.keras")


if __name__ == "__main__":
    run()