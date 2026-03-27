"""
train_flow.py — Train Optical Flow Model
Loads flow_X.npy + flow_y.npy
Note: flow dataset is violence-only (200 clips, all label=1)
We add calm flow (near-zero motion arrays) as NonViolence class
"""

import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
import tensorflow as tf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    FLOW_X, FLOW_Y, WEIGHTS_DIR,
    BATCH_SIZE, EPOCHS, LEARNING_RATE,
    SEQUENCE_LEN, IMG_SIZE
)
import src.model_flow as model_def


def synthesise_calm_flow(n_samples: int,
                          seq_len: int,
                          img_size: int) -> np.ndarray:
    """
    Creates synthetic calm (non-violent) optical flow sequences.
    Calm crowds have small, smooth, uniform motion.
    """
    rng = np.random.default_rng(42)
    flows = []
    for _ in range(n_samples):
        # Small random uniform motion (like people walking slowly)
        base_dx = rng.uniform(-0.05, 0.05)
        base_dy = rng.uniform(-0.02, 0.02)

        seq = []
        for _ in range(seq_len):
            flow = np.zeros((img_size, img_size, 2), dtype=np.float32)
            flow[:, :, 0] = base_dx + rng.normal(0, 0.01, (img_size, img_size))
            flow[:, :, 1] = base_dy + rng.normal(0, 0.01, (img_size, img_size))
            seq.append(flow)
        flows.append(np.array(seq))

    return np.array(flows, dtype=np.float32)


def get_callbacks(name):
    return [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(WEIGHTS_DIR, f"{name}_model.keras"),
            monitor="val_auc", mode="max",
            save_best_only=True, verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_auc", patience=7,
            restore_best_weights=True, verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=3, min_lr=1e-7, verbose=1
        ),
    ]


def run():
    print("\n" + "=" * 55)
    print("  TRAINING — Optical Flow Model")
    print("=" * 55)

    # ── Load data ──────────────────────────────────────────────────────────
    print("\n  Loading data...")
    X = np.load(FLOW_X, mmap_mode="r")
    y = np.load(FLOW_Y)
    print(f"  X={X.shape}  y={y.shape}")
    print(f"  Violent={y.sum()}  NonViolent={len(y)-y.sum()}")

    seq_len  = X.shape[1]
    img_size = X.shape[2]

    # ── Synthesise calm flow if no NonViolence samples ─────────────────────
    n_violent  = int((y == 1).sum())
    n_nonviol  = int((y == 0).sum())

    if n_nonviol == 0:
        print(f"\n  [INFO] No NonViolence flow found.")
        print(f"         Synthesising {n_violent} calm flow sequences...")
        X_calm = synthesise_calm_flow(n_violent, seq_len, img_size)
        y_calm = np.zeros(n_violent, dtype=np.int8)

        X = np.concatenate([np.array(X), X_calm], axis=0)
        y = np.concatenate([y, y_calm], axis=0)

        perm = np.random.permutation(len(y))
        X, y = X[perm], y[perm]
        print(f"  After synthesis: {len(y)} samples  "
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
    model = model_def.build(sequence_len=seq_len, img_size=img_size)
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
        callbacks=get_callbacks("flow"),
        verbose=1
    )

    # ── Evaluate ───────────────────────────────────────────────────────────
    print("\n  Final evaluation:")
    results = model.evaluate(X_val, y_val, verbose=0)
    for name, val in zip(model.metrics_names, results):
        print(f"    {name}: {val:.4f}")

    print(f"\n  Best model saved → {WEIGHTS_DIR}/flow_model.keras")


if __name__ == "__main__":
    run()