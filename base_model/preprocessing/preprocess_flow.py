"""
Stream 5 — Optical Flow Preprocessing
Dataset : SCVD (Smart-City CCTV Violence Detection)
Output  : flow_X.npy  shape (N, 30, 224, 224, 2)  (dx, dy) normalised
          flow_y.npy  shape (N,)  0=NonViolence  1=Violence

Optical flow captures HOW the crowd is moving between frames —
fast chaotic motion = likely violence,  slow regular motion = calm crowd.
"""

import os
import sys
import cv2
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    SCVD_DIR, FLOW_X, FLOW_Y,
    IMG_SIZE, SEQUENCE_LEN, VIDEO_EXTS, MAX_VIDEOS_PER_CLASS
)

# Farneback optical flow parameters
FB_PARAMS = dict(
    pyr_scale  = 0.5,   # pyramid scale
    levels     = 3,     # pyramid levels
    winsize    = 15,    # averaging window
    iterations = 3,     # iterations per level
    poly_n     = 5,     # pixel neighbourhood size
    poly_sigma = 1.2,   # Gaussian std for polynomial expansion
    flags      = 0
)


# ─────────────────────────────────────────────
# Helper: extract optical flow sequence from video
# ─────────────────────────────────────────────
def extract_flow_sequence(video_path: str,
                           n: int = SEQUENCE_LEN) -> np.ndarray:
    """
    Reads N+1 evenly spaced frames, computes N flow maps between
    consecutive pairs. Returns (N, H, W, 2) float32, normalised -1 to 1.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  [WARN] Cannot open: {video_path}")
        return np.zeros((n, IMG_SIZE, IMG_SIZE, 2), dtype=np.float32)

    total = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 1)
    # Need n+1 frames to compute n flows
    indices = np.linspace(0, total - 1, n + 1, dtype=int)

    # Read all frames as grayscale
    grays = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.uint8)
        grays.append(gray)
    cap.release()

    # Pad if needed
    while len(grays) < n + 1:
        grays.append(np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.uint8))

    # Compute flow between consecutive frames
    flows = []
    for i in range(n):
        flow = cv2.calcOpticalFlowFarneback(
            grays[i], grays[i + 1], None, **FB_PARAMS
        )  # shape: (H, W, 2)

        # Normalise: divide by max magnitude to keep -1 to 1
        max_val = np.max(np.abs(flow)) + 1e-6
        flow    = flow / max_val
        flows.append(flow.astype(np.float32))

    return np.array(flows, dtype=np.float32)   # (N, H, W, 2)


# ─────────────────────────────────────────────
# Helper: load a class folder
# ─────────────────────────────────────────────
def load_folder(folder: str, label: int,
                X: list, y: list) -> None:
    if not os.path.exists(folder):
        print(f"  [SKIP] Not found: {folder}")
        return

    videos = [f for f in os.listdir(folder)
              if f.lower().endswith(VIDEO_EXTS)]
    if not videos:
        print(f"  [WARN] No videos in: {folder}")
        return

    print(f"  {len(videos)} videos  label={label}  → {folder}")
    for v in tqdm(videos, desc=f"  {'Violence' if label else 'NonViolence'}"):
        flow_seq = extract_flow_sequence(os.path.join(folder, v))
        X.append(flow_seq)
        y.append(label)


# ─────────────────────────────────────────────
# Main preprocessing function
# ─────────────────────────────────────────────
def run():
    print("\n" + "=" * 55)
    print("  STREAM 5 — Optical Flow Preprocessing (SCVD)")
    print("=" * 55)

    if not os.path.exists(SCVD_DIR):
        print(f"\n[ERROR] SCVD_DIR not found: {SCVD_DIR}")
        return

    # Collect all sources
    sources = []
    for split in ["Train", "Test"]:
        for cls, label in [("Violence", 1), ("NonViolence", 0)]:
            folder = os.path.join(SCVD_DIR, split, cls)
            if os.path.exists(folder):
                sources.append((folder, label))
            else:
                print(f"  [SKIP] Not found: {folder}")

    # Count total videos respecting limit
    total = 0
    limited_sources = []
    for folder, label in sources:
        videos = [f for f in os.listdir(folder)
                  if f.lower().endswith(VIDEO_EXTS)]
        if MAX_VIDEOS_PER_CLASS:
            videos = videos[:MAX_VIDEOS_PER_CLASS]
        total += len(videos)
        limited_sources.append((folder, label, videos))

    if total == 0:
        print("\n[ERROR] No videos found.")
        return

    est_gb = (total * SEQUENCE_LEN * IMG_SIZE * IMG_SIZE * 2 * 4) / 1e9
    print(f"  Total videos: {total}  (limit={MAX_VIDEOS_PER_CLASS})  est. {est_gb:.1f} GB")

    X_map = np.lib.format.open_memmap(
        FLOW_X, mode='w+', dtype=np.float32,
        shape=(total, SEQUENCE_LEN, IMG_SIZE, IMG_SIZE, 2)
    )
    y_map = np.lib.format.open_memmap(
        FLOW_Y, mode='w+', dtype=np.int8, shape=(total,)
    )

    idx = 0
    for folder, label, videos in limited_sources:
        lname = "Violence" if label else "NonViolence"
        print(f"  {len(videos)} videos  label={label}  → {folder}")
        for v in tqdm(videos, desc=f"  {lname}"):
            flow_seq = extract_flow_sequence(os.path.join(folder, v))
            X_map[idx] = flow_seq
            y_map[idx] = label
            idx += 1
            if idx % 50 == 0:
                X_map.flush()
                y_map.flush()

    X_map.flush()
    y_map.flush()
    violent = int(y_map[:idx].sum())
    print(f"\n  Saved flow_X.npy  shape={X_map.shape}")
    print(f"  Done. Total={idx}  Violent={violent}  NonViolent={idx - violent}")


if __name__ == "__main__":
    run()