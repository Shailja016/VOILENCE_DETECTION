"""
model_fer.py — Facial Expression Model
Architecture : MobileNetV2 CNN classifier
Input        : (batch, 64, 64, 3)
Output       : (batch, 1)  sigmoid  →  0=Calm  1=Aggressive
               (angry / disgust / fear = aggressive)

FER images are small (48x48 originally, upscaled to 64x64).
MobileNetV2 is lightweight enough to handle this size efficiently.
"""

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2


def build(img_size=64):
    # ── CNN backbone ───────────────────────────────────────────────────────
    base_cnn = MobileNetV2(
        input_shape=(img_size, img_size, 3),
        include_top=False,
        weights="imagenet",
        pooling="avg"      # → (batch, 1280)
    )
    base_cnn.trainable = False

    # ── Full model ─────────────────────────────────────────────────────────
    inputs = layers.Input(shape=(img_size, img_size, 3),
                          name="fer_input")

    x = base_cnn(inputs, training=False)
    # shape: (batch, 1280)

    x = layers.Dense(256, activation="relu", name="dense_1")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation="relu", name="dense_2")(x)
    x = layers.Dropout(0.4)(x)
    output = layers.Dense(1, activation="sigmoid", name="fer_output")(x)

    model = models.Model(inputs=inputs, outputs=output,
                         name="fer_model")
    return model


def unfreeze_top(model, n_layers=20):
    base_cnn = None
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            base_cnn = layer
            break
    if base_cnn is None:
        print("  [WARN] MobileNetV2 layer not found, skipping unfreeze")
        return
    base_cnn.trainable = True
    for layer in base_cnn.layers[:-n_layers]:
        layer.trainable = False
    print(f"  Unfroze top {n_layers} layers of {base_cnn.name}")


def compile(model, lr=1e-4):
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


if __name__ == "__main__":
    m = build()
    m.summary()