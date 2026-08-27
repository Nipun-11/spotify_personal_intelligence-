"""Unit tests for the Flagship Discovery Catalyst Engine."""

import pytest
import pandas as pd
from src.discovery.catalyst_engine import compute_discovery_catalysts, identify_discovery_type
from src.discovery.ranking import compute_catalyst_rankings

def test_discovery_type_classification():
    # 1. First artist play -> Artist Discovery
    row1 = pd.Series({"is_first_artist_play": True, "artist_plays_before": 0, "is_first_project_play": True})
    assert identify_discovery_type(row1) == "Artist Discovery"

    # 2. Known artist, first project play -> Project Discovery
    row2 = pd.Series({"is_first_artist_play": False, "artist_plays_before": 20, "is_first_project_play": True, "time_since_last_artist_play_days": 5.0})
    assert identify_discovery_type(row2) == "Project Discovery"

    # 3. Known artist and project, long gap -> Re-engagement
    row3 = pd.Series({"is_first_artist_play": False, "artist_plays_before": 50, "is_first_project_play": False, "time_since_last_artist_play_days": 60.0})
    assert identify_discovery_type(row3) == "Re-engagement"

def test_7d_discovery_window_metrics():
    # Construct sequence: Catalyst song at T0, followed by 2 new tracks within 3 days
    events = [
        {
            "event_id": "e_cat",
            "content_type": "music",
            "artist_id": "art_test",
            "artist_name": "Test Artist",
            "project_id": "prj_test",
            "project_name": "Test Proj",
            "track_id": "trk_cat",
            "track_name": "Catalyst Track",
            "timestamp_utc": pd.to_datetime("2024-05-01T12:00:00Z"),
            "date": "2024-05-01",
            "year": 2024,
            "minutes_played": 3.5,
            "is_first_song_play": True,
            "is_first_artist_play": True,
            "is_first_project_play": True,
            "artist_plays_before": 0,
            "time_since_last_artist_play_days": 0.0
        },
        {
            "event_id": "e_follow1",
            "content_type": "music",
            "artist_id": "art_test",
            "artist_name": "Test Artist",
            "project_id": "prj_test",
            "project_name": "Test Proj",
            "track_id": "trk_follow1",
            "track_name": "Followup Track 1",
            "timestamp_utc": pd.to_datetime("2024-05-02T15:00:00Z"), # Day 1
            "date": "2024-05-02",
            "year": 2024,
            "minutes_played": 4.0,
            "is_first_song_play": True,
            "is_first_artist_play": False,
            "is_first_project_play": False,
            "artist_plays_before": 1,
            "time_since_last_artist_play_days": 1.0
        },
        {
            "event_id": "e_follow2",
            "content_type": "music",
            "artist_id": "art_test",
            "artist_name": "Test Artist",
            "project_id": "prj_test",
            "project_name": "Test Proj",
            "track_id": "trk_follow2",
            "track_name": "Followup Track 2",
            "timestamp_utc": pd.to_datetime("2024-05-04T18:00:00Z"), # Day 3
            "date": "2024-05-04",
            "year": 2024,
            "minutes_played": 3.0,
            "is_first_song_play": True,
            "is_first_artist_play": False,
            "is_first_project_play": False,
            "artist_plays_before": 2,
            "time_since_last_artist_play_days": 2.0
        },
    ]
    df_events = pd.DataFrame(events)
    catalysts_df = compute_discovery_catalysts(df_events)

    cat_row = catalysts_df[catalysts_df["catalyst_track_id"] == "trk_cat"].iloc[0]
    assert cat_row["tracks_added_7d"] == 3 # trk_cat + trk_follow1 + trk_follow2
    assert cat_row["plays_added_7d"] == 3
    assert cat_row["minutes_added_7d"] == 10.5
    assert cat_row["is_meaningful_expansion_7d"] == True
