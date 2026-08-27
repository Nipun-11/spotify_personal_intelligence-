# Spotify Personal Intelligence Engine — Full Execution Plan

## 0. Project Mission

Build a portfolio-grade **Spotify Personal Intelligence Engine** that transforms Spotify Extended Streaming History into:

1. A reliable analytical data pipeline
2. A deep behavioral analytics layer
3. A music discovery and lifecycle engine
4. An explainable machine-learning system
5. A polished interactive dashboard
6. A professional GitHub portfolio project

### Central research question

> **How does a listener's musical taste actually develop over time?**

The project should explain not only **what was listened to**, but:

- how songs are discovered
- how songs survive or disappear
- how artists enter and leave listening patterns
- how one song leads to deeper catalog exploration
- how albums and EPs are consumed
- how listening changes by time of day
- how music networks evolve
- whether future listening behavior can be predicted

---

# 1. Non-Negotiable Analytical Rules

These definitions must remain consistent across the project.

## 1.1 Project exploration threshold

A project qualifies as **explored** when:

> **At least 3 unique tracks from that project were played.**

Reason: some EPs contain only 3 tracks.

Do NOT revert to the previous 4-track threshold.

### Examples

```text
3-track EP
3 tracks heard
= 100% completion
```

```text
20-track album
3 tracks heard
= explored
= 15% penetration
```

Exploration and completion are different metrics.

---

## 1.2 Discovery window

Discovery analysis uses:

> **7 days**

Do not require an immediate next-song transition.

A song may be considered a potential catalyst when meaningful artist/project expansion happens during the following 7 days.

---

## 1.3 Retention windows

Use:

- 7-day expansion
- 30-day retention
- 90-day impact

Potentially add 180-day/1-year analysis for long-term lifecycle work.

---

## 1.4 Causality language

Listening chronology does not prove causality.

Do not say:

> Song A caused Song B.

Prefer:

- discovery pathway
- catalog expansion
- catalyst signal
- re-engagement
- project re-entry
- downstream listening
- followed by

---

## 1.5 Discovery categories

Every relevant event should be classified as one of:

### Artist Discovery

First meaningful exposure to an artist.

### Project Discovery

A new album/EP/project from an already-known artist.

### Catalog Deepening

A song is followed by deeper exploration of an artist's existing catalog.

### Re-engagement

An artist/project that had become inactive returns to listening after a new exposure.

---

# 2. Development Strategy

Build in this order:

```text
Phase 0
Project setup
      ↓
Phase 1
Data ingestion + validation
      ↓
Phase 2
Canonical data model
      ↓
Phase 3
Feature engineering
      ↓
Phase 4
Core analytics
      ↓
Phase 5
Discovery engine
      ↓
Phase 6
Metadata enrichment
      ↓
Phase 7
ML datasets
      ↓
Phase 8
ML models
      ↓
Phase 9
Backend/API
      ↓
Phase 10
Dashboard
      ↓
Phase 11
Testing + performance
      ↓
Phase 12
Deployment + GitHub
      ↓
Phase 13
Portfolio presentation
```

Do not start with dashboard UI.

The data model and feature layer must come first.

---

# 3. Phase 0 — Repository & Environment Setup

## Objectives

Create a professional repository before analysis becomes large.

### Tasks

- Initialize Git repository
- Create Python environment
- Add dependency management
- Add `.gitignore`
- Add environment configuration
- Add project README
- Add license
- Add initial documentation
- Create directory structure
- Add pre-commit configuration if useful
- Add basic CI workflow

### Repository

```text
spotify-personal-intelligence/
```

### Initial structure

```text
spotify-personal-intelligence/
│
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── .env.example
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── sample/
│
├── src/
│   ├── ingestion/
│   ├── cleaning/
│   ├── validation/
│   ├── features/
│   ├── analytics/
│   ├── discovery/
│   ├── metadata/
│   ├── ml/
│   └── api/
│
├── dashboard/
│
├── notebooks/
│
├── tests/
│
├── docs/
│
└── scripts/
```

