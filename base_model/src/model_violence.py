"""
model_violence.py — Violence Video Model
Architecture : TimeDistributed MobileNetV2 (CNN) + LSTM
Input        : (batch, 16, 112, 112, 3)
Output       : (batch, 1)  sigmoid  →  0=NonViolence  1=Violence
"""

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2


def build(sequence_len=16, img_size=112):
    # ── CNN backbone ───────────────────────────────────────────────────────
    base_cnn = MobileNetV2(
        input_shape=(img_size, img_size, 3),
        include_top=False,
        weights="imagenet",
        pooling="avg"       # global average pooling → (batch, 1280)
    )
    base_cnn.trainable = False   # freeze for initial training

    # ── Full model ─────────────────────────────────────────────────────────
    inputs = layers.Input(shape=(sequence_len, img_size, img_size, 3),
                          name="violence_input")

    # Apply CNN to every frame independently
    x = layers.TimeDistributed(base_cnn, name="frame_features")(inputs)
    # shape: (batch, 16, 1280)

    # LSTM learns temporal patterns across frames
    x = layers.LSTM(256, return_sequences=True, name="lstm_1")(x)
    x = layers.Dropout(0.4)(x)
    x = layers.LSTM(128, name="lstm_2")(x)
    x = layers.Dropout(0.4)(x)

    # Classification head
    x = layers.Dense(256, activation="relu", name="dense_1")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation="relu", name="dense_2")(x)
    output = layers.Dense(1, activation="sigmoid", name="violence_output")(x)

    model = models.Model(inputs=inputs, outputs=output,
                         name="violence_model")
    return model


def unfreeze_top(model, n_layers=30):
    """
    Call after initial training converges.
    Unfreezes the top N layers of MobileNetV2 for fine-tuning.
    """
    base_cnn = model.get_layer("frame_features").layer
    base_cnn.trainable = True
    for layer in base_cnn.layers[:-n_layers]:
        layer.trainable = False
    print(f"  Unfroze top {n_layers} layers of MobileNetV2")


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
    print(f"\nTrainable params: {sum(tf.size(v).numpy() for v in m.trainable_variables):,}")