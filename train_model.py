"""
Model Training and Evaluation Pipeline.
Algorithm: Logistic Regression (L2 Regularized)
Solver: lbfgs / saga

Evaluates:
- Accuracy
- Precision
- Recall
- F1 Score
- Matthews Correlation Coefficient (MCC)
- ROC-AUC Curve & Score (Binary and Multi-class One-vs-Rest)
"""

import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import label_binarize, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    matthews_corrcoef, roc_auc_score, roc_curve, auc, classification_report
)

def train_and_evaluate():
    ws_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(ws_dir, "movies_featured.csv")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing {data_path}. Please run feature_engineering.py first.")
        
    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} records with {df.shape[1]} columns.")
    
    # Feature construction: NLP representation combining title, franchise root, decade, era
    df['feature_text'] = (
        df['clean_title'].astype(str) + " " +
        df['franchise_root'].astype(str) + " " +
        df['decade'].astype(str) + " " +
        df['era'].astype(str)
    ).fillna('')

    # =========================================================================
    # Task 1: Binary Genre Classification (Action vs Non-Action)
    # =========================================================================
    print("\n=======================================================")
    print("1. Binary Classification: Action vs Non-Action")
    print("   Algorithm: Logistic Regression (L2 Penalty, C=1.0)")
    print("=======================================================")
    
    sample_n = min(30000, len(df))
    sample_bin = df.sample(n=sample_n, random_state=42)
    
    tfidf_bin = TfidfVectorizer(max_features=4000, stop_words='english', ngram_range=(1, 2))
    X_bin = tfidf_bin.fit_transform(sample_bin['feature_text'])
    y_bin = np.array(sample_bin['genre_action'].tolist(), dtype=int)
    
    X_tr_b, X_te_b, y_tr_b, y_te_b = train_test_split(
        X_bin, y_bin, test_size=0.2, random_state=42, stratify=y_bin
    )
    
    model_bin = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    t0 = time.time()
    model_bin.fit(X_tr_b, y_tr_b)
    y_pred_b = model_bin.predict(X_te_b)
    y_prob_b = model_bin.predict_proba(X_te_b)[:, 1]
    t_bin = time.time() - t0
    
    bin_metrics = {
        "Accuracy": float(accuracy_score(y_te_b, y_pred_b)),
        "Precision": float(precision_score(y_te_b, y_pred_b, zero_division=0)),
        "Recall": float(recall_score(y_te_b, y_pred_b, zero_division=0)),
        "F1 Score": float(f1_score(y_te_b, y_pred_b, zero_division=0)),
        "MCC": float(matthews_corrcoef(y_te_b, y_pred_b)),
        "ROC AUC": float(roc_auc_score(y_te_b, y_prob_b))
    }
    
    fpr_b, tpr_b, _ = roc_curve(y_te_b, y_prob_b)
    
    print(f"Trained & Evaluated in: {t_bin:.2f} seconds")
    for metric_name, val in bin_metrics.items():
        print(f"  {metric_name:12s}: {val:.4f}")
        
    # Plot Binary ROC Curve
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    fig.patch.set_facecolor('#0d0c15')
    ax.set_facecolor('#13111f')
    
    ax.plot(fpr_b, tpr_b, color='#38bdf8', lw=2.8, label=f'Logistic Regression (AUC = {bin_metrics["ROC AUC"]:.3f})')
    ax.plot([0, 1], [0, 1], color='#64748b', lw=1.5, linestyle='--', label='Chance Baseline (AUC = 0.500)')
    
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.05])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12, color='#e2e8f0', labelpad=10)
    ax.set_ylabel('True Positive Rate (Recall / Sensitivity)', fontsize=12, color='#e2e8f0', labelpad=10)
    ax.set_title('Binary ROC Curve: Action Movie Prediction\n(Logistic Regression with L2 Regularization)', fontsize=13, fontweight='bold', color='#ffffff', pad=14)
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_color('#2e284a')
    ax.legend(loc="lower right", fontsize=10.5, facecolor='#1e1b2e', edgecolor='#0284c7', labelcolor='#ffffff')
    ax.grid(True, linestyle=':', alpha=0.35, color='#64748b')
    
    plt.tight_layout()
    bin_plot_path = os.path.join(ws_dir, "roc_curve_binary.png")
    plt.savefig(bin_plot_path)
    plt.close()
    print(f"Saved Binary ROC Curve: {bin_plot_path}")

    # =========================================================================
    # Task 2: Multi-Class Genre Prediction (Top 5 Primary Genres)
    # =========================================================================
    print("\n=======================================================")
    print("2. Multi-Class Classification: Top 5 Primary Genres")
    print("   (Drama, Comedy, Action, Documentary, Horror)")
    print("   Algorithm: Logistic Regression (Multinomial, C=1.0)")
    print("=======================================================")
    
    top_genres = ['Drama', 'Comedy', 'Action', 'Documentary', 'Horror']
    sub_df = df[df['primary_genre'].isin(top_genres)].copy()
    sub_sample = sub_df.sample(n=min(25000, len(sub_df)), random_state=42)
    
    tfidf_multi = TfidfVectorizer(max_features=4000, stop_words='english', ngram_range=(1, 2))
    X_multi = tfidf_multi.fit_transform(sub_sample['feature_text'])
    
    le = LabelEncoder()
    y_multi = le.fit_transform(sub_sample['primary_genre'].values)
    classes = le.classes_
    
    X_tr_m, X_te_m, y_tr_m, y_te_m = train_test_split(
        X_multi, y_multi, test_size=0.2, random_state=42, stratify=y_multi
    )
    
    y_te_bin = label_binarize(y_te_m, classes=range(len(classes)))
    
    model_multi = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    t0 = time.time()
    model_multi.fit(X_tr_m, y_tr_m)
    y_pred_m = model_multi.predict(X_te_m)
    y_prob_m = model_multi.predict_proba(X_te_m)
    t_multi = time.time() - t0
    
    multi_metrics = {
        "Accuracy": float(accuracy_score(y_te_m, y_pred_m)),
        "Precision (Weighted)": float(precision_score(y_te_m, y_pred_m, average='weighted', zero_division=0)),
        "Recall (Weighted)": float(recall_score(y_te_m, y_pred_m, average='weighted', zero_division=0)),
        "F1 Score (Weighted)": float(f1_score(y_te_m, y_pred_m, average='weighted', zero_division=0)),
        "MCC": float(matthews_corrcoef(y_te_m, y_pred_m)),
        "ROC AUC (Weighted OvR)": float(roc_auc_score(y_te_bin, y_prob_m, multi_class='ovr', average='weighted'))
    }
    
    print(f"Trained & Evaluated in: {t_multi:.2f} seconds")
    for metric_name, val in multi_metrics.items():
        print(f"  {metric_name:24s}: {val:.4f}")
        
    print("\nDetailed Classification Report:")
    print(classification_report(y_te_m, y_pred_m, target_names=classes, digits=4, zero_division=0))
    
    # Plot Multi-Class One-vs-Rest ROC Curves
    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=150)
    fig.patch.set_facecolor('#0d0c15')
    ax.set_facecolor('#13111f')
    
    palette = ['#38bdf8', '#fbbf24', '#f43f5e', '#34d399', '#a855f7']
    for i, (genre, col) in enumerate(zip(classes, palette)):
        fpr_cls, tpr_cls, _ = roc_curve(y_te_bin[:, i], y_prob_m[:, i])
        cls_auc = auc(fpr_cls, tpr_cls)
        ax.plot(fpr_cls, tpr_cls, color=col, lw=2.2, label=f'{genre} (AUC = {cls_auc:.3f})')
        
    ax.plot([0, 1], [0, 1], color='#64748b', lw=1.5, linestyle='--', label='Chance Baseline (AUC = 0.500)')
    
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.05])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12, color='#e2e8f0', labelpad=10)
    ax.set_ylabel('True Positive Rate (Recall / Sensitivity)', fontsize=12, color='#e2e8f0', labelpad=10)
    ax.set_title(f'One-vs-Rest ROC Curves: Top 5 Genre Prediction\n(Logistic Regression, Weighted OvR AUC = {multi_metrics["ROC AUC (Weighted OvR)"]:.3f})',
                 fontsize=13, fontweight='bold', color='#ffffff', pad=14)
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_color('#2e284a')
    ax.legend(loc="lower right", fontsize=10, facecolor='#1e1b2e', edgecolor='#0284c7', labelcolor='#ffffff')
    ax.grid(True, linestyle=':', alpha=0.35, color='#64748b')
    
    plt.tight_layout()
    multi_plot_path = os.path.join(ws_dir, "roc_curve_multiclass.png")
    plt.savefig(multi_plot_path)
    plt.close()
    print(f"Saved Multi-Class ROC Curve: {multi_plot_path}")

    return {
        "binary_metrics": bin_metrics,
        "multiclass_metrics": multi_metrics,
        "binary_plot": bin_plot_path,
        "multiclass_plot": multi_plot_path
    }

if __name__ == "__main__":
    train_and_evaluate()