### Definition of done

- Repository runs locally
- Environment installs successfully
- Basic test passes
- No personal Spotify data is committed

---

# 4. Phase 1 — Raw Data Ingestion

## Goal

Create a reproducible ingestion pipeline.

### Inputs

Spotify Extended Streaming History JSON files.

### Tasks

1. Discover all raw files
2. Load JSON
3. Normalize schema
4. Concatenate history
5. Preserve original raw files locally
6. Record source filename
7. Validate required fields
8. Save normalized intermediate dataset

### Required fields

At minimum:

```text
timestamp
track
artist
album/project
ms_played
track_uri
```

Additional fields should be retained when available:

```text
reason_start
reason_end
shuffle
platform/device
offline
skipped
```

### Data quality checks

- Missing timestamps
- Missing track names
- Missing artists
- Missing project names
- Duplicate records
- Invalid playback durations
- Impossible timestamps
- Zero-duration records
- Negative durations
- Encoding problems
- Time-zone consistency

### Deliverables

```text
src/ingestion/
src/validation/
tests/test_ingestion.py
docs/data_dictionary.md
```

---

# 5. Phase 2 — Canonical Data Model

Create a stable analytical representation.

## Playback Event

One row per playback event.

Suggested schema:

```text
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

ms_played
track_duration_ms
play_ratio
skipped

start_reason
end_reason
shuffle
device
offline

session_id
session_position
```

### Identity normalization

Create canonical identifiers for:

- track
- artist
- project

Handle:

- punctuation
- capitalization
- Unicode
- alternate artist strings
- featured artist naming where appropriate

Do not over-normalize names if it causes different entities to merge incorrectly.

---

# 6. Phase 3 — Sessionization

Default session boundary:

> **30 minutes of inactivity**

### Session features

```text
session_id
session_start
session_end
session_duration
listening_duration
track_count
unique_tracks
unique_artists
unique_projects
skip_count
skip_rate
discovery_count
repetition_count
shuffle_rate
```

### Session classifications

- Short burst
- Normal session
- Long session
- Rabbit hole
- Album session
- Artist exploration session
- Discovery session

### Validation

Manually inspect a sample of sessions to make sure 30 minutes produces sensible boundaries.

---

# 7. Phase 4 — Core Feature Engineering

Create reusable features instead of calculating them separately inside dashboards.

## 7.1 Song history features

For every event:

```text
song_first_seen
song_last_seen
song_play_count_before
song_unique_days_before
song_unique_months_before
song_age_days
is_first_song_play
is_new_song
```

---

## 7.2 Artist history features

```text
artist_first_seen
artist_play_count_before
artist_unique_tracks_before
artist_unique_projects_before
artist_age_days
is_new_artist
is_recent_artist
```

---

## 7.3 Project history features

```text
project_first_seen
project_play_count_before
project_tracks_heard_before
project_age_days
is_new_project
is_recent_project
```

---

## 7.4 Temporal features

```text
hour
day_of_week
weekend
month
quarter
year
season
hour_bucket
```

---

## 7.5 Sequence features

```text
previous_track
previous_artist
previous_project
next_track
next_artist
next_project
same_artist_as_previous
same_project_as_previous
```

---

## 7.6 Listening intensity

```text
play_ratio
full_play
short_play
skip
repeat_within_24h
repeat_within_7d
```

---

# 8. Phase 5 — Metadata Enrichment

The Spotify history should remain the behavioral source of truth.

Enrich it separately.

## Project metadata

Obtain reliable release information where available:

- album
- EP
- single
- compilation
- soundtrack
- release date
- track count

## Genre metadata

Build artist/genre mappings.

Potential genre families:

```text
Indian Hip-Hop
Pakistani Hip-Hop
Punjabi
Bollywood / Indian Film
Indian Indie
International Hip-Hop
R&B / Soul
Pop
Electronic
Rock
Other
```

