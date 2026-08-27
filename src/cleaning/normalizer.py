"""Data normalization and entity standardization module."""

import re
import hashlib
import unicodedata
from typing import Optional, Tuple
import pandas as pd
import pytz

from src.config import LOCAL_TIMEZONE, TIME_OF_DAY_BUCKETS

def slugify(text: Optional[str]) -> str:
    """Create a URL-safe normalized slug from arbitrary text."""
    if not text or pd.isna(text):
        return "unknown"
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", text)

def generate_deterministic_id(prefix: str, *components: str) -> str:
    """Generate a deterministic ID based on component strings."""
    raw_str = "||".join(str(c).strip().lower() for c in components if c is not None)
    digest = hashlib.md5(raw_str.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"

def extract_track_id(track_uri: Optional[str], track_name: Optional[str], artist_name: Optional[str]) -> str:
    """Extract Spotify track ID or generate deterministic fallback."""
    if track_uri and isinstance(track_uri, str) and track_uri.startswith("spotify:track:"):
        return track_uri.split(":")[-1]
    return generate_deterministic_id("trk", track_name or "unknown", artist_name or "unknown")

def extract_artist_id(artist_name: Optional[str]) -> str:
    """Generate canonical deterministic artist ID."""
    clean_name = str(artist_name).strip() if artist_name and not pd.isna(artist_name) else "unknown"
    return generate_deterministic_id("art", clean_name)

def extract_project_id(artist_name: Optional[str], project_name: Optional[str]) -> str:
    """Generate canonical deterministic project (album/EP) ID."""
    clean_artist = str(artist_name).strip() if artist_name and not pd.isna(artist_name) else "unknown"
    clean_proj = str(project_name).strip() if project_name and not pd.isna(project_name) else "unknown"
    return generate_deterministic_id("prj", clean_artist, clean_proj)

def get_time_of_day_bucket(hour: int) -> str:
    """Assign an hour (0-23) to one of the 8 standard 3-hour buckets."""
    for bucket_name, (start_h, end_h) in TIME_OF_DAY_BUCKETS.items():
        if start_h <= hour < end_h:
            return bucket_name
    return "12AM-3AM"

def normalize_platform(platform_str: Optional[str]) -> str:
    """Normalize raw device platform string into standard categories."""
    if not platform_str or pd.isna(platform_str):
        return "other"
    p_lower = str(platform_str).lower()
    if "android" in p_lower:
        return "android"
    elif "windows" in p_lower:
        return "windows"
    elif "web" in p_lower:
        return "web_player"
    elif "ios" in p_lower or "iphone" in p_lower or "ipad" in p_lower:
        return "ios"
    elif "mac" in p_lower or "osx" in p_lower:
        return "macos"
    elif "cast" in p_lower or "tv" in p_lower:
        return "smart_speaker_tv"
    return "other"

def determine_content_type(row: pd.Series) -> str:
    """Determine content type: music, podcast, audiobook, or video."""
    if row.get("_source_type") == "video":
        return "video"
    if pd.notna(row.get("audiobook_title")):
        return "audiobook"
    if pd.notna(row.get("episode_name")) or pd.notna(row.get("spotify_episode_uri")):
        return "podcast"
    if pd.notna(row.get("master_metadata_track_name")):
        return "music"
    return "other"

def normalize_playback_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw DataFrame into standardized, normalized intermediate DataFrame."""
    clean_df = df.copy()
    
    # 1. Parse timestamps in UTC
    clean_df["timestamp_utc"] = pd.to_datetime(clean_df["ts"], utc=True)
    
    # Sort chronologically
    clean_df = clean_df.sort_values("timestamp_utc").reset_index(drop=True)
    
    # 2. Local timestamp in IST (Asia/Kolkata)
    local_tz = pytz.timezone(LOCAL_TIMEZONE)
    clean_df["timestamp_local"] = clean_df["timestamp_utc"].dt.tz_convert(local_tz)
    
    # Calendar features
    clean_df["date"] = clean_df["timestamp_local"].dt.strftime("%Y-%m-%d")
    clean_df["year"] = clean_df["timestamp_local"].dt.year
    clean_df["month"] = clean_df["timestamp_local"].dt.month
    clean_df["week"] = clean_df["timestamp_local"].dt.isocalendar().week.astype(int)
    clean_df["day_of_week"] = clean_df["timestamp_local"].dt.dayofweek # 0=Monday, 6=Sunday
    clean_df["hour"] = clean_df["timestamp_local"].dt.hour
    clean_df["is_weekend"] = clean_df["day_of_week"].isin([5, 6])
    clean_df["time_of_day_bucket"] = clean_df["hour"].apply(get_time_of_day_bucket)
    
    # Content type
    clean_df["content_type"] = clean_df.apply(determine_content_type, axis=1)
    
    # Identifiers
    clean_df["track_name"] = clean_df["master_metadata_track_name"].fillna("").astype(str).str.strip()
    clean_df["artist_name"] = clean_df["master_metadata_album_artist_name"].fillna("").astype(str).str.strip()
    clean_df["project_name"] = clean_df["master_metadata_album_album_name"].fillna("").astype(str).str.strip()
    
    clean_df["track_id"] = clean_df.apply(
        lambda r: extract_track_id(r.get("spotify_track_uri"), r.get("track_name"), r.get("artist_name")),
        axis=1
    )
    clean_df["artist_id"] = clean_df["artist_name"].apply(extract_artist_id)
    clean_df["project_id"] = clean_df.apply(
        lambda r: extract_project_id(r.get("artist_name"), r.get("project_name")),
        axis=1
    )
    
    # Durations
    clean_df["ms_played"] = clean_df["ms_played"].fillna(0).astype(int)
    clean_df["seconds_played"] = clean_df["ms_played"] / 1000.0
    clean_df["minutes_played"] = clean_df["ms_played"] / 60000.0
    
    # Booleans
    clean_df["skipped"] = clean_df["skipped"].fillna(False).astype(bool)
    clean_df["shuffle"] = clean_df["shuffle"].fillna(False).astype(bool)
    clean_df["offline"] = clean_df["offline"].fillna(False).astype(bool)
    clean_df["incognito_mode"] = clean_df["incognito_mode"].fillna(False).astype(bool)
    
    # Playback metadata
    clean_df["start_reason"] = clean_df["reason_start"].fillna("unknown").astype(str)
    clean_df["end_reason"] = clean_df["reason_end"].fillna("unknown").astype(str)
    clean_df["platform_raw"] = clean_df["platform"].fillna("unknown").astype(str)
    clean_df["platform"] = clean_df["platform_raw"].apply(normalize_platform)
    
    # Event ID
    clean_df["event_id"] = clean_df.apply(
        lambda r: f"evt_{r.name:06d}_{hashlib.md5(f'{r.timestamp_utc}_{r.track_id}_{r.ms_played}'.encode()).hexdigest()[:8]}",
        axis=1
    )
    
    return clean_df
