"""Data quality checks and validation report generation."""

import logging
from typing import Dict, Any, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

def run_data_quality_checks(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Run comprehensive data quality checks on raw loaded DataFrame.
    
    Args:
        df: Raw DataFrame containing streaming history records.
        
    Returns:
        Tuple of (cleaned_df, quality_report_dict).
    """
    total_raw_records = len(df)
    report: Dict[str, Any] = {
        "total_records_ingested": total_raw_records,
        "null_timestamps": int(df["ts"].isnull().sum()) if "ts" in df else 0,
        "negative_duration_records": int((df["ms_played"] < 0).sum()) if "ms_played" in df else 0,
        "zero_duration_records": int((df["ms_played"] == 0).sum()) if "ms_played" in df else 0,
        "excessive_duration_records": int((df["ms_played"] > 86_400_000).sum()) if "ms_played" in df else 0, # > 24 hours
        "podcast_records": int(df["episode_name"].notnull().sum()) if "episode_name" in df else 0,
        "audiobook_records": int(df["audiobook_title"].notnull().sum()) if "audiobook_title" in df else 0,
        "video_records": int((df["_source_type"] == "video").sum()) if "_source_type" in df else 0,
    }
    
    # Clean invalid records
    valid_df = df.copy()
    
    # 1. Drop records without timestamps
    valid_df = valid_df.dropna(subset=["ts"])
    
    # 2. Filter out negative or extreme durations
    valid_df = valid_df[(valid_df["ms_played"] >= 0) & (valid_df["ms_played"] <= 86_400_000)]
    
    # 3. Deduplicate exact duplicate rows
    initial_len = len(valid_df)
    dedup_cols = ["ts", "spotify_track_uri", "ms_played", "master_metadata_track_name"]
    existing_dedup_cols = [c for c in dedup_cols if c in valid_df.columns]
    valid_df = valid_df.drop_duplicates(subset=existing_dedup_cols)
    report["duplicate_records_removed"] = initial_len - len(valid_df)
    report["valid_records_retained"] = len(valid_df)
    
    logger.info(f"Data Quality Report: {report}")
    return valid_df, report
