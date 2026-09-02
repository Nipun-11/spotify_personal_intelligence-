"""FastAPI application factory and static dashboard mounting."""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.config import BASE_DIR
from src.api.routes import router

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure production FastAPI application."""
    app = FastAPI(
        title="Spotify Personal Intelligence Engine API",
        description="REST API serving behavioral listening intelligence, catalog discovery analytics, and ML predictions.",
        version="1.0.0"
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router)
    
    # Mount Dashboard static assets at /static AND at root level
    dashboard_dir = BASE_DIR / "dashboard"
    if dashboard_dir.exists():
        # Serve static assets both at /static and at root so relative paths work
        app.mount("/static", StaticFiles(directory=str(dashboard_dir)), name="static")

        @app.get("/")
        async def serve_index():
            return FileResponse(dashboard_dir / "index.html")

        @app.get("/app.js")
        async def serve_appjs():
            return FileResponse(dashboard_dir / "app.js", media_type="application/javascript")

        @app.get("/style.css")
        async def serve_css():
            return FileResponse(dashboard_dir / "style.css", media_type="text/css")

    return app

app = create_app()
