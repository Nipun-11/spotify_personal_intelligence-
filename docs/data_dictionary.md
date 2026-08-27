# Spotify Personal Intelligence Engine — Data Dictionary

## 1. Canonical Playback Table (`canonical_playback.parquet`)

| Column | Type | Description |
|---|---|---|
| `event_id` | `string` | Unique deterministic playback event identifier (`evt_######_########`). |
| `timestamp_utc` | `timestamp` | Raw playback timestamp in UTC. |
| `timestamp_local` | `timestamp` | Local playback timestamp converted to listener timezone (`Asia/Kolkata` IST). |
| `date` | `string` | Calendar date (`YYYY-MM-DD`). |
| `year` | `int` | Calendar year (2020–2026). |
| `month` | `int` | Calendar month (1–12). |
| `week` | `int` | ISO calendar week. |
| `day_of_week` | `int` | Day of week (0 = Monday, 6 = Sunday). |
| `hour` | `int` | Hour of day (0–23) in listener local time. |
| `time_of_day_bucket`| `string` | One of 8 diurnal 3-hour buckets (`12AM-3AM`, `3AM-6AM`, etc.). |
| `is_weekend` | `bool` | True if Saturday or Sunday. |
| `content_type` | `string` | `music`, `podcast`, `audiobook`, or `video`. |
| `track_id` | `string` | Spotify Track ID extracted from URI or deterministic fallback. |
| `track_name` | `string` | Track title string. |
| `artist_id` | `string` | Deterministic artist ID (`art_########`). |
| `artist_name` | `string` | Standardized artist name. |
| `project_id` | `string` | Deterministic project ID (`prj_########`). |
| `project_name` | `string` | Album or EP name. |
| `ms_played` | `int` | Milliseconds played during playback event. |
| `seconds_played` | `float` | Seconds played. |
| `minutes_played` | `float` | Minutes played. |
| `skipped` | `bool` | True if playback was skipped. |
| `shuffle` | `bool` | True if shuffle mode was active. |
| `platform` | `string` | Standardized device category (`android`, `windows`, `web_player`, etc.). |
| `session_id` | `string` | Session ID based on 30-min inactivity gap. |
| `session_position` | `int` | 1-indexed position of track within the session. |
| `song_plays_before`| `int` | Number of previous plays of this track strictly prior to timestamp $T$. |
| `artist_plays_before`| `int`| Number of previous plays of this artist strictly prior to timestamp $T$. |
| `project_plays_before`| `int`| Number of previous plays of this project strictly prior to timestamp $T$. |
| `is_first_artist_play`| `bool`| True if this event is the first recorded exposure to this artist. |

---

## 2. Discovery Events Table (`discovery_events.parquet`)

| Column | Type | Description |
|---|---|---|
| `catalyst_event_id` | `string` | Identifier of the candidate catalyst playback event. |
| `catalyst_track_name`| `string`| Name of catalyst song. |
| `catalyst_artist_name`| `string`| Name of artist. |
| `discovery_type` | `string` | `Artist Discovery`, `Project Discovery`, `Catalog Deepening`, or `Re-engagement`. |
| `tracks_added_7d` | `int` | Unique new artist tracks heard in $[T, T+7\text{d}]$ not heard prior to $T$. |
| `projects_added_7d`| `int` | Unique new projects entered in $[T, T+7\text{d}]$. |
| `minutes_added_7d` | `float` | Total artist listening minutes accumulated in $[T, T+7\text{d}]$. |
| `retention_30d` | `bool` | True if artist listening occurred between Day 14 and Day 30 after $T$. |
| `retention_90d` | `bool` | True if artist listening occurred between Day 30 and Day 90 after $T$. |
| `future_hours_unlocked`| `float` | Total downstream artist listening hours generated from $T$ onwards. |
| `is_meaningful_expansion_7d`| `bool` | True if $\ge 2$ new tracks or $\ge 30$ mins from artist in next 7 days. |

---

## 3. Projects Table (`projects.parquet`)

| Column | Type | Description |
|---|---|---|
| `project_id` | `string` | Project identifier. |
| `project_name` | `string` | Album/EP title. |
| `artist_name` | `string` | Artist name. |
| `tracks_heard` | `int` | Unique tracks played from this project. |
| `is_explored` | `bool` | **True iff tracks_heard $\ge 3$** (Non-negotiable rule). |
| `top_song_name` | `string` | Name of top-driving song in the project. |
| `top_song_share_pct`| `float`| Contribution of top song to total project listening time (%). |
| `listening_style` | `string` | `Hit-Driven Project`, `Deep Exploration`, `Explored (3 tracks)`, etc. |
| `sequentiality_rate`| `float`| Frequency of consecutive playback of tracks within this project. |
