"""
model_fusion.py — Optimized Late Fusion Model (Anti-Overfitting Version)
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    WEIGHTS_DIR,
    LOW_THRESHOLD, MEDIUM_THRESHOLD, HIGH_THRESHOLD
)


# ─────────────────────────────────────────────
# Build fusion model (IMPROVED)
# ─────────────────────────────────────────────
def build():
    """
    Takes 5 scalar probability inputs (one per stream)
    and outputs a final violence probability.
    """

    # Inputs
    in_violence = layers.Input(shape=(1,), name="in_violence")
    in_pose     = layers.Input(shape=(1,), name="in_pose")
    in_fer      = layers.Input(shape=(1,), name="in_fer")
    in_crowd    = layers.Input(shape=(1,), name="in_crowd")
   
    x = layers.Concatenate()(
    [in_violence, in_pose, in_fer, in_crowd]
)
    # 🔥 IMPROVED NETWORK (Anti-overfitting)
    x = layers.Dense(
        16,
        activation="relu",
        kernel_regularizer=regularizers.l2(0.001),
        name="fusion_dense_1"
    )(x)

    x = layers.Dropout(0.5)(x)

    x = layers.Dense(
        8,
        activation="relu",
        kernel_regularizer=regularizers.l2(0.001),
        name="fusion_dense_2"
    )(x)

    x = layers.Dropout(0.5)(x)

    # Output
    output = layers.Dense(
        1,
        activation="sigmoid",
        name="fusion_output"
    )(x)

    model = models.Model(
        inputs=[in_violence, in_pose, in_fer, in_crowd],
        outputs=output,
        name="fusion_model"
    )

    return model


# ─────────────────────────────────────────────
# Compile
# ─────────────────────────────────────────────
def compile(model, lr=1e-3):
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ]
    )
    return model


# ─────────────────────────────────────────────
# Load submodels
# ─────────────────────────────────────────────
def load_submodels():
    submodels = {}
    names = ["violence", "pose", "fer", "crowd", "flow"]

    for name in names:
        path = os.path.join(WEIGHTS_DIR, f"{name}_model.keras")
        if os.path.exists(path):
            submodels[name] = tf.keras.models.load_model(path)
            print(f"  Loaded {name}_model.keras")
        else:
            print(f"  [WARN] Not found: {path} — using zeros for {name}")
            submodels[name] = None

    return submodels


# ─────────────────────────────────────────────
# Predict scores
# ─────────────────────────────────────────────
def predict_scores(submodels: dict,
                   violence_frames=None,
                   pose_seq=None,
                   face_img=None,
                   crowd_img=None,
                   flow_seq=None):

    scores = {}

    def safe_predict(model, x):
        if model is not None and x is not None:
            return float(model.predict(x, verbose=0)[0][0])
        return 0.5

    scores["violence"] = safe_predict(submodels.get("violence"), violence_frames)
    scores["pose"]     = safe_predict(submodels.get("pose"), pose_seq)
    scores["fer"]      = safe_predict(submodels.get("fer"), face_img)
    scores["crowd"]    = safe_predict(submodels.get("crowd"), crowd_img)
    scores["flow"]     = safe_predict(submodels.get("flow"), flow_seq)

    return scores


# ─────────────────────────────────────────────
# Risk scoring engine
# ─────────────────────────────────────────────
def compute_risk(scores: dict, crowd_count: float = 0):

    # Crowd multiplier
    if crowd_count < 20:
        crowd_mult = 1.0
    elif crowd_count < 100:
        crowd_mult = 1.3
    elif crowd_count < 500:
        crowd_mult = 1.7
    else:
        crowd_mult = 2.5

    # Weighted fusion
    weights = {
        "violence": 0.35,
        "flow":     0.25,
        "pose":     0.20,
        "fer":      0.15,
        "crowd":    0.05,
    }

    weighted_score = sum(
        scores.get(k, 0.5) * w for k, w in weights.items()
    )

    final_score = min(weighted_score * crowd_mult, 1.0)

    # Alert level
    if final_score >= HIGH_THRESHOLD:
        level = "HIGH"
    elif final_score >= MEDIUM_THRESHOLD:
        level = "MEDIUM"
    elif final_score >= LOW_THRESHOLD:
        level = "LOW"
    else:
        level = "SAFE"

    return {
        "level": level,
        "score": round(final_score, 4),
        "crowd_mult": crowd_mult,
        "stream_scores": scores,
    }


# ─────────────────────────────────────────────
# Test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    m = build()
    m.summary()

    test_scores = {
        "violence": 0.85,
        "flow":     0.72,
        "pose":     0.60,
        "fer":      0.45,
        "crowd":    0.30,
    }

    result = compute_risk(test_scores, crowd_count=150)

    print("\nRisk score test:")
    print(f"Final score : {result['score']}")
    print(f"Alert level : {result['level']}")