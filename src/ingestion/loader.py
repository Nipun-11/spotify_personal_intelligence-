"""Raw Spotify data ingestion module."""

import json
import glob
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from src.config import RAW_DATA_DIR, INTERIM_DATA_DIR

logger = logging.getLogger(__name__)

def discover_raw_files(raw_dir: Path = RAW_DATA_DIR) -> Dict[str, List[Path]]:
    """Discover all raw audio and video streaming history JSON files.
    
    Args:
        raw_dir: Directory containing raw Spotify JSON files.
        
    Returns:
        Dictionary with keys 'audio' and 'video' mapping to lists of file paths.
    """
    raw_path = Path(raw_dir)
    audio_files = sorted(list(raw_path.glob("Streaming_History_Audio_*.json")))
    video_files = sorted(list(raw_path.glob("Streaming_History_Video_*.json")))
    
    logger.info(f"Discovered {len(audio_files)} audio files and {len(video_files)} video files in {raw_dir}")
    return {
        "audio": audio_files,
        "video": video_files
    }

def load_json_records(file_paths: List[Path], source_type: str = "audio") -> List[Dict[str, Any]]:
    """Load JSON records from a list of files, adding metadata.
    
    Args:
        file_paths: List of JSON file paths to load.
        source_type: Type of source ('audio' or 'video').
        
    Returns:
        List of raw dictionaries with added source_file and source_type.
    """
    records = []
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                for item in data:
                    item["_source_file"] = file_path.name
                    item["_source_type"] = source_type
                    records.append(item)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise
    return records

def load_raw_dataset(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load all raw Spotify streaming history records into a single raw DataFrame.
    
    Args:
        raw_dir: Directory containing raw files.
        
    Returns:
        Combined pandas DataFrame of all audio and video streaming records.
    """
    files = discover_raw_files(raw_dir)
    audio_records = load_json_records(files["audio"], source_type="audio")
    video_records = load_json_records(files["video"], source_type="video")
    
    all_records = audio_records + video_records
    df = pd.DataFrame(all_records)
    logger.info(f"Loaded total {len(df)} raw playback records ({len(audio_records)} audio, {len(video_records)} video)")
    return df
