from __future__ import annotations

import numpy as np
from .metrics import classification_metrics


def train_quantum_qsvc(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray):
    """Train a Qiskit quantum-kernel support-vector classifier.

    The main hackathon path uses Qiskit. If qiskit-machine-learning is not installed,
    a polynomial SVM fallback keeps the dashboard runnable, but the README and deck
    should present the Qiskit path.
    """
    try:
        from qiskit.circuit.library import ZZFeatureMap
        from qiskit_machine_learning.kernels import FidelityQuantumKernel
        from qiskit_machine_learning.algorithms import QSVC

        feature_map = ZZFeatureMap(
            feature_dimension=x_train.shape[1], reps=2, entanglement="linear"
        )
        quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)
        model = QSVC(quantum_kernel=quantum_kernel, probability=True)
        backend = "qiskit-qsvc"
    except Exception as exc:  # pragma: no cover - fallback for machines without Qiskit
        from sklearn.svm import SVC

        model = SVC(kernel="poly", degree=2, probability=True, C=2.0, random_state=7)
        backend = f"fallback-poly-svm: {exc.__class__.__name__}"

    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    if hasattr(model, "predict_proba"):
        score = model.predict_proba(x_test)[:, 1]
    else:
        score = pred.astype(float)
    metrics = classification_metrics(y_test, pred, score)
    return model, pred, score, metrics, backend
