"""Configuration and constants for Spotify Personal Intelligence Engine."""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw" / "Spotify Extended Streaming History"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
ML_DATA_DIR = DATA_DIR / "ml"
MODELS_DIR = BASE_DIR / "models"
DOCS_DIR = BASE_DIR / "docs"

# Ensure directories exist
for directory in [
    DATA_DIR,
    RAW_DATA_DIR,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
    SAMPLE_DATA_DIR,
    ML_DATA_DIR,
    MODELS_DIR,
    DOCS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Timezone
LOCAL_TIMEZONE = "Asia/Kolkata"  # IST (+05:30)

# Non-negotiable analytical rules
PROJECT_EXPLORATION_MIN_TRACKS = 3  # Must be at least 3 unique tracks heard
SESSION_INACTIVITY_MINUTES = 30     # 30-minute inactivity threshold for new session
DISCOVERY_CATALYST_WINDOW_DAYS = 7  # 7-day catalyst evaluation window
RETENTION_SHORT_DAYS = 30           # 30-day retention evaluation window
RETENTION_LONG_DAYS = 90            # 90-day impact evaluation window

# ML Temporal splits
TRAIN_END_YEAR = 2024
VAL_YEAR = 2025
TEST_YEAR = 2026

# Time-of-day buckets (8 standard 3-hour blocks)
TIME_OF_DAY_BUCKETS = {
    "12AM-3AM": (0, 3),
    "3AM-6AM": (3, 6),
    "6AM-9AM": (6, 9),
    "9AM-12PM": (9, 12),
    "12PM-3PM": (12, 15),
    "3PM-6PM": (15, 18),
    "6PM-9PM": (18, 21),
    "9PM-12AM": (21, 24),
}

# API configuration
API_HOST = "127.0.0.1"
API_PORT = 8000
