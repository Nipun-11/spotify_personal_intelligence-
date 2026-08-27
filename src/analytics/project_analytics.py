"""Project (Album/EP) analytical engine with non-negotiable >= 3-track exploration rule (vectorized)."""

import logging
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

from src.config import PROJECT_EXPLORATION_MIN_TRACKS

logger = logging.getLogger(__name__)

def compute_project_analytics(df_events: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compute project-level analytics and project-driving song metrics (high-performance vectorized).
    
    Args:
        df_events: Canonical playback events DataFrame (music only).
        
    Returns:
        Tuple of (df_projects, df_project_driving_songs).
    """
    logger.info("Computing project (Album/EP) analytics...")
    music_df = df_events[df_events["content_type"] == "music"].copy()
    music_df["year_month"] = music_df["timestamp_local"].dt.strftime("%Y-%m")
    
    # 1. Base aggregations per project
    base_agg = music_df.groupby("project_id").agg(
        project_name=("project_name", "first"),
        artist_id=("artist_id", "first"),
        artist_name=("artist_name", "first"),
        first_heard_utc=("timestamp_utc", "min"),
        last_heard_utc=("timestamp_utc", "max"),
        total_plays=("event_id", "count"),
        total_minutes=("minutes_played", "sum"),
        tracks_heard=("track_id", "nunique"),
        active_months=("year_month", "nunique"),
        same_proj_transitions=("is_same_project_as_prev", "sum")
    ).reset_index()
    
    base_agg["total_hours"] = (base_agg["total_minutes"] / 60.0).round(2)
    base_agg["total_minutes"] = base_agg["total_minutes"].round(2)
    base_agg["is_explored"] = base_agg["tracks_heard"] >= PROJECT_EXPLORATION_MIN_TRACKS
    base_agg["sequentiality_rate"] = (base_agg["same_proj_transitions"] / np.maximum(1, base_agg["total_plays"] - 1)).round(4)
    base_agg.drop(columns=["same_proj_transitions"], inplace=True)
    
    # 2. Track contributions per project
    track_proj = music_df.groupby(["project_id", "track_id"]).agg(
        track_name=("track_name", "first"),
        artist_id=("artist_id", "first"),
        artist_name=("artist_name", "first"),
        project_name=("project_name", "first"),
        track_plays=("event_id", "count"),
        track_minutes=("minutes_played", "sum")
    ).reset_index()
    
    # Merge project totals to compute percentages
    track_proj = track_proj.merge(
        base_agg[["project_id", "total_plays", "total_minutes"]].rename(
            columns={"total_plays": "proj_total_plays", "total_minutes": "proj_total_minutes"}
        ),
        on="project_id",
        how="left"
    )
    
    track_proj["track_play_share_pct"] = ((track_proj["track_plays"] / np.maximum(1, track_proj["proj_total_plays"])) * 100.0).round(2)
    track_proj["track_minute_share_pct"] = ((track_proj["track_minutes"] / np.maximum(0.001, track_proj["proj_total_minutes"])) * 100.0).round(2)
    track_proj["track_minutes"] = track_proj["track_minutes"].round(2)
    
    # Find top song for each project
    idx_top_song = track_proj.groupby("project_id")["track_minutes"].idxmax()
    top_songs_df = track_proj.loc[idx_top_song].rename(
        columns={
            "track_id": "top_song_id",
            "track_name": "top_song_name",
            "track_plays": "top_song_plays",
            "track_minutes": "top_song_minutes",
            "track_minute_share_pct": "top_song_share_pct"
        }
    )[["project_id", "top_song_id", "top_song_name", "top_song_plays", "top_song_minutes", "top_song_share_pct"]]
    
    # Mark top song in driving songs
    track_proj["is_top_song"] = track_proj["track_id"].isin(top_songs_df["top_song_id"])
    df_project_driving_songs = track_proj[[
        "project_id", "project_name", "artist_id", "artist_name",
        "track_id", "track_name", "track_plays", "track_minutes",
        "track_play_share_pct", "track_minute_share_pct", "is_top_song"
    ]].copy()
    
    # Merge top song info into projects
    df_projects = base_agg.merge(top_songs_df, on="project_id", how="left")
    
    # Listening Style classification
    def assign_project_style(row):
        th = row["tracks_heard"]
        share = row["top_song_share_pct"]
        if th == 1:
            return "Single Track Only"
        elif th == 2:
            return "Sampled (2 tracks)"
        elif share >= 50.0:
            return "Hit-Driven Project"
        elif th >= 7:
            return "Broad / Complete Consumption"
        elif th >= 4:
            return "Deep Exploration"
        else:
            return "Explored (3 tracks)"
            
    df_projects["listening_style"] = df_projects.apply(assign_project_style, axis=1)
    
    # Format ISO timestamps
    df_projects["first_heard_utc"] = df_projects["first_heard_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df_projects["last_heard_utc"] = df_projects["last_heard_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    df_projects.drop(columns=["top_song_id"], inplace=True)
    df_projects = df_projects.sort_values("total_minutes", ascending=False).reset_index(drop=True)
    
    logger.info(f"Built projects table ({len(df_projects)} projects, {df_projects['is_explored'].sum()} explored with >= 3 tracks)")
    return df_projects, df_project_driving_songs
