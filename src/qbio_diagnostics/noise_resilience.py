"""Classifier-level noise-resilience benchmark for the quantum kernel."""
from __future__ import annotations

from typing import Dict
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from .quantum_reference import (
    pure_state_kernel,
    density_matrix_stack,
    density_overlap_kernel,
    zne_extrapolate_kernels,
)


def _evaluate_precomputed(k_train, k_test, y_train, y_test) -> dict:
    model = SVC(kernel="precomputed", C=2.0, probability=True, random_state=7)
    model.fit(k_train, y_train)
    pred = model.predict(k_test)
    score = model.predict_proba(k_test)[:, 1]
    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro")),
        "auc_roc": float(roc_auc_score(y_test, score)),
    }


def run_noise_classification_benchmark(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    p1: float = 0.015,
    p2: float = 0.060,
) -> Dict[str, object]:
    """Compare ideal, noisy, and ZNE-mitigated classifier performance.

    If Qiskit Aer is available in the participant environment, the repository can
    be extended to execute the same circuits there. The packaged metrics are from
    the deterministic reference density-matrix simulator and are explicitly
    labeled as such, never as IBM hardware results.
    """
    ideal_train = pure_state_kernel(x_train, reps=1, entanglement="full")
    ideal_test = pure_state_kernel(x_test, x_train, reps=1, entanglement="full")
    ideal_metrics = _evaluate_precomputed(ideal_train, ideal_test, y_train, y_test)

    scales = [1.0, 2.0, 3.0]
    train_ks = []
    test_ks = []
    for scale in scales:
        rho_tr = density_matrix_stack(x_train, p1=p1, p2=p2, noise_scale=scale, reps=1, entanglement="full")
        rho_te = density_matrix_stack(x_test, p1=p1, p2=p2, noise_scale=scale, reps=1, entanglement="full")
        train_ks.append(density_overlap_kernel(rho_tr))
        test_ks.append(density_overlap_kernel(rho_te, rho_tr))

    noisy_metrics = _evaluate_precomputed(train_ks[0], test_ks[0], y_train, y_test)
    zne_train = zne_extrapolate_kernels(train_ks, scales)
    zne_test = zne_extrapolate_kernels(test_ks, scales)
    zne_metrics = _evaluate_precomputed(zne_train, zne_test, y_train, y_test)

    aer_available = False
    aer_detail = None
    try:
        import qiskit_aer  # noqa: F401
        aer_available = True
        aer_detail = "Qiskit Aer detected; packaged numeric table remains reference-simulator output unless rerun with an Aer-specific path."
    except Exception as exc:
        aer_detail = f"Qiskit Aer not installed in packaging environment ({exc.__class__.__name__})."

    return {
        "simulator": "reference 4-qubit density-matrix simulator",
        "noise_model": {
            "one_qubit_depolarizing_probability": p1,
            "two_qubit_depolarizing_probability": p2,
            "scale_factors_for_zne": scales,
        },
        "ideal": ideal_metrics,
        "noisy": noisy_metrics,
        "zne_mitigated": zne_metrics,
        "qiskit_aer_available_in_packaging_environment": aer_available,
        "qiskit_aer_note": aer_detail,
        "ibm_hardware": {
            "status": "not_run",
            "reason": "Requires participant IBM Quantum account/token and queued QPU execution. No hardware result is claimed.",
        },
    }