Keep the raw metadata and a normalized genre-family layer.

### Important

Do not assume a project is an album or EP purely from its name.

---

# 9. Phase 6 — Project Intelligence

Apply the permanent rule:

> **≥3 unique tracks heard = explored project**

## Metrics

For each project:

```text
tracks_available
tracks_heard
penetration
total_plays
total_minutes
average_plays_per_track
first_heard
last_heard
active_days
active_months
```

### Completion categories

```text
0–24%      Sampled
25–49%     Partial
50–74%     Deep
75–99%     Near Complete
100%       Complete
```

For very small projects, also report absolute track counts.

---

## 9.1 Project listening style

Classify:

### Hit-driven

Small number of tracks dominate listening.

### Partial exploration

Several tracks heard, but project incomplete.

### Deep exploration

Large percentage of project heard.

### Full-project consumption

Most/all tracks heard.

---

## 9.2 Project-driving songs

Calculate:

```text
song_minutes / total_project_minutes
```

Rank songs by project contribution.

Also calculate:

```text
song_plays / total_project_plays
```

This identifies projects where one song drives listening versus projects consumed broadly.

---

# 10. Phase 7 — Artist Lifecycle Engine

For each artist:

```text
Discovery
   ↓
Exploration
   ↓
Growth
   ↓
Peak
   ↓
Decline
   ↓
Dormancy
   ↓
Re-engagement / Revival
```

## Metrics

- First heard
- First meaningful exploration
- Peak month
- Peak year
- Total plays
- Total hours
- Unique tracks
- Unique projects
- Active days
- Active months
- Longest gap
- Number of revivals
- Current activity

### Lifecycle classification

Create deterministic rules first.

Do not use ML until a reliable rule-based label exists.

---

# 11. Phase 8 — Song Lifecycle Engine

Classify songs into:

```text
New Discovery
Trial
Failed Discovery
Repeat
Obsession
Rotation
Declining
Evergreen
Revival
Dormant
```

## Metrics

- First play
- Last play
- Total plays
- Total minutes
- Active days
- First 24h plays
- First 7d plays
- 30d retention
- 90d retention
- Maximum inactivity gap
- Replay rate
- Skip rate

### Important distinction

Calculate both:

**Raw lifespan**

```text
last_play - first_play
```

and

**Active lifespan**

A measure based on actual periods of continued activity.

---

# 12. Phase 9 — Discovery Catalyst Engine

This is the flagship analytics system.

## Goal

Identify songs that are followed by meaningful expansion into the artist's wider catalog.

### Event definition

For each relevant song exposure:

1. Identify catalyst timestamp.
2. Examine following 7 days.
3. Determine whether additional artist tracks were played.
4. Determine whether additional projects were entered.
5. Count downstream minutes.
6. Measure 30-day retention.
7. Measure 90-day impact.

---

## 12.1 Artist Discovery

A meaningful first exposure to an artist followed by additional exploration.

Possible rule:

```text
artist was not meaningfully present before catalyst
AND
additional artist activity occurs within 7d
```

---

## 12.2 Project Discovery

Known artist + new project entered.

```text
artist known
AND
project not recently active
AND
project exploration follows catalyst
```

---

## 12.3 Catalog Deepening

Known artist + meaningful expansion into additional tracks/projects.

---

## 12.4 Re-engagement

Previously inactive artist/project returns after catalyst.

---

# 13. Discovery Metrics

For every catalyst:

```text
catalyst_track
catalyst_artist
catalyst_project
catalyst_timestamp

tracks_added_7d
projects_added_7d
artist_minutes_7d
artist_plays_7d

minutes_30d
minutes_90d
tracks_30d
tracks_90d
projects_30d
projects_90d

retention_30d
retention_90d

future_hours_unlocked
```

### Catalyst score

Create an explainable composite score.

Possible components:

```text
7D expansion
30D retention
90D impact
project depth
future hours unlocked
```

Do not hide the underlying metrics.

---

# 14. Discovery Example Validation

