"""
model_flow.py — Optical Flow Model
Architecture : TimeDistributed CNN + LSTM
Input        : (batch, 16, 112, 112, 2)  →  (dx, dy) flow maps
Output       : (batch, 1)  sigmoid  →  0=Calm  1=Violent crowd motion

Optical flow captures HOW pixels move between frames.
Violent crowds have chaotic, high-magnitude, multi-directional flow.
Calm crowds have smooth, low-magnitude, uniform flow.
"""

import tensorflow as tf
from tensorflow.keras import layers, models


def flow_cnn_block(img_size=112):
    """
    Lightweight CNN applied to each flow frame.
    Input: (112, 112, 2) — 2 channels: horizontal + vertical flow
    Output: 512-dim feature vector
    """
    inp = layers.Input(shape=(img_size, img_size, 2))

    x = layers.Conv2D(32, 7, strides=2, padding="same",
                      activation="relu")(inp)        # 56x56
    x = layers.BatchNormalization()(x)

    x = layers.Conv2D(64, 5, strides=2, padding="same",
                      activation="relu")(x)          # 28x28
    x = layers.BatchNormalization()(x)

    x = layers.Conv2D(128, 3, strides=2, padding="same",
                      activation="relu")(x)          # 14x14
    x = layers.BatchNormalization()(x)

    x = layers.Conv2D(256, 3, strides=2, padding="same",
                      activation="relu")(x)          # 7x7
    x = layers.BatchNormalization()(x)

    x = layers.GlobalAveragePooling2D()(x)           # 256-dim

    return models.Model(inputs=inp, outputs=x, name="flow_cnn")


def build(sequence_len=16, img_size=112):
    inputs = layers.Input(
        shape=(sequence_len, img_size, img_size, 2),
        name="flow_input"
    )

    # Apply flow CNN to each frame
    cnn = flow_cnn_block(img_size)
    x = layers.TimeDistributed(cnn, name="flow_frame_features")(inputs)
    # shape: (batch, 16, 256)

    # LSTM learns temporal patterns in crowd motion
    x = layers.LSTM(128, return_sequences=True, name="lstm_1")(x)
    x = layers.Dropout(0.4)(x)
    x = layers.LSTM(64, name="lstm_2")(x)
    x = layers.Dropout(0.4)(x)

    # Classification head
    x = layers.Dense(128, activation="relu", name="dense_1")(x)
    x = layers.Dropout(0.4)(x)
    output = layers.Dense(1, activation="sigmoid", name="flow_output")(x)

    model = models.Model(inputs=inputs, outputs=output,
                         name="flow_model")
    return model


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