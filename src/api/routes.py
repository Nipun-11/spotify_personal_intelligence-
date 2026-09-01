"""FastAPI route handlers for serving preprocessed analytical and ML data."""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.config import PROCESSED_DATA_DIR, ML_DATA_DIR, MODELS_DIR

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

# Preload analytical tables in memory for ultra-low latency response (< 5ms)
def load_parquet_safe(filename: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / filename
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()

def load_json_safe(filename: str, directory: Path = PROCESSED_DATA_DIR) -> Dict[str, Any]:
    path = directory / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}

# In-memory cached DataFrames
df_canonical = load_parquet_safe("canonical_playback.parquet")
df_sessions = load_parquet_safe("sessions.parquet")
df_artists = load_parquet_safe("artist_lifecycles.parquet")
df_songs = load_parquet_safe("song_lifecycles.parquet")
df_projects = load_parquet_safe("projects.parquet")
df_project_driving = load_parquet_safe("project_driving_songs.parquet")
df_catalysts = load_parquet_safe("discovery_events.parquet")
df_catalyst_rankings = load_parquet_safe("discovery_rankings.parquet")
df_track_transitions = load_parquet_safe("track_transitions.parquet")
df_artist_transitions = load_parquet_safe("artist_transitions.parquet")
df_3song_sequences = load_parquet_safe("three_song_sequences.parquet")
df_genre_time = load_parquet_safe("genre_time_matrix.parquet")
df_yearly_genre = load_parquet_safe("yearly_genre_share.parquet")
df_freshness = load_parquet_safe("freshness_distribution.parquet")
df_freshness_yr = load_parquet_safe("freshness_by_year.parquet")
df_feature_importance = load_parquet_safe(ML_DATA_DIR / "feature_importance.parquet") if (ML_DATA_DIR / "feature_importance.parquet").exists() else pd.DataFrame()
df_benchmark = load_parquet_safe(ML_DATA_DIR / "benchmark_comparison.parquet") if (ML_DATA_DIR / "benchmark_comparison.parquet").exists() else pd.DataFrame()

network_data = load_json_safe("network.json")
taste_fingerprint = load_json_safe("taste_fingerprint.json")
quality_report = load_json_safe("quality_report.json")
ml_summary = load_json_safe("ml_summary.json", ML_DATA_DIR)
error_analysis = load_json_safe("error_analysis.json", ML_DATA_DIR)
temporal_audit = load_json_safe("temporal_leakage_audit.json", ML_DATA_DIR)

# Load trained model
catalyst_model_artifact = None
if (MODELS_DIR / "catalyst_lightgbm.joblib").exists():
    try:
        catalyst_model_artifact = joblib.load(MODELS_DIR / "catalyst_lightgbm.joblib")
    except Exception as e:
        logger.warning(f"Could not load ML model artifact: {e}")

@router.get("/health")
def health_check():
    return {"status": "ok", "app": "Spotify Personal Intelligence Engine", "version": "1.0.0"}

@router.get("/overview")
def get_overview_dna():
    """DNA Overview: headline KPIs, taste fingerprint, listening intensity, yearly evolution."""
    tot_events = len(df_canonical)
    music_events = int((df_canonical["content_type"] == "music").sum())
    total_hours = round(float(df_canonical["minutes_played"].sum() / 60.0), 1)
    
    unique_tracks = int(df_songs["track_id"].nunique()) if len(df_songs) > 0 else 0
    unique_artists = int(df_artists["artist_id"].nunique()) if len(df_artists) > 0 else 0
    unique_projects = int(df_projects["project_id"].nunique()) if len(df_projects) > 0 else 0
    explored_projects = int((df_projects["is_explored"]).sum()) if len(df_projects) > 0 else 0
    total_sessions = len(df_sessions)
    
    # Yearly listening breakdown
    yearly_summary = df_canonical[df_canonical["content_type"] == "music"].groupby("year").agg(
        listening_hours=("minutes_played", lambda m: round(float(m.sum() / 60.0), 1)),
        plays=("event_id", "count"),
        unique_artists=("artist_id", "nunique"),
        unique_tracks=("track_id", "nunique"),
        skip_rate=("skipped", lambda s: round(float(s.mean() * 100.0), 1))
    ).reset_index().to_dict(orient="records")
    
    # Top 10 artists by listening time
    top_artists = df_artists.head(10)[["artist_name", "total_hours", "total_plays", "lifecycle_stage"]].to_dict(orient="records")
    
    # Discovery rate: % of events that are first-time song plays
    first_plays = int((df_canonical["is_first_song_play"]).sum()) if "is_first_song_play" in df_canonical.columns else 0
    discovery_rate_pct = round((first_plays / max(1, tot_events)) * 100.0, 1)
    
    return {
        "kpis": {
            "total_hours": total_hours,
            "total_playback_events": tot_events,
            "music_events": music_events,
            "unique_tracks": unique_tracks,
            "unique_artists": unique_artists,
            "unique_projects": unique_projects,
            "explored_projects_ge3": explored_projects,
            "total_sessions": total_sessions,
            "discovery_rate_pct": discovery_rate_pct,
            "overall_skip_rate_pct": round(float(df_canonical["skipped"].mean() * 100.0), 1) if "skipped" in df_canonical.columns else 0.0,
            "date_range": {
                "first_date": df_canonical["date"].min() if len(df_canonical) > 0 else "",
                "last_date": df_canonical["date"].max() if len(df_canonical) > 0 else ""
            }
        },
        "taste_fingerprint": taste_fingerprint,
        "yearly_evolution": yearly_summary,
        "top_artists": top_artists,
        "quality_report": quality_report
    }

