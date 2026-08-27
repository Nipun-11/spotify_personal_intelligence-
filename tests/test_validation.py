"""Unit tests for schema validation and data quality checks."""

import pytest
import pandas as pd
from src.validation.quality_checks import run_data_quality_checks
from src.validation.schema import RawSpotifyRecord

def test_raw_spotify_record_model():
    record = RawSpotifyRecord(
        ts="2024-03-31T20:02:05Z",
        ms_played=193263,
        master_metadata_track_name="Aa Jao",
        master_metadata_album_artist_name="Panther",
        master_metadata_album_album_name="Aa Jao",
        spotify_track_uri="spotify:track:sample123"
    )
    assert record.ms_played == 193263
    assert record.master_metadata_track_name == "Aa Jao"

def test_data_quality_checks_filters_invalid_durations():
    raw_sample = pd.DataFrame([
        {"ts": "2024-01-01T00:00:00Z", "ms_played": 1000, "spotify_track_uri": "uri1", "master_metadata_track_name": "T1"},
        {"ts": "2024-01-01T00:05:00Z", "ms_played": -50, "spotify_track_uri": "uri2", "master_metadata_track_name": "T2"},  # Invalid negative
        {"ts": None, "ms_played": 2000, "spotify_track_uri": "uri3", "master_metadata_track_name": "T3"},                    # Null timestamp
    ])
    valid_df, report = run_data_quality_checks(raw_sample)
    assert len(valid_df) == 1
    assert report["null_timestamps"] == 1
    assert report["negative_duration_records"] == 1