Explicitly test the framework against known examples.

## Panther

```text
Aa Jao
   ↓
Panther catalog exploration
   ↓
Chahat / Flying Towards The City
```

The output should identify this as a strong catalog-expansion/re-entry signal if the data confirms it.

## Frappe Ash

```text
Ice Cream Frappe
   ↓
Frappe Ash catalog
   ↓
Junkie
```

Because Frappe Ash was already known, classify as:

> Catalog Deepening / Re-engagement

not first-ever artist discovery.

---

# 15. Phase 10 — Listening Sequences

Analyze transitions at multiple levels.

## Song → Song

```text
A → B
```

## Artist → Artist

```text
Artist A → Artist B
```

## Project → Project

```text
Project A → Project B
```

## Discovery transition

```text
A → B
B is previously unplayed/new
```

### Metrics

- transition count
- transition probability
- conditional probability
- repeated transitions
- transition recency
- artist bridge strength

---

# 16. Phase 11 — Music Network

Build graph representations.

## Artist network

Nodes:

> Artists

Edges:

> Listening transitions / repeated pathways

Node size:

> Listening time

Edge weight:

> Transition frequency

### Graph metrics

- Degree
- Weighted degree
- Betweenness centrality
- PageRank
- Community detection

### Views

- All time
- Year
- Month
- Genre
- Minimum transition threshold

---

# 17. Phase 12 — Genre × Time × Year

Build a three-dimensional behavioral analysis.

## Time buckets

```text
12–3 AM
3–6 AM
6–9 AM
9 AM–12 PM
12–3 PM
3–6 PM
6–9 PM
9 PM–12 AM
```

## Analyze

- genre share
- listening minutes
- artist share
- discovery rate
- skip rate
- repetition
- genre migration
- yearly changes

Primary question:

> What genre dominates at different times of day, and how has that changed over the years?

---

# 18. Phase 13 — Artist × Time-of-Day Lifecycle

For each major artist:

```text
Year × Hour
```

Visualize as a heatmap.

Questions:

- When did the artist become important?
- What time of day is the artist associated with?
- Did the artist's time-of-day identity change?
- Did the artist move from morning to evening?
- Is the shift artist-specific or part of a broader genre shift?

---

# 19. Phase 14 — Taste Fingerprint

Build behavioral scores.

## Exploration Score

New artists/tracks/projects relative to total listening.

## Loyalty Score

Concentration around core artists.

## Repetition Score

Repeat behavior.

## Catalog Depth Score

Depth across artist projects.

## Album Affinity

Project-based listening vs isolated tracks.

## Discovery Retention

Percentage of discoveries that survive.

## Nostalgia Score

Long-gap re-engagement.

## Selectivity Score

Skip/short-play behavior.

## Taste Stability

Distribution change over time.

## Novelty Tolerance

Share of recent discoveries.

Use actual metrics underneath every score.

---

# 20. Phase 15 — Failed Discovery Analysis

Identify:

```text
New exposure
   ↓
Short play / skip
   ↓
No meaningful return
```

Calculate:

- one-time songs
- one-day songs
- low-retention artists
- low-retention projects
- high-skip artists/projects
- high-skip genres

Compare failed discoveries with successful discoveries.

This creates a useful contrast for ML.

---

# 21. Phase 16 — Nostalgia & Revival

Identify:

```text
Active
 ↓
Long inactivity
 ↓
Return
```

Metrics:

- gap duration
- revival count
- post-revival listening
- revival duration
- revival intensity

Questions:

> Which artists come back?

> Which songs survive years?

> What tends to trigger a revival?

---

# 22. Phase 17 — Freshness / Music Age

For every play:

```text
song_age_in_personal_history
artist_age_in_personal_history
project_age_in_personal_history
```

Create listening-age buckets:

```text
< 7 days
7–30 days
1–3 months
3–12 months
1–2 years
2+ years
```

Calculate the monthly/annual freshness curve.

---

# 23. Phase 18 — Shuffle & Playback Context

