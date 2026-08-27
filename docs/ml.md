# Machine Learning Architecture & Temporal Leakage Audit

## 1. Flagship ML Problem Formulation

### Song → 7-Day Catalog Expansion Prediction
> **Question**: Given a song playback event at timestamp $T$ and all behavioral context available *strictly up to that point*, what is the probability that the listener will meaningfully expand into the artist's catalog during the following 7 days?

### Target Definition:
$$\text{Target} = 1 \iff \text{New Artist Tracks in }[T, T+7\text{d}] \ge 2 \lor (\text{Minutes in }[T, T+7\text{d}] \ge 30.0 \land \text{Plays} \ge 4)$$

---

## 2. Temporal Leakage Prevention

### Fundamental Rules:
1. **Chronological Splitting**: Data is split strictly by calendar year:
   - **Training Set**: 2020–2024 (11,679 events, 12.4% positive rate)
   - **Validation Set**: 2025 (13,368 events, 7.9% positive rate)
   - **Test Set**: 2026 (7,180 events, 6.4% positive rate)
   - **No random shuffling across time** is permitted.
2. **Feature Definition Invariant**: Every feature vector at time $T$ is computed using only events with $t < T$.
   - Valid: `artist_plays_before_T`, `project_minutes_before_T`
   - Forbidden: Any whole-dataset global summary metrics.

---

## 3. Benchmark Results on Unseen Test Year (2026)

| Model | PR-AUC | ROC-AUC | Precision | Recall | F1 Score | Brier Score |
|---|---|---|---|---|---|---|
| 1. Majority Class Baseline | 0.0642 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0601 |
| 2. Heuristic Transition Baseline | 0.0605 | 0.4752 | 0.0603 | 0.0304 | 0.0404 | 0.0812 |
| 3. Regularized Logistic Regression | 0.6088 | 0.9620 | 0.4560 | 0.8547 | 0.5947 | 0.0694 |
| **4. LightGBM Gradient Boosted Trees (Main)** | **0.7302** | **0.9718** | **0.5385** | **0.8503** | **0.6594** | **0.0315** |

### Top Predictive Features (LightGBM Gain Importance):
1. `is_first_artist_play` (Initial artist discovery signal)
2. `seconds_played` (Playback completion / listening intensity)
3. `artist_tracks_heard_before` (Prior catalog familiarity)
4. `skipped` (Explicit negative behavioral signal)
5. `artist_plays_before` (Historical artist affinity)
6. `hour` & `time_since_prev_event_seconds` (Session context)
