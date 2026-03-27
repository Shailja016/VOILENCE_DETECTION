"""
model_pose.py — Body Pose / Skeleton Model
Architecture : Bidirectional LSTM on keypoint sequences
Input        : (batch, 30, 17, 2)  →  flattened to (batch, 30, 34)
Output       : (batch, 1)  sigmoid  →  0=NonViolence  1=Violence

17 COCO keypoints × 2 coords (x,y) = 34 features per frame
The LSTM learns what aggressive motion patterns look like
over time — fast arm movements, crouching, etc.
"""

import tensorflow as tf
from tensorflow.keras import layers, models


def build(sequence_len=30, num_keypoints=17, coords=2):
    inputs = layers.Input(
        shape=(sequence_len, num_keypoints, coords),
        name="pose_input"
    )

    # Flatten keypoints: (batch, 30, 17, 2) → (batch, 30, 34)
    x = layers.Reshape(
        (sequence_len, num_keypoints * coords),
        name="flatten_keypoints"
    )(inputs)

    # Batch norm to handle varying camera distances/scales
    x = layers.BatchNormalization()(x)

    # Bidirectional LSTM — looks at motion forward AND backward
    # This helps catch the "windup" before a punch, etc.
    x = layers.Bidirectional(
        layers.LSTM(128, return_sequences=True), name="bilstm_1"
    )(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Bidirectional(
        layers.LSTM(64), name="bilstm_2"
    )(x)
    x = layers.Dropout(0.3)(x)

    # Classification head
    x = layers.Dense(128, activation="relu", name="dense_1")(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(64, activation="relu", name="dense_2")(x)
    output = layers.Dense(1, activation="sigmoid", name="pose_output")(x)

    model = models.Model(inputs=inputs, outputs=output,
                         name="pose_model")
    return model


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


if __name__ == "__main__":
    m = build()
    m.summary()