Compare:

```text
shuffle
vs
non-shuffle
```

Metrics:

- discovery rate
- skip rate
- artist diversity
- song repetition
- project completion
- sequentiality
- session duration

Also analyze:

- device
- offline status
- start reason
- end reason

Do not infer user intent without evidence.

---

# 24. Phase 19 — ML Dataset Construction

Create supervised examples from historical data.

## Flagship target

### Song → Artist/Project Expansion Prediction

Input:

> A song exposure + context

Target:

> Whether meaningful catalog expansion occurs within 7 days.

Possible labels:

```text
0 = No meaningful expansion
1 = Artist expansion
2 = Project expansion
3 = Major catalog expansion
```

Alternative binary target can be used for the first model:

```text
0 = no expansion
1 = meaningful expansion
```

Start simple.

---

# 25. ML Feature Set

Potential features:

### Song

- previous play count
- song age
- first-listen duration
- skip
- replay within 24h
- replay within 7d

### Artist

- prior artist plays
- artist familiarity
- artist catalog depth
- prior retention
- prior project count

### Project

- project familiarity
- project penetration
- project size
- project release age

### Context

- hour
- day
- weekday/weekend
- session position
- session length
- shuffle
- device

### Sequence

- previous artist
- previous project
- previous song
- transition probability

### Discovery

- first-time artist
- first-time project
- recent artist exposure
- recent genre exposure

---

# 26. ML Training Strategy

Never randomly split the complete history if future information can leak backward.

Use chronological splitting.

Example:

```text
Train
2022–2024

Validation
2025

Test
2026
```

Adjust based on actual dataset coverage.

---

# 27. ML Model Progression

## Baseline 1

No-expansion majority-class baseline.

## Baseline 2

Transition probability / Markov model.

## Baseline 3

Logistic regression.

## Main model

XGBoost or LightGBM.

## Advanced model

Only if justified:

- sequence model
- recurrent neural network
- transformer

Do not use deep learning simply because it sounds impressive.

---

# 28. ML Evaluation

Report:

- Precision
- Recall
- F1
- PR-AUC
- ROC-AUC where appropriate
- Calibration
- Confusion matrix
- Baseline comparison

Also include:

- feature importance
- SHAP explanations
- error analysis

### Required question

> When the model is wrong, what kind of listening behavior is it failing to understand?

This is more valuable than a single accuracy number.

---

# 29. Secondary ML Models

After the flagship model:

## Song Retention

Predict:

```text
One-time
Short-lived
Medium-lived
Long-term
Evergreen
```

## Project Completion

Predict whether a project will be deeply explored after initial exposure.

## Artist Lifecycle

Predict whether an artist will become a sustained listener favorite.

## Next Song

Predict the next likely track/artist.

## Recommendation

Predict which songs are likely to fit the current listening context.

---

# 30. Recommendation System

Build this last.

The recommendation system should use:

- current time
- day
- recent songs
- current artist
- current project
- recent genres
- historical affinity
- current taste era
- song freshness
- skip behavior
- discovery state

The goal is:

> **What song is most likely to fit this listener right now?**

Not merely:

> What songs are similar?

---

# 31. Backend/API

Build a lightweight API once analytical tables are stable.

Possible endpoints:

```text
GET /overview
GET /artists
GET /artists/{artist}
GET /artists/{artist}/lifecycle
GET /artists/{artist}/projects
GET /songs
GET /songs/{song}
GET /songs/{song}/lifecycle
GET /projects
GET /projects/{project}
GET /discovery/catalysts
GET /discovery/{song}
GET /network
GET /genres/time
GET /ml/discovery
```

Keep API logic separate from analytical computation.

---

# 32. Dashboard

Recommended stack:

```text
Frontend
React / Next.js

Visualization
Plotly / D3.js

Backend
FastAPI

Database
PostgreSQL

Analytics
Python

ML
scikit-learn + XGBoost/LightGBM
```

A simpler stack is acceptable if it produces a better result.

