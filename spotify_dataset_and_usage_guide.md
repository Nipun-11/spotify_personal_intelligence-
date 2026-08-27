# Spotify Personal Intelligence Engine — Dataset Guide

## 1. Purpose

This document defines the **actual Spotify dataset currently available for the project**, how it should be stored, what each field means, how it should be transformed, and how the resulting data will power analytics and machine learning.

The central principle is:

> **Raw Spotify JSON is the source of truth. It is not the format that the entire application should use directly.**

The project will preserve the original JSON, transform it into clean analytical tables, and use those tables for analytics, ML, and the dashboard.

---

# 2. Dataset Currently Available

The current Spotify export contains **Spotify Extended Streaming History**.

### Audio history

Files:

```text
Streaming_History_Audio_2020.json
Streaming_History_Audio_2021.json
Streaming_History_Audio_2022.json
Streaming_History_Audio_2023.json
Streaming_History_Audio_2024.json
Streaming_History_Audio_2025.json
Streaming_History_Audio_2026.json
```

### Current audio dataset statistics

| Metric | Value |
|---|---:|
| Audio JSON files | 7 |
| Playback/event records | **32,297** |
| Distinct tracks | **6,830** |
| Distinct artists | **1,787** |
| Distinct album/project names | **4,294** |
| Total recorded playback time | **~908.4 hours** |
| First event | **2020-05-29 05:33:26 UTC** |
| Last event | **2026-08-20 13:31:07 UTC** |
| Skipped events | **18,725** |
| Shuffle events | **11,415** |
| Offline events | **59** |

There are also **399 video-history records** spanning 2023–2026. These should be retained separately unless the project later decides that video consumption belongs in the main listening model.

### Important

The statistics above are generated from the current files and should **not be hard-coded into production code**. The pipeline should recalculate them whenever new Spotify data is imported.

---

# 3. Raw Dataset Structure

The raw project storage should look like:

```text
data/
└── raw/
    └── spotify/
        └── extended_streaming_history/
            ├── Streaming_History_Audio_2020.json
            ├── Streaming_History_Audio_2021.json
            ├── Streaming_History_Audio_2022.json
            ├── Streaming_History_Audio_2023.json
            ├── Streaming_History_Audio_2024.json
            ├── Streaming_History_Audio_2025.json
            └── Streaming_History_Audio_2026.json
```

The raw files should be treated as **immutable**.

Never edit them to fix data-quality issues.

Instead:

```text
Raw
 ↓
Cleaning
 ↓
Processed
```

---

# 4. Raw JSON Schema

A representative audio-history record looks like:

```json
{
  "ts": "2020-05-29T05:33:26Z",
  "platform": "Android OS 7.0 API 24 (Xiaomi, Redmi Note 4)",
  "ms_played": 16240,
  "conn_country": "IN",
  "ip_addr": "...",
  "master_metadata_track_name": "Old Skool",
  "master_metadata_album_artist_name": "Sidhu Moose Wala",
  "master_metadata_album_album_name": "Old Skool",
  "spotify_track_uri": "spotify:track:1pZbjOj49hg04l9VBO97hp",
  "episode_name": null,
  "episode_show_name": null,
  "spotify_episode_uri": null,
  "audiobook_title": null,
  "audiobook_uri": null,
  "audiobook_chapter_uri": null,
  "audiobook_chapter_title": null,
  "reason_start": "clickrow",
  "reason_end": "remote",
  "shuffle": false,
  "skipped": false,
  "offline": false,
  "offline_timestamp": null,
  "incognito_mode": false
}
```

---

# 5. Raw Field Dictionary

## `ts`

Timestamp of the playback event.

Example:

```text
2020-05-29T05:33:26Z
```

### Use

This is one of the most important fields.

It powers:

- date analysis
- year/month analysis
- day-of-week analysis
- hour-of-day analysis
- sessions
- song lifecycle
- artist lifecycle
- discovery windows
- retention
- sequence analysis
- ML temporal features

Store the raw UTC timestamp and create a normalized analysis timestamp separately.

---

## `platform`

Device/platform information.

Example:

```text
Android OS 7.0 API 24 (Xiaomi, Redmi Note 4)
```

### Use

