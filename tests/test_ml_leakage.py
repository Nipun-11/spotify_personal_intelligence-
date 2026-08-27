"""Unit tests for machine learning temporal integrity and leakage prevention."""

import pytest
import pandas as pd
from src.config import PROCESSED_DATA_DIR, ML_DATA_DIR
from src.ml.explainability import run_temporal_leakage_audit
from src.ml.dataset_builder import build_ml_dataset

def test_temporal_leakage_audit_passes():
    canonical_path = PROCESSED_DATA_DIR / "canonical_playback.parquet"
    catalysts_path = PROCESSED_DATA_DIR / "discovery_events.parquet"

    if not canonical_path.exists() or not catalysts_path.exists():
        pytest.skip("Processed parquet files not found; run pipeline first.")

    df_events = pd.read_parquet(canonical_path)
    df_catalysts = pd.read_parquet(catalysts_path)

    audit_report = run_temporal_leakage_audit(df_events, df_catalysts)
    assert audit_report["audit_passed"] == True
    assert audit_report["chronological_monotonicity_verified"] == True
    assert audit_report["zero_initial_song_counts_verified"] == True
    assert audit_report["zero_initial_artist_counts_verified"] == True

def test_chronological_splits_integrity():
    canonical_path = PROCESSED_DATA_DIR / "canonical_playback.parquet"
    catalysts_path = PROCESSED_DATA_DIR / "discovery_events.parquet"

    if not canonical_path.exists() or not catalysts_path.exists():
        pytest.skip("Processed parquet files not found.")

    df_events = pd.read_parquet(canonical_path)
    df_catalysts = pd.read_parquet(catalysts_path)

    _, splits = build_ml_dataset(df_events, df_catalysts)

    # Train years must be <= 2024
    assert splits["train"]["year"].max() <= 2024
    # Val year must be 2025
    assert splits["val"]["year"].unique().tolist() == [2025]
    # Test year must be >= 2026
    assert splits["test"]["year"].min() >= 2026
