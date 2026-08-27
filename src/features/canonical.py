"""Canonical Playback Table construction with strictly historical feature engineering."""

import logging
from typing import Optional
import pandas as pd
import numpy as np

from src.sessions.sessionizer import assign_sessions

logger = logging.getLogger(__name__)

def build_canonical_playback_events(df_normalized: pd.DataFrame) -> pd.DataFrame:
    """Transform normalized playback data into canonical playback events with strictly historical features.
    
    Args:
        df_normalized: Normalized playback DataFrame sorted by timestamp_utc.
        
    Returns:
        Canonical playback events DataFrame.
    """
    logger.info("Building canonical playback events table...")
    df = df_normalized.sort_values("timestamp_utc").reset_index(drop=True).copy()
    
    # 1. Assign sessions and session positions
    df = assign_sessions(df)
    
    # 2. Add Sequence Lags and Leads (global and session-aware)
    df["previous_track_id"] = df["track_id"].shift(1)
    df["previous_track_name"] = df["track_name"].shift(1)
    df["previous_artist_id"] = df["artist_id"].shift(1)
    df["previous_artist_name"] = df["artist_name"].shift(1)
    df["previous_project_id"] = df["project_id"].shift(1)
    df["previous_project_name"] = df["project_name"].shift(1)
    
    df["next_track_id"] = df["track_id"].shift(-1)
    df["next_track_name"] = df["track_name"].shift(-1)
    df["next_artist_id"] = df["artist_id"].shift(-1)
    df["next_artist_name"] = df["artist_name"].shift(-1)
    df["next_project_id"] = df["project_id"].shift(-1)
    df["next_project_name"] = df["project_name"].shift(-1)
    
    df["time_since_prev_event_seconds"] = (df["timestamp_utc"] - df["timestamp_utc"].shift(1)).dt.total_seconds().fillna(0)
    df["is_same_artist_as_prev"] = (df["artist_id"] == df["previous_artist_id"]) & (df["previous_artist_id"].notna())
    df["is_same_project_as_prev"] = (df["project_id"] == df["previous_project_id"]) & (df["previous_project_id"].notna())
    
    # Reset transition if across different sessions or gap > 30 min
    different_session = df["session_id"] != df["session_id"].shift(1)
    df.loc[different_session, "is_same_artist_as_prev"] = False
    df.loc[different_session, "is_same_project_as_prev"] = False
    
    # 3. Retrospective Historical Cumulative Metrics (NO FUTURE LEAKAGE)
    logger.info("Computing cumulative historical metrics (strictly pre-T)...")
    
    # Track-level history
    df["song_plays_before"] = df.groupby("track_id").cumcount()
    df["is_first_song_play"] = df["song_plays_before"] == 0
    df["song_first_seen_utc"] = df.groupby("track_id")["timestamp_utc"].transform("first")
    df["song_age_days_at_play"] = (df["timestamp_utc"] - df["song_first_seen_utc"]).dt.total_seconds() / 86400.0
    
    # Cumulative minutes before
    df["song_minutes_before"] = df.groupby("track_id")["minutes_played"].cumsum() - df["minutes_played"]
    
    # Artist-level history
    df["artist_plays_before"] = df.groupby("artist_id").cumcount()
    df["is_first_artist_play"] = df["artist_plays_before"] == 0
    df["artist_first_seen_utc"] = df.groupby("artist_id")["timestamp_utc"].transform("first")
    df["artist_age_days_at_play"] = (df["timestamp_utc"] - df["artist_first_seen_utc"]).dt.total_seconds() / 86400.0
    df["artist_minutes_before"] = df.groupby("artist_id")["minutes_played"].cumsum() - df["minutes_played"]
    
    # Artist unique tracks heard before (cumulative unique tracks)
    # Using cumcount of unique track first encounters per artist
    first_track_artist_mask = df.groupby(["artist_id", "track_id"]).cumcount() == 0
    df["_is_first_track_for_artist"] = first_track_artist_mask.astype(int)
    df["artist_tracks_heard_before"] = df.groupby("artist_id")["_is_first_track_for_artist"].cumsum() - df["_is_first_track_for_artist"]
    df.drop(columns=["_is_first_track_for_artist"], inplace=True)
    
    # Project-level history
    df["project_plays_before"] = df.groupby("project_id").cumcount()
    df["is_first_project_play"] = df["project_plays_before"] == 0
    df["project_first_seen_utc"] = df.groupby("project_id")["timestamp_utc"].transform("first")
    df["project_age_days_at_play"] = (df["timestamp_utc"] - df["project_first_seen_utc"]).dt.total_seconds() / 86400.0
    df["project_minutes_before"] = df.groupby("project_id")["minutes_played"].cumsum() - df["minutes_played"]
    
    # Project unique tracks heard before
    first_track_project_mask = df.groupby(["project_id", "track_id"]).cumcount() == 0
    df["_is_first_track_for_project"] = first_track_project_mask.astype(int)
    df["project_tracks_heard_before"] = df.groupby("project_id")["_is_first_track_for_project"].cumsum() - df["_is_first_track_for_project"]
    df.drop(columns=["_is_first_track_for_project"], inplace=True)
    
    logger.info(f"Canonical table successfully built with {len(df)} records and {len(df.columns)} columns")
    return df
