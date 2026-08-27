"""FastAPI server startup script."""

import sys
import uvicorn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import API_HOST, API_PORT

def main():
    print(f"Starting Spotify Personal Intelligence Engine on http://{API_HOST}:{API_PORT}")
    uvicorn.run("src.api.app:app", host=API_HOST, port=API_PORT, reload=False)

if __name__ == "__main__":
    main()
