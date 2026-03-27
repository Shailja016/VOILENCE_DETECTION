"""
model_crowd.py — Crowd Density / Count Model
Architecture : CSRNet-inspired CNN (VGG frontend + dilated convolutions)
Input        : (batch, 256, 256, 3)
Output       : (batch, 1)  →  estimated crowd count (regression)

Instead of full density map prediction (needs point annotations),
we do count regression directly — simpler and works with our dataset
which only has count labels, not point coordinates.
"""

import tensorflow as tf
from tensorflow.keras import layers, models


def build(img_size=256):
    inputs = layers.Input(shape=(img_size, img_size, 3),
                          name="crowd_input")

    # ── Frontend: VGG-style feature extractor ─────────────────────────────
    # Block 1
    x = layers.Conv2D(64, 3, padding="same", activation="relu")(inputs)
    x = layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = layers.MaxPooling2D(2)(x)

    # Block 2
    x = layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = layers.MaxPooling2D(2)(x)

    # Block 3
    x = layers.Conv2D(256, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(256, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(256, 3, padding="same", activation="relu")(x)
    x = layers.MaxPooling2D(2)(x)

    # Block 4
    x = layers.Conv2D(512, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(512, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(512, 3, padding="same", activation="relu")(x)
    x = layers.MaxPooling2D(2)(x)

    # ── Backend: dilated convolutions for density context ─────────────────
    # Dilated convs capture large receptive fields without losing resolution
    x = layers.Conv2D(512, 3, padding="same", dilation_rate=2,
                      activation="relu")(x)
    x = layers.Conv2D(512, 3, padding="same", dilation_rate=2,
                      activation="relu")(x)
    x = layers.Conv2D(256, 3, padding="same", dilation_rate=2,
                      activation="relu")(x)
    x = layers.Conv2D(128, 3, padding="same", dilation_rate=2,
                      activation="relu")(x)
    x = layers.Conv2D(64,  3, padding="same", dilation_rate=2,
                      activation="relu")(x)

    # ── Regression head ────────────────────────────────────────────────────
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(64, activation="relu")(x)
    # No activation on output — raw count regression
    output = layers.Dense(1, name="crowd_output")(x)

    model = models.Model(inputs=inputs, outputs=output,
                         name="crowd_model")
    return model


def compile(model, lr=1e-4):
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr),
        loss="mae",         # Mean Absolute Error for count regression
        metrics=["mae", "mse"]
    )
    return model


if __name__ == "__main__":
    m = build()
    m.summary()