"""Unit tests for artist and song lifecycle calculations."""

import pytest
import pandas as pd
from src.analytics.artist_lifecycle import compute_artist_lifecycles
from src.analytics.song_lifecycle import compute_song_lifecycles

def test_song_raw_vs_active_lifespan():
    # Song played in 2020 and again in 2024
    sample = pd.DataFrame([
        {
            "event_id": "e_1",
            "content_type": "music",
            "track_id": "trk_isolated",
            "track_name": "Isolated Song",
            "artist_id": "art_iso",
            "artist_name": "Iso Artist",
            "project_id": "prj_iso",
            "project_name": "Iso Album",
            "timestamp_utc": pd.to_datetime("2020-01-01T00:00:00Z"),
            "date": "2020-01-01",
            "year": 2020,
            "minutes_played": 3.0,
            "seconds_played": 180.0,
            "skipped": False
        },
        {
            "event_id": "e_2",
            "content_type": "music",
            "track_id": "trk_isolated",
            "track_name": "Isolated Song",
            "artist_id": "art_iso",
            "artist_name": "Iso Artist",
            "project_id": "prj_iso",
            "project_name": "Iso Album",
            "timestamp_utc": pd.to_datetime("2024-01-01T00:00:00Z"),
            "date": "2024-01-01",
            "year": 2024,
            "minutes_played": 3.0,
            "seconds_played": 180.0,
            "skipped": False
        }
    ])
    
    songs_df = compute_song_lifecycles(sample)
    song = songs_df.iloc[0]
    
    assert song["raw_lifespan_days"] >= 1460
    assert song["active_lifespan_days"] >= 0
    assert song["total_plays"] == 2

def test_artist_lifecycle_discovery_state():
    sample = pd.DataFrame([{
        "event_id": "e_art1",
        "content_type": "music",
        "artist_id": "art_new",
        "artist_name": "New Artist",
        "track_id": "trk_1",
        "track_name": "Track 1",
        "project_id": "prj_1",
        "project_name": "Project 1",
        "timestamp_utc": pd.to_datetime("2024-05-01T12:00:00Z"),
        "timestamp_local": pd.to_datetime("2024-05-01T17:30:00+05:30"),
        "date": "2024-05-01",
        "year": 2024,
        "minutes_played": 3.5,
        "time_of_day_bucket": "3PM-6PM"
    }])
    
    artists_df = compute_artist_lifecycles(sample)
    art = artists_df.iloc[0]
    
    assert art["total_plays"] == 1
    assert art["unique_tracks"] == 1
    assert "lifecycle_stage" in art
