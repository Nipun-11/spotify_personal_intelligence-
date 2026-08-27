# Spotify Personal Intelligence Engine

## Project Overview

**Spotify Personal Intelligence Engine** is a portfolio-grade data analytics, machine learning, and interactive visualization project built from Spotify Extended Streaming History.

The goal is to move beyond a conventional Spotify Wrapped dashboard and model **how a listener's taste develops over time**:

- How artists enter, peak, decline, and return
- How songs become obsessions, favorites, evergreen tracks, or failed discoveries
- How one song can lead to exploration of an artist's wider catalog
- How albums and EPs are explored and completed
- Which songs drive the majority of a project's listening
- Which songs are repeatedly listened to together
- How genres and artists vary by time of day and year
- How listening sessions behave
- How the personal music network evolves
- Whether machine learning can predict future catalog exploration

The project is intended to be strong enough for **GitHub and company/job applications**, demonstrating data engineering, analytics, ML, visualization, and software engineering.

---

## Core Research Question

> **How does a listener's musical taste actually develop?**

Rather than only asking:

> What are the top artists and songs?

the system asks:

> What causes a song, artist, or project to become part of the listener's longer-term musical ecosystem?

---

# 1. Project Goals

### Primary goals

1. Build a reliable Spotify listening-history data pipeline.
2. Create a reusable feature-engineered analytical dataset.
3. Analyze artist, song, album/EP, session, and discovery behavior.
4. Reconstruct song-to-song and artist-to-artist listening pathways.
5. Identify discovery catalysts and catalog-expansion events.
6. Model song and artist lifecycles.
7. Build an interactive dashboard.
8. Add an explainable ML layer.
9. Package the project professionally for GitHub and job applications.

### Portfolio goals

The project should demonstrate:

- Data Engineering
- Exploratory Data Analysis
- Behavioral Analytics
- Feature Engineering
- Machine Learning
- Time-Series Analysis
- Network Analysis
- Data Visualization
- API/backend development
- Software Engineering
- Product thinking

---

# 2. Dataset

Primary source:

**Spotify Extended Streaming History**

The history contains playback-level information such as:

- Timestamp
- Track
- Artist
- Album/project
- Track URI
- Playback duration
- Skip/end information
- Start reason
- End reason
- Shuffle state
- Device
- Offline status
- Other Spotify playback metadata

The working history currently contains roughly:

- **32K+ playback events**
- **6K+ distinct tracks**
- **1.7K+ artists**

Exact numbers should always be generated from the final processing pipeline rather than hard-coded.

---

# 3. Project Architecture

```text
Spotify Extended Streaming History
                |
                v
        Data Ingestion
                |
                v
       Cleaning & Validation
                |
                v
      Feature Engineering
                |
        +-------+-------+
        |               |
        v               v
   Deterministic       ML
     Analytics        Models
        |               |
        +-------+-------+
                |
                v
          API / Data Layer
                |
                v
        Interactive Dashboard
```

Recommended implementation:

```text
Python
├── Pandas / Polars
├── scikit-learn
├── XGBoost / LightGBM
├── NetworkX
└── FastAPI

Dashboard
├── React / Next.js
├── Plotly / D3.js
└── Interactive filtering

Infrastructure
├── PostgreSQL
├── Docker
└── GitHub Actions (optional)
```

Technology choices can be adjusted based on implementation complexity. The goal is quality and clarity, not collecting technologies.

---

# 4. Data Model

The central analytical dataset should contain one row per playback event.

Example conceptual schema:

```text
playback_event
-----------------------------
event_id
timestamp
date
year
month
week
day_of_week
hour
track_uri
track_name
artist
album
duration_ms
ms_played
skipped
start_reason
end_reason
shuffle
device
offline
session_id

song_first_seen
song_age_days
artist_first_seen
artist_age_days
project_first_seen
project_age_days

song_play_count_before
artist_play_count_before
project_play_count_before

is_first_song_play
is_new_artist
is_new_project
is_catalog_reengagement

project_tracks_heard
project_track_count
project_penetration

session_position
session_length
previous_track
previous_artist
next_track
next_artist
```

Derived outcome features should include:

```text
expansion_7d
new_artist_tracks_7d
new_projects_7d
downstream_minutes_7d
retention_30d
retention_90d
downstream_minutes_30d
downstream_minutes_90d
future_hours_unlocked
```

---

# 5. Artist Lifecycle Analysis

For every artist:

```text
First Discovery
      |
      v
Initial Exploration
      |
      v
Growth
      |
      v
Peak
      |
      v
Decline
      |
      +------> Revival
      |
      v
Dormant / Current
```

Metrics:

- First heard
- Last heard
- Total listening time
- Total plays
- Unique tracks
- Unique projects
- Active days
- Active months
- Peak month
- Peak year
- Time-to-peak
- Longest inactivity gap
- Number of revivals
- Current activity
- Time-of-day profile
- Genre profile
- Catalog depth

### Artist categories

Artists can be classified as:

- Current favorite
- Era artist
- Long-term artist
- Evergreen artist
- Nostalgia artist
- Failed discovery
- Gateway artist
- Catalog artist
- Re-engagement artist

---

# 6. Song Lifecycle Analysis

Every song can be modeled as:

```text
Discovery
   |
   v
Trial
   |
   +----> Failed Discovery
   |
   v
Repeat
   |
   v
Obsession
   |
   v
Rotation
   |
   +----> Decline
   |
   +----> Evergreen
   |
   +----> Revival
```

Metrics:

- First played
- Last played
- Total plays
- Total minutes
- Active days
- Active months
- First-to-last lifespan
- Active lifespan
- Maximum inactivity gap
- Plays in first 24 hours
- Plays in first 7 days
- 30-day retention
- 90-day retention
- Skip rate
- Replay rate

### Important distinction

**Raw lifespan**

```text
First play → Last play
```

**Active lifespan**

Accounts for gaps and measures sustained active participation.

A song played in 2023 and once again in 2026 should not automatically be interpreted as continuously relevant.

---

# 7. Song Discovery Catalysts

This is the flagship analytical concept.

Instead of requiring:

```text
Song A → Song B immediately
```

use a broader **7-day discovery window**.

The question becomes:

> After encountering Song A, did listening behavior expand into more of that artist's catalog during the following seven days?

For every potential catalyst:

```text
Catalyst Song
     |
     v
7-Day Window
     |
     +--> Other Artist Tracks
     |
     +--> New Projects
     |
     +--> Listening Minutes
     |
     v
30-Day Retention
     |
     v
90-Day Impact
```

### Metrics

**Artist Expansion — 7D**

Number of additional tracks from the artist.

**Project Expansion — 7D**

Number of additional projects entered.

**Listening Impact — 7D**

Additional minutes generated.

**Retention — 30D**

How much of the newly explored catalog survives.

**Retention — 90D**

Whether the discovery materially changes longer-term behavior.

**Future Hours Unlocked**

Total downstream listening generated by the discovery pathway.

---

# 8. Three Discovery Types

## 8.1 Artist Discovery

The artist was not previously present in the listening history.

```text
Song
 ↓
New Artist
 ↓
Additional Artist Tracks
 ↓
Additional Projects
```

## 8.2 Project Discovery

The artist is already known, but the listener enters a project not recently explored.

```text
Known Artist
 ↓
New Album / EP
 ↓
Catalog Exploration
```

## 8.3 Catalog Deepening / Re-engagement

The artist is already known and the song causes deeper or renewed exploration.

Example:

```text
Ice Cream Frappe
       ↓
Frappe Ash catalog
       ↓
Junkie
```

This is **not** first-ever artist discovery if Frappe Ash was already present in the history.

---

# 9. Key Discovery Examples

## Panther — Aa Jao

The track **Aa Jao** is a key example of a catalog-expansion signal.

The analysis should examine:

```text
Aa Jao
   ↓
Chahat
   ↓
Additional Panther tracks
   ↓
Flying Towards The City
   ↓
Additional catalog exploration
   ↓
Longer-term Panther listening
```

The important claim is:

> Aa Jao was followed by substantial Panther catalog exploration.

Do not claim that Aa Jao causally caused the exploration.

Use language such as:

- Discovery pathway
- Catalog expansion
- Re-entry
- Catalyst signal

---

## Frappe Ash — Ice Cream Frappe

The user's example:

> "i heard Ice cream frappe and then later that weak i listened Junkie"

This is a strong example of **catalog deepening/re-engagement**.

The relevant pathway is:

```text
Ice Cream Frappe
       ↓
Frappe Ash exploration
       ↓
Junkie
       ↓
Additional Frappe Ash tracks
       ↓
Longer-term retention
```

Again, do not label this as first-ever artist discovery because Frappe Ash was already known.

---

# 10. Discovery Catalyst Ranking

Create a ranking of songs by:

```text
Discovery Power
+
Discovery Quality
+
Downstream Listening
+
30D Retention
+
90D Retention
```

Possible metrics:

### Discovery Power
How many new songs/projects followed?

### Discovery Quality
How many of those discoveries survived?

### Discovery Impact
How many future listening minutes/hours were generated?

### Discovery Depth
How deeply the artist/project was explored.

### Discovery Durability
How much activity remains after 30/90 days.

The dashboard should be able to show:

```text
Aa Jao — Panther

7D:
24 additional tracks
2 projects
X minutes

30D:
X additional minutes

90D:
X additional minutes

Classification:
Strong Catalog Expansion
```

Exact numbers should come from the final pipeline.

---

# 11. Album & EP Intelligence

The project must distinguish:

- Album
- EP
- Single
- Compilation
- Soundtrack
- Other release types

The raw Spotify Extended History does not reliably provide enough release-type information to assume these classifications.

Therefore:

> Enrich project metadata before making exact Album vs EP claims.

---

# 12. Project Qualification Rule

### Permanent rule:

> **A project qualifies as “explored” when at least 3 unique tracks from that project were heard.**

This threshold was deliberately changed from 4 to 3 because some EPs contain only 3 tracks.

Therefore:

```text
3-track EP
3/3 heard
= Complete project
```

while:

```text
20-track album
3/20 heard
= Explored, but only 15% penetration
```

These must not be treated as equivalent.

---

# 13. Project Metrics

For every project:

- Artist
- Project name
- Release type
- Total tracks
- Tracks heard
- Project penetration
- Total plays
- Total minutes
- Average play duration
- Average plays per track
- Top song
- Top-song contribution
- First heard
- Last heard
- Project lifespan
- Active months
- Sequentiality
- Completion
- Discovery/gateway song
- Common track sequences

### Project listening styles

Classify projects as:

**Hit-driven**

One or two tracks dominate.

**Partial exploration**

Several tracks heard, but project incomplete.

**Deep exploration**

Large percentage of project heard.

**Full-project consumption**

Most/all tracks heard.

---

# 14. Album-Driving Songs

For each project:

```text
Song Listening Time
-------------------
Total Project Listening Time
```

This gives the song's contribution to the project's overall listening.

Example conceptual output:

```text
Project: Open Letter

Glass Half Full
37.4% of project listening
```

Compare this with a catalog-driven project:

```text
DL91 FM

Top song
~8.8% of project listening
```

Interpretation:

- High percentage → hit-driven project
- Low percentage + broad track coverage → catalog-driven project

---

# 15. Album/EP Sequencing

Analyze repeated track sequences.

Example:

```text
Track A
  ↓
Track B
  ↓
Track C
```

Metrics:

- A → B transition count
- B → C transition count
- Album sequentiality
- Same-project transition rate
- Cross-project transition rate
- Same-artist transition rate

This distinguishes:

### Album Listener

Follows project sequence.

### Album Sampler

Explores multiple tracks but in irregular order.

### Hit Hunter

Returns repeatedly to a small number of tracks.

---

# 16. Song-to-Song Discovery

Separate simple transitions from actual discovery.

### Immediate transition

```text
A → B
```

### Discovery transition

```text
A → B
B is new
```

### 7-day discovery pathway

```text
A
 ↓
B / C / D
within 7 days
```

### Durable discovery

```text
A
 ↓
B
 ↓
B survives 30/90 days
```

Never assume that a consecutive transition proves causality.

---

# 17. Multi-Project Artist Exploration

Use the ≥3-track project threshold.

For each artist calculate:

```text
Number of qualifying projects
Average project penetration
Total projects completed
Average tracks/project
Total artist listening
```

This distinguishes:

> “I like this artist”

from:

> “I explore this artist's discography.”

Prior analysis found approximately **60 artists with 2+ qualifying projects** and around **321 qualifying projects**, but these are preliminary and should be regenerated after metadata enrichment.

---

# 18. Listening Time by Genre and Time of Day

Once artist/project metadata is enriched with genre information, analyze:

```text
Genre × Time × Year
```

Time buckets:

- 12–3 AM
- 3–6 AM
- 6–9 AM
- 9 AM–12 PM
- 12–3 PM
- 3–6 PM
- 6–9 PM
- 9 PM–12 AM

Analyze:

- Genre share
- Artist share
- Listening minutes
- Discovery rate
- Skip rate
- Repetition
- Genre migration
- Time-of-day changes across years

Important question:

> Does a change in artist represent a broader genre change, or only a change within the same genre?

