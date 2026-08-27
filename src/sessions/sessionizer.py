"""Sessionization and session metrics calculation module (high performance vectorized)."""

import logging
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

from src.config import SESSION_INACTIVITY_MINUTES

logger = logging.getLogger(__name__)

def assign_sessions(df: pd.DataFrame, inactivity_minutes: int = SESSION_INACTIVITY_MINUTES) -> pd.DataFrame:
    """Assign session_id and session_position to chronologically sorted playback events.
    
    Args:
        df: Normalized playback events DataFrame sorted by timestamp_utc.
        inactivity_minutes: Inactivity gap in minutes that triggers a new session.
        
    Returns:
        DataFrame with session_id and session_position added.
    """
    df_sorted = df.sort_values("timestamp_utc").reset_index(drop=True).copy()
    
    # Calculate time delta between consecutive events in minutes
    time_diff = df_sorted["timestamp_utc"].diff()
    time_diff_min = time_diff.dt.total_seconds() / 60.0
    
    # New session condition: first event or gap > inactivity_minutes
    is_new_session = (time_diff_min > inactivity_minutes) | (time_diff.isna())
    
    # Session numeric index
    session_num = is_new_session.cumsum()
    
    # Formatted session_id
    date_str = df_sorted["date"]
    df_sorted["session_id"] = date_str + "_" + session_num.astype(str).str.zfill(6)
    
    # Session position (1-indexed)
    df_sorted["session_position"] = df_sorted.groupby("session_id").cumcount() + 1
    
    # Session track count
    session_counts = df_sorted.groupby("session_id")["event_id"].transform("count")
    df_sorted["session_length"] = session_counts
    
    logger.info(f"Generated {df_sorted['session_id'].nunique()} distinct sessions from {len(df_sorted)} playback events")
    return df_sorted

def classify_session_type(
    track_count: int,
    listening_minutes: float,
    unique_artists: int,
    unique_projects: int,
    discovery_count: int,
    dominant_artist_share: float,
    dominant_project_share: float
) -> str:
    """Classify session into standard behavioral taxonomy."""
    if track_count <= 2 or listening_minutes < 5:
        return "short_burst"
    if discovery_count >= 3 and unique_artists >= 4:
        return "rabbit_hole"
    if discovery_count / max(1, track_count) >= 0.5 and discovery_count >= 2:
        return "discovery_session"
    if dominant_project_share >= 0.70 and track_count >= 3:
        return "album_session"
    if dominant_artist_share >= 0.70 and track_count >= 3:
        return "artist_exploration"
    if track_count > 10 and listening_minutes >= 30:
        return "long_session"
    return "normal_session"

def build_sessions_table(df_events: pd.DataFrame) -> pd.DataFrame:
    """Build aggregated gold sessions table from playback events (vectorized).
    
    Args:
        df_events: Canonical playback events with session_id, session_position, and discovery indicators.
        
    Returns:
        Aggregated sessions DataFrame.
    """
    logger.info("Building aggregated sessions table...")
    
    # 1. Base aggregations per session
    base_agg = df_events.groupby("session_id").agg(
        start_time_utc=("timestamp_utc", "min"),
        end_time_utc=("timestamp_utc", "max"),
        start_time_local=("timestamp_local", "min"),
        date=("date", "first"),
        year=("year", "first"),
        month=("month", "first"),
        day_of_week=("day_of_week", "first"),
        hour=("hour", "first"),
        time_of_day_bucket=("time_of_day_bucket", "first"),
        is_weekend=("is_weekend", "first"),
        listening_minutes=("minutes_played", "sum"),
        track_count=("event_id", "count"),
        unique_tracks=("track_id", "nunique"),
        unique_artists=("artist_id", "nunique"),
        unique_projects=("project_id", "nunique"),
        skip_count=("skipped", "sum"),
        shuffle_count=("shuffle", "sum"),
        discovery_count=("is_first_artist_play", lambda s: int(s.sum()) if "is_first_artist_play" in s else 0),
        primary_platform=("platform", lambda p: p.mode()[0] if len(p.mode()) > 0 else "other")
    ).reset_index()
    
    # Compute derived metrics
    base_agg["session_duration_minutes"] = (
        (base_agg["end_time_utc"] - base_agg["start_time_utc"]).dt.total_seconds() / 60.0
    ).round(2)
    base_agg["listening_minutes"] = base_agg["listening_minutes"].round(2)
    base_agg["skip_rate"] = (base_agg["skip_count"] / np.maximum(1, base_agg["track_count"])).round(4)
    base_agg["shuffle_rate"] = (base_agg["shuffle_count"] / np.maximum(1, base_agg["track_count"])).round(4)
    base_agg["repetition_count"] = base_agg["track_count"] - base_agg["unique_tracks"]
    
    # 2. Dominant artist and project shares
    art_counts = df_events.groupby(["session_id", "artist_name"]).size().reset_index(name="count")
    idx_max_art = art_counts.groupby("session_id")["count"].idxmax()
    dominant_art_df = art_counts.loc[idx_max_art].rename(columns={"artist_name": "dominant_artist", "count": "dominant_art_count"})
    
    proj_counts = df_events.groupby(["session_id", "project_name"]).size().reset_index(name="count")
    idx_max_proj = proj_counts.groupby("session_id")["count"].idxmax()
    dominant_proj_df = proj_counts.loc[idx_max_proj].rename(columns={"project_name": "dominant_project", "count": "dominant_proj_count"})
    
    # Merge
    res = base_agg.merge(dominant_art_df[["session_id", "dominant_artist", "dominant_art_count"]], on="session_id", how="left")
    res = res.merge(dominant_proj_df[["session_id", "dominant_project", "dominant_proj_count"]], on="session_id", how="left")
    
    res["dominant_artist_share"] = (res["dominant_art_count"] / np.maximum(1, res["track_count"])).round(4)
    res["dominant_project_share"] = (res["dominant_proj_count"] / np.maximum(1, res["track_count"])).round(4)
    
    # Session taxonomy classification
    res["session_type"] = res.apply(
        lambda r: classify_session_type(
            track_count=r["track_count"],
            listening_minutes=r["listening_minutes"],
            unique_artists=r["unique_artists"],
            unique_projects=r["unique_projects"],
            discovery_count=r["discovery_count"],
            dominant_artist_share=r["dominant_artist_share"],
            dominant_project_share=r["dominant_project_share"]
        ),
        axis=1
    )
    
    # Format timestamps
    res["start_time_utc"] = res["start_time_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    res["end_time_utc"] = res["end_time_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    res["start_time_local"] = res["start_time_local"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    cols_to_drop = ["dominant_art_count", "dominant_proj_count", "shuffle_count"]
    res.drop(columns=[c for c in cols_to_drop if c in res.columns], inplace=True)
    
    logger.info(f"Built gold sessions table with {len(res)} session rows")
    return res
