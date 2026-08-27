"""Discovery Catalyst ranking and scoring module."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def compute_catalyst_rankings(df_catalysts: pd.DataFrame) -> pd.DataFrame:
    """Rank catalyst songs by multi-dimensional discovery power, impact, and durability.
    
    Args:
        df_catalysts: Raw discovery catalyst events DataFrame.
        
    Returns:
        Ranked and aggregated catalyst tracks DataFrame with transparent metrics.
    """
    logger.info("Computing Discovery Catalyst Rankings...")
    if len(df_catalysts) == 0:
        return pd.DataFrame()
        
    # Aggregate by catalyst track (taking the most impactful catalyst event per track)
    track_catalysts = df_catalysts.groupby(["catalyst_track_id", "catalyst_track_name", "catalyst_artist_name", "catalyst_project_name"]).agg(
        first_catalyst_timestamp=("catalyst_timestamp_utc", "min"),
        discovery_type=("discovery_type", "first"),
        max_tracks_added_7d=("tracks_added_7d", "max"),
        max_projects_added_7d=("projects_added_7d", "max"),
        max_minutes_added_7d=("minutes_added_7d", "max"),
        max_minutes_30d=("minutes_30d", "max"),
        max_minutes_90d=("minutes_90d", "max"),
        retention_30d=("retention_30d", "max"),
        retention_90d=("retention_90d", "max"),
        future_hours_unlocked=("future_hours_unlocked", "max"),
        is_meaningful_expansion_7d=("is_meaningful_expansion_7d", "max")
    ).reset_index()
    
    # Discovery Power: 0 to 100 based on tracks and projects added in 7d
    power_raw = (track_catalysts["max_tracks_added_7d"] * 8.0) + (track_catalysts["max_projects_added_7d"] * 15.0)
    track_catalysts["discovery_power_score"] = np.clip(power_raw, 0, 100).round(1)
    
    # Discovery Impact: 0 to 100 based on future hours unlocked
    impact_raw = (track_catalysts["future_hours_unlocked"] / 25.0) * 100.0
    track_catalysts["discovery_impact_score"] = np.clip(impact_raw, 0, 100).round(1)
    
    # Discovery Quality: 0 to 100 based on 30d/90d retention and minutes
    quality_raw = (
        (track_catalysts["retention_30d"].astype(int) * 40.0) +
        (track_catalysts["retention_90d"].astype(int) * 40.0) +
        (np.clip(track_catalysts["max_minutes_30d"] / 60.0, 0, 20.0))
    )
    track_catalysts["discovery_quality_score"] = np.clip(quality_raw, 0, 100).round(1)
    
    # Overall Composite Catalyst Index (Weighted combination, but raw values remain primary)
    track_catalysts["catalyst_index"] = (
        track_catalysts["discovery_power_score"] * 0.40 +
        track_catalysts["discovery_impact_score"] * 0.35 +
        track_catalysts["discovery_quality_score"] * 0.25
    ).round(1)
    
    # Sort by catalyst index
    track_catalysts = track_catalysts.sort_values(["catalyst_index", "future_hours_unlocked"], ascending=[False, False]).reset_index(drop=True)
    track_catalysts["rank"] = track_catalysts.index + 1
    
    logger.info(f"Ranked {len(track_catalysts)} discovery catalyst tracks")
    return track_catalysts
