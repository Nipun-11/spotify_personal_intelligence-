"""Song Lifecycle analytical engine (high performance vectorized)."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def compute_song_lifecycles(df_events: pd.DataFrame) -> pd.DataFrame:
    """Compute comprehensive lifecycle metrics for all songs.
    
    Args:
        df_events: Canonical playback events DataFrame (music only).
        
    Returns:
        DataFrame with one row per track containing full lifecycle indicators.
    """
    logger.info("Computing song lifecycles...")
    music_df = df_events[df_events["content_type"] == "music"].copy()
    dataset_max_ts = music_df["timestamp_utc"].max()
    
    # 1. Base aggregations per track
    base_agg = music_df.groupby("track_id").agg(
        track_name=("track_name", "first"),
        artist_id=("artist_id", "first"),
        artist_name=("artist_name", "first"),
        project_id=("project_id", "first"),
        project_name=("project_name", "first"),
        first_played_utc=("timestamp_utc", "min"),
        last_played_utc=("timestamp_utc", "max"),
        total_plays=("event_id", "count"),
        total_minutes=("minutes_played", "sum"),
        skip_count=("skipped", "sum"),
        avg_play_duration_sec=("seconds_played", "mean")
    ).reset_index()
    
    base_agg["total_minutes"] = base_agg["total_minutes"].round(2)
    base_agg["skip_rate"] = (base_agg["skip_count"] / base_agg["total_plays"]).round(4)
    base_agg["avg_play_duration_sec"] = base_agg["avg_play_duration_sec"].round(1)
    
    # 2. Raw lifespan
    base_agg["raw_lifespan_days"] = (
        (base_agg["last_played_utc"] - base_agg["first_played_utc"]).dt.total_seconds() / 86400.0
    ).round(1)
    
    # 3. Velocity in first 24h and first 7d
    merged = music_df.merge(base_agg[["track_id", "first_played_utc"]], on="track_id", how="left")
    time_since_first = (merged["timestamp_utc"] - merged["first_played_utc"]).dt.total_seconds() / 86400.0
    
    merged["is_first_24h"] = (time_since_first <= 1.0).astype(int)
    merged["is_first_7d"] = (time_since_first <= 7.0).astype(int)
    merged["is_after_30d"] = (time_since_first >= 30.0).astype(int)
    merged["is_after_90d"] = (time_since_first >= 90.0).astype(int)
    
    vel_agg = merged.groupby("track_id").agg(
        plays_first_24h=("is_first_24h", "sum"),
        plays_first_7d=("is_first_7d", "sum"),
        retained_30d=("is_after_30d", lambda s: bool(s.max() > 0)),
        retained_90d=("is_after_90d", lambda s: bool(s.max() > 0)),
    ).reset_index()
    
    # 4. Gaps and Active Lifespan
    sorted_df = music_df.sort_values(["track_id", "timestamp_utc"])
    sorted_df["gap_days"] = sorted_df.groupby("track_id")["timestamp_utc"].diff().dt.total_seconds() / 86400.0
    
    # Active gaps are <= 45 days
    sorted_df["active_gap"] = np.where(sorted_df["gap_days"] <= 45.0, sorted_df["gap_days"], 0.0)
    
    gap_agg = sorted_df.groupby("track_id").agg(
        max_inactivity_gap_days=("gap_days", "max"),
        active_lifespan_days=("active_gap", "sum")
    ).reset_index().fillna(0.0)
    
    gap_agg["max_inactivity_gap_days"] = gap_agg["max_inactivity_gap_days"].round(1)
    gap_agg["active_lifespan_days"] = gap_agg["active_lifespan_days"].round(1)
    
    # 5. Active Years
    active_years_series = music_df.groupby("track_id")["year"].unique().apply(
        lambda yrs: (len(yrs), ",".join(map(str, sorted(yrs))))
    )
    active_years_df = pd.DataFrame(
        active_years_series.tolist(),
        index=active_years_series.index,
        columns=["active_years_count", "active_years"]
    ).reset_index()
    
    # Merge all
    res = base_agg.merge(vel_agg, on="track_id", how="left")
    res = res.merge(gap_agg, on="track_id", how="left")
    res = res.merge(active_years_df, on="track_id", how="left")
    
    # Recency
    res["days_since_last_play"] = (
        (dataset_max_ts - res["last_played_utc"]).dt.total_seconds() / 86400.0
    ).round(1)
    
    # Lifecycle category
    def assign_song_category(row):
        total_plays = row["total_plays"]
        skip_rate = row["skip_rate"]
        raw_life = row["raw_lifespan_days"]
        p7d = row["plays_first_7d"]
        active_yrs = row["active_years_count"]
        days_since = row["days_since_last_play"]
        max_gap = row["max_inactivity_gap_days"]
        
        if total_plays <= 2 and (skip_rate >= 0.5 or raw_life <= 1.0):
            return "Failed Discovery"
        elif total_plays >= 20 and p7d >= 8:
            return "Obsession Track"
        elif active_yrs >= 3 and total_plays >= 15:
            return "Evergreen Favorite"
        elif total_plays >= 15 and days_since <= 60:
            return "Heavy Rotation"
        elif total_plays >= 10 and max_gap >= 90 and days_since <= 90:
            return "Revived Track"
        elif total_plays >= 5:
            return "Casual Favorite"
        else:
            return "Short-Lived / Trial"
            
    res["lifecycle_category"] = res.apply(assign_song_category, axis=1)
    
    # Format ISO timestamps
    res["first_played_utc"] = res["first_played_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    res["last_played_utc"] = res["last_played_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    res = res.sort_values("total_minutes", ascending=False).reset_index(drop=True)
    logger.info(f"Built song lifecycles table with {len(res)} songs")
    return res