Can power:

- device evolution
- device-level skip behavior
- device-level listening time
- session behavior

Do not unnecessarily expose detailed device identifiers in public visualizations.

---

## `ms_played`

Milliseconds played during the event.

Example:

```text
16240
```

Convert to:

```text
seconds
minutes
hours
```

### Use

This is the primary listening-intensity measure.

Do not treat every playback event as a complete play.

A 5-second event and a 4-minute event are behaviorally different.

---

## `conn_country`

Country associated with the connection.

Current data contains `IN` in the inspected records.

### Use

Potentially useful for:

- geography analysis
- data validation
- travel/context analysis

This should not be unnecessarily surfaced in the public dashboard.

---

## `ip_addr`

IP address associated with the event.

### Important privacy rule

**Do not use raw IP addresses in the analytical dashboard or public GitHub repository.**

Prefer:

- discard after validation
- hash if absolutely required for a private analysis
- aggregate to a safe geographic level if needed

For this project, IP is not required for the core analysis.

---

## `master_metadata_track_name`

Track title.

Example:

```text
Old Skool
```

### Use

Primary song identifier when combined with `spotify_track_uri`.

---

## `master_metadata_album_artist_name`

Artist associated with the track.

Example:

```text
Sidhu Moose Wala
```

### Use

Powers:

- artist lifecycle
- artist popularity
- artist transitions
- artist discovery
- artist catalog depth
- artist time-of-day analysis
- music network

---

## `master_metadata_album_album_name`

Album/project name.

Example:

```text
Old Skool
```

### Use

Powers:

- album/EP exploration
- project penetration
- project completion
- project-driving songs
- project lifecycle

This field alone cannot reliably distinguish Album vs EP vs Single.

That requires metadata enrichment.

---

## `spotify_track_uri`

Spotify track URI.

Example:

```text
spotify:track:1pZbjOj49hg04l9VBO97hp
```

### Use

Preferred stable track identifier.

Extract the Spotify ID:

```text
1pZbjOj49hg04l9VBO97hp
```

Use the ID as the canonical `track_id` when possible.

---

# 6. Podcast / Episode Fields

The same audio-history structure can contain podcast episodes.

Fields:

```text
episode_name
episode_show_name
spotify_episode_uri
```

The current audio dataset contains **32 records with episode fields populated**.

These should be separated from music records.

Create:

```text
content_type = music
content_type = podcast
```

Do not mix podcast events into music-specific metrics such as:

- album completion
- artist lifecycle
- song lifespan
- music discovery catalysts

unless explicitly intended.

---

# 7. Audiobook Fields

Fields:

```text
audiobook_title
audiobook_uri
audiobook_chapter_uri
audiobook_chapter_title
```

The current audio records inspected contain no populated audiobook fields.

Still preserve the fields during ingestion because future exports could contain audiobook activity.

---

# 8. Playback Reason Fields

## `reason_start`

Why playback started.

Examples can include:

```text
clickrow
```

Potential values should be profiled from the actual dataset rather than hard-coded.

### Use

Useful for:

- intentional vs recommendation-like starts
- session behavior
- discovery analysis
- shuffle analysis

---

## `reason_end`

Why playback ended.

Potential values can include:

- track finished
- forward
- remote action
- logout/session ending
- other Spotify playback events

Exact categories should be derived from observed values.

### Use

Useful for:

- skip behavior
- completion behavior
- listening interruption
- session analysis

---

# 9. `shuffle`

Boolean.

```text
true / false
```

### Use

Compare:

```text
Shuffle
vs
Non-shuffle
```

Metrics:

- discovery rate
- skip rate
- artist diversity
- repetition
- project sequentiality
- session duration
- project completion

---

# 10. `skipped`

Boolean.

Current dataset:

```text
18,725 skipped events
```

This field is useful, but **must not automatically be interpreted as dislike**.

A skip can mean:

- intentional rejection
- context change
- interruption
- navigation
- accidental interaction

Use it as a behavioral signal.

---

# 11. `offline`

Boolean.

Current dataset:

```text
59 offline events
```

Potential use:

- offline vs online listening
- device behavior
- travel/context analysis

This is a secondary feature, not a core project feature.

