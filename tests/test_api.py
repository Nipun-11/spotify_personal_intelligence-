"""Integration tests for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"

def test_api_overview():
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "taste_fingerprint" in data
    assert data["kpis"]["total_hours"] > 0

def test_api_artists():
    res = client.get("/api/artists?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "artists" in data
    assert len(data["artists"]) > 0

def test_api_catalysts():
    res = client.get("/api/discovery/catalysts?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "catalysts" in data
    assert len(data["catalysts"]) > 0

def test_api_ml_metrics():
    res = client.get("/api/ml/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "benchmark_table" in data
    assert len(data["benchmark_table"]) >= 3

def test_api_predict():
    payload = {
        "is_first_artist_play": 1,
        "seconds_played": 210.0,
        "skipped": 0,
        "shuffle": 0,
        "artist_tracks_heard_before": 0,
        "artist_plays_before": 0,
        "hour": 22
    }
    res = client.post("/api/ml/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "expansion_probability" in data
    assert "predicted_expansion" in data
    assert 0.0 <= data["expansion_probability"] <= 1.0
