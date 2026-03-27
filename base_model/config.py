import os

# ── Root — dynamic path based on file location ──────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))

# ── All datasets live inside the 'dataset' subfolder ──────────────────────
DATASET_DIR = os.path.join(ROOT, "dataset")
OUT_DIR     = os.path.join(ROOT, "data", "preprocessed")
WEIGHTS_DIR = os.path.join(ROOT, "models", "weights")

# ── Individual dataset paths (matched to your exact folder names) ──────────
VIOLENCE_DIR  = os.path.join(DATASET_DIR,
                             "Real Life Violence",
                             "Real Life Violence Dataset")

VIOLENCE2_DIR = os.path.join(DATASET_DIR,
                             "Real Life Violence",
                             "real life violence situations",
                             "Real Life Violence Dataset")

SCVD_DIR      = os.path.join(DATASET_DIR,
                             "Smart-City CCTV Violence Detection",
                             "SCVD",
                             "SCVD_converted_sec_split")

POSE_DIR      = os.path.join(DATASET_DIR, "CCTV Human Pose Estimation")

FER_DIR       = os.path.join(DATASET_DIR, "FER-2013")

CROWD_DIR     = os.path.join(DATASET_DIR, "Crowd Counting")

# ── Output .npy file names ─────────────────────────────────────────────────
VIOLENCE_X   = os.path.join(OUT_DIR, "violence_X.npy")
VIOLENCE_Y   = os.path.join(OUT_DIR, "violence_y.npy")
POSE_X       = os.path.join(OUT_DIR, "pose_X.npy")
POSE_Y       = os.path.join(OUT_DIR, "pose_y.npy")
FER_X        = os.path.join(OUT_DIR, "fer_X.npy")
FER_Y        = os.path.join(OUT_DIR, "fer_y.npy")
CROWD_X      = os.path.join(OUT_DIR, "crowd_X.npy")
CROWD_Y      = os.path.join(OUT_DIR, "crowd_y.npy")
FLOW_X       = os.path.join(OUT_DIR, "flow_X.npy")
FLOW_Y       = os.path.join(OUT_DIR, "flow_y.npy")

# ── Model hyperparameters ──────────────────────────────────────────────────
IMG_SIZE      = 112   # reduced from 224 — 4x smaller files
CROWD_SIZE    = 256   # reduced from 512
SEQUENCE_LEN  = 16    # reduced from 30 — still enough for motion
BATCH_SIZE    = 8
EPOCHS        = 30
LEARNING_RATE = 1e-4

# ── Max videos per class (prevents disk overflow) ─────────────────────────
# 500 per class → ~2GB for violence stream
# Set to None to use all videos (needs ~15GB free)
MAX_VIDEOS_PER_CLASS = 100

# ── Alert thresholds ───────────────────────────────────────────────────────
LOW_THRESHOLD    = 0.30
MEDIUM_THRESHOLD = 0.60
HIGH_THRESHOLD   = 0.85

# ── Emotion → aggression label map (for FER-2013) ─────────────────────────
AGGRESSIVE_EMOTIONS = {
    "angry":    1,
    "disgust":  1,
    "fear":     1,
    "happy":    0,
    "neutral":  0,
    "sad":      0,
    "surprise": 0,
}

# ── Video file extensions ──────────────────────────────────────────────────
VIDEO_EXTS = ('.mp4', '.avi', '.mkv', '.mov')
IMAGE_EXTS = ('.jpg', '.jpeg', '.png')

# ── Create output directories on import ───────────────────────────────────
for _dir in [OUT_DIR, WEIGHTS_DIR]:
    os.makedirs(_dir, exist_ok=True)