"""Leakage-safe 5-fold stratified validation for classical and quantum models."""
from __future__ import annotations

from typing import Dict
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from .features import make_fold_qubit_features
from .quantum_reference import pure_state_kernel


def _stats(rows: list[dict]) -> dict:
    out = {"folds": rows}
    for key in ("accuracy", "macro_f1", "auc_roc"):
        vals = np.asarray([r[key] for r in rows], dtype=float)
        out[f"mean_{key}"] = float(vals.mean())
        out[f"std_{key}"] = float(vals.std(ddof=0))
    return out


def run_stratified_5fold_cv(images: np.ndarray, labels: np.ndarray, qubits: int = 4, seed: int = 7) -> Dict[str, object]:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    classical_rows: list[dict] = []
    quantum_rows: list[dict] = []

    for fold, (tr_idx, te_idx) in enumerate(skf.split(images, labels), start=1):
        x_tr, x_te, _ = make_fold_qubit_features(images, tr_idx, te_idx, qubits=qubits, seed=seed)
        y_tr, y_te = labels[tr_idx], labels[te_idx]

        classical = SVC(kernel="rbf", C=2.0, gamma="scale", probability=True, random_state=seed)
        classical.fit(x_tr, y_tr)
        c_pred = classical.predict(x_te)
        c_score = classical.predict_proba(x_te)[:, 1]
        classical_rows.append({
            "fold": fold,
            "accuracy": float(accuracy_score(y_te, c_pred)),
            "macro_f1": float(f1_score(y_te, c_pred, average="macro")),
            "auc_roc": float(roc_auc_score(y_te, c_score)),
        })

        k_tr = pure_state_kernel(x_tr, reps=1, entanglement="full")
        k_te = pure_state_kernel(x_te, x_tr, reps=1, entanglement="full")
        quantum = SVC(kernel="precomputed", C=2.0, probability=True, random_state=seed)
        quantum.fit(k_tr, y_tr)
        q_pred = quantum.predict(k_te)
        q_score = quantum.predict_proba(k_te)[:, 1]
        quantum_rows.append({
            "fold": fold,
            "accuracy": float(accuracy_score(y_te, q_pred)),
            "macro_f1": float(f1_score(y_te, q_pred, average="macro")),
            "auc_roc": float(roc_auc_score(y_te, q_score)),
        })

    return {
        "protocol": "5-fold stratified cross-validation; feature scaling fit inside each training fold",
        "classical_rbf_svm": _stats(classical_rows),
        "reference_quantum_kernel_svm": _stats(quantum_rows),
        "note": "Reference quantum-kernel CV reproduces the circuit mathematics without claiming IBM hardware execution.",
    }