---

# 12. `offline_timestamp`

Optional timestamp related to offline activity.

Current data has many null values.

Treat as nullable.

---

# 13. `incognito_mode`

Boolean.

Potentially useful for filtering.

For the main personal-taste model, incognito activity should be evaluated carefully because it may represent listening the user did not intend to contribute to normal taste patterns.

---

# 14. Raw → Canonical Transformation

The raw JSON should be transformed into a canonical playback table.

```text
Spotify JSON
     ↓
Parser
     ↓
Schema validation
     ↓
Content-type classification
     ↓
Normalization
     ↓
Canonical playback_events
```

---

# 15. Canonical `playback_events` Table

Recommended columns:

```text
event_id
timestamp_utc
timestamp_local

date
year
month
week
day_of_week
hour
is_weekend

content_type

track_id
track_name

artist_id
artist_name

project_id
project_name

ms_played
seconds_played
minutes_played

skipped
shuffle
offline
incognito_mode

start_reason
end_reason
platform

session_id
session_position
```

---

# 16. IDs

The project should create stable internal IDs.

## Track

Prefer:

```text
spotify_track_id
```

## Artist

Spotify history does not necessarily provide a dedicated artist URI.

Initially use a normalized artist name:

```text
artist_id = normalized artist key
```

Later, metadata enrichment can map it to a Spotify artist ID.

## Project

Initially:

```text
project_id = normalized artist + normalized project
```

This prevents two artists with similarly named albums from being incorrectly merged.

---

# 17. Time Zone Handling

The raw `ts` value is UTC.

Example:

```text
2025-09-07T19:13:00Z
```

The project should preserve:

```text
timestamp_utc
```

and derive:

```text
timestamp_local
```

using the appropriate analysis timezone.

All time-of-day analysis should use the **local analysis timestamp**, not UTC.

This is critical for:

- morning/evening analysis
- artist time-of-day profiles
- genre-time heatmaps
- sessions
- discovery windows

---

# 18. Data Processing Layers

Use three conceptual layers.

## Bronze — Raw

```text
data/raw/
```

Original Spotify JSON.

Never modify.

---

## Silver — Clean

```text
data/processed/
```

Cleaned and normalized playback events.

Example:

```text
playback_events.parquet
```

---

## Gold — Analytical

Derived datasets:

```text
artists.parquet
songs.parquet
projects.parquet
sessions.parquet
transitions.parquet
discovery_events.parquet
song_lifecycles.parquet
artist_lifecycles.parquet
project_metrics.parquet
```

---

# 19. Why Parquet?

The project should convert JSON to Parquet after validation.

Recommended flow:

```text
JSON
 ↓
Pandas / Polars
 ↓
Parquet
```

Parquet is preferred for analytical work because it:

- is columnar
- is compressed
- preserves types
- is fast for analytical queries
- works well with Pandas
- works well with Polars
- works well with DuckDB

The raw JSON remains available for reproducibility.

---

# 20. Core Analytical Tables

## 20.1 `playback_events`

One row per event.

This is the fundamental fact table.

---

## 20.2 `songs`

One row per unique track.

Suggested fields:

```text
track_id
track_name
artist_id
project_id

first_seen
last_seen

total_plays
total_minutes
unique_days
unique_months

skip_count
skip_rate

active_lifespan
raw_lifespan
```

---

## 20.3 `artists`

One row per artist.

```text
artist_id
artist_name

first_seen
last_seen

total_plays
total_minutes

unique_tracks
unique_projects

active_days
active_months

peak_date
peak_month
peak_year

longest_gap
revival_count
```

---

## 20.4 `projects`

One row per project.

```text
project_id
project_name
artist_id

release_type
release_date
track_count

first_heard
last_heard

tracks_heard
penetration

total_plays
total_minutes

completion_category
listening_style
```

---

## 20.5 `sessions`

One row per listening session.

Default boundary:

> **30 minutes of inactivity**

Fields:

```text
session_id
start_time
end_time
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

---

# 21. `discovery_events`

This table powers one of the most important features of the project.

Suggested schema:

```text
catalyst_event_id

catalyst_track_id
catalyst_artist_id
catalyst_project_id
catalyst_timestamp

