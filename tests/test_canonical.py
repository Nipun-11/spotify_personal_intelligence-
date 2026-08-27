"""Unit tests for canonical playback table generation and timezone handling."""

import pytest
import pandas as pd
from src.cleaning.normalizer import normalize_playback_dataframe
from src.features.canonical import build_canonical_playback_events

def test_timezone_conversion_to_ist():
    # UTC timestamp 12:00:00 -> IST (+05:30) 17:30:00
    sample = pd.DataFrame([{
        "ts": "2024-06-15T12:00:00Z",
        "ms_played": 180000,
        "master_metadata_track_name": "Test Track",
        "master_metadata_album_artist_name": "Test Artist",
        "master_metadata_album_album_name": "Test Album",
        "spotify_track_uri": "spotify:track:test12345",
        "platform": "Android OS 14",
        "reason_start": "trackdone",
        "reason_end": "trackdone",
        "shuffle": False,
        "skipped": False,
        "offline": False,
        "incognito_mode": False
    }])
    
    normalized = normalize_playback_dataframe(sample)
    canonical = build_canonical_playback_events(normalized)
    row = canonical.iloc[0]
    
    assert row["hour"] == 17  # 12 UTC + 5:30 = 17:30 IST
    assert row["time_of_day_bucket"] == "3PM-6PM"
    assert row["is_weekend"] == True  # 2024-06-15 is Saturday
    assert row["is_first_song_play"] == True
    assert row["song_plays_before"] == 0
