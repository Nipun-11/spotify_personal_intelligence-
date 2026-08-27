"""Sequence and transition analytics module."""

import logging
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def compute_transitions(df_events: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Compute transition matrices, probabilities, and 3-track sequence patterns.
    
    Args:
        df_events: Canonical playback events DataFrame.
        
    Returns:
        Dictionary of DataFrames:
          - 'track_transitions'
          - 'artist_transitions'
          - 'project_transitions'
          - 'three_song_sequences'
    """
    logger.info("Computing listening sequence and transition analytics...")
    music_df = df_events[df_events["content_type"] == "music"].copy()
    
    # Filter valid transitions within the same session (time gap <= 30 min)
    valid_transitions = music_df[
        (music_df["previous_track_id"].notna()) &
        (music_df["is_same_artist_as_prev"] | (music_df["time_since_prev_event_seconds"] <= 1800))
    ].copy()
    
    # 1. Track-to-Track Transitions
    track_trans = valid_transitions.groupby([
        "previous_track_id", "previous_track_name", "previous_artist_name",
        "track_id", "track_name", "artist_name"
    ]).size().reset_index(name="transition_count")
    
    # Calculate transition probability P(next_track | from_track)
    track_totals = track_trans.groupby("previous_track_id")["transition_count"].transform("sum")
    track_trans["transition_probability"] = (track_trans["transition_count"] / track_totals).round(4)
    track_trans = track_trans.sort_values("transition_count", ascending=False).reset_index(drop=True)
    
    # 2. Artist-to-Artist Transitions
    artist_trans = valid_transitions.groupby([
        "previous_artist_id", "previous_artist_name",
        "artist_id", "artist_name"
    ]).size().reset_index(name="transition_count")
    
    artist_totals = artist_trans.groupby("previous_artist_id")["transition_count"].transform("sum")
    artist_trans["transition_probability"] = (artist_trans["transition_count"] / artist_totals).round(4)
    artist_trans["is_self_transition"] = artist_trans["previous_artist_id"] == artist_trans["artist_id"]
    artist_trans = artist_trans.sort_values("transition_count", ascending=False).reset_index(drop=True)
    
    # 3. Project-to-Project Transitions
    proj_trans = valid_transitions.groupby([
        "previous_project_id", "previous_project_name", "previous_artist_name",
        "project_id", "project_name", "artist_name"
    ]).size().reset_index(name="transition_count")
    
    proj_totals = proj_trans.groupby("previous_project_id")["transition_count"].transform("sum")
    proj_trans["transition_probability"] = (proj_trans["transition_count"] / proj_totals).round(4)
    proj_trans["is_self_transition"] = proj_trans["previous_project_id"] == proj_trans["project_id"]
    proj_trans = proj_trans.sort_values("transition_count", ascending=False).reset_index(drop=True)
    
    # 4. Three-Song Sequences (A -> B -> C)
    music_df["prev2_track_name"] = music_df["track_name"].shift(2)
    music_df["prev2_artist_name"] = music_df["artist_name"].shift(2)
    music_df["prev_track_name"] = music_df["track_name"].shift(1)
    music_df["prev_artist_name"] = music_df["artist_name"].shift(1)
    
    # Ensure same session
    same_session_3 = (music_df["session_id"] == music_df["session_id"].shift(1)) & \
                     (music_df["session_id"] == music_df["session_id"].shift(2))
    
    triplets = music_df[same_session_3 & music_df["prev2_track_name"].notna()].groupby([
        "prev2_track_name", "prev2_artist_name",
        "prev_track_name", "prev_artist_name",
        "track_name", "artist_name"
    ]).size().reset_index(name="sequence_count")
    
    triplets = triplets.sort_values("sequence_count", ascending=False).reset_index(drop=True)
    
    logger.info(f"Built transition tables: {len(track_trans)} track pairs, {len(artist_trans)} artist pairs, {len(triplets)} 3-song chains")
    return {
        "track_transitions": track_trans,
        "artist_transitions": artist_trans,
        "project_transitions": proj_trans,
        "three_song_sequences": triplets
    }
