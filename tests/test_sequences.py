"""Unit tests for Markov sequence transitions and 3-song chains."""

import pytest
import pandas as pd
from src.analytics.transitions import compute_transitions

def test_markov_track_transitions():
    events = [
        {
            "event_id": "e_1",
            "content_type": "music",
            "session_id": "s1",
            "session_position": 1,
            "track_id": "t1",
            "track_name": "T1",
            "artist_id": "a1",
            "artist_name": "A1",
            "project_id": "p1",
            "project_name": "P1",
            "previous_track_id": None,
            "previous_track_name": None,
            "previous_artist_id": None,
            "previous_artist_name": None,
            "previous_project_id": None,
            "previous_project_name": None,
            "is_same_artist_as_prev": False,
            "time_since_prev_event_seconds": 0.0
        },
        {
            "event_id": "e_2",
            "content_type": "music",
            "session_id": "s1",
            "session_position": 2,
            "track_id": "t2",
            "track_name": "T2",
            "artist_id": "a1",
            "artist_name": "A1",
            "project_id": "p1",
            "project_name": "P1",
            "previous_track_id": "t1",
            "previous_track_name": "T1",
            "previous_artist_id": "a1",
            "previous_artist_name": "A1",
            "previous_project_id": "p1",
            "previous_project_name": "P1",
            "is_same_artist_as_prev": True,
            "time_since_prev_event_seconds": 180.0
        },
        {
            "event_id": "e_3",
            "content_type": "music",
            "session_id": "s1",
            "session_position": 3,
            "track_id": "t3",
            "track_name": "T3",
            "artist_id": "a2",
            "artist_name": "A2",
            "project_id": "p2",
            "project_name": "P2",
            "previous_track_id": "t2",
            "previous_track_name": "T2",
            "previous_artist_id": "a1",
            "previous_artist_name": "A1",
            "previous_project_id": "p1",
            "previous_project_name": "P1",
            "is_same_artist_as_prev": False,
            "time_since_prev_event_seconds": 210.0
        },
    ]
    df_events = pd.DataFrame(events)
    results = compute_transitions(df_events)
    df_trk = results["track_transitions"]
    df_3song = results["three_song_sequences"]

    assert len(df_trk) == 2
    assert len(df_3song) == 1
    assert df_3song.iloc[0]["track_name"] == "T3"
    assert df_3song.iloc[0]["prev_track_name"] == "T2"
    assert df_3song.iloc[0]["prev2_track_name"] == "T1"
