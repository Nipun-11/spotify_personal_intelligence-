"""ML Dataset Builder with strict temporal integrity and no forward leakage."""

import logging
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np

from src.config import (
    TRAIN_END_YEAR,
    VAL_YEAR,
    TEST_YEAR,
    DISCOVERY_CATALYST_WINDOW_DAYS,
)

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "song_plays_before",
    "song_minutes_before",
    "song_age_days_at_play",
    "seconds_played",
    "skipped",
    "shuffle",
    "artist_plays_before",
    "artist_tracks_heard_before",
    "artist_minutes_before",
    "artist_age_days_at_play",
    "project_plays_before",
    "project_tracks_heard_before",
    "project_minutes_before",
    "project_age_days_at_play",
    "session_position",
    "hour",
    "day_of_week",
    "is_weekend",
    "is_first_artist_play",
    "is_first_project_play",
    "is_first_song_play",
    "is_same_artist_as_prev",
    "is_same_project_as_prev",
    "time_since_prev_event_seconds",
    "platform_android",
    "platform_windows",
    "platform_web_player",
]

def build_ml_dataset(
    df_events: pd.DataFrame,
    df_catalysts: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Build leakage-free ML dataset with strictly historical features and 7D forward target.
    
    Args:
        df_events: Canonical playback events DataFrame.
        df_catalysts: Precomputed discovery catalyst DataFrame with targets.
        
    Returns:
        Tuple of (full_ml_df, split_dict with 'train', 'val', 'test').
    """
    logger.info("Building strictly temporal ML dataset...")
    music_df = df_events[df_events["content_type"] == "music"].sort_values("timestamp_utc").reset_index(drop=True).copy()
    
    # Map precomputed target from catalyst engine
    target_map = df_catalysts.set_index("catalyst_event_id")["is_meaningful_expansion_7d"].to_dict()
    
    # Target: 1 if meaningful expansion within 7d, 0 otherwise
    music_df["target_expansion_7d"] = music_df["event_id"].map(target_map).fillna(False).astype(int)
    
    # Secondary Target: 30-day retention
    retention_map = df_catalysts.set_index("catalyst_event_id")["retention_30d"].to_dict()
    music_df["target_retention_30d"] = music_df["event_id"].map(retention_map).fillna(False).astype(int)
    
    # One-hot encode platform
    music_df["platform_android"] = (music_df["platform"] == "android").astype(int)
    music_df["platform_windows"] = (music_df["platform"] == "windows").astype(int)
    music_df["platform_web_player"] = (music_df["platform"] == "web_player").astype(int)
    
    # Cast booleans to int
    bool_cols = [
        "skipped", "shuffle", "is_weekend", "is_first_artist_play",
        "is_first_project_play", "is_first_song_play",
        "is_same_artist_as_prev", "is_same_project_as_prev"
    ]
    for c in bool_cols:
        if c in music_df.columns:
            music_df[c] = music_df[c].astype(int)
            
    # Fill any remaining NaNs safely
    for col in FEATURE_COLUMNS:
        if col not in music_df.columns:
            music_df[col] = 0
        else:
            music_df[col] = music_df[col].fillna(0)
            
    # Chronological Split (No random shuffling across time)
    train_mask = music_df["year"] <= TRAIN_END_YEAR  # 2020-2024
    val_mask = music_df["year"] == VAL_YEAR          # 2025
    test_mask = music_df["year"] >= TEST_YEAR         # 2026
    
    df_train = music_df[train_mask].copy()
    df_val = music_df[val_mask].copy()
    df_test = music_df[test_mask].copy()
    
    logger.info(
        f"Chronological split complete: Train={len(df_train)} ({df_train['target_expansion_7d'].mean():.3f} positive rate), "
        f"Val={len(df_val)} ({df_val['target_expansion_7d'].mean():.3f} positive rate), "
        f"Test={len(df_test)} ({df_test['target_expansion_7d'].mean():.3f} positive rate)"
    )
    
    splits = {
        "train": df_train,
        "val": df_val,
        "test": df_test
    }
    
    return music_df, splits
