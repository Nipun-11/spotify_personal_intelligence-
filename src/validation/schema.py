"""Data schema definitions using Pydantic and DataFrame field definitions."""

from typing import Optional
from pydantic import BaseModel, Field

class RawSpotifyRecord(BaseModel):
    """Pydantic model representing a raw record in Spotify Extended Streaming History."""
    ts: str
    platform: Optional[str] = None
    ms_played: int
    conn_country: Optional[str] = None
    ip_addr: Optional[str] = None
    master_metadata_track_name: Optional[str] = None
    master_metadata_album_artist_name: Optional[str] = None
    master_metadata_album_album_name: Optional[str] = None
    spotify_track_uri: Optional[str] = None
    episode_name: Optional[str] = None
    episode_show_name: Optional[str] = None
    spotify_episode_uri: Optional[str] = None
    audiobook_title: Optional[str] = None
    audiobook_uri: Optional[str] = None
    audiobook_chapter_uri: Optional[str] = None
    audiobook_chapter_title: Optional[str] = None
    reason_start: Optional[str] = None
    reason_end: Optional[str] = None
    shuffle: Optional[bool] = False
    skipped: Optional[bool] = False
    offline: Optional[bool] = False
    offline_timestamp: Optional[int] = None
    incognito_mode: Optional[bool] = False

class CanonicalPlaybackEvent(BaseModel):
    """Pydantic model representing a validated canonical playback event."""
    event_id: str
    timestamp_utc: str
    timestamp_local: str
    date: str
    year: int
    month: int
    week: int
    day_of_week: int
    hour: int
    time_of_day_bucket: str
    is_weekend: bool
    content_type: str  # 'music', 'podcast', 'audiobook', 'video'
    track_id: Optional[str] = None
    track_name: Optional[str] = None
    artist_id: Optional[str] = None
    artist_name: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    ms_played: int
    seconds_played: float
    minutes_played: float
    skipped: bool
    shuffle: bool
    offline: bool
    incognito_mode: bool
    start_reason: Optional[str] = None
    end_reason: Optional[str] = None
    platform: Optional[str] = None
    session_id: Optional[str] = None
    session_position: Optional[int] = None