---

# 19. Artist × Time-of-Day Lifecycle

For each major artist:

```text
Year
 ↓
Hour of Day
 ↓
Listening Minutes
```

Build a heatmap:

```text
           12AM  3AM  6AM  9AM  12PM  3PM  6PM  9PM
2024
2025
2026
```

This can reveal changes such as:

- An artist shifting from morning to evening
- An artist becoming more night-oriented
- An artist moving from occasional to all-day listening

---

# 20. Sessions

Define a new session after **30+ minutes of inactivity**.

For each session:

- Session ID
- Start time
- End time
- Duration
- Actual listening time
- Number of tracks
- Number of artists
- Number of projects
- Skip rate
- Discovery count
- Repetition count
- Shuffle state
- Device

Session categories:

- Short burst
- Normal session
- Long session
- Rabbit hole
- Album session
- Artist exploration session
- Discovery session

---

# 21. Music Network

Create a personal listening graph.

### Nodes

Artists.

### Edges

Repeated artist-to-artist transitions.

### Node size

Listening time or plays.

### Edge weight

Transition frequency.

Potential views:

```text
2024
2025
2026
```

This allows analysis of how the personal music ecosystem changes.

Seedhe Maut has appeared as a major hub in preliminary analysis, connecting artists such as:

- Panther
- King
- Talha Anjum
- KR$NA
- Rawal
- Naam Sujal
- Frappe Ash

Do not hard-code these relationships; regenerate them from the pipeline.

---

# 22. Music Bridges

Identify artists that connect otherwise separate listening clusters.

Potential categories:

- Indian hip-hop ↔ mainstream Indian
- Indian hip-hop ↔ Pakistani hip-hop
- Indian hip-hop ↔ international R&B/pop
- Punjabi ↔ Indian hip-hop
- Bollywood ↔ modern Indian music

Metrics:

- Betweenness centrality
- PageRank
- Cross-cluster transitions
- Discovery influence

---

# 23. Taste Fingerprint

Derive behavioral scores rather than inventing personality labels.

Potential metrics:

### Exploration
How often new artists/tracks are encountered.

### Loyalty
How concentrated listening is around core artists.

### Repetition
How often songs are replayed.

### Catalog Depth
How deeply artists/projects are explored.

### Album Affinity
Project listening vs isolated tracks.

### Discovery Retention
How often discoveries survive.

### Nostalgia
Frequency of old songs returning after long gaps.

### Selectivity
Skip and short-play behavior.

### Taste Stability
How much the listening distribution changes over time.

### Novelty Tolerance
Share of listening from recently discovered music.

---

# 24. Nostalgia Analysis

Identify tracks/artists with long inactivity gaps followed by revival.

Metrics:

- First play
- Revival date
- Maximum gap
- Number of revivals
- Listening generated after revival

Classifications:

- Evergreen
- Nostalgia revival
- Temporary revival
- Dormant

---

# 25. Failed Discovery Analysis

Identify:

```text
First encounter
     ↓
Short play / skip
     ↓
No meaningful return
```

Metrics:

- One-time tracks
- One-day tracks
- Artists with low retention
- Projects with low penetration
- Songs with high skip rates

This is the negative counterpart to Discovery Catalysts.

---

# 26. Listening Freshness

For every playback calculate:

```text
Age of song in personal history
Age of artist in personal history
Age of project in personal history
```

Then determine what percentage of listening comes from:

- Newly discovered
- 1–7 days old
- 1–4 weeks
- 1–3 months
- 3–12 months
- 1–2 years
- 2+ years

This produces a **Listening Freshness / Nostalgia Curve**.

---

# 27. Shuffle vs Intentional Listening

Use shuffle metadata to compare:

- Discovery rate
- Skip rate
- Artist diversity
- Song repetition
- Album completion
- Project sequentiality
- Session duration

Questions:

> Does shuffle produce more discoveries?

> Are favorite songs more likely to be intentionally selected?

> Are albums consumed more sequentially without shuffle?

---

# 28. Device and Playback Context

Where supported by the data:

- Device usage over time
- Offline vs online listening
- Start reasons
- End reasons
- Skip behavior by device
- Session length by device
- Discovery rate by playback context

Do not infer user intent unless supported by data.

---

# 29. Machine Learning Layer

## Flagship ML Problem

### Song → Artist/Project Discovery Prediction

Prediction target:

> Given a song and listening context, how likely is the listener to expand into the artist's catalog within 7 days?

