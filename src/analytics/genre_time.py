"""Genre and Time-of-Day analytical module."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

from src.metadata.genre_rules import infer_genre
from src.config import TIME_OF_DAY_BUCKETS

logger = logging.getLogger(__name__)

def compute_genre_time_analytics(df_events: pd.DataFrame) -> Dict[str, Any]:
    """Compute Genre x Time-of-Day x Year matrices, genre migrations, and time-of-day heatmaps.
    
    Args:
        df_events: Canonical playback events DataFrame (music only).
        
    Returns:
        Dictionary containing:
          - 'genre_time_matrix': DataFrame of (genre, time_of_day_bucket, year, minutes, plays, share)
          - 'yearly_genre_share': DataFrame of (year, genre, minutes, share)
          - 'artist_time_heatmap': DataFrame of (artist_name, time_of_day_bucket, minutes, share)
    """
    logger.info("Computing genre x time-of-day analytics...")
    music_df = df_events[df_events["content_type"] == "music"].copy()
    
    # Assign genre to each event
    music_df["genre"] = music_df["artist_name"].apply(infer_genre)
    
    # 1. Genre x Time Bucket x Year
    genre_time = music_df.groupby(["genre", "time_of_day_bucket", "year"]).agg(
        total_minutes=("minutes_played", "sum"),
        total_plays=("event_id", "count"),
        skip_count=("skipped", "sum")
    ).reset_index()
    
    genre_time["skip_rate"] = (genre_time["skip_count"] / genre_time["total_plays"]).round(4)
    genre_time["total_minutes"] = genre_time["total_minutes"].round(2)
    
    # Calculate yearly share
    yearly_totals = genre_time.groupby("year")["total_minutes"].transform("sum")
    genre_time["yearly_minute_share_pct"] = ((genre_time["total_minutes"] / yearly_totals) * 100.0).round(2)
    
    # 2. Yearly Genre Share
    yearly_genre = music_df.groupby(["year", "genre"]).agg(
        total_minutes=("minutes_played", "sum"),
        total_plays=("event_id", "count")
    ).reset_index()
    
    y_tot = yearly_genre.groupby("year")["total_minutes"].transform("sum")
    yearly_genre["genre_share_pct"] = ((yearly_genre["total_minutes"] / y_tot) * 100.0).round(2)
    yearly_genre["total_minutes"] = yearly_genre["total_minutes"].round(2)
    yearly_genre = yearly_genre.sort_values(["year", "total_minutes"], ascending=[True, False]).reset_index(drop=True)
    
    # 3. Artist x Time of Day (for top 25 artists)
    top_artists = music_df["artist_name"].value_counts().head(25).index.tolist()
    top_artist_df = music_df[music_df["artist_name"].isin(top_artists)]
    
    artist_time = top_artist_df.groupby(["artist_name", "time_of_day_bucket"]).agg(
        total_minutes=("minutes_played", "sum"),
        total_plays=("event_id", "count")
    ).reset_index()
    
    art_tot = artist_time.groupby("artist_name")["total_minutes"].transform("sum")
    artist_time["bucket_share_pct"] = ((artist_time["total_minutes"] / art_tot) * 100.0).round(2)
    artist_time["total_minutes"] = artist_time["total_minutes"].round(2)
    
    logger.info("Computed genre time matrix and yearly genre migrations")
    return {
        "genre_time_matrix": genre_time,
        "yearly_genre_share": yearly_genre,
        "artist_time_heatmap": artist_time
    }
