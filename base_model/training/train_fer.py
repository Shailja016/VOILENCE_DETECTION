"""
train_fer.py — Train Facial Expression Model
Loads fer_X.npy + fer_y.npy
Two-phase training: frozen backbone → fine-tune
"""

import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
import tensorflow as tf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    FER_X, FER_Y, WEIGHTS_DIR,
    BATCH_SIZE, EPOCHS, LEARNING_RATE
)
import src.model_fer as model_def

FER_IMG_SIZE = 64


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
    print("  TRAINING — Facial Expression Model (FER-2013)")
    print("=" * 55)

    # ── Load data ──────────────────────────────────────────────────────────
    print("\n  Loading data...")
    X = np.load(FER_X, mmap_mode="r")
    y = np.load(FER_Y)
    print(f"  X={X.shape}  y={y.shape}")
    print(f"  Aggressive={y.sum()}  Calm={len(y)-y.sum()}")

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
    print(f"  Class weights: {class_weights}")

    # ── Build model ────────────────────────────────────────────────────────
    model = model_def.build(img_size=FER_IMG_SIZE)
    model = model_def.compile(model, lr=LEARNING_RATE)
    model.summary()

    # ══ Phase 1: Frozen backbone ═══════════════════════════════════════════
    print("\n  Phase 1: Frozen backbone...")
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=32,        # larger batch for image data
        class_weight=class_weights,
        callbacks=get_callbacks("fer"),
        verbose=1
    )

    # ══ Phase 2: Fine-tune ═════════════════════════════════════════════════
    print("\n  Phase 2: Fine-tuning...")
    model_def.unfreeze_top(model, n_layers=20)
    model_def.compile(model, lr=LEARNING_RATE / 10)

    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=10,
        batch_size=32,
        class_weight=class_weights,
        callbacks=get_callbacks("fer"),
        verbose=1
    )

    # ── Evaluate ───────────────────────────────────────────────────────────
    print("\n  Final evaluation:")
    results = model.evaluate(X_val, y_val, verbose=0)
    for name, val in zip(model.metrics_names, results):
        print(f"    {name}: {val:.4f}")

    print(f"\n  Best model saved → {WEIGHTS_DIR}/fer_model.keras")


if __name__ == "__main__":
    run()