Possible labels:

```text
0 = No meaningful expansion
1 = Artist expansion
2 = Project expansion
3 = Major catalog expansion
```

Potential features:

- Song familiarity
- Artist familiarity
- Project familiarity
- First-listen duration
- Skip status
- Time of day
- Day of week
- Session position
- Session length
- Shuffle
- Artist historical retention
- Project penetration
- Recent artist exposure
- Recent genre exposure
- Previous transitions
- Song position in project
- Discovery context

---

# 30. Secondary ML Models

### Song Retention Prediction

Predict:

```text
One-time
Short-lived
Medium-lived
Long-term
Evergreen
```

### Artist Lifecycle Prediction

Predict whether a newly discovered artist becomes:

- Temporary phase
- Regular artist
- Long-term favorite

### Project Completion Prediction

After the first few tracks:

> Will the listener explore the rest of the project?

### Next Song Prediction

Predict the next likely song/artist using recent sequence + context.

### Personalized Recommendation

Predict:

> What song is most likely to be enjoyed right now?

Context:

- Current time
- Day
- Recent sequence
- Current artist
- Current project
- Current genre
- Current listening era
- Historical affinity

---

# 31. ML Methodology

Do not begin with deep learning.

Start with:

```text
Markov / Transition Baseline
        ↓
Logistic Regression / Simple Baseline
        ↓
XGBoost / LightGBM
        ↓
Sequence Model only if justified
```

Use chronological splitting to avoid temporal leakage.

Example:

```text
Training
2022–2024

Validation
2025

Test
2026
```

Evaluate:

- Precision
- Recall
- F1
- PR-AUC / ROC-AUC where appropriate
- Calibration
- Confusion matrix
- Baseline comparison
- Feature importance
- SHAP/explainability

Do not report accuracy alone.

---

# 32. Deterministic Analytics vs ML

Keep these layers separate.

### Deterministic analytics

Explains:

> **What happened?**

Examples:

- Aa Jao was followed by Panther catalog expansion.
- DL91 FM had broad project penetration.
- A song survived across multiple years.

### ML

Predicts:

> **What is likely to happen next?**

Examples:

- Probability of project expansion
- Probability of song retention
- Likely next artist/song

---

# 33. Dashboard Structure

## Page 1 — Overview / Spotify DNA

Headline metrics:

- Total listening hours
- Total tracks
- Total artists
- Total projects
- Sessions
- Discovery rate
- Retention rate

Main visual:

**Taste Evolution Timeline**

---

## Page 2 — Artist Lifecycle

Interactive:

```text
Artist
 ↓
First discovery
 ↓
Peak
 ↓
Decline
 ↓
Revival
```

Include time-of-day heatmap.

---

## Page 3 — Albums & EPs

Filters:

- Artist
- Album
- EP
- Year
- Completion

Show:

- Tracks heard / total
- Penetration
- Listening time
- Top song
- Top-song contribution
- Sequence behavior

---

## Page 4 — Discovery Catalysts

Show:

> **Songs that changed the listening path**

Metrics:

- 7D expansion
- Projects entered
- Downstream minutes
- 30D retention
- 90D impact
- Future hours unlocked

---

## Page 5 — Song Lifecycles

Visualize:

```text
Discovery → Peak → Decline → Revival
```

Filters:

- Artist
- Project
- Year
- Lifecycle type

---

## Page 6 — Listening Sequences

Show:

- Most common song pairs
- Three-song sequences
- Album loops
- Artist transitions
- Discovery pathways

---

## Page 7 — Music Network

Interactive artist graph.

Filters:

- Year
- Genre
- Artist
- Minimum transition count

---

## Page 8 — Genre × Time × Year

Heatmap:

```text
Genre
×
Hour
×
Year
```

---

## Page 9 — Deep Dive

Select:

```text
Artist
Project
Song
```

Then show all associated history.

Example:

```text
Panther
 ├── Aa Jao
 │    ├── Discovery event
 │    ├── Projects entered
 │    └── Downstream listening
 │
 ├── Chahat
 ├── Flying Towards The City
 └── Song lifecycles
```

---

# 34. GitHub Repository Structure

