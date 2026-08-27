"""Genre mapping rules and artist genre assignment heuristics."""

import re
from typing import Optional, Dict

# High-fidelity curated artist to genre mappings based on dataset discography
ARTIST_GENRE_MAP: Dict[str, str] = {
    # Desi Hip-Hop / Indian Hip-Hop (DHH)
    "seedhe maut": "Desi Hip-Hop",
    "panther": "Desi Hip-Hop",
    "frappe ash": "Desi Hip-Hop",
    "rawal": "Desi Hip-Hop",
    "aniket raturi": "Desi Hip-Hop",
    "naam sujal": "Desi Hip-Hop",
    "og lucifer": "Desi Hip-Hop",
    "kr$na": "Desi Hip-Hop",
    "krsna": "Desi Hip-Hop",
    "raftaar": "Desi Hip-Hop",
    "ikka": "Desi Hip-Hop",
    "divine": "Desi Hip-Hop",
    "yungsta": "Desi Hip-Hop",
    "ahmer": "Desi Hip-Hop",
    "chaar diwaari": "Experimental / DHH",
    "sez on the beat": "Desi Hip-Hop / Production",
    "bhaskar": "Desi Hip-Hop",
    "calm": "Desi Hip-Hop",
    "encore abj": "Desi Hip-Hop",
    "dakait": "Desi Hip-Hop",
    "gravity": "Desi Hip-Hop",
    "rebel 7": "Desi Hip-Hop",
    "foosie gang": "Desi Hip-Hop",
    "qaab": "Desi Hip-Hop",
    "ab 17": "Desi Hip-Hop",
    
    # Pakistani Hip-Hop (PHH)
    "talha anjum": "Pakistani Hip-Hop",
    "talhah yunus": "Pakistani Hip-Hop",
    "young stunners": "Pakistani Hip-Hop",
    "umair": "Pakistani Hip-Hop",
    "hasan raheem": "Pakistani Indie / Pop",
    "faris shafi": "Pakistani Hip-Hop",
    "aleemrk": "Pakistani Hip-Hop",
    "jj47": "Pakistani Hip-Hop",
    "abdul hannan": "Pakistani Indie / Pop",
    
    # Punjabi Pop / Hip-Hop
    "karan aujla": "Punjabi Pop / Hip-Hop",
    "diljit dosanjh": "Punjabi Pop",
    "sidhu moose wala": "Punjabi Hip-Hop",
    "ap dhillon": "Punjabi Pop",
    "shubh": "Punjabi Pop / Hip-Hop",
    "gurinder gill": "Punjabi Pop",
    "amrit maan": "Punjabi Pop",
    "tarnvir singh": "Punjabi Pop",
    "wazir patar": "Punjabi Hip-Hop",
    
    # Indian Pop / Commercial
    "king": "Indian Pop",
    "badshah": "Indian Pop / Commercial",
    "prateek kuhad": "Indian Indie Pop",
    "anuv jain": "Indian Indie Pop",
    "zaeden": "Indian Pop / EDM",
    "aditya a": "Indian Indie Pop",
    "arjan dhillon": "Punjabi Pop",
    
    # Bollywood / Film Music
    "pritam": "Bollywood",
    "arijit singh": "Bollywood",
    "a.r. rahman": "Bollywood / Classical",
    "sachin-jigar": "Bollywood",
    "vishal-shekhar": "Bollywood",
    "amit trivedi": "Bollywood / Indie",
    "shankar-ehsaan-loy": "Bollywood",
    "shreya ghoshal": "Bollywood",
    "atif aslam": "Bollywood / Pop",
    "alka yagnik": "Bollywood Retro",
    "kishore kumar": "Bollywood Retro",
    "lata mangeshkar": "Bollywood Retro",
    "udit narayan": "Bollywood Retro",
    "kumar sanu": "Bollywood Retro",
    
    # Global Hip-Hop / R&B / Pop
    "the weeknd": "Global R&B / Pop",
    "drake": "Global Hip-Hop / Rap",
    "travis scott": "Global Hip-Hop / Rap",
    "kanye west": "Global Hip-Hop / Rap",
    "kendrick lamar": "Global Hip-Hop / Rap",
    "post malone": "Global Pop / Hip-Hop",
    "metro boomin": "Global Hip-Hop / Rap",
    "eminem": "Global Hip-Hop / Rap",
    "21 savage": "Global Hip-Hop / Rap",
    "j. cole": "Global Hip-Hop / Rap",
    "dua lipa": "Global Pop",
    "taylor swift": "Global Pop",
    "billie eilish": "Global Pop / Alternative",
}

def infer_genre(artist_name: Optional[str]) -> str:
    """Infer primary genre of an artist using mapping and keyword heuristics."""
    if not artist_name:
        return "Unknown Genre"
    clean = artist_name.strip().lower()
    
    # Exact match
    if clean in ARTIST_GENRE_MAP:
        return ARTIST_GENRE_MAP[clean]
        
    # Substring match
    for mapped_art, genre in ARTIST_GENRE_MAP.items():
        if mapped_art in clean or clean in mapped_art:
            return genre
            
    # Generic keywords
    if any(k in clean for k in ["moose", "aujla", "dosanjh", "dhillon", "singh", "sandhu", "maan", "dhillon"]):
        return "Punjabi Pop / Hip-Hop"
    if any(k in clean for k in ["singh", "kumar", "sharma", "burman", "ghoshal", "narayan"]):
        return "Bollywood / Indian Film"
    if any(k in clean for k in ["lil", "mc", "dj", "beat", "prod", "rap", "hip hop"]):
        return "Hip-Hop / Rap"
        
    return "Independent / Other"