discovery_type

tracks_added_7d
projects_added_7d
plays_added_7d
minutes_added_7d

tracks_30d
projects_30d
minutes_30d

tracks_90d
projects_90d
minutes_90d

retention_30d
retention_90d

future_hours_unlocked
```

---

# 22. Discovery Event Types

### Artist Discovery

New artist followed by meaningful artist exploration.

### Project Discovery

Known artist followed by exploration of a previously inactive/new project.

### Catalog Deepening

Known artist followed by deeper catalog exploration.

### Re-engagement

Previously dormant artist/project becomes active again.

---

# 23. 7-Day Discovery Algorithm

For each candidate catalyst event:

```text
T = catalyst timestamp

Look at:
T → T + 7 days
```

Then calculate:

```text
additional artist tracks
additional projects
additional listening minutes
```

The catalyst can be evaluated against the listener's history immediately before `T`.

### Example

```text
Ice Cream Frappe
       ↓
within 7 days
       ↓
Junkie
       ↓
more Frappe Ash tracks
```

This is a **catalog expansion signal**.

It is not proof of causality.

---

# 24. 30-Day and 90-Day Follow-up

After the 7-day expansion window:

```text
7D
 ↓
30D
 ↓
90D
```

Measure:

- continued tracks
- continued projects
- continued minutes
- repeated listening
- retention

This distinguishes:

### Temporary exploration

from:

### Durable taste change

---

# 25. Future Hours Unlocked

For a catalyst event:

```text
downstream listening minutes
```

can be converted to:

```text
future hours unlocked
```

This is one of the project's strongest derived metrics.

It answers:

> How much later listening followed this discovery pathway?

Again, describe it as downstream impact, not proven causation.

---

# 26. Project Qualification

Permanent rule:

> **A project is considered explored after at least 3 unique tracks have been heard.**

This includes 3-track EPs.

Example:

```text
3-track EP
3 heard
= 100% complete
```

```text
20-track album
3 heard
= 15% penetration
```

Do not confuse the two.

---

# 27. Project Penetration

Formula:

```text
tracks_heard / tracks_available
```

Example:

```text
8 tracks heard
10 tracks available

penetration = 80%
```

---

# 28. Project-Driving Song

For every project:

```text
song_minutes / project_total_minutes
```

This identifies songs responsible for a disproportionate amount of project listening.

Also calculate:

```text
song_plays / project_total_plays
```

A project with one song accounting for 50% of listening is fundamentally different from one where listening is distributed across 15 tracks.

---

# 29. Song Lifespan

Two metrics must be retained.

## Raw lifespan

```text
last_play - first_play
```

## Active lifespan

Measures sustained listening while accounting for long inactivity gaps.

This prevents a song played once in 2020 and once in 2026 from being interpreted as continuously active.

---

# 30. Artist Lifecycle

Use:

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
Revival
```

Metrics come from the event table and artist aggregate table.

---

# 31. Genre Enrichment

The raw Extended Streaming History does not reliably provide the genre of every track.

Therefore:

```text
Spotify history
      +
metadata enrichment
      ↓
genre mapping
```

Use broad genre families for the dashboard.

Potential categories:

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

Keep:

```text
raw genre metadata
```

separate from:

```text
normalized genre family
```

---

# 32. Genre × Time × Year

Once genre metadata is available:

```text
Genre
 ×
Hour
 ×
Year
```

This powers questions such as:

- What genre dominates mornings?
- What genre dominates evenings?
- Has the morning genre changed?
- Did an artist change time-of-day behavior because the broader genre changed?
- Which genres are discovery-heavy?

---

# 33. Sequence Data

From sorted playback events, create:

```text
previous_track
previous_artist
previous_project

next_track
next_artist
next_project
```

This enables:

- song transitions
- artist transitions
- project transitions
- discovery pathways
- music network construction

---

# 34. Music Network

Build:

```text
Artist = node
Transition = edge
Listening time = node weight
Transition frequency = edge weight
```

Potential graph metrics:

- degree
- weighted degree
- betweenness
- PageRank
- communities

This can show the user's personal music ecosystem.

---

# 35. ML Dataset

The ML dataset should not simply be the raw playback table.

