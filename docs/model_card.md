# Model Card: Spotify Catalog Expansion Predictor

## Model Details
- **Model Name**: Spotify Catalog Expansion Predictor (LightGBM)
- **Model Version**: 1.0.0
- **Model Type**: Gradient Boosted Decision Tree Classifier (`LGBMClassifier`)
- **Primary Task**: Predict whether an exposure to a track will lead to meaningful downstream artist catalog expansion within a 7-day window.

## Intended Use
- **Primary Use Case**: Behavioral analytics, discovery pathway modeling, personalized recommendation trigger modeling.
- **Out of Scope**: Real-time content ranking without user history or multi-user cold start prediction.

## Training & Evaluation Data
- **Dataset**: Spotify Extended Streaming History (32,649 events across 2020–2026).
- **Temporal Split**:
  - Training: 2020–2024
  - Validation: 2025
  - Test: 2026 (Unseen future data)

## Performance Metrics (Test Set 2026)
- **PR-AUC**: 0.7302 (vs 0.0642 majority baseline)
- **ROC-AUC**: 0.9718
- **F1 Score**: 0.6594
- **Precision**: 0.5385
- **Recall**: 0.8503
- **Brier Calibration Score**: 0.0315

## Failure Modes & Error Analysis
- **False Positives**: Isolated full-duration plays of hit singles from popular artists where no further discography exploration occurred.
- **False Negatives**: Serendipitous late-night listening sessions where an initially skipped track later sparked an exploration session.