```text
spotify-personal-intelligence/
│
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── ingestion/
│   ├── cleaning/
│   ├── features/
│   ├── analytics/
│   │   ├── artist_lifecycle.py
│   │   ├── song_lifecycle.py
│   │   ├── project_analysis.py
│   │   ├── discovery.py
│   │   ├── sessions.py
│   │   └── transitions.py
│   │
│   ├── ml/
│   │   ├── discovery_model.py
│   │   ├── retention_model.py
│   │   └── recommendation.py
│   │
│   └── api/
│
├── dashboard/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_artist_lifecycle.ipynb
│   ├── 03_project_analysis.ipynb
│   ├── 04_discovery_analysis.ipynb
│   └── 05_ml_experiments.ipynb
│
├── tests/
│
└── docs/
    ├── methodology.md
    ├── data_dictionary.md
    └── ml.md
```

---

# 35. Engineering Standards

The project should include:

- Reproducible pipelines
- Configuration files
- Type hints where useful
- Unit tests for feature calculations
- Data validation
- Logging
- Clear documentation
- No hard-coded analytical results
- No personal raw Spotify data committed to GitHub
- Anonymized/sample data for public demonstration
- Reproducible setup instructions
- Environment-variable based secrets/configuration

---

# 36. Privacy

The actual Spotify history contains personal behavioral data.

Therefore:

**Never commit the raw personal listening history to a public repository.**

The GitHub project should contain:

- Schema
- Synthetic/sample dataset
- Pipeline
- Code
- Screenshots
- Aggregated/anonymized results
- Documentation

Personal raw data should remain local/private.

---

# 37. Recommended Development Phases

## Phase 1 — Data Foundation

- Import Spotify history
- Clean records
- Validate timestamps
- Normalize tracks/artists/projects
- Create event IDs
- Build session IDs
- Create processed Parquet/CSV/database tables

## Phase 2 — Core Analytics

- Artist lifecycle
- Song lifecycle
- Project analytics
- Session analytics
- Skip analysis
- Time-of-day analysis
- Transition analysis

## Phase 3 — Discovery Engine

- 7-day catalyst detection
- Artist expansion
- Project expansion
- 30-day retention
- 90-day impact
- Future hours unlocked
- Discovery ranking

## Phase 4 — Metadata Enrichment

- Album/EP classification
- Genre metadata
- Track/project metadata
- Artist metadata

## Phase 5 — ML

- Feature engineering
- Baseline
- Discovery prediction
- Retention prediction
- Model evaluation
- Explainability

## Phase 6 — Dashboard

- UI
- Filters
- Artist deep dive
- Project deep dive
- Discovery visualization
- Music network
- Genre/time heatmaps

## Phase 7 — Deployment & Portfolio

- Docker
- Documentation
- Synthetic public dataset
- Screenshots
- Demo
- GitHub README
- Resume bullets
- Deployment

---

# 38. Success Criteria

The finished project should allow a visitor to answer:

### Listening

- How much music was consumed?
- When is listening highest?
- How long are sessions?

### Taste

- How has taste changed?
- Which artists are long-term?
- Which artists were temporary eras?

### Songs

- Which songs became signature tracks?
- How long does a song survive?
- Which songs were obsessions?
- Which songs were revived years later?

### Projects

- Which albums/EPs were explored deeply?
- Which projects were hit-driven?
- Which songs carry project listening?
- How often are projects consumed sequentially?
- How many artists have 2+ substantial projects explored?

### Discovery

- Which songs led to catalog expansion?
- Which songs introduced new artists?
- Which songs caused project re-entry?
- Which discoveries survived 30/90 days?
- Which songs unlocked the most future listening?

### ML

- Can the system predict catalog expansion?
- Can it predict song retention?
- How well does it perform against simple baselines?
- Which features drive predictions?

---

# 39. Portfolio Positioning

Recommended project title:

> **Spotify Personal Intelligence Engine**

Recommended subtitle:

> **Behavioral Analytics, Music Discovery Modeling & Personalized Listening Intelligence**

Short description:

> A data engineering, behavioral analytics, and machine-learning system that models how a listener discovers, explores, retains, and revisits music using Spotify Extended Streaming History.

The project should be positioned as a **personal behavioral intelligence system**, not merely a dashboard.

---

# 40. Core Product Idea

The central product philosophy:

> **Don't just show what was listened to. Explain how listening behavior evolved.**

The most distinctive feature should be:

> **Discovery Catalysts — identifying songs that are followed by meaningful expansion into an artist's catalog and measuring the downstream impact over 7, 30, and 90 days.**

The project should combine:

```text
Data
 ↓
Behavior
 ↓
Patterns
 ↓
Discovery
 ↓
Prediction
 ↓
Interactive Intelligence
```

This is the core blueprint for the Spotify Personal Intelligence Engine.
