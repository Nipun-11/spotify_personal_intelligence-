"""Machine learning package."""
from src.ml.dataset_builder import build_ml_dataset, FEATURE_COLUMNS
from src.ml.baselines import train_and_eval_baselines, evaluate_predictions
from src.ml.catalyst_model import train_catalyst_model
from src.ml.retention_model import train_retention_model
from src.ml.evaluation import generate_benchmark_comparison, perform_error_analysis
from src.ml.explainability import run_temporal_leakage_audit

__all__ = [
    "build_ml_dataset",
    "FEATURE_COLUMNS",
    "train_and_eval_baselines",
    "evaluate_predictions",
    "train_catalyst_model",
    "train_retention_model",
    "generate_benchmark_comparison",
    "perform_error_analysis",
    "run_temporal_leakage_audit",
]
