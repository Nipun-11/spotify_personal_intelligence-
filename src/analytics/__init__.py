"""Analytics package."""
from src.analytics.artist_lifecycle import compute_artist_lifecycles
from src.analytics.song_lifecycle import compute_song_lifecycles
from src.analytics.project_analytics import compute_project_analytics
from src.analytics.transitions import compute_transitions
from src.analytics.networks import build_music_network
from src.analytics.genre_time import compute_genre_time_analytics
from src.analytics.freshness import compute_freshness_analytics

__all__ = [
    "compute_artist_lifecycles",
    "compute_song_lifecycles",
    "compute_project_analytics",
    "compute_transitions",
    "build_music_network",
    "compute_genre_time_analytics",
    "compute_freshness_analytics",
]
