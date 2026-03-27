"""
train_all.py — Master Training Runner
Trains all models in correct order.
Fusion model is always trained last.

Usage:
    py -3.10 training/train_all.py          # train all
    py -3.10 training/train_all.py 1        # train only violence
    py -3.10 training/train_all.py 3        # train only FER
    py -3.10 training/train_all.py fusion   # train only fusion
"""

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from train_violence import run as run_violence
from train_pose     import run as run_pose
from train_fer      import run as run_fer
from train_crowd    import run as run_crowd
from train_flow     import run as run_flow
from train_fusion   import run as run_fusion

MODELS = [
    ("1", "Violence Video",       run_violence),
    ("2", "Body Pose",            run_pose),
    ("3", "Facial Expression",    run_fer),
    ("4", "Crowd Density",        run_crowd),
    ("5", "Optical Flow",         run_flow),
    ("fusion", "Fusion Model",    run_fusion),
]

if __name__ == "__main__":
    # Single model mode
    if len(sys.argv) > 1:
        key = sys.argv[1].lower()
        match = [(k, n, fn) for k, n, fn in MODELS if k == key]
        if not match:
            print(f"[ERROR] Unknown model '{key}'. Choose from: "
                  f"{[k for k,_,_ in MODELS]}")
            sys.exit(1)
        k, name, fn = match[0]
        print(f"\nTraining: {name}")
        t0 = time.time()
        fn()
        print(f"\nDone in {time.time()-t0:.1f}s")
        sys.exit(0)

    # Train all in order
    timings = {}
    for key, name, fn in MODELS:
        print(f"\n{'='*55}")
        print(f"  Starting: {name}")
        print(f"{'='*55}")
        t0 = time.time()
        try:
            fn()
            timings[name] = time.time() - t0
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")
            timings[name] = -1

    # Summary
    print("\n" + "=" * 55)
    print("  Training Complete — Summary")
    print("=" * 55)
    for name, elapsed in timings.items():
        status = f"{elapsed/60:.1f} min" if elapsed >= 0 else "FAILED"
        print(f"  {name:<25} {status}")