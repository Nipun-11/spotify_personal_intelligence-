"""Listening freshness, nostalgia curves, and taste fingerprint analytics."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def categorize_song_age(age_days: float) -> str:
    """Categorize song age in listener history into standard freshness bands."""
    if age_days < 7.0:
        return "< 7 Days (Newly Discovered)"
    elif age_days < 30.0:
        return "7-30 Days (Recent Discovery)"
    elif age_days < 90.0:
        return "1-3 Months (Developing Catalog)"
    elif age_days < 365.0:
        return "3-12 Months (Established Rotation)"
    elif age_days < 730.0:
        return "1-2 Years (Long-Term Vault)"
    else:
        return "2+ Years (Nostalgia / Deep Vault)"

def compute_freshness_analytics(df_events: pd.DataFrame) -> Dict[str, Any]:
    """Compute Listening Freshness curves and 8-dimensional Taste Fingerprint metrics.
    
    Args:
        df_events: Canonical playback events DataFrame (music only).
        
    Returns:
        Dictionary containing:
          - 'freshness_distribution': DataFrame of (age_band, total_minutes, share_pct, total_plays)
          - 'freshness_by_year': DataFrame of (year, age_band, total_minutes, share_pct)
          - 'taste_fingerprint': Dict of 8 normalized (0-100) behavioral traits
    """
    logger.info("Computing listening freshness and taste fingerprint...")
    music_df = df_events[df_events["content_type"] == "music"].copy()
    
    # Age band assignment
    music_df["age_band"] = music_df["song_age_days_at_play"].apply(categorize_song_age)
    
    # 1. Overall Freshness Distribution
    freshness = music_df.groupby("age_band").agg(
        total_minutes=("minutes_played", "sum"),
        total_plays=("event_id", "count")
    ).reset_index()
    
    tot_min = freshness["total_minutes"].sum()
    freshness["share_pct"] = ((freshness["total_minutes"] / max(0.001, tot_min)) * 100.0).round(2)
    freshness["total_minutes"] = freshness["total_minutes"].round(2)
    
    # 2. Freshness by Year
    freshness_yr = music_df.groupby(["year", "age_band"]).agg(
        total_minutes=("minutes_played", "sum"),
        total_plays=("event_id", "count")
    ).reset_index()
    
    y_tot = freshness_yr.groupby("year")["total_minutes"].transform("sum")
    freshness_yr["share_pct"] = ((freshness_yr["total_minutes"] / np.maximum(0.001, y_tot)) * 100.0).round(2)
    freshness_yr["total_minutes"] = freshness_yr["total_minutes"].round(2)
    
    # 3. Taste Fingerprint (8 Key Dimensions normalized 0 to 100)
    total_music_events = len(music_df)
    unique_tracks = music_df["track_id"].nunique()
    unique_artists = music_df["artist_id"].nunique()
    unique_projects = music_df["project_id"].nunique()
    
    # A. Exploration Score (Discovery rate: unique artists per 100 plays)
    discovery_rate = (unique_artists / max(1, total_music_events)) * 100.0
    exploration_score = min(100.0, max(10.0, discovery_rate * 8.0))
    
    # B. Loyalty Score (Concentration of top 5 artists listening time)
    top5_artists_min = music_df.groupby("artist_name")["minutes_played"].sum().nlargest(5).sum()
    loyalty_share = (top5_artists_min / max(0.001, tot_min)) * 100.0
    loyalty_score = min(100.0, max(10.0, loyalty_share * 1.5))
    
    # C. Repetition Score (Plays per unique track)
    repetition_ratio = total_music_events / max(1, unique_tracks)
    repetition_score = min(100.0, max(10.0, (repetition_ratio / 6.0) * 100.0))
    
    # D. Catalog Depth Score (Unique tracks per artist heard)
    tracks_per_artist = unique_tracks / max(1, unique_artists)
    catalog_depth_score = min(100.0, max(10.0, (tracks_per_artist / 5.0) * 100.0))
    
    # E. Album Affinity Score (% of plays in explored projects >= 3 tracks)
    # Using session same-project transition rate as proxy for album affinity
    album_trans_rate = (music_df["is_same_project_as_prev"]).mean() * 100.0
    album_affinity_score = min(100.0, max(10.0, album_trans_rate * 2.5))
    
    # F. Discovery Retention Score (% of tracks played more than once)
    track_counts = music_df["track_id"].value_counts()
    retention_pct = ((track_counts > 1).sum() / max(1, len(track_counts))) * 100.0
    discovery_retention_score = min(100.0, max(10.0, retention_pct))
    
    # G. Nostalgia Score (% of listening from tracks older than 1 year)
    nostalgia_min = music_df[music_df["song_age_days_at_play"] >= 365.0]["minutes_played"].sum()
    nostalgia_pct = (nostalgia_min / max(0.001, tot_min)) * 100.0
    nostalgia_score = min(100.0, max(10.0, nostalgia_pct * 3.0))
    
    # H. Selectivity Score (Skip rate behavior)
    skip_rate = music_df["skipped"].mean() * 100.0
    selectivity_score = min(100.0, max(10.0, skip_rate * 1.2))
    
    taste_fingerprint = {
        "Exploration": round(exploration_score, 1),
        "Artist Loyalty": round(loyalty_score, 1),
        "Song Repetition": round(repetition_score, 1),
        "Catalog Depth": round(catalog_depth_score, 1),
        "Album Affinity": round(album_affinity_score, 1),
        "Discovery Retention": round(discovery_retention_score, 1),
        "Nostalgia / Vault": round(nostalgia_score, 1),
        "Listening Selectivity": round(selectivity_score, 1),
    }
    
    logger.info(f"Taste fingerprint derived: {taste_fingerprint}")
    return {
        "freshness_distribution": freshness,
        "freshness_by_year": freshness_yr,
        "taste_fingerprint": taste_fingerprint
    }