It should be generated from historical features.

Example:

```text
catalyst_event
+
features available before catalyst
+
future outcome label
```

### Historical features

Safe inputs:

```text
song_previous_plays
artist_previous_plays
artist_previous_projects
project_previous_plays
song_age
artist_age
project_age
hour
day_of_week
session_position
session_length
shuffle
recent_artist_affinity
recent_genre_affinity
previous_transition_probability
```

### Future outcomes

Targets:

```text
expansion_7d
tracks_added_7d
projects_added_7d
minutes_7d
retention_30d
minutes_90d
```

Future outcomes must **never** be used as input features.

---

# 36. ML Leakage Rule

For a prediction at time `T`:

> Every input feature must be computable using information available at or before `T`.

Bad:

```text
artist_total_plays
```

if it includes plays after `T`.

Good:

```text
artist_plays_before_T
```

Bad:

```text
project_total_future_minutes
```

Good:

```text
project_minutes_before_T
```

---

# 37. ML Time Split

Use chronological evaluation.

Example:

```text
TRAIN
2022–2024

VALIDATION
2025

TEST
2026
```

Actual boundaries should be based on available data and documented.

Do not randomly mix future and past events.

---

# 38. ML Flagship Target

Primary problem:

> **Predict whether a song exposure will lead to meaningful artist/project catalog expansion within 7 days.**

Initial binary version:

```text
0 = no meaningful expansion
1 = meaningful expansion
```

Then optionally extend to:

```text
0 = no expansion
1 = artist expansion
2 = project expansion
3 = major catalog expansion
```

---

# 39. Model Progression

Start simple:

```text
Markov / transition baseline
        ↓
Logistic regression
        ↓
XGBoost / LightGBM
        ↓
Advanced sequence model only if justified
```

Do not use deep learning simply to make the project look advanced.

---

# 40. ML Evaluation

Report:

- Precision
- Recall
- F1
- PR-AUC
- ROC-AUC where appropriate
- Calibration
- Confusion matrix
- Baseline comparison
- Feature importance
- SHAP explanations
- Error analysis

Accuracy alone is insufficient.

---

# 41. Dashboard Data Flow

The dashboard should not read raw JSON.

Instead:

```text
Raw JSON
   ↓
Pipeline
   ↓
Parquet / Database
   ↓
Analytical tables
   ↓
API
   ↓
Dashboard
```

Example:

```text
Dashboard request:
GET /discovery/catalysts

API
 ↓
discovery_events
 ↓
JSON response
 ↓
React visualization
```

Here, **JSON can be used as the API response format**, but that is different from using raw Spotify JSON as the application's main data source.

---

# 42. Recommended Technology Flow

## Ingestion

```text
Python
```

## Processing

```text
Pandas or Polars
```

## Storage

Initially:

```text
Parquet
+
DuckDB
```

Later, if needed:

```text
PostgreSQL
```

## ML

```text
scikit-learn
XGBoost / LightGBM
```

## API

```text
FastAPI
```

## Dashboard

```text
React / Next.js
Plotly / D3
```

---

# 43. Recommended Data Directory

```text
data/
│
├── raw/
│   └── spotify/
│       └── extended_streaming_history/
│           ├── Streaming_History_Audio_2020.json
│           ├── Streaming_History_Audio_2021.json
│           ├── Streaming_History_Audio_2022.json
│           ├── Streaming_History_Audio_2023.json
│           ├── Streaming_History_Audio_2024.json
│           ├── Streaming_History_Audio_2025.json
│           └── Streaming_History_Audio_2026.json
│
├── interim/
│   └── normalized_playback.parquet
│
├── processed/
│   ├── playback_events.parquet
│   ├── songs.parquet
│   ├── artists.parquet
│   ├── projects.parquet
│   ├── sessions.parquet
│   ├── transitions.parquet
│   └── discovery_events.parquet
│
└── ml/
    ├── discovery_train.parquet
    ├── discovery_validation.parquet
    └── discovery_test.parquet
```

---

# 44. Data Pipeline Commands

The final project should eventually support commands conceptually like:

```bash
python -m src.ingestion.run
```

Then:

```bash
python -m src.features.build
```

Then:

```bash
python -m src.analytics.run
```

Then:

```bash
python -m src.ml.train_discovery
```

Then:

```bash
python -m src.api.run
```

The exact command structure can be finalized during implementation.

---

# 45. Data Validation Checklist

Every ingestion run should validate:

### Schema

- [ ] Required fields exist
- [ ] Types are correct
- [ ] New/unexpected fields are logged

### Timestamps

- [ ] Valid timestamps
- [ ] UTC parsing works
- [ ] No impossible dates

### Playback

- [ ] `ms_played >= 0`
- [ ] No impossible duration values
- [ ] Missing track fields handled

### IDs

- [ ] Track URI format validated
- [ ] Artist normalization checked
- [ ] Project normalization checked

### Duplicates

- [ ] Exact duplicate events identified
- [ ] Duplicates not removed blindly

### Content

- [ ] Music separated from podcast/audiobook content

### Privacy

- [ ] IP addresses excluded from public outputs
- [ ] Raw personal data excluded from GitHub

---

# 46. Important Analytical Caveats

## Playback event ≠ complete song

A playback event may represent only a few seconds.

Therefore:

```text
play count
```

and:

```text
listening minutes
```

must both be retained.

---

## Skip ≠ dislike

Use skip as a behavioral signal, not a direct preference label.

---

## Transition ≠ causality

A song followed by another song does not prove that the first caused the second.

---

## Album field ≠ release type

Album/EP/Single classification requires metadata enrichment.

---

## First play ≠ first discovery

The dataset only tells when the track was recorded as played.

A listener could have encountered the song elsewhere before that event.

Use:

> first recorded exposure

rather than claiming absolute first-ever discovery.

---

# 47. Privacy Policy for the Project

The dataset contains personal behavioral information.

The public GitHub repository should **never contain**:

- raw Spotify history
- IP addresses
- personally identifying account data
- private device details when unnecessary
- unaggregated personal listening records

Public repository should use:

```text
synthetic/sample data
+
aggregated results
+
code
+
documentation
+
screenshots
```

The real dataset stays local/private.

---

# 48. How New Spotify Data Will Be Added

When a new export becomes available:

```text
New Spotify JSON
       ↓
Copy to raw/
       ↓
Run ingestion
       ↓
Validate
       ↓
Rebuild canonical table
       ↓
Rebuild features
       ↓
Rebuild analytics
       ↓
Recalculate ML data
       ↓
Refresh dashboard
```

Do not manually edit the processed tables.

---

# 49. Final Data Architecture

```text
                    SPOTIFY
                       |
                       v
              Extended History
                   JSON
                       |
                       v
              ┌────────────────┐
              │ RAW / BRONZE   │
              │ Immutable JSON │
              └───────┬────────┘
                      |
                      v
              Ingestion + QA
                      |
                      v
              ┌────────────────┐
              │ SILVER         │
              │ playback_events│
              │ Parquet        │
              └───────┬────────┘
                      |
          ┌───────────┼────────────┐
          v           v            v
       Songs       Artists      Projects
          |           |            |
          └───────────┼────────────┘
                      v
               Feature Layer
                      |
        ┌─────────────┼──────────────┐
        v             v              v
    Sessions      Discovery       Sequences
        |             |              |
        └─────────────┼──────────────┘
                      v
                GOLD ANALYTICS
                      |
             ┌────────┴────────┐
             v                 v
          ML Layer         Dashboard
             |                 |
             v                 v
       Predictions          FastAPI
                               |
                               v
                         React / Next.js
```

---

# 50. Bottom Line

The project will **use the Spotify JSON directly only at the ingestion layer**.

The recommended architecture is:

```text
JSON
 ↓
Clean + Normalize
 ↓
Parquet
 ↓
Canonical tables
 ↓
Feature engineering
 ↓
Analytics + ML
 ↓
Database/API
 ↓
Dashboard
```

The raw JSON remains the **source of truth**.

Parquet becomes the primary analytical storage format.

Canonical tables become the foundation for analytics.

Derived feature tables power the ML models.

The API serves processed results to the dashboard.

This structure makes the project reproducible, scalable, testable, privacy-conscious, and much more credible as a professional GitHub/data-science project.
