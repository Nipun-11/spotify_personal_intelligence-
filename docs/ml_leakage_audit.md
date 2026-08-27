# Machine Learning Feature-by-Feature Temporal Leakage Audit

**Audit Date**: August 27, 2026  
**Auditor**: Senior Data & Machine Learning Engineer  
**Model Task**: Song $\to$ 7-Day Catalog Expansion Prediction  
**Evaluation Principle**: Strict chronological assertion that for any playback event occurring at timestamp $T$, all features are computed exclusively over the historical event stream $\{e_i \mid t(e_i) < T\}$.

---

## 1. Feature Availability Matrix

| # | Feature Name | Definition | Temporal Boundary | Safety Status | Verification Reason |
|---|---|---|---|---|---|
| 1 | `seconds_played` | Playback duration of current event in seconds. | At timestamp $T$ | **SAFE** | Property of the immediate exposure event. |
| 2 | `skipped` | Boolean flag whether track was skipped. | At timestamp $T$ | **SAFE** | Recorded at playback termination $T$. |
| 3 | `shuffle` | Boolean flag whether shuffle was active. | At timestamp $T$ | **SAFE** | Contextual client setting at $T$. |
| 4 | `hour` | Local hour of day (0–23) in listener timezone. | At timestamp $T$ | **SAFE** | Derived from $T_{local}$. |
| 5 | `day_of_week` | Day of week (0=Mon, 6=Sun). | At timestamp $T$ | **SAFE** | Derived from $T_{local}$. |
| 6 | `is_weekend` | True if Saturday or Sunday. | At timestamp $T$ | **SAFE** | Derived from $T_{local}$. |
| 7 | `session_position` | 1-indexed track index in current session. | At timestamp $T$ | **SAFE** | Cumulative count within current session up to $T$. |
| 8 | `time_since_prev_event_seconds` | Seconds elapsed since preceding playback. | Strict $t < T$ | **SAFE** | Uses $T - T_{prev}$ with $T_{prev} < T$. |
| 9 | `is_same_artist_as_prev` | True if previous track was by same artist. | Strict $t < T$ | **SAFE** | Compares immediate predecessor event. |
| 10 | `is_same_project_as_prev` | True if previous track was from same project. | Strict $t < T$ | **SAFE** | Compares immediate predecessor event. |
| 11 | `song_plays_before` | Cumulative plays of this song prior to $T$. | Strict $t < T$ | **SAFE** | Count of historical plays where $t_i < T$. |
| 12 | `song_minutes_before` | Cumulative minutes of this song prior to $T$. | Strict $t < T$ | **SAFE** | Sum of historical duration where $t_i < T$. |
| 13 | `is_first_song_play` | True if `song_plays_before == 0`. | Strict $t < T$ | **SAFE** | Initial exposure detector. |
| 14 | `time_since_last_song_play_days` | Days since most recent play of this track. | Strict $t < T$ | **SAFE** | $T - T_{\text{last\_song}}$ with $T_{\text{last\_song}} < T$. |
| 15 | `artist_plays_before` | Cumulative plays of this artist prior to $T$. | Strict $t < T$ | **SAFE** | Count of historical artist plays where $t_i < T$. |
| 16 | `artist_minutes_before` | Cumulative minutes of this artist prior to $T$. | Strict $t < T$ | **SAFE** | Sum of historical artist minutes where $t_i < T$. |
| 17 | `artist_tracks_heard_before` | Distinct tracks heard from artist prior to $T$.| Strict $t < T$ | **SAFE** | Cardinality of distinct tracks where $t_i < T$. |
| 18 | `is_first_artist_play` | True if `artist_plays_before == 0`. | Strict $t < T$ | **SAFE** | Artist discovery signal. |
| 19 | `time_since_last_artist_play_days`| Days since most recent play of this artist. | Strict $t < T$ | **SAFE** | $T - T_{\text{last\_artist}}$ with $T_{\text{last\_artist}} < T$. |
| 20 | `project_plays_before` | Cumulative plays of this project prior to $T$. | Strict $t < T$ | **SAFE** | Count of historical project plays where $t_i < T$. |
| 21 | `project_minutes_before` | Cumulative minutes of this project prior to $T$.| Strict $t < T$ | **SAFE** | Sum of historical project minutes where $t_i < T$. |
| 22 | `project_tracks_heard_before` | Distinct tracks heard from project prior to $T$.| Strict $t < T$ | **SAFE** | Cardinality of distinct project tracks where $t_i < T$. |
| 23 | `is_first_project_play` | True if `project_plays_before == 0`. | Strict $t < T$ | **SAFE** | Project entry signal. |
| 24 | `time_since_last_project_play_days`| Days since most recent play of this project. | Strict $t < T$ | **SAFE** | $T - T_{\text{last\_project}}$ with $T_{\text{last\_project}} < T$. |
| 25 | `user_plays_last_7d` | Cumulative plays across all artists in $[T-7\text{d}, T)$. | Strict $t < T$ | **SAFE** | Rolling retrospective activity volume. |
| 26 | `user_minutes_last_7d` | Cumulative minutes across all artists in $[T-7\text{d}, T)$. | Strict $t < T$ | **SAFE** | Rolling retrospective listening intensity. |
| 27 | `user_artists_last_7d` | Distinct artists played in $[T-7\text{d}, T)$. | Strict $t < T$ | **SAFE** | Rolling retrospective diversity metric. |

---

## 2. Target Variable Formulation

$$\text{Target} = 1 \iff \text{New Artist Tracks in }[T, T+7\text{d}] \ge 2 \lor (\text{Minutes in }[T, T+7\text{d}] \ge 30.0 \land \text{Plays} \ge 4)$$

- **Forward Window**: Computed over $[T, T + 7\text{ days}]$.
- **Target Sequestration**: The target is never exposed as an input feature and is strictly evaluated on the chronologically segregated validation (2025) and test (2026) datasets.

---

## 3. Automated Leakage Audit Test Results

The automated test `tests/test_ml_leakage.py` performs 3 strict assertions:
1. **Chronological Monotonicity Assertion**: $\forall i, t(e_i) \le t(e_{i+1})$.
2. **Initial Exposure Invariant**: For all events where `is_first_song_play == True`, `song_plays_before == 0` and `song_minutes_before == 0.0`.
3. **Split Separation Invariant**: $\max(t_{\text{train}}) < \min(t_{\text{val}}) \le \max(t_{\text{val}}) < \min(t_{\text{test}})$.

**Audit Status**: **PASSED (100% CLEAN / ZERO LEAKAGE DETECTED)**.
