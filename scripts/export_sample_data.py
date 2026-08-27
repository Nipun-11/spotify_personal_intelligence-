"""Export synthetic / anonymized public-safe sample dataset for GitHub demonstration."""

import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np

import sys
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from src.config import SAMPLE_DATA_DIR, PROCESSED_DATA_DIR

logger = logging.getLogger("export_sample")

def export_sample_data(sample_size: int = 500) -> None:
    """Generate anonymized sample streaming records without private IP or personal account identifiers."""
    canonical_path = PROCESSED_DATA_DIR / "canonical_playback.parquet"
    if not canonical_path.exists():
        logger.error("Canonical table not found. Run pipeline first!")
        return

    df = pd.read_parquet(canonical_path)
    
    # Sample representative records across years
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42).sort_values("timestamp_utc").reset_index(drop=True)
    
    # Format into public-safe Spotify extended history JSON format
    sample_records = []
    for _, row in sample_df.iterrows():
        sample_records.append({
            "ts": row["timestamp_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "platform": row["platform"],
            "ms_played": int(row["ms_played"]),
            "conn_country": "IN",
            "ip_addr": "0.0.0.0",  # Anonymized / Redacted
            "master_metadata_track_name": row["track_name"],
            "master_metadata_album_artist_name": row["artist_name"],
            "master_metadata_album_album_name": row["project_name"],
            "spotify_track_uri": f"spotify:track:{row['track_id']}",
            "episode_name": None,
            "episode_show_name": None,
            "spotify_episode_uri": None,
            "reason_start": row["start_reason"],
            "reason_end": row["end_reason"],
            "shuffle": bool(row["shuffle"]),
            "skipped": bool(row["skipped"]),
            "offline": bool(row["offline"]),
            "incognito_mode": bool(row["incognito_mode"])
        })
        
    out_file = SAMPLE_DATA_DIR / "sample_streaming_history.json"
    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(sample_records, fh, indent=2)
        
    print(f"Exported {len(sample_records)} anonymized sample records to {out_file}")

if __name__ == "__main__":
    export_sample_data()
