"""Unit tests for the non-negotiable >= 3-track project exploration rule and penetration."""

import pytest
import pandas as pd
from src.analytics.project_analytics import compute_project_analytics
from src.config import PROJECT_EXPLORATION_MIN_TRACKS

def test_project_min_3_track_rule():
    assert PROJECT_EXPLORATION_MIN_TRACKS == 3

    # Create mock playback data with 3 projects:
    # Proj 1: 2 unique tracks (Not explored)
    # Proj 2: 3 unique tracks (Explored)
    # Proj 3: 5 unique tracks (Deep exploration)
    events = []
    
    # Proj 1: 2 tracks
    for trk in ["t1", "t2"]:
        events.append({
            "content_type": "music",
            "project_id": "prj_1",
            "project_name": "Two Track EP",
            "artist_id": "art_1",
            "artist_name": "Artist 1",
            "track_id": trk,
            "track_name": f"Track {trk}",
            "event_id": f"e_{trk}",
            "timestamp_utc": pd.to_datetime("2024-01-01T12:00:00Z"),
            "timestamp_local": pd.to_datetime("2024-01-01T17:30:00+05:30"),
            "minutes_played": 3.0,
            "is_same_project_as_prev": False
        })
        
    # Proj 2: 3 tracks
    for trk in ["t3", "t4", "t5"]:
        events.append({
            "content_type": "music",
            "project_id": "prj_2",
            "project_name": "Three Track EP",
            "artist_id": "art_1",
            "artist_name": "Artist 1",
            "track_id": trk,
            "track_name": f"Track {trk}",
            "event_id": f"e_{trk}",
            "timestamp_utc": pd.to_datetime("2024-01-02T12:00:00Z"),
            "timestamp_local": pd.to_datetime("2024-01-02T17:30:00+05:30"),
            "minutes_played": 3.0,
            "is_same_project_as_prev": True
        })

    df_events = pd.DataFrame(events)
    df_projects, df_driving = compute_project_analytics(df_events)

    p1 = df_projects[df_projects["project_id"] == "prj_1"].iloc[0]
    p2 = df_projects[df_projects["project_id"] == "prj_2"].iloc[0]

    assert p1["tracks_heard"] == 2
    assert p1["is_explored"] == False  # 2 tracks is NOT explored

    assert p2["tracks_heard"] == 3
    assert p2["is_explored"] == True   # 3 tracks IS explored
