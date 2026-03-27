"""
run_all.py — Master preprocessing runner
Runs all 5 streams in order and prints a final summary.

Usage:
    python preprocessing/run_all.py

Or run individual streams:
    python preprocessing/preprocess_violence.py
    python preprocessing/preprocess_pose.py
    python preprocessing/preprocess_fer.py
    python preprocessing/preprocess_crowd.py
    python preprocessing/preprocess_flow.py
"""

import os
import sys
import time
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import OUT_DIR

# ── Import all stream preprocessors ──────────────────────────────────────
from preprocess_violence import run as run_violence
from preprocess_pose     import run as run_pose
from preprocess_fer      import run as run_fer
from preprocess_crowd    import run as run_crowd
from preprocess_flow     import run as run_flow


# ─────────────────────────────────────────────
# Helper: print a summary of all saved .npy files
# ─────────────────────────────────────────────
def print_summary():
    print("\n" + "=" * 55)
    print("  PREPROCESSING COMPLETE — Output Summary")
    print("=" * 55)

    npy_files = sorted([f for f in os.listdir(OUT_DIR)
                        if f.endswith(".npy")])
    if not npy_files:
        print("  No .npy files found in:", OUT_DIR)
        return

    total_mb = 0
    print(f"\n  {'File':<30} {'Shape':<25} {'Size (MB)'}")
    print("  " + "-" * 65)

    for fname in npy_files:
        fpath = os.path.join(OUT_DIR, fname)
        arr   = np.load(fpath, mmap_mode='r')
        size  = os.path.getsize(fpath) / 1e6
        total_mb += size
        print(f"  {fname:<30} {str(arr.shape):<25} {size:>8.1f}")

    print("  " + "-" * 65)
    print(f"  {'TOTAL':<55} {total_mb:>8.1f} MB")
    print(f"\n  All files saved to: {os.path.abspath(OUT_DIR)}")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
STREAMS = [
    ("Stream 1 — Violence Video",        run_violence),
    ("Stream 2 — Body Pose Keypoints",   run_pose),
    ("Stream 3 — Facial Expression",     run_fer),
    ("Stream 4 — Crowd Density",         run_crowd),
    ("Stream 5 — Optical Flow",          run_flow),
]

if __name__ == "__main__":
    # Allow running a single stream: python run_all.py 1
    # (pass the stream number as argument, e.g. 1–5)
    if len(sys.argv) > 1:
        try:
            idx = int(sys.argv[1]) - 1
            name, fn = STREAMS[idx]
            print(f"\nRunning only: {name}")
            t0 = time.time()
            fn()
            print(f"\n  Time: {time.time() - t0:.1f}s")
            print_summary()
            sys.exit(0)
        except (IndexError, ValueError):
            print(f"[ERROR] Pass a stream number 1-{len(STREAMS)}")
            sys.exit(1)

    # Run all streams
    timings = {}
    for name, fn in STREAMS:
        t0 = time.time()
        try:
            fn()
            timings[name] = time.time() - t0
        except Exception as e:
            print(f"\n[ERROR] {name} failed: {e}")
            timings[name] = -1

    # Timing summary
    print("\n" + "=" * 55)
    print("  Timing Summary")
    print("=" * 55)
    for name, elapsed in timings.items():
        status = f"{elapsed:.1f}s" if elapsed >= 0 else "FAILED"
        print(f"  {name:<40} {status}")

    print_summary()