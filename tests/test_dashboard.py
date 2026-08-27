"""Smoke tests for dashboard static assets and structure."""

import pytest
from pathlib import Path
from src.config import BASE_DIR

def test_dashboard_files_exist():
    dash_dir = BASE_DIR / "dashboard"
    assert (dash_dir / "index.html").exists()
    assert (dash_dir / "index.css").exists()
    assert (dash_dir / "app.js").exists()

def test_dashboard_html_contains_all_10_views():
    html_content = (BASE_DIR / "dashboard" / "index.html").read_text(encoding="utf-8")
    views = [
        "tab-overview",
        "tab-catalysts",
        "tab-artists",
        "tab-projects",
        "tab-songs",
        "tab-sequences",
        "tab-network",
        "tab-genres",
        "tab-deepdive",
        "tab-ml"
    ]
    for view in views:
        assert view in html_content, f"Missing view tab: {view}"

def test_dashboard_css_has_dark_tokens():
  css_content = (BASE_DIR / "dashboard" / "index.css").read_text(encoding="utf-8")
  assert "--bg-base" in css_content
  assert "--accent-green" in css_content
