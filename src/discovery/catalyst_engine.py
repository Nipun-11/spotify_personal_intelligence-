"""Flagship Discovery Catalyst Engine (ultra-fast numpy accelerated)."""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from src.config import (
    DISCOVERY_CATALYST_WINDOW_DAYS,
    RETENTION_SHORT_DAYS,
    RETENTION_LONG_DAYS,
)

logger = logging.getLogger(__name__)

def identify_discovery_type(row: pd.Series) -> str:
    """Classify the discovery nature of an event based on prior history.
    
    Args:
        row: Event row with strictly historical features.
        
    Returns:
        Discovery classification string.
    """
    is_first_artist = bool(row.get("is_first_artist_play", False))
    is_first_proj = bool(row.get("is_first_project_play", False))
    artist_plays_before = int(row.get("artist_plays_before", 0))
    time_since_last_artist = float(row.get("time_since_last_artist_play_days", 0.0))
    
    if is_first_artist or artist_plays_before == 0:
        return "Artist Discovery"
    elif is_first_proj:
        return "Project Discovery"
    elif time_since_last_artist >= 45.0:
        return "Re-engagement"
    else:
        return "Catalog Deepening"

def compute_discovery_catalysts(df_events: pd.DataFrame) -> pd.DataFrame:
    """Compute downstream 7D/30D/90D catalog expansion metrics for candidate catalyst events.
    
    Args:
        df_events: Canonical playback events DataFrame (music only).
        
    Returns:
        DataFrame of discovery events and catalyst scores.
    """
    logger.info("Running Flagship Discovery Catalyst Engine...")
    music_df = df_events[df_events["content_type"] == "music"].sort_values("timestamp_utc").reset_index(drop=True).copy()
    
    # Precompute time since last artist play for each event
    music_df["prev_artist_play_ts"] = music_df.groupby("artist_id")["timestamp_utc"].shift(1)
    music_df["time_since_last_artist_play_days"] = (
        (music_df["timestamp_utc"] - music_df["prev_artist_play_ts"]).dt.total_seconds() / 86400.0
    ).fillna(0.0)
    
    # Candidate catalysts
    candidate_mask = (
        (music_df["is_first_song_play"]) |
        (music_df["is_first_artist_play"]) |
        (music_df["is_first_project_play"]) |
        (music_df["time_since_last_artist_play_days"] >= 45.0)
    )
    
    candidates = music_df[candidate_mask].copy()
    logger.info(f"Identified {len(candidates)} candidate catalyst events out of {len(music_df)} total music plays")
    
    # Group pre-sorted artist data arrays for high speed slicing
    artist_data = {}
    for art_id, grp in music_df.groupby("artist_id"):
        artist_data[art_id] = {
            "ts": grp["timestamp_utc"].values,
            "track_id": grp["track_id"].values,
            "project_id": grp["project_id"].values,
            "minutes": grp["minutes_played"].values,
        }
        
    dt_7d = np.timedelta64(DISCOVERY_CATALYST_WINDOW_DAYS, "D")
    dt_14d = np.timedelta64(14, "D")
    dt_30d = np.timedelta64(RETENTION_SHORT_DAYS, "D")
    dt_90d = np.timedelta64(RETENTION_LONG_DAYS, "D")
    
    catalyst_records = []
    
    for _, row in candidates.iterrows():
        t = row["timestamp_utc"]
        t_val = t.to_datetime64()
        art_id = row["artist_id"]
        trk_id = row["track_id"]
        
        art_d = artist_data.get(art_id)
        if art_d is None or len(art_d["ts"]) == 0:
            continue
            
        ts_arr = art_d["ts"]
        track_arr = art_d["track_id"]
        proj_arr = art_d["project_id"]
        min_arr = art_d["minutes"]
        
        # Binary search indices
        idx_t = np.searchsorted(ts_arr, t_val, side="left")
        idx_7d = np.searchsorted(ts_arr, t_val + dt_7d, side="right")
        idx_14d = np.searchsorted(ts_arr, t_val + dt_14d, side="right")
        idx_30d = np.searchsorted(ts_arr, t_val + dt_30d, side="right")
        idx_90d = np.searchsorted(ts_arr, t_val + dt_90d, side="right")
        
        # Prior tracks and projects heard before T
        prior_tracks = set(track_arr[:idx_t])
        prior_projects = set(proj_arr[:idx_t])
        
        # 1. 7-Day Window [T, T + 7d]
        w7_tracks = set(track_arr[idx_t:idx_7d])
        w7_projects = set(proj_arr[idx_t:idx_7d])
        
        tracks_added_7d = len(w7_tracks - prior_tracks)
        projects_added_7d = len(w7_projects - prior_projects)
        plays_added_7d = idx_7d - idx_t
        minutes_added_7d = float(np.sum(min_arr[idx_t:idx_7d]))
        
        # 2. 30-Day Window [T, T + 30d]
        w30_tracks = set(track_arr[idx_t:idx_30d])
        w30_projects = set(proj_arr[idx_t:idx_30d])
        
        tracks_30d = len(w30_tracks - prior_tracks)
        projects_30d = len(w30_projects - prior_projects)
        plays_30d = idx_30d - idx_t
        minutes_30d = float(np.sum(min_arr[idx_t:idx_30d]))
        retention_30d = bool((idx_30d - idx_14d) > 0)
        
        # 3. 90-Day Window [T, T + 90d]
        w90_tracks = set(track_arr[idx_t:idx_90d])
        w90_projects = set(proj_arr[idx_t:idx_90d])
        
        tracks_90d = len(w90_tracks - prior_tracks)
        projects_90d = len(w90_projects - prior_projects)
        plays_90d = idx_90d - idx_t
        minutes_90d = float(np.sum(min_arr[idx_t:idx_90d]))
        retention_90d = bool((idx_90d - idx_30d) > 0)
        
        # 4. Total Future Hours Unlocked
        future_hours_unlocked = float(np.sum(min_arr[idx_t:]) / 60.0)
        
        disc_type = identify_discovery_type(row)
        is_meaningful_expansion_7d = bool((tracks_added_7d >= 2) or (minutes_added_7d >= 30.0 and plays_added_7d >= 4))
        
        catalyst_records.append({
            "catalyst_event_id": row["event_id"],
            "catalyst_track_id": trk_id,
            "catalyst_track_name": row["track_name"],
            "catalyst_artist_id": art_id,
            "catalyst_artist_name": row["artist_name"],
            "catalyst_project_id": row["project_id"],
            "catalyst_project_name": row["project_name"],
            "catalyst_timestamp_utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "catalyst_date": row["date"],
            "catalyst_year": int(row["year"]),
            "discovery_type": disc_type,
            "is_meaningful_expansion_7d": is_meaningful_expansion_7d,
            "tracks_added_7d": tracks_added_7d,
            "projects_added_7d": projects_added_7d,
            "plays_added_7d": plays_added_7d,
            "minutes_added_7d": round(minutes_added_7d, 2),
            "tracks_30d": tracks_30d,
            "projects_30d": projects_30d,
            "plays_30d": plays_30d,
            "minutes_30d": round(minutes_30d, 2),
            "retention_30d": retention_30d,
            "tracks_90d": tracks_90d,
            "projects_90d": projects_90d,
            "plays_90d": plays_90d,
            "minutes_90d": round(minutes_90d, 2),
            "retention_90d": retention_90d,
            "future_hours_unlocked": round(future_hours_unlocked, 2)
        })
        
    df_catalysts = pd.DataFrame(catalyst_records)
    logger.info(f"Computed discovery catalyst metrics for {len(df_catalysts)} events")
    return df_catalysts
