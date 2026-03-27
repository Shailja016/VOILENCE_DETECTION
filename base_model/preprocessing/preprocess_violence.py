"""
Stream 1 — Violence Video Preprocessing
Datasets : Real Life Violence + SCVD
Output   : violence_X.npy  shape (N, 30, 224, 224, 3)
           violence_y.npy  shape (N,)   0=NonViolence  1=Violence
"""

import os
import sys
import cv2
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    VIOLENCE_DIR, VIOLENCE2_DIR, SCVD_DIR, VIOLENCE_X, VIOLENCE_Y,
    IMG_SIZE, SEQUENCE_LEN, VIDEO_EXTS, MAX_VIDEOS_PER_CLASS
)


# ─────────────────────────────────────────────
# Helper: extract N evenly spaced frames
# ─────────────────────────────────────────────
def extract_frames(video_path: str, n: int = SEQUENCE_LEN) -> np.ndarray:
    """
    Opens a video file and returns N evenly spaced RGB frames.
    Shape: (N, IMG_SIZE, IMG_SIZE, 3)  dtype: float32  range: 0-1
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  [WARN] Cannot open: {video_path}")
        return np.zeros((n, IMG_SIZE, IMG_SIZE, 3), dtype=np.float32)

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total = max(total, 1)
    indices = np.linspace(0, total - 1, n, dtype=int)

    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.astype(np.float32) / 255.0
        else:
            frame = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.float32)
        frames.append(frame)

    cap.release()

    # Pad if short
    while len(frames) < n:
        frames.append(np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.float32))

    return np.array(frames[:n], dtype=np.float32)


# ─────────────────────────────────────────────
# Helper: load all videos from a folder
# ─────────────────────────────────────────────
def load_videos_from_folder(folder: str, label: int,
                             X: list, y: list) -> None:
    if not os.path.exists(folder):
        print(f"  [SKIP] Folder not found: {folder}")
        return

    videos = [f for f in os.listdir(folder)
              if f.lower().endswith(VIDEO_EXTS)]

    if not videos:
        print(f"  [WARN] No videos found in: {folder}")
        return

    print(f"  Loading {len(videos)} videos  label={label}  from {folder}")
    for v in tqdm(videos, desc=f"  {'Violence' if label else 'NonViolence'}"):
        frames = extract_frames(os.path.join(folder, v))
        X.append(frames)
        y.append(label)


# ─────────────────────────────────────────────
# Main preprocessing function
# ─────────────────────────────────────────────
def save_in_batches(sources, out_x, out_y, batch_size=100):
    # Count total videos respecting per-class limit
    total = 0
    counted_sources = []
    for folder, label in sources:
        if not os.path.exists(folder):
            continue
        videos = [f for f in os.listdir(folder)
                  if f.lower().endswith(VIDEO_EXTS)]
        if MAX_VIDEOS_PER_CLASS:
            videos = videos[:MAX_VIDEOS_PER_CLASS]
        total += len(videos)
        counted_sources.append((folder, label, videos))

    if total == 0:
        print("  [ERROR] No videos found in any source folder.")
        return 0

    print(f"  Total videos to process: {total}  (limit={MAX_VIDEOS_PER_CLASS} per class)")
    est_gb = (total * SEQUENCE_LEN * 112 * 112 * 3 * 4) / 1e9
    print(f"  Estimated disk usage: {est_gb:.1f} GB")

    X_map = np.lib.format.open_memmap(
        out_x, mode='w+', dtype=np.float32,
        shape=(total, SEQUENCE_LEN, IMG_SIZE, IMG_SIZE, 3)
    )
    y_map = np.lib.format.open_memmap(
        out_y, mode='w+', dtype=np.int8, shape=(total,)
    )

    idx = 0
    for folder, label, videos in counted_sources:
        lname = "Violence" if label else "NonViolence"
        print(f"  {len(videos)} videos  label={label}  → {folder}")
        for v in tqdm(videos, desc=f"  {lname}"):
            frames = extract_frames(os.path.join(folder, v))
            X_map[idx] = frames
            y_map[idx] = label
            idx += 1
            if idx % batch_size == 0:
                X_map.flush()
                y_map.flush()

    X_map.flush()
    y_map.flush()
    return idx


def run():
    print("\n" + "=" * 55)
    print("  STREAM 1 — Violence Video Preprocessing")
    print("=" * 55)

    sources = []

    # Source 1: Real Life Violence Dataset
    print("\n[1/3] Real Life Violence Dataset")
    sources += [
        (os.path.join(VIOLENCE_DIR, "Violence"),    1),
        (os.path.join(VIOLENCE_DIR, "NonViolence"), 0),
    ]

    # Source 2: Real Life Violence Situations
    print("[2/3] Real Life Violence Situations")
    sources += [
        (os.path.join(VIOLENCE2_DIR, "Violence"),    1),
        (os.path.join(VIOLENCE2_DIR, "NonViolence"), 0),
    ]

    # Source 3: SCVD
    print("[3/3] SCVD")
    for split in ["Train", "Test"]:
        sources += [
            (os.path.join(SCVD_DIR, split, "Violence"),    1),
            (os.path.join(SCVD_DIR, split, "NonViolence"), 0),
        ]

    count = save_in_batches(sources, VIOLENCE_X, VIOLENCE_Y)
    if count:
        print(f"\n  Done. Saved {count} clips → {VIOLENCE_X}")


if __name__ == "__main__":
    run()