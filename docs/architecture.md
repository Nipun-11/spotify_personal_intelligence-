# Spotify Personal Intelligence Engine — System Architecture

## 1. High-Level Architecture

The **Spotify Personal Intelligence Engine** is a layered behavioral analytics and machine learning system structured across bronze, silver, and gold analytical data layers.

```mermaid
graph TD
    A[Raw Spotify Extended JSON] -->|Phase 1: Ingestion & Validation| B[Validated Event Stream]
    B -->|Phase 2 & 3: Normalization & Sessionization| C[Canonical Playback Table (Silver Parquet)]
    C -->|Phase 4: Core Analytics| D[Artist & Song Lifecycles (Gold)]
    C -->|Phase 4: Project Engine| E[Albums & EPs Intelligence (Gold)]
    C -->|Phase 4: Sequences| F[Transitions & Music Network (Gold)]
    C -->|Phase 5: Discovery Engine| G[Discovery Catalyst Events (Gold)]
    C -->|Phase 7: Temporal Feature Store| H[Strictly Historical ML Datasets]
    H -->|Phase 7: Training & Baselines| I[LightGBM & Baselines]
    D & E & F & G & I -->|Phase 8: High-Performance REST API| J[FastAPI Backend]
    J -->|Phase 9: Client Serving| K[Interactive Web Dashboard]
```

---

## 2. Layered Data Architecture

### Bronze Layer (`data/raw/`)
- **Immutability Principle**: Raw Spotify JSON exports (`Streaming_History_Audio_*.json`, `Streaming_History_Video_*.json`) are never modified in-place.
- Ingestion handles UTF-8 normalization, malformed timestamps, zero/negative durations, and isolates non-music content (podcasts, video, audiobooks).

### Silver Layer (`data/processed/canonical_playback.parquet`)
- Single canonical tabular representation (one row per playback event).
- Schema includes extracted stable IDs (`track_id`, `artist_id`, `project_id`), local timezone conversion (`Asia/Kolkata` IST), session identifiers (`session_id`, `session_position`), lag/lead sequence features, and retrospective pre-$T$ historical cumulative counters.

### Gold Layer (`data/processed/`)
- Specialized analytical tables optimized for low-latency queries and visualization:
  - `artist_lifecycles.parquet`
  - `song_lifecycles.parquet`
  - `projects.parquet` (enforcing $\ge 3$-track rule)
  - `project_driving_songs.parquet`
  - `sessions.parquet`
  - `discovery_events.parquet` & `discovery_rankings.parquet`
  - `track_transitions.parquet`, `artist_transitions.parquet`, `three_song_sequences.parquet`
  - `genre_time_matrix.parquet`, `yearly_genre_share.parquet`
  - `network.json` & `taste_fingerprint.json`

---

## 3. Technology Stack

- **Data Processing**: Python 3.10+, Pandas, NumPy, PyArrow (Parquet), DuckDB.
- **Machine Learning**: LightGBM, Scikit-learn, XGBoost.
- **Network Analysis**: NetworkX (PageRank, Betweenness Centrality, Greedy Modularity Communities).
- **Backend API**: FastAPI, Uvicorn, Pydantic V2.
- **Interactive UI**: HTML5, Vanilla CSS (Glassmorphic dark design system), JavaScript (ES6+), Plotly.js, Canvas force graph.
- **Containerization**: Docker, Docker Compose.
