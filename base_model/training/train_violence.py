"""
train_violence.py — Train Violence Video Model
Loads violence_X.npy + violence_y.npy
Trains CNN-LSTM model in two phases:
  Phase 1: frozen CNN backbone  (fast, ~10 epochs)
  Phase 2: fine-tune top layers (slow, ~10 epochs)
"""

import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
import tensorflow as tf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    VIOLENCE_X, VIOLENCE_Y, WEIGHTS_DIR,
    BATCH_SIZE, EPOCHS, LEARNING_RATE
)
import src.model_violence as model_def


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
        tf.keras.callbacks.TensorBoard(
            log_dir=os.path.join(WEIGHTS_DIR, "logs", name)
        ),
    ]


def run():
    print("\n" + "=" * 55)
    print("  TRAINING — Violence Video Model")
    print("=" * 55)

    # ── Load data ──────────────────────────────────────────────────────────
    print("\n  Loading data...")
    X = np.load(VIOLENCE_X, mmap_mode="r")
    y = np.load(VIOLENCE_Y)
    print(f"  X={X.shape}  y={y.shape}")
    print(f"  Violent={y.sum()}  NonViolent={len(y)-y.sum()}")

    # ── Train/val split ────────────────────────────────────────────────────
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train={len(y_train)}  Val={len(y_val)}")

    # ── Class weights (handles imbalanced data) ────────────────────────────
    cw = class_weight.compute_class_weight(
        "balanced", classes=np.unique(y_train), y=y_train
    )
    class_weights = dict(enumerate(cw))
    print(f"  Class weights: {class_weights}")

    # ── Build model ────────────────────────────────────────────────────────
    model = model_def.build(
        sequence_len=X.shape[1],
        img_size=X.shape[2]
    )
    model = model_def.compile(model, lr=LEARNING_RATE)
    model.summary()

    # ══ Phase 1: Frozen backbone ═══════════════════════════════════════════
    print("\n  Phase 1: Training with frozen CNN backbone...")
    history1 = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weights,
        callbacks=get_callbacks("violence"),
        verbose=1
    )

    # ══ Phase 2: Fine-tune top CNN layers ══════════════════════════════════
    print("\n  Phase 2: Fine-tuning top CNN layers...")
    model_def.unfreeze_top(model, n_layers=30)
    model_def.compile(model, lr=LEARNING_RATE / 10)

    history2 = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=15,
        batch_size=BATCH_SIZE,
        class_weight=class_weights,
        callbacks=get_callbacks("violence"),
        verbose=1
    )

    # ── Final evaluation ───────────────────────────────────────────────────
    print("\n  Final evaluation on validation set:")
    results = model.evaluate(X_val, y_val, verbose=0)
    for name, val in zip(model.metrics_names, results):
        print(f"    {name}: {val:.4f}")

    print(f"\n  Best model saved → {WEIGHTS_DIR}/violence_model.keras")


if __name__ == "__main__":
    run()