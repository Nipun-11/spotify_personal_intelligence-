"""Secondary ML Model: 30-day and 90-day Song Retention Prediction."""

import logging
from typing import Dict, Any
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb

from src.config import MODELS_DIR
from src.ml.dataset_builder import FEATURE_COLUMNS
from src.ml.baselines import evaluate_predictions

logger = logging.getLogger(__name__)

def train_retention_model(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame
) -> Dict[str, Any]:
    """Train Gradient Boosted Classifier to predict 30-day song retention."""
    logger.info("Training Song Retention Prediction Model...")
    
    target_col = "target_retention_30d"
    X_train, y_train = df_train[FEATURE_COLUMNS], df_train[target_col].values
    X_val, y_val = df_val[FEATURE_COLUMNS], df_val[target_col].values
    X_test, y_test = df_test[FEATURE_COLUMNS], df_test[target_col].values
    
    n_neg = int(np.sum(y_train == 0))
    n_pos = int(np.sum(y_train == 1))
    pos_scale = max(1.0, n_neg / max(1, n_pos))
    
    model = lgb.LGBMClassifier(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=5,
        scale_pos_weight=pos_scale,
        random_state=42,
        verbose=-1
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(stopping_rounds=15, verbose=False)]
    )
    
    test_probs = model.predict_proba(X_test)[:, 1]
    metrics = evaluate_predictions(y_test, test_probs, threshold=0.5)
    
    # Save model
    model_path = MODELS_DIR / "retention_lightgbm.joblib"
    joblib.dump({
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": metrics
    }, model_path)
    
    return {
        "model": model,
        "test_metrics": metrics
    }
