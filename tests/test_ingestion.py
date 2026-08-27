"""Unit tests for data ingestion."""

import pytest
from pathlib import Path
from src.ingestion.loader import discover_raw_files, load_json_records, load_raw_dataset
from src.config import RAW_DATA_DIR

def test_discover_raw_files():
    files = discover_raw_files(RAW_DATA_DIR)
    assert "audio" in files
    assert "video" in files
    assert len(files["audio"]) >= 1

def test_load_raw_dataset_schema():
    df = load_raw_dataset(RAW_DATA_DIR)
    assert len(df) > 0
    assert "ts" in df.columns
    assert "ms_played" in df.columns
    assert "master_metadata_track_name" in df.columns
    assert "spotify_track_uri" in df.columns
