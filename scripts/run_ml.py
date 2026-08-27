"""ML Training, Evaluation, and Temporal Leakage Audit runner."""

import sys
import os
import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import PROCESSED_DATA_DIR, ML_DATA_DIR, MODELS_DIR
from src.ml.dataset_builder import build_ml_dataset, FEATURE_COLUMNS
from src.ml.baselines import train_and_eval_baselines
from src.ml.catalyst_model import train_catalyst_model
from src.ml.retention_model import train_retention_model
from src.ml.evaluation import generate_benchmark_comparison, perform_error_analysis
from src.ml.explainability import run_temporal_leakage_audit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("run_ml")

def run_ml_pipeline() -> None:
    """Execute complete ML dataset construction, training, validation, and benchmarking."""
    logger.info("=" * 60)
    logger.info("STARTING SPOTIFY MACHINE LEARNING PIPELINE")
    logger.info("=" * 60)
    
    # 1. Load canonical tables
    logger.info("[ML Step 1/6] Loading canonical playback and discovery tables...")
    events_path = PROCESSED_DATA_DIR / "canonical_playback.parquet"
    catalysts_path = PROCESSED_DATA_DIR / "discovery_events.parquet"
    
    if not events_path.exists() or not catalysts_path.exists():
        raise FileNotFoundError("Canonical tables not found. Run scripts/run_pipeline.py first!")
        
    df_events = pd.read_parquet(events_path)
    df_catalysts = pd.read_parquet(catalysts_path)
    
    # 2. Build ML Dataset with chronological splits
    logger.info("[ML Step 2/6] Building strictly chronological ML dataset...")
    full_ml_df, splits = build_ml_dataset(df_events, df_catalysts)
    
    # Save ML splits
    full_ml_df.to_parquet(ML_DATA_DIR / "ml_features_all.parquet", index=False)
    for split_name, split_df in splits.items():
        split_df.to_parquet(ML_DATA_DIR / f"ml_features_{split_name}.parquet", index=False)
        
    df_train = splits["train"]
    df_val = splits["val"]
    df_test = splits["test"]
    
    # 3. Run Temporal Leakage Audit
    logger.info("[ML Step 3/6] Executing Temporal Leakage Audit...")
    audit_report = run_temporal_leakage_audit(df_events, df_catalysts)
    with open(ML_DATA_DIR / "temporal_leakage_audit.json", "w", encoding="utf-8") as fh:
        json.dump(audit_report, fh, indent=2)
        
    # 4. Train Baselines
    logger.info("[ML Step 4/6] Training and evaluating baseline models...")
    baseline_results = train_and_eval_baselines(df_train, df_val, df_test)
    
    # 5. Train Main Catalyst Model (LightGBM)
    logger.info("[ML Step 5/6] Training Flagship LightGBM Model with validation threshold tuning...")
    lightgbm_results = train_catalyst_model(df_train, df_val, df_test)
    
    # Train Secondary Retention Model
    retention_results = train_retention_model(df_train, df_val, df_test)
    
    # 6. Benchmark Comparison and Error Analysis
    logger.info("[ML Step 6/6] Generating benchmark comparison and error analysis...")
    benchmark_df = generate_benchmark_comparison(baseline_results, lightgbm_results)
    benchmark_df.to_parquet(ML_DATA_DIR / "benchmark_comparison.parquet", index=False)
    
    error_report = perform_error_analysis(
        df_test=df_test,
        y_prob=np.array(lightgbm_results["test_predictions"]["y_prob"]),
        threshold=lightgbm_results["best_threshold"]
    )
    with open(ML_DATA_DIR / "error_analysis.json", "w", encoding="utf-8") as fh:
        json.dump(error_report, fh, indent=2)
        
    # Save feature importances
    lightgbm_results["feature_importance"].to_parquet(ML_DATA_DIR / "feature_importance.parquet", index=False)
    
    # Save summary metrics JSON
    summary_metrics = {
        "benchmark_table": benchmark_df.to_dict(orient="records"),
        "lightgbm_test_metrics": lightgbm_results["test_metrics"],
        "retention_test_metrics": retention_results["test_metrics"],
        "top_features": lightgbm_results["feature_importance"].head(10).to_dict(orient="records"),
        "audit_passed": audit_report["audit_passed"]
    }
    with open(ML_DATA_DIR / "ml_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary_metrics, fh, indent=2)
        
    logger.info("=" * 60)
    logger.info("ML BENCHMARK RESULTS (TEST SET: 2026):")
    for _, row in benchmark_df.iterrows():
        logger.info(
            f"  {row['Model']:<40} | PR-AUC: {row['PR-AUC']:.4f} | ROC-AUC: {row['ROC-AUC']:.4f} | "
            f"F1: {row['F1 Score']:.4f} | Prec: {row['Precision']:.4f} | Rec: {row['Recall']:.4f}"
        )
    logger.info("=" * 60)
    logger.info("ML PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_ml_pipeline()
