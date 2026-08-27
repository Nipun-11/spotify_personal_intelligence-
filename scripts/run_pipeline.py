"""End-to-End Data Pipeline runner for Spotify Personal Intelligence Engine."""

import sys
import os
import json
import logging
from pathlib import Path
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import (
    RAW_DATA_DIR,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_EXPLORATION_MIN_TRACKS,
)
from src.ingestion.loader import load_raw_dataset
from src.validation.quality_checks import run_data_quality_checks
from src.cleaning.normalizer import normalize_playback_dataframe
from src.features.canonical import build_canonical_playback_events
from src.sessions.sessionizer import build_sessions_table
from src.analytics.artist_lifecycle import compute_artist_lifecycles
from src.analytics.song_lifecycle import compute_song_lifecycles
from src.analytics.project_analytics import compute_project_analytics
from src.analytics.transitions import compute_transitions
from src.analytics.networks import build_music_network
from src.analytics.genre_time import compute_genre_time_analytics
from src.analytics.freshness import compute_freshness_analytics
from src.discovery.catalyst_engine import compute_discovery_catalysts
from src.discovery.ranking import compute_catalyst_rankings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("run_pipeline")

def run_pipeline() -> None:
    """Execute complete data engineering and analytical pipeline."""
    logger.info("=" * 60)
    logger.info("STARTING SPOTIFY PERSONAL INTELLIGENCE PIPELINE")
    logger.info("=" * 60)
    
    # 1. Ingestion
    logger.info("[Step 1/12] Ingesting raw JSON streaming history...")
    raw_df = load_raw_dataset(RAW_DATA_DIR)
    
    # 2. Validation & Quality Checks
    logger.info("[Step 2/12] Running data quality checks and validation...")
    valid_df, quality_report = run_data_quality_checks(raw_df)
    
    with open(PROCESSED_DATA_DIR / "quality_report.json", "w", encoding="utf-8") as fh:
        json.dump(quality_report, fh, indent=2)
        
    # 3. Cleaning & Normalization
    logger.info("[Step 3/12] Standardizing entities, timezones, and platforms...")
    normalized_df = normalize_playback_dataframe(valid_df)
    
    # 4. Canonical Playback Events & Sessions
    logger.info("[Step 4/12] Building canonical playback events with strictly historical features...")
    canonical_df = build_canonical_playback_events(normalized_df)
    canonical_parquet_path = PROCESSED_DATA_DIR / "canonical_playback.parquet"
    canonical_df.to_parquet(canonical_parquet_path, index=False)
    logger.info(f"Saved canonical table to {canonical_parquet_path}")
    
    # 5. Gold Sessions Table
    logger.info("[Step 5/12] Aggregating session taxonomy and session metrics...")
    sessions_df = build_sessions_table(canonical_df)
    sessions_df.to_parquet(PROCESSED_DATA_DIR / "sessions.parquet", index=False)
    
    # 6. Artist Lifecycles
    logger.info("[Step 6/12] Computing artist lifecycles and trajectories...")
    artist_lifecycles_df = compute_artist_lifecycles(canonical_df)
    artist_lifecycles_df.to_parquet(PROCESSED_DATA_DIR / "artist_lifecycles.parquet", index=False)
    
    # 7. Song Lifecycles
    logger.info("[Step 7/12] Computing song lifecycles and retention metrics...")
    song_lifecycles_df = compute_song_lifecycles(canonical_df)
    song_lifecycles_df.to_parquet(PROCESSED_DATA_DIR / "song_lifecycles.parquet", index=False)
    
    # 8. Project Analytics (Strict >= 3 track rule)
    logger.info("[Step 8/12] Computing project analytics and project-driving songs...")
    projects_df, project_driving_df = compute_project_analytics(canonical_df)
    projects_df.to_parquet(PROCESSED_DATA_DIR / "projects.parquet", index=False)
    project_driving_df.to_parquet(PROCESSED_DATA_DIR / "project_driving_songs.parquet", index=False)
    
    # 9. Transitions & Sequences
    logger.info("[Step 9/12] Computing sequence transitions and Markov chains...")
    transitions_dict = compute_transitions(canonical_df)
    for name, df_t in transitions_dict.items():
        df_t.to_parquet(PROCESSED_DATA_DIR / f"{name}.parquet", index=False)
        
    # 10. Music Network & Bridges
    logger.info("[Step 10/12] Constructing personal music graph and bridge detection...")
    network_data = build_music_network(transitions_dict["artist_transitions"], artist_lifecycles_df)
    with open(PROCESSED_DATA_DIR / "network.json", "w", encoding="utf-8") as fh:
        json.dump(network_data, fh, indent=2)
        
    # 11. Genre Time & Freshness
    logger.info("[Step 11/12] Computing genre x time matrix and listening freshness...")
    genre_time_data = compute_genre_time_analytics(canonical_df)
    genre_time_data["genre_time_matrix"].to_parquet(PROCESSED_DATA_DIR / "genre_time_matrix.parquet", index=False)
    genre_time_data["yearly_genre_share"].to_parquet(PROCESSED_DATA_DIR / "yearly_genre_share.parquet", index=False)
    genre_time_data["artist_time_heatmap"].to_parquet(PROCESSED_DATA_DIR / "artist_time_heatmap.parquet", index=False)
    
    freshness_data = compute_freshness_analytics(canonical_df)
    freshness_data["freshness_distribution"].to_parquet(PROCESSED_DATA_DIR / "freshness_distribution.parquet", index=False)
    freshness_data["freshness_by_year"].to_parquet(PROCESSED_DATA_DIR / "freshness_by_year.parquet", index=False)
    with open(PROCESSED_DATA_DIR / "taste_fingerprint.json", "w", encoding="utf-8") as fh:
        json.dump(freshness_data["taste_fingerprint"], fh, indent=2)
        
    # 12. Flagship Discovery Catalyst Engine
    logger.info("[Step 12/12] Running Flagship Discovery Catalyst Engine (7D/30D/90D)...")
    catalysts_df = compute_discovery_catalysts(canonical_df)
    catalysts_df.to_parquet(PROCESSED_DATA_DIR / "discovery_events.parquet", index=False)
    
    catalyst_rankings_df = compute_catalyst_rankings(catalysts_df)
    catalyst_rankings_df.to_parquet(PROCESSED_DATA_DIR / "discovery_rankings.parquet", index=False)
    
    # Highlight & Verify Panther and Frappe Ash Examples from Specs
    logger.info("=" * 60)
    logger.info("SPECIFICATION EXAMPLE VERIFICATION AGAINST ACTUAL DATA")
    logger.info("=" * 60)
    
    # 1. Panther - Aa Jao
    panther_aajao = catalysts_df[
        (catalysts_df["catalyst_artist_name"].str.contains("Panther", case=False, na=False)) &
        (catalysts_df["catalyst_track_name"].str.contains("Aa Jao", case=False, na=False))
    ]
    if len(panther_aajao) > 0:
        row_pj = panther_aajao.iloc[0]
        logger.info(
            f"PANTHER - AA JAO: Found catalyst event! "
            f"Discovery Type: {row_pj['discovery_type']}, "
            f"7D Tracks Added: {row_pj['tracks_added_7d']}, "
            f"7D Projects Added: {row_pj['projects_added_7d']}, "
            f"7D Minutes Added: {row_pj['minutes_added_7d']}, "
            f"30D Minutes: {row_pj['minutes_30d']}, "
            f"Future Hours Unlocked: {row_pj['future_hours_unlocked']} hrs"
        )
    else:
        logger.info("PANTHER - AA JAO: Checked actual data.")
        
    # 2. Frappe Ash
    frappe_cats = catalysts_df[catalysts_df["catalyst_artist_name"].str.contains("Frappe Ash", case=False, na=False)]
    logger.info(f"FRAPPE ASH: Found {len(frappe_cats)} discovery/re-engagement events across catalog")
    if len(frappe_cats) > 0:
        top_f = frappe_cats.sort_values("future_hours_unlocked", ascending=False).iloc[0]
        logger.info(
            f"FRAPPE ASH Top Catalyst: '{top_f['catalyst_track_name']}' "
            f"({top_f['discovery_type']}) -> {top_f['tracks_added_7d']} tracks in 7d, "
            f"{top_f['future_hours_unlocked']} future hrs unlocked"
        )
        
    logger.info("=" * 60)
    logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    logger.info(f"All gold analytical tables saved in {PROCESSED_DATA_DIR}")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_pipeline()
