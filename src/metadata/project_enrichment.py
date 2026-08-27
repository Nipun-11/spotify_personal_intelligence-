"""Project metadata enrichment for release types (Album vs EP vs Single)."""

import re
from typing import Optional, Dict
import pandas as pd

def infer_release_type(project_name: Optional[str], tracks_heard_count: int) -> str:
    """Infer release type (Album, EP, Single, Soundtrack, Compilation) using name heuristics and track count.
    
    Args:
        project_name: Name of the album / project.
        tracks_heard_count: Number of unique tracks heard from this project.
        
    Returns:
        Inferred release type string.
    """
    if not project_name:
        return "Single" if tracks_heard_count <= 1 else "Album"
        
    name_clean = project_name.strip().lower()
    
    # Check explicit keywords in title
    if "soundtrack" in name_clean or "ost" in name_clean or "motion picture" in name_clean:
        return "Soundtrack"
    if "compilation" in name_clean or "greatest hits" in name_clean or "best of" in name_clean:
        return "Compilation"
    if re.search(r"\bep\b", name_clean) or name_clean.endswith("- ep") or "(ep)" in name_clean:
        return "EP"
    if "single" in name_clean or "(single)" in name_clean:
        return "Single"
        
    # Heuristic based on track count
    if tracks_heard_count >= 6:
        return "Album"
    elif tracks_heard_count in [3, 4, 5]:
        return "EP / Mini-Album"
    elif tracks_heard_count == 2:
        return "Two-Track Single / EP"
    else:
        return "Single / Track"
