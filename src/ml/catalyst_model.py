"""Main Gradient Boosted Classifier (LightGBM/XGBoost) for Catalog Expansion Prediction."""

import logging
import os
from typing import Dict, Any, Tuple
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.ensemble import HistGradientBoostingClassifier

from src.config import MODELS_DIR
from src.ml.dataset_builder import FEATURE_COLUMNS
from src.ml.baselines import evaluate_predictions

logger = logging.getLogger(__name__)

def train_catalyst_model(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
    target_col: str = "target_expansion_7d"
) -> Dict[str, Any]:
    """Train flagship Gradient Boosted Classifier with validation threshold tuning and test evaluation.
    
    Args:
        df_train: Training DataFrame (<= 2024).
        df_val: Validation DataFrame (2025).
        df_test: Test DataFrame (2026).
        target_col: Target column name.
        
    Returns:
        Dictionary of test metrics, validation metrics, feature importances, and trained model object.
    """
    logger.info("Training Flagship Discovery Catalyst Model (LightGBM)...")
    
    X_train, y_train = df_train[FEATURE_COLUMNS], df_train[target_col].values
    X_val, y_val = df_val[FEATURE_COLUMNS], df_val[target_col].values
    X_test, y_test = df_test[FEATURE_COLUMNS], df_test[target_col].values
    
    # Calculate positive weight ratio
    n_neg = int(np.sum(y_train == 0))
    n_pos = int(np.sum(y_train == 1))
    pos_scale = max(1.0, n_neg / max(1, n_pos))
    
    # Initialize LightGBM Classifier
    model = lgb.LGBMClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        scale_pos_weight=pos_scale,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1
    )
    
    # Fit model with early stopping on validation set
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(stopping_rounds=20, verbose=False)]
    )
    
    val_probs = model.predict_proba(X_val)[:, 1]
    test_probs = model.predict_proba(X_test)[:, 1]
    
    # Threshold optimization on Validation split
    best_threshold = 0.5
    best_f1 = 0.0
    for th in np.linspace(0.1, 0.9, 33):
        m = evaluate_predictions(y_val, val_probs, threshold=th)
        if m["f1"] > best_f1:
            best_f1 = m["f1"]
            best_threshold = float(th)
            
    val_metrics = evaluate_predictions(y_val, val_probs, threshold=best_threshold)
    test_metrics = evaluate_predictions(y_test, test_probs, threshold=best_threshold)
    
    # Feature importances
    importances_gain = model.booster_.feature_importance(importance_type="gain")
    importances_split = model.booster_.feature_importance(importance_type="split")
    
    fi_list = []
    for col, gain, split in zip(FEATURE_COLUMNS, importances_gain, importances_split):
        fi_list.append({
            "feature": col,
            "gain_importance": round(float(gain), 2),
            "split_importance": int(split)
        })
        
    fi_df = pd.DataFrame(fi_list).sort_values("gain_importance", ascending=False).reset_index(drop=True)
    
    # Save trained model artifact
    model_path = MODELS_DIR / "catalyst_lightgbm.joblib"
    joblib.dump({
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "best_threshold": best_threshold,
        "metrics": test_metrics
    }, model_path)
    logger.info(f"Model saved to {model_path}")
    
    return {
        "model": model,
        "best_threshold": best_threshold,
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "feature_importance": fi_df,
        "test_predictions": {
            "y_true": y_test.tolist(),
            "y_prob": test_probs.tolist()
        }
    }
