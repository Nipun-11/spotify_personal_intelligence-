"""Unit tests for sessionization rules and taxonomy."""

import pytest
import pandas as pd
from src.sessions.sessionizer import assign_sessions, classify_session_type

def test_session_boundary_30_minutes():
    # 2 events 10 mins apart (same session) and 1 event 45 mins later (new session)
    sample = pd.DataFrame([
        {"timestamp_utc": pd.to_datetime("2024-01-01T10:00:00Z"), "date": "2024-01-01", "event_id": "e1"},
        {"timestamp_utc": pd.to_datetime("2024-01-01T10:10:00Z"), "date": "2024-01-01", "event_id": "e2"},
        {"timestamp_utc": pd.to_datetime("2024-01-01T10:55:00Z"), "date": "2024-01-01", "event_id": "e3"},
    ])
    sessionized = assign_sessions(sample, inactivity_minutes=30)
    assert sessionized["session_id"].nunique() == 2
    assert sessionized.iloc[0]["session_position"] == 1
    assert sessionized.iloc[1]["session_position"] == 2
    assert sessionized.iloc[2]["session_position"] == 1

def test_classify_session_type():
    assert classify_session_type(1, 2.0, 1, 1, 0, 1.0, 1.0) == "short_burst"
    assert classify_session_type(8, 25.0, 1, 1, 0, 1.0, 1.0) == "album_session"
    assert classify_session_type(15, 45.0, 6, 4, 4, 0.2, 0.2) == "rabbit_hole"