@router.get("/overview/taste-fingerprint")
def get_taste_fingerprint():
    """Taste fingerprint dimensions."""
    return taste_fingerprint

@router.get("/overview/yearly-evolution")
def get_yearly_evolution():
    """Yearly listening breakdown."""
    return df_canonical[df_canonical["content_type"] == "music"].groupby("year").agg(
        hours=("minutes_played", lambda m: round(float(m.sum() / 60.0), 2)),
        listening_hours=("minutes_played", lambda m: round(float(m.sum() / 60.0), 2)),
        plays=("event_id", "count"),
        unique_artists=("artist_id", "nunique"),
        unique_tracks=("track_id", "nunique"),
        skip_rate=("skipped", lambda s: round(float(s.mean() * 100.0), 1))
    ).reset_index().to_dict(orient="records")

@router.get("/artists")
def get_artists(
    search: Optional[str] = Query(None, description="Search artist name"),
    stage: Optional[str] = Query(None, description="Filter by lifecycle stage"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List artists with filtering, sorting, and pagination."""
    res_df = df_artists.copy()
    if search:
        res_df = res_df[res_df["artist_name"].str.contains(search, case=False, na=False)]
    if stage:
        res_df = res_df[res_df["lifecycle_stage"] == stage]
        
    total_count = len(res_df)
    artists_slice = res_df.iloc[offset:offset+limit].to_dict(orient="records")
    
    stages_distribution = df_artists["lifecycle_stage"].value_counts().to_dict()
    
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "stages_distribution": stages_distribution,
        "artists": artists_slice
    }

@router.get("/artists/{artist_name}/lifecycle")
def get_artist_lifecycle(artist_name: str):
    """Detailed lifecycle, monthly listening curve, projects, and top tracks for a specific artist."""
    art_row = df_artists[df_artists["artist_name"].str.lower() == artist_name.lower().strip()]
    if len(art_row) == 0:
        art_row = df_artists[df_artists["artist_id"] == artist_name]
    if len(art_row) == 0:
        # Fallback substring match
        art_row = df_artists[df_artists["artist_name"].str.contains(artist_name, case=False, na=False)]
        if len(art_row) == 0:
            raise HTTPException(status_code=404, detail=f"Artist '{artist_name}' not found")
            
    art_info = art_row.iloc[0].to_dict()
    art_id = art_info["artist_id"]
    
    # Monthly timeline
    art_events = df_canonical[df_canonical["artist_id"] == art_id]
    monthly = art_events.groupby(art_events["timestamp_local"].dt.strftime("%Y-%m")).agg(
        minutes=("minutes_played", "sum"),
        plays=("event_id", "count")
    ).reset_index().rename(columns={"timestamp_local": "year_month"})
    monthly["minutes"] = monthly["minutes"].round(1)
    
    # Top tracks
    top_tracks = df_songs[df_songs["artist_id"] == art_id].head(10).to_dict(orient="records")
    
    # Projects
    art_projects = df_projects[df_projects["artist_id"] == art_id].to_dict(orient="records")
    
    # Time of day profile
    tod = art_events.groupby("time_of_day_bucket")["minutes_played"].sum().round(1).to_dict()
    
    # Discovery events for this artist
    art_catalysts = df_catalysts[df_catalysts["catalyst_artist_id"] == art_id].to_dict(orient="records")
    
    return {
        "artist": art_info,
        "monthly_timeline": monthly.to_dict(orient="records"),
        "top_tracks": top_tracks,
        "projects": art_projects,
        "time_of_day_profile": tod,
        "discovery_catalyst_events": art_catalysts
    }

@router.get("/projects")
def get_projects(
    search: Optional[str] = Query(None, description="Search project name"),
    explored_only: Optional[bool] = Query(False, description="Filter explored (>=3 tracks) only"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List projects (Albums & EPs) with exploration status and listening style."""
    res_df = df_projects.copy()
    if search:
        res_df = res_df[
            res_df["project_name"].str.contains(search, case=False, na=False) |
            res_df["artist_name"].str.contains(search, case=False, na=False)
        ]
    if explored_only:
        res_df = res_df[res_df["is_explored"]]
        
    total_count = len(res_df)
    projects_slice = res_df.iloc[offset:offset+limit].to_dict(orient="records")
    
    explored_count = int(df_projects["is_explored"].sum())
    hit_driven_count = int((df_projects["listening_style"] == "Hit-Driven Project").sum())
    
    return {
        "total": total_count,
        "explored_count_ge3": explored_count,
        "hit_driven_count": hit_driven_count,
        "limit": limit,
        "offset": offset,
        "projects": projects_slice
    }

@router.get("/projects/{project_id}")
def get_project_details(project_id: str):
    """Get project driving songs and consumption breakdown."""
    proj_row = df_projects[df_projects["project_id"] == project_id]
    if len(proj_row) == 0:
        raise HTTPException(status_code=404, detail="Project not found")
        
    proj_info = proj_row.iloc[0].to_dict()
    driving_songs = df_project_driving[df_project_driving["project_id"] == project_id].to_dict(orient="records")
    
    return {
        "project": proj_info,
        "driving_songs": driving_songs
    }

@router.get("/songs")
def get_songs(
    search: Optional[str] = Query(None, description="Search song title"),
    category: Optional[str] = Query(None, description="Filter by lifecycle category"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List songs with lifecycle categories and retention stats."""
    res_df = df_songs.copy()
    if search:
        res_df = res_df[
            res_df["track_name"].str.contains(search, case=False, na=False) |
            res_df["artist_name"].str.contains(search, case=False, na=False)
        ]
    if category:
        res_df = res_df[res_df["lifecycle_category"] == category]
        
    total_count = len(res_df)
    songs_slice = res_df.iloc[offset:offset+limit].to_dict(orient="records")
    categories_dist = df_songs["lifecycle_category"].value_counts().to_dict()
    
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "categories_distribution": categories_dist,
        "songs": songs_slice
    }

@router.get("/songs/{track_id}")
def get_song_detail(track_id: str):
    """Get detail for a single song by track_id."""
    row = df_songs[df_songs["track_id"] == track_id]
    if len(row) == 0:
        raise HTTPException(status_code=404, detail=f"Song '{track_id}' not found")
    song_info = row.iloc[0].to_dict()
    # Monthly play history for this song
    song_events = df_canonical[df_canonical["track_id"] == track_id]
    monthly = song_events.groupby(song_events["timestamp_local"].dt.strftime("%Y-%m")).agg(
        plays=("event_id", "count"),
        minutes=("minutes_played", "sum")
    ).reset_index().rename(columns={"timestamp_local": "year_month"})
    monthly["minutes"] = monthly["minutes"].round(1)
    return {
        "song": song_info,
        "monthly_history": monthly.to_dict(orient="records")
    }

@router.get("/discovery/summary")
def get_discovery_summary():
    """Aggregate summary stats for the Discovery Catalysts hero section."""
    if len(df_catalyst_rankings) == 0:
        return {"total_catalysts": 0, "artist_discoveries": 0, "project_discoveries": 0,
                "catalog_deepenings": 0, "reengagements": 0, "total_downstream_hours": 0.0}
    types = df_catalyst_rankings["discovery_type"].value_counts().to_dict()
    hrs_col = "future_hours_unlocked" if "future_hours_unlocked" in df_catalyst_rankings.columns else "hours_unlocked"
    total_hours = round(float(df_catalyst_rankings[hrs_col].sum()), 2) if hrs_col in df_catalyst_rankings.columns else 0.0
    return {
        "total_catalysts": len(df_catalyst_rankings),
        "meaningful_catalysts": int(df_catalyst_rankings["is_meaningful_expansion_7d"].sum()),
        "artist_discoveries": types.get("Artist Discovery", 0),
        "project_discoveries": types.get("Project Discovery", 0),
        "catalog_deepenings": types.get("Catalog Deepening", 0),
        "reengagements": types.get("Re-engagement", 0),
        "total_downstream_hours": total_hours
    }

@router.get("/discovery/catalysts")
def get_discovery_catalysts(
    discovery_type: Optional[str] = Query(None, description="Filter by discovery type"),
    meaningful_only: Optional[bool] = Query(False, description="Show only meaningful catalog expansion"),
    search: Optional[str] = Query(None, description="Search by track or artist name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Top Ranked Discovery Catalysts with 7D/30D/90D metrics and unlocked future hours."""
    res_df = df_catalyst_rankings.copy()
    if discovery_type:
        res_df = res_df[res_df["discovery_type"] == discovery_type]
    if meaningful_only:
        res_df = res_df[res_df["is_meaningful_expansion_7d"]]
    if search:
        res_df = res_df[
            res_df["catalyst_track_name"].str.contains(search, case=False, na=False) |
            res_df["catalyst_artist_name"].str.contains(search, case=False, na=False)
        ]
        
    total_count = len(res_df)
    catalysts_slice = res_df.iloc[offset:offset+limit].to_dict(orient="records")
    
    types_dist = df_catalyst_rankings["discovery_type"].value_counts().to_dict()
    
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "discovery_types_distribution": types_dist,
        "catalysts": catalysts_slice
    }

@router.get("/discovery/pathway/{artist_name}")
def get_artist_discovery_pathway(artist_name: str):
    """Reconstruct chronological discovery pathway and catalog expansion tree for an artist."""
    art_cats = df_catalysts[df_catalysts["catalyst_artist_name"].str.lower() == artist_name.lower().strip()]
    if len(art_cats) == 0:
        art_cats = df_catalysts[df_catalysts["catalyst_artist_name"].str.contains(artist_name, case=False, na=False)]
        
    if len(art_cats) == 0:
        raise HTTPException(status_code=404, detail=f"No discovery events found for '{artist_name}'")
        
    pathway_events = art_cats.sort_values("catalyst_timestamp_utc").to_dict(orient="records")
    
    return {
        "artist_name": artist_name,
        "total_catalyst_events": len(pathway_events),
        "pathway": pathway_events
    }

@router.get("/network")
def get_network(min_weight: int = Query(2, ge=1, le=20)):
    """Music network nodes, edges, community clusters, and betweenness bridges."""
    if not network_data:
        return {"nodes": [], "edges": [], "bridges": [], "summary": {}}
        
    filtered_edges = [e for e in network_data.get("edges", []) if e["weight"] >= min_weight]
    active_node_ids = set()
    for e in filtered_edges:
        active_node_ids.add(e["source"])
        active_node_ids.add(e["target"])
        
    filtered_nodes = [n for n in network_data.get("nodes", []) if n["id"] in active_node_ids]
    
    return {
        "nodes": filtered_nodes,
        "edges": filtered_edges,
        "bridges": network_data.get("bridges", [])[:10],
        "summary": {
            **network_data.get("summary", {}),
            "visible_nodes": len(filtered_nodes),
            "visible_edges": len(filtered_edges)
        }
    }

@router.get("/sequences/top")
def get_top_sequences(limit: int = Query(20, ge=1, le=100)):
    """Top 2-song transitions and 3-song Markov sequence loops."""
    top_tracks = df_track_transitions.head(limit).to_dict(orient="records")
    top_artists = df_artist_transitions.head(limit).to_dict(orient="records")
    top_triplets = df_3song_sequences.head(limit).to_dict(orient="records")
    
    return {
        "transitions": top_tracks,
        "top_track_transitions": top_tracks,
        "top_artist_transitions": top_artists,
        "three_song_sequences": top_triplets
    }

@router.get("/sequences/artists")
def get_artist_sequences(limit: int = Query(20, ge=1, le=100)):
    """Top artist-to-artist transitions."""
    top_artists = df_artist_transitions.head(limit).to_dict(orient="records")
    return {"transitions": top_artists, "total": len(df_artist_transitions)}

@router.get("/sequences/three-song")
def get_three_song_sequences(limit: int = Query(20, ge=1, le=100)):
    """Top 3-song Markov sequence chains."""
    top_triplets = df_3song_sequences.head(limit).to_dict(orient="records")
    return {"sequences": top_triplets, "total": len(df_3song_sequences)}

@router.get("/projects/{project_id}/songs")
def get_project_songs(project_id: str):
    """Get songs belonging to a project."""
    songs = df_songs[df_songs["project_id"] == project_id]
    if len(songs) == 0:
        # Try finding in canonical playback
        songs_canon = df_canonical[df_canonical["project_id"] == project_id].groupby(["track_id", "track_name", "artist_name"]).agg(
            total_plays=("event_id", "count"),
            total_minutes=("minutes_played", "sum")
        ).reset_index()
        return {"project_id": project_id, "songs": songs_canon.to_dict(orient="records")}
    return {"project_id": project_id, "songs": songs.to_dict(orient="records")}

@router.get("/genres/time-matrix")
def get_genre_time_matrix():
    """Genre x Time-of-Day x Year matrix and yearly genre migrations."""
    gt_list = df_genre_time.to_dict(orient="records") if len(df_genre_time) > 0 else []
    yg_list = df_yearly_genre.to_dict(orient="records") if len(df_yearly_genre) > 0 else []
    
    return {
        "genre_time_matrix": gt_list,
        "yearly_genre_share": yg_list
    }

@router.get("/freshness")
def get_freshness_data():
    """Listening Freshness distributions and Taste Fingerprint."""
    return {
        "freshness_distribution": df_freshness.to_dict(orient="records") if len(df_freshness) > 0 else [],
        "freshness_by_year": df_freshness_yr.to_dict(orient="records") if len(df_freshness_yr) > 0 else [],
        "taste_fingerprint": taste_fingerprint
    }

@router.get("/ml/metrics")
def get_ml_metrics():
    """Comprehensive ML benchmark table, calibration, and test metrics."""
    return {
        "benchmark_table": df_benchmark.to_dict(orient="records") if len(df_benchmark) > 0 else [],
        "ml_summary": ml_summary,
        "error_analysis": error_analysis,
        "temporal_audit": temporal_audit
    }

@router.get("/ml/feature-importance")
def get_ml_feature_importance():
    """LightGBM tree gain and split feature importances."""
    return {
        "feature_importance": df_feature_importance.to_dict(orient="records") if len(df_feature_importance) > 0 else []
    }

@router.get("/ml/audit")
def get_temporal_audit():
    """Temporal Leakage Audit Report confirming zero future leakage."""
    return temporal_audit

class PredictRequest(BaseModel):
    is_first_artist_play: int = 1
    seconds_played: float = 180.0
    skipped: int = 0
    shuffle: int = 0
    artist_plays_before: int = 0
    artist_tracks_heard_before: int = 0
    artist_minutes_before: float = 0.0
    artist_age_days_at_play: float = 0.0
    project_plays_before: int = 0
    project_tracks_heard_before: int = 0
    project_minutes_before: float = 0.0
    project_age_days_at_play: float = 0.0
    song_plays_before: int = 0
    song_minutes_before: float = 0.0
    song_age_days_at_play: float = 0.0
    session_position: int = 1
    hour: int = 21
    day_of_week: int = 4
    is_weekend: int = 0
    is_first_project_play: int = 1
    is_first_song_play: int = 1
    is_same_artist_as_prev: int = 0
    is_same_project_as_prev: int = 0
    time_since_prev_event_seconds: float = 120.0
    platform_android: int = 1
    platform_windows: int = 0
    platform_web_player: int = 0

@router.post("/ml/predict")
def predict_catalog_expansion(req: PredictRequest):
    """Interactive real-time prediction of 7-day catalog expansion probability."""
    if not catalyst_model_artifact:
        raise HTTPException(status_code=503, detail="ML Model artifact not loaded")
        
    model = catalyst_model_artifact["model"]
    feature_cols = catalyst_model_artifact["feature_columns"]
    best_th = catalyst_model_artifact.get("best_threshold", 0.5)
    
    input_dict = req.model_dump()
    feature_vals = [input_dict.get(c, 0) for c in feature_cols]
    X_input = pd.DataFrame([feature_vals], columns=feature_cols)
    
    prob = float(model.predict_proba(X_input)[0, 1])
    is_expansion = bool(prob >= best_th)
    
    confidence = "High" if abs(prob - best_th) > 0.25 else "Moderate"
    
    explanation = []
    if req.is_first_artist_play:
        explanation.append("First-time artist discovery significantly increases base expansion potential.")
    if req.seconds_played > 120 and req.skipped == 0:
        explanation.append("Full-length track completion signals high engagement.")
    if req.artist_tracks_heard_before >= 3:
        explanation.append("Listener has already explored multiple tracks from this artist, indicating established catalog interest.")
    if req.skipped == 1:
        explanation.append("Track was skipped, dampening immediate exploration probability.")
        
    return {
        "expansion_probability": round(prob, 4),
        "predicted_expansion": is_expansion,
        "decision_threshold": round(best_th, 3),
        "confidence_level": confidence,
        "explanation": explanation
    }