---

# 33. Dashboard Pages

## 33.1 Overview — Spotify DNA

Show:

- total hours
- tracks
- artists
- projects
- sessions
- discovery rate
- retention
- catalog depth

Hero visualization:

> Taste Evolution Timeline

---

## 33.2 Artist Lifecycle

Interactive artist selection.

Show:

```text
Discovery → Growth → Peak → Decline → Revival
```

Include:

- listening volume
- unique tracks
- projects
- time-of-day heatmap

---

## 33.3 Albums & EPs

Filters:

- artist
- project
- release type
- year
- completion

Show:

- penetration
- listening time
- top song
- top-song share
- sequence behavior

---

## 33.4 Discovery Catalysts

Main view:

> Songs that changed the listening path

Columns:

```text
Catalyst
Artist
7D tracks
7D projects
7D minutes
30D retention
90D impact
Future hours
```

---

## 33.5 Song Lifecycles

Show:

```text
Discovery → Peak → Decline → Revival
```

---

## 33.6 Listening Sequences

Show:

- top song pairs
- top 3-song sequences
- artist transitions
- project transitions
- discovery pathways

---

## 33.7 Music Network

Interactive graph.

Filters:

- year
- genre
- artist
- minimum transition count

---

## 33.8 Genre × Time × Year

Heatmaps and trend charts.

---

## 33.9 Deep Dive

Single interface for:

```text
Artist
Project
Song
```

Example:

```text
Panther
  ↓
Aa Jao
  ↓
Discovery event
  ↓
Projects entered
  ↓
Track expansion
  ↓
30/90-day impact
```

---

## 33.10 ML Intelligence

Show:

- prediction
- probability
- model explanation
- important features
- prediction history
- model performance

Example:

```text
Song: Example Song

Probability of catalog expansion:
82%

Likely outcome:
Project exploration

Main drivers:
+ Strong artist-transition history
+ High project affinity
+ High historical retention
```

---

# 34. UX Principles

Do not build a dashboard containing dozens of unrelated charts.

Every visualization must answer a question.

Examples:

> Which songs changed listening behavior?

> Which artists were explored deeply?

> How long do songs survive?

> Which projects were actually consumed?

> What genres dominate at different times?

> How does artist behavior change over time?

> Can future exploration be predicted?

Use progressive disclosure:

```text
Overview
  ↓
Interesting pattern
  ↓
Click
  ↓
Deep dive
  ↓
Raw supporting evidence
```

---

# 35. Testing Strategy

## Unit tests

Test:

- sessionization
- project penetration
- lifecycle labels
- discovery windows
- retention calculations
- transition probabilities
- feature calculations

## Data tests

Validate:

- schema
- null rates
- duplicates
- timestamp range
- duration ranges
- unique IDs

## ML tests

Test:

- target generation
- temporal split
- feature leakage
- reproducibility
- prediction schema

## UI tests

At least smoke-test:

- dashboard loads
- filters work
- artist deep dive works
- project deep dive works
- discovery view works

---

# 36. Data Leakage Prevention

This is critical.

A feature used to predict an outcome at time `T` must not contain information from after `T`.

For example:

Bad:

```text
artist_total_plays
```

when calculated using the complete future dataset.

Good:

```text
artist_plays_before_catalyst
```

Similarly:

Bad:

```text
project_total_future_minutes
```

Good:

```text
project_minutes_before_catalyst
```

Every ML feature must have a clear temporal definition.

---

# 37. Reproducibility

A fresh environment should be able to run:

```text
raw data
   ↓
pipeline
   ↓
processed data
   ↓
features
   ↓
analytics
   ↓
ML
   ↓
dashboard
```

Use:

- deterministic seeds
- configuration files
- documented commands
- versioned schemas
- fixed feature definitions

---

# 38. Privacy & GitHub

Never publish personal raw Spotify history.

Public repository should contain:

```text
Code
Documentation
Synthetic/sample data
Aggregated/anonymized outputs
Screenshots
Model artifacts where safe
```

