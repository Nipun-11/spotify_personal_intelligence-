"""Metadata package."""
from src.metadata.genre_rules import infer_genre, ARTIST_GENRE_MAP
from src.metadata.project_enrichment import infer_release_type

__all__ = ["infer_genre", "ARTIST_GENRE_MAP", "infer_release_type"]
