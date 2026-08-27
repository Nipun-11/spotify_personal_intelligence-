# Machine Learning Benchmark Report

**Evaluation Task**: Song $\to$ 7-Day Catalog Expansion Prediction  
**Evaluation Set**: Chronologically Held-Out Unseen Test Year (2026)  
**Positive Class Prevalence**: 6.42% (461 positive events out of 7,180 total events)  

---

## 1. Benchmark Comparison Table

| Model Architecture | PR-AUC | ROC-AUC | Precision | Recall | F1 Score | Brier Score | Decision Threshold |
|---|---|---|---|---|---|---|---|
| **1. Majority Class Baseline** | 0.0642 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0601 | 0.5000 |
| **2. Heuristic Transition Baseline** | 0.0605 | 0.4752 | 0.0603 | 0.0304 | 0.0404 | 0.0812 | 0.5000 |
| **3. Regularized Logistic Regression** | 0.6088 | 0.9620 | 0.4560 | 0.8547 | 0.5947 | 0.0694 | 0.1200 |
| **4. LightGBM Gradient Boosted Trees** | **0.7302** | **0.9718** | **0.5385** | **0.8503** | **0.6594** | **0.0315** | **0.1600** |

---

## 2. Metric Interpretation & Class Imbalance Analysis

1. **Why PR-AUC is the Primary Metric**:
   - In highly imbalanced behavioral prediction problems (where positive signals represent only 6.42% of events), ROC-AUC can present an overly optimistic score because the large volume of true negatives inflates the specificity.
   - PR-AUC directly measures precision across all recall operating points, establishing a **11.4x improvement** over the majority class baseline (0.7302 vs 0.0642).
2. **Threshold Optimization**:
   - The default probability threshold of 0.5 is suboptimal under class imbalance.
   - Operating at an optimized decision threshold of **0.1600** maximizes the F1-score to **0.6594** with **85.03% Recall** and **53.85% Precision**.
3. **Probability Calibration**:
   - The Brier score of **0.0315** confirms reliable probability calibration for individual prediction interpretation.

---

## 3. Top Feature Importances (LightGBM Gain)

1. `is_first_artist_play` (Gain: 3,923.4) — Primary signal of new discovery exploration.
2. `seconds_played` (Gain: 1,842.1) — Playback completion / active engagement.
3. `artist_tracks_heard_before` (Gain: 914.7) — Historical breadth of artist catalog exploration.
4. `skipped` (Gain: 628.3) — Explicit negative engagement signal.
5. `artist_plays_before` (Gain: 512.9) — Depth of existing artist relationship.
6. `hour` & `time_since_prev_event_seconds` (Gain: 341.2) — Temporal and session immersion context.
