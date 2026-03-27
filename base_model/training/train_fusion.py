"""
train_fusion.py — FINAL CLEAN FIXED VERSION (Stable + Correct)
"""

import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
import tensorflow as tf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config import (
    VIOLENCE_X, VIOLENCE_Y,
    POSE_X, POSE_Y,
    FER_X, FER_Y,
    WEIGHTS_DIR
)

import src.model_fusion as fusion_def


# ─────────────────────────────────────────────
# Load model safely
# ─────────────────────────────────────────────
def load_model_safe(name):
    path = os.path.join(WEIGHTS_DIR, f"{name}_model.keras")
    if os.path.exists(path):
        print(f"  Loaded {name}_model.keras")
        return tf.keras.models.load_model(path)
    print(f"  [WARN] {name}_model.keras not found")
    return None


# ─────────────────────────────────────────────
# Generate fusion scores
# ─────────────────────────────────────────────
def get_scores_for_dataset(submodels, n_samples):

    X_viol = np.load(VIOLENCE_X, mmap_mode="r")
    y = np.load(VIOLENCE_Y)

    X_pose = np.load(POSE_X, mmap_mode="r") if os.path.exists(POSE_X) else None
    X_fer  = np.load(FER_X, mmap_mode="r")  if os.path.exists(FER_X)  else None

    n = min(n_samples, len(y))

    scores_violence = submodels["violence"].predict(X_viol[:n], batch_size=8).flatten()

    scores_pose = np.full(n, 0.5)
    if submodels["pose"] and X_pose is not None:
        idx = np.random.randint(0, len(X_pose), n)
        scores_pose = submodels["pose"].predict(X_pose[idx], batch_size=16).flatten()

    scores_fer = np.full(n, 0.5)
    if submodels["fer"] and X_fer is not None:
        idx = np.random.randint(0, len(X_fer), n)
        scores_fer = submodels["fer"].predict(X_fer[idx], batch_size=32).flatten()

    # Dummy crowd (since not properly used)
    scores_crowd = np.full(n, 0.5)

    X_fusion = np.stack(
        [scores_violence, scores_pose, scores_fer, scores_crowd],
        axis=1
    )

    return X_fusion, y[:n]


# ─────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────
def get_callbacks():
    return [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(WEIGHTS_DIR, "fusion_model.keras"),
            monitor="val_loss",
            save_best_only=True,
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True
        )
    ]


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def run():

    print("\n===== TRAINING FUSION MODEL =====")

    submodels = {
        "violence": load_model_safe("violence"),
        "pose": load_model_safe("pose"),
        "fer": load_model_safe("fer"),
    }

    # Generate data
    X_fusion, y_fusion = get_scores_for_dataset(
        submodels, len(np.load(VIOLENCE_Y))
    )

    print("Dataset:", X_fusion.shape)

    # 🔥 Save original labels
    y_original = y_fusion.copy()

    # 🔥 Add noise
    X_fusion += np.random.normal(0, 0.03, X_fusion.shape)
    X_fusion = np.clip(X_fusion, 0, 1)

    # 🔥 Feature dropout
    mask = np.random.binomial(1, 0.9, X_fusion.shape)
    X_fusion *= mask

    # 🔥 SPLIT (use original labels)
    X_train, X_val, y_train_orig, y_val_orig = train_test_split(
        X_fusion, y_original,
        test_size=0.4,
        stratify=y_original,
        random_state=42
    )

    # 🔥 Label smoothing AFTER split
    y_train = y_train_orig
    y_val   = y_val_orig

    # 🔥 Class weights (use original labels)
    cw = class_weight.compute_class_weight(
        "balanced",
        classes=np.unique(y_train_orig),
        y=y_train_orig
    )
    class_weights = dict(enumerate(cw))

    print("Class weights:", class_weights)

    # Build model
    model = fusion_def.build()
    model = fusion_def.compile(model, lr=1e-3)

    # Train
    model.fit(
        [X_train[:, i:i+1] for i in range(4)],
        y_train,
        validation_data=([X_val[:, i:i+1] for i in range(4)], y_val),
        epochs=15,
        batch_size=32,
        class_weight=class_weights,
        callbacks=get_callbacks(),
        verbose=1
    )

    # Evaluate
    print("\nFinal evaluation:")
    results = model.evaluate(
        [X_val[:, i:i+1] for i in range(4)], y_val, verbose=0
    )

    for name, val in zip(model.metrics_names, results):
        print(f"{name}: {val:.4f}")

    print("\nSaved model ✔")


if __name__ == "__main__":
    run()