Personal data remains local/private.

Provide a sample dataset that allows the pipeline to run.

---

# 39. Performance Plan

Start with local Parquet/Pandas or Polars.

If analytical complexity grows:

```text
Parquet
   ↓
DuckDB
   ↓
PostgreSQL
```

Use PostgreSQL primarily for application serving rather than forcing all experimentation into the database.

Cache expensive:

- network calculations
- discovery calculations
- lifecycle calculations
- ML predictions

---

# 40. Documentation Plan

Create:

```text
docs/
├── architecture.md
├── data_dictionary.md
├── methodology.md
├── discovery_methodology.md
├── lifecycle_methodology.md
├── ml.md
├── model_card.md
├── privacy.md
└── dashboard.md
```

Each methodology document should explain:

- definition
- formula
- assumptions
- limitations
- example
- implementation location

---

# 41. GitHub README Plan

README structure:

```text
1. Project title
2. One-line description
3. Demo / screenshots
4. Why this project exists
5. Research questions
6. Architecture
7. Key features
8. Discovery Catalyst concept
9. ML approach
10. Results
11. Tech stack
12. Repository structure
13. How to run
14. Privacy
15. Limitations
16. Future work
```

Strong opening:

> **Spotify Personal Intelligence Engine**
>
> A behavioral analytics and machine-learning system that models how a listener discovers, explores, retains, and revisits music using Spotify Extended Streaming History.

---

# 42. Portfolio Story

The project should tell a coherent story:

```text
Problem
How does music taste evolve?

Data
Spotify Extended Streaming History

Challenge
Raw playback events do not directly represent discovery or preference.

Solution
Feature engineering + lifecycle modeling + discovery pathways.

Insight
Songs can act as catalysts for wider catalog exploration.

ML
Predict whether a song will lead to catalog expansion.

Product
Interactive dashboard that explains personal music behavior.
```

---

# 43. Resume Positioning

Potential final resume bullets:

> **Spotify Personal Intelligence Engine | Python, XGBoost, FastAPI, React, PostgreSQL**

> • Engineered a behavioral analytics pipeline processing **32K+ Spotify playback events**, modeling artist lifecycles, song longevity, project exploration, sessions, and listening transitions.

> • Developed a **7-day discovery-catalyst framework** quantifying how individual songs are followed by expansion into an artist's wider catalog, with 30/90-day retention analysis.

> • Built a temporal ML pipeline predicting **artist/project catalog expansion following song exposure**, using chronological train/validation/test splits to prevent temporal leakage.

> • Designed an interactive dashboard visualizing **music discovery networks, album/EP penetration, song lifecycles, genre-time patterns, and artist evolution**.

Final numbers must be generated from the production pipeline.

---

# 44. Milestone Checklist

## Milestone 1 — Data Foundation

- [ ] Repository created
- [ ] Environment configured
- [ ] Raw ingestion works
- [ ] Schema validated
- [ ] Canonical event table created
- [ ] Tests added

## Milestone 2 — Feature Layer

- [ ] Sessions
- [ ] Song history
- [ ] Artist history
- [ ] Project history
- [ ] Temporal features
- [ ] Sequence features

## Milestone 3 — Core Analytics

- [ ] Artist lifecycle
- [ ] Song lifecycle
- [ ] Project intelligence
- [ ] Skip analysis
- [ ] Session analysis
- [ ] Time-of-day analysis

## Milestone 4 — Discovery Engine

- [ ] 7D catalyst detection
- [ ] Artist discovery
- [ ] Project discovery
- [ ] Catalog deepening
- [ ] Re-engagement
- [ ] 30D retention
- [ ] 90D impact
- [ ] Future hours unlocked
- [ ] Catalyst ranking

## Milestone 5 — Metadata

- [ ] Album/EP classification
- [ ] Genre enrichment
- [ ] Metadata validation

## Milestone 6 — Network

- [ ] Song transitions
- [ ] Artist transitions
- [ ] Project transitions
- [ ] Artist graph
- [ ] Community detection

## Milestone 7 — ML

- [ ] Target generation
- [ ] Leakage audit
- [ ] Temporal split
- [ ] Baselines
- [ ] XGBoost/LightGBM
- [ ] Evaluation
- [ ] SHAP
- [ ] Error analysis

## Milestone 8 — Product

- [ ] API
- [ ] Dashboard
- [ ] Filters
- [ ] Deep dive
- [ ] Discovery view
- [ ] Network view
- [ ] ML view

## Milestone 9 — Production Quality

- [ ] Unit tests
- [ ] Data tests
- [ ] API tests
- [ ] UI smoke tests
- [ ] Performance optimization
- [ ] Docker
- [ ] CI

## Milestone 10 — Portfolio

- [ ] Public sample dataset
- [ ] Screenshots
- [ ] README
- [ ] Methodology docs
- [ ] Model card
- [ ] Demo
- [ ] Resume bullets
- [ ] GitHub cleanup

---

# 45. Suggested Work Order for Actual Development

Do not attempt all features simultaneously.

The recommended sequence is:

### Step 1

**Build the canonical playback table.**

### Step 2

**Build sessions and historical features.**

### Step 3

**Build project intelligence using the ≥3-track rule.**

### Step 4

**Build artist and song lifecycle engines.**

### Step 5

**Build the 7-day discovery-catalyst engine.**

### Step 6

**Validate Panther “Aa Jao” and Frappe Ash examples.**

### Step 7

**Run the catalyst analysis across the entire history.**

### Step 8

**Build genre/time and artist/time analysis.**

### Step 9

**Build music-network analysis.**

### Step 10

**Create the ML training dataset with strict temporal features.**

### Step 11

**Train baseline → logistic regression → XGBoost/LightGBM.**

### Step 12

**Perform model evaluation and error analysis.**

### Step 13

**Build backend/API.**

### Step 14

**Build dashboard.**

### Step 15

**Add deployment, tests, documentation, and GitHub polish.**

---

# 46. Definition of a Finished Project

The project is finished when:

### Data

A reproducible pipeline transforms raw Spotify history into validated analytical tables.

### Analytics

The system can explain:

- artist lifecycles
- song lifecycles
- project depth
- project-driving songs
- listening sessions
- sequences
- discovery pathways
- genre/time behavior
- music-network structure

### Discovery

The system can identify and rank:

> **Songs that are followed by meaningful catalog expansion.**

### ML

The system can predict:

> **Whether a song exposure will lead to artist/project expansion within 7 days.**

with proper temporal evaluation.

### Product

A polished dashboard lets a user move from:

```text
Overview
 → Artist
 → Project
 → Song
 → Discovery event
 → Listening pathway
 → Long-term impact
```

### Portfolio

The repository is:

- reproducible
- documented
- tested
- privacy-safe
- visually polished
- technically defensible
- easy for a recruiter to understand

---

# 47. Future Extensions

Only after the core system works:

- personalized real-time recommendation
- contextual bandits
- sequence transformers
- taste-state Hidden Markov Model
- automatic playlist generation
- counterfactual discovery analysis
- “what changed my taste?” detection
- music recommendation explanation engine
- multi-user comparison using synthetic/public datasets
- streaming/real-time recommendation API

These are optional.

Do not sacrifice the quality of the core system to add advanced models.

---

# 48. Guiding Principle

The project should always follow this progression:

> **Observe → Measure → Explain → Predict**

### Observe

What happened?

### Measure

How strongly did it happen?

### Explain

What behavioral pattern describes it?

### Predict

What is likely to happen next?

The most important product insight remains:

> **Don't just show what was listened to. Explain how listening behavior evolved.**

And the most distinctive analytical feature remains:

> **Discovery Catalysts — identifying songs that are followed by meaningful expansion into an artist's catalog and measuring the downstream impact over 7, 30, and 90 days.**
