"""Artist Lifecycle analytical engine (high performance vectorized)."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def compute_artist_lifecycles(df_events: pd.DataFrame) -> pd.DataFrame:
    """Compute comprehensive lifecycle metrics for all artists.
    
    Args:
        df_events: Canonical playback events DataFrame (music only).
        
    Returns:
        DataFrame with one row per artist containing full lifecycle indicators.
    """
    logger.info("Computing artist lifecycles...")
    music_df = df_events[df_events["content_type"] == "music"].copy()
    dataset_max_ts = music_df["timestamp_utc"].max()
    
    music_df["year_month"] = music_df["timestamp_local"].dt.strftime("%Y-%m")
    
    # 1. Base aggregations per artist
    base_agg = music_df.groupby("artist_id").agg(
        artist_name=("artist_name", "first"),
        first_heard_utc=("timestamp_utc", "min"),
        last_heard_utc=("timestamp_utc", "max"),
        total_plays=("event_id", "count"),
        total_minutes=("minutes_played", "sum"),
        unique_tracks=("track_id", "nunique"),
        unique_projects=("project_id", "nunique"),
        active_days=("date", "nunique"),
        active_months=("year_month", "nunique"),
    ).reset_index()
    
    base_agg["total_hours"] = (base_agg["total_minutes"] / 60.0).round(2)
    base_agg["total_minutes"] = base_agg["total_minutes"].round(2)
    
    # 2. Peak Month per artist
    monthly_art = music_df.groupby(["artist_id", "year_month"])["minutes_played"].sum().reset_index()
    idx_max_month = monthly_art.groupby("artist_id")["minutes_played"].idxmax()
    peak_months_df = monthly_art.loc[idx_max_month].rename(
        columns={"year_month": "peak_month", "minutes_played": "peak_month_minutes"}
    )
    
    # 3. Peak Year & Active Years per artist
    yearly_art = music_df.groupby(["artist_id", "year"])["minutes_played"].sum().reset_index()
    idx_max_year = yearly_art.groupby("artist_id")["minutes_played"].idxmax()
    peak_years_df = yearly_art.loc[idx_max_year].rename(
        columns={"year": "peak_year"}
    )[["artist_id", "peak_year"]]
    
    active_years_series = music_df.groupby("artist_id")["year"].unique().apply(
        lambda yrs: (len(yrs), ",".join(map(str, sorted(yrs))))
    )
    active_years_df = pd.DataFrame(active_years_series.tolist(), index=active_years_series.index, columns=["active_years_count", "active_years"]).reset_index()
    
    # 4. Top Time of Day per artist
    tod_art = music_df.groupby(["artist_id", "time_of_day_bucket"])["minutes_played"].sum().reset_index()
    idx_max_tod = tod_art.groupby("artist_id")["minutes_played"].idxmax()
    top_tod_df = tod_art.loc[idx_max_tod].rename(columns={"time_of_day_bucket": "preferred_time_of_day"})[["artist_id", "preferred_time_of_day"]]
    
    # 5. Inactivity Gaps and Revivals
    sorted_df = music_df.sort_values(["artist_id", "timestamp_utc"])
    sorted_df["gap_days"] = sorted_df.groupby("artist_id")["timestamp_utc"].diff().dt.total_seconds() / 86400.0
    
    gap_stats = sorted_df.groupby("artist_id").agg(
        longest_inactivity_gap_days=("gap_days", "max"),
        revival_count=("gap_days", lambda g: int((g >= 60.0).sum()))
    ).reset_index().fillna(0.0)
    
    # Merge all components
    res = base_agg.merge(peak_months_df[["artist_id", "peak_month", "peak_month_minutes"]], on="artist_id", how="left")
    res = res.merge(peak_years_df, on="artist_id", how="left")
    res = res.merge(active_years_df, on="artist_id", how="left")
    res = res.merge(top_tod_df, on="artist_id", how="left")
    res = res.merge(gap_stats, on="artist_id", how="left")
    
    # Recency & Time to Peak
    res["days_since_last_play"] = (dataset_max_ts - res["last_heard_utc"]).dt.total_seconds() / 86400.0
    res["days_since_last_play"] = res["days_since_last_play"].round(1)
    
    # Time to peak days
    peak_date_series = pd.to_datetime(res["peak_month"] + "-01", utc=True)
    res["time_to_peak_days"] = np.maximum(0.0, (peak_date_series - res["first_heard_utc"]).dt.total_seconds() / 86400.0).round(1)
    
    res["catalog_depth_tracks_per_project"] = (res["unique_tracks"] / np.maximum(1, res["unique_projects"])).round(2)
    res["longest_inactivity_gap_days"] = res["longest_inactivity_gap_days"].round(1)
    res["peak_month_minutes"] = res["peak_month_minutes"].round(2)
    
    # Lifecycle Stage Classification
    def assign_stage(row):
        total_plays = row["total_plays"]
        days_since = row["days_since_last_play"]
        active_years_cnt = row["active_years_count"]
        revivals = row["revival_count"]
        
        if total_plays <= 2:
            return "Failed / One-Time Discovery"
        elif days_since <= 45 and total_plays >= 20:
            if active_years_cnt >= 2:
                return "Long-Term Favorite"
            else:
                return "Current Obsession"
        elif active_years_cnt >= 3 and total_plays >= 50:
            return "Evergreen Artist"
        elif revivals >= 1 and days_since <= 90:
            return "Revived Artist"
        elif total_plays >= 30 and days_since > 180:
            return "Era Artist (Dormant)"
        elif days_since > 180:
            return "Dormant"
        else:
            return "Regular Rotation"
            
    res["lifecycle_stage"] = res.apply(assign_stage, axis=1)
    
    # Format ISO strings for timestamps
    res["first_heard_utc"] = res["first_heard_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    res["last_heard_utc"] = res["last_heard_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    res = res.sort_values("total_minutes", ascending=False).reset_index(drop=True)
    logger.info(f"Built artist lifecycles table with {len(res)} artists")
    return res
