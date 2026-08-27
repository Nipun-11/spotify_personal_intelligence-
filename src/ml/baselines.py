"""Baseline models for catalog expansion prediction."""

import logging
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
)

from src.ml.dataset_builder import FEATURE_COLUMNS

logger = logging.getLogger(__name__)

def evaluate_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5
) -> Dict[str, Any]:
    """Calculate comprehensive classification metrics including PR-AUC and ROC-AUC."""
    y_pred = (y_prob >= threshold).astype(int)
    
    # Handle single-class edge cases gracefully
    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5
        
    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = float(np.mean(y_true))
        
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    brier = float(brier_score_loss(y_true, y_prob))
    cm = confusion_matrix(y_true, y_pred).tolist()
    
    return {
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4),
        "brier_score": round(brier, 4),
        "threshold": round(threshold, 3),
        "confusion_matrix": cm,
        "support_positive": int(np.sum(y_true)),
        "support_total": int(len(y_true)),
    }

class MajorityClassBaseline:
    """Predicts empirical training prior probability for all samples."""
    def __init__(self):
        self.prior = 0.0
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.prior = float(np.mean(y))
        return self
        
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.prior)

class HeuristicTransitionBaseline:
    """Simple heuristic baseline: predicts higher expansion probability for first-time artist plays and high-duration plays."""
    def __init__(self):
        pass
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        return self
        
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        # Heuristic scoring formula: combines first artist play with listening seconds
        is_first = X.get("is_first_artist_play", 0).values
        sec = np.clip(X.get("seconds_played", 0).values / 200.0, 0, 1)
        prob = 0.05 + 0.35 * is_first + 0.15 * sec
        return np.clip(prob, 0.01, 0.99)

def train_and_eval_baselines(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
    target_col: str = "target_expansion_7d"
) -> Dict[str, Any]:
    """Train and evaluate Majority Class, Heuristic, and Logistic Regression baselines."""
    X_train, y_train = df_train[FEATURE_COLUMNS], df_train[target_col].values
    X_val, y_val = df_val[FEATURE_COLUMNS], df_val[target_col].values
    X_test, y_test = df_test[FEATURE_COLUMNS], df_test[target_col].values
    
    # 1. Majority Class
    maj = MajorityClassBaseline().fit(X_train, y_train)
    maj_val_prob = maj.predict_proba(X_val)
    maj_test_prob = maj.predict_proba(X_test)
    maj_metrics = evaluate_predictions(y_test, maj_test_prob)
    
    # 2. Heuristic Baseline
    heur = HeuristicTransitionBaseline().fit(X_train, y_train)
    heur_test_prob = heur.predict_proba(X_test)
    heur_metrics = evaluate_predictions(y_test, heur_test_prob, threshold=0.25)
    
    # 3. Logistic Regression (Standardized)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    
    lr_val_prob = lr.predict_proba(X_val_scaled)[:, 1]
    lr_test_prob = lr.predict_proba(X_test_scaled)[:, 1]
    
    # Find best threshold on validation set
    best_thresh = 0.5
    best_f1 = 0.0
    for th in np.linspace(0.1, 0.9, 17):
        m = evaluate_predictions(y_val, lr_val_prob, threshold=th)
        if m["f1"] > best_f1:
            best_f1 = m["f1"]
            best_thresh = th
            
    lr_metrics = evaluate_predictions(y_test, lr_test_prob, threshold=best_thresh)
    
    return {
        "majority_class": maj_metrics,
        "heuristic": heur_metrics,
        "logistic_regression": lr_metrics,
        "models": {
            "logistic_regression": lr,
            "scaler": scaler
        }
    }
