"""
Stream 2 — Body Pose Keypoint Preprocessing
Dataset : CCTV Human Pose Estimation
Output  : pose_X.npy  shape (N, 30, 17, 2)   normalised keypoints
          pose_y.npy  shape (N,)  0=NonViolence  1=Violence
"""

import os
import sys
import cv2
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    POSE_DIR, POSE_X, POSE_Y,
    IMG_SIZE, SEQUENCE_LEN, VIDEO_EXTS, IMAGE_EXTS
)

NUM_KEYPOINTS = 17   # COCO skeleton: nose → ankles


# ─────────────────────────────────────────────
# Helper: extract keypoints from a single frame
# ─────────────────────────────────────────────
def extract_keypoints_from_frame(frame: np.ndarray,
                                  pose_model) -> np.ndarray:
    """
    Runs YOLOv8-Pose on one frame.
    Returns (17, 2) array of (x, y) normalised 0-1.
    If no person detected, returns zeros.
    """
    h, w = frame.shape[:2]
    results = pose_model(frame, verbose=False)
    kps = results[0].keypoints

    if kps is None or len(kps.xy) == 0:
        return np.zeros((NUM_KEYPOINTS, 2), dtype=np.float32)

    # Take the first (most confident) person detected
    pts = kps.xy[0].cpu().numpy()          # shape: (K, 2)

    # Normalise to 0-1
    pts = pts / np.array([w, h], dtype=np.float32)

    # Pad or trim to exactly 17 keypoints
    if pts.shape[0] < NUM_KEYPOINTS:
        pad = np.zeros((NUM_KEYPOINTS - pts.shape[0], 2), dtype=np.float32)
        pts = np.vstack([pts, pad])

    return pts[:NUM_KEYPOINTS].astype(np.float32)


# ─────────────────────────────────────────────
# Helper: extract keypoint sequence from video
# ─────────────────────────────────────────────
def extract_pose_sequence(video_path: str,
                           pose_model,
                           n: int = SEQUENCE_LEN) -> np.ndarray:
    """
    Returns (N, 17, 2) keypoint sequence from a video file.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return np.zeros((n, NUM_KEYPOINTS, 2), dtype=np.float32)

    total = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 1)
    indices = np.linspace(0, total - 1, n, dtype=int)
    sequence = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
            kp = extract_keypoints_from_frame(frame, pose_model)
        else:
            kp = np.zeros((NUM_KEYPOINTS, 2), dtype=np.float32)
        sequence.append(kp)

    cap.release()
    return np.array(sequence, dtype=np.float32)  # (N, 17, 2)


# ─────────────────────────────────────────────
# Helper: extract keypoints from a still image
# (dataset may contain images instead of videos)
# ─────────────────────────────────────────────
def extract_pose_from_image(img_path: str,
                             pose_model,
                             n: int = SEQUENCE_LEN) -> np.ndarray:
    """
    Loads an image and repeats its keypoints N times to
    simulate a static sequence.
    """
    frame = cv2.imread(img_path)
    if frame is None:
        return np.zeros((n, NUM_KEYPOINTS, 2), dtype=np.float32)
    frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    kp = extract_keypoints_from_frame(frame, pose_model)
    return np.tile(kp[np.newaxis], (n, 1, 1))  # (N, 17, 2)


# ─────────────────────────────────────────────
# Helper: load a class folder
# ─────────────────────────────────────────────
def load_folder(folder: str, label: int,
                pose_model, X: list, y: list) -> None:
    if not os.path.exists(folder):
        print(f"  [SKIP] Not found: {folder}")
        return

    files = [f for f in os.listdir(folder)
             if f.lower().endswith(VIDEO_EXTS + IMAGE_EXTS)]
    print(f"  {len(files)} files  label={label}  → {folder}")

    for f in tqdm(files, desc=f"  {'Violence' if label else 'NonViolence'}"):
        path = os.path.join(folder, f)
        if f.lower().endswith(VIDEO_EXTS):
            seq = extract_pose_sequence(path, pose_model)
        else:
            seq = extract_pose_from_image(path, pose_model)
        X.append(seq)
        y.append(label)


# ─────────────────────────────────────────────
# Main preprocessing function
# ─────────────────────────────────────────────
def run():
    print("\n" + "=" * 55)
    print("  STREAM 2 — Body Pose Keypoint Preprocessing")
    print("=" * 55)

    # Import here so the module is optional when not running this stream
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] ultralytics not installed. Run: pip install ultralytics")
        return

    print("\n  Loading YOLOv8-Pose model (downloads on first run)...")
    pose_model = YOLO("yolov8n-pose.pt")   # nano = fastest; swap to yolov8s-pose for accuracy

    X, y = [], []

    # CCTV Human Pose dataset — may have Violence / NonViolence subfolders
    # or flat image folders — we handle both
    print(f"\n  Scanning: {POSE_DIR}")

    violence_folder    = os.path.join(POSE_DIR, "Violence")
    nonviolence_folder = os.path.join(POSE_DIR, "NonViolence")

    if os.path.exists(violence_folder) or os.path.exists(nonviolence_folder):
        # Structured layout
        load_folder(violence_folder,    1, pose_model, X, y)
        load_folder(nonviolence_folder, 0, pose_model, X, y)
    else:
        # Flat layout — treat all files in POSE_DIR as unlabelled (label=0)
        print("  [INFO] No Violence/NonViolence subfolders found.")
        print("         Loading all files from POSE_DIR as label=0 (use for pretraining only)")
        load_folder(POSE_DIR, 0, pose_model, X, y)

    if not X:
        print("\n[ERROR] No pose data loaded. Check POSE_DIR in config.py")
        return

    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y, dtype=np.int8)

    print(f"\n  Saving {POSE_X}  shape={X_arr.shape}")
    np.save(POSE_X, X_arr)
    np.save(POSE_Y, y_arr)

    total   = len(y_arr)
    violent = int(y_arr.sum())
    print(f"  Done. Total={total}  Violent={violent}  NonViolent={total - violent}")


if __name__ == "__main__":
    run()