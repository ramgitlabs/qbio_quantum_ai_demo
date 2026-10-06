from __future__ import annotations

import numpy as np
from sklearn.svm import SVC
from .metrics import classification_metrics
from .quantum_reference import pure_state_kernel


class PrecomputedQuantumKernelModel:
    """Small wrapper used by the reference simulator path."""
    def __init__(self, svc: SVC, x_train: np.ndarray, reps: int = 1, entanglement: str = "full"):
        self.svc = svc
        self.x_train = np.asarray(x_train)
        self.reps = reps
        self.entanglement = entanglement

    def predict(self, x: np.ndarray):
        k = pure_state_kernel(np.asarray(x), self.x_train, reps=self.reps, entanglement=self.entanglement)
        return self.svc.predict(k)

    def decision_function(self, x: np.ndarray):
        k = pure_state_kernel(np.asarray(x), self.x_train, reps=self.reps, entanglement=self.entanglement)
        return self.svc.decision_function(k)


def train_quantum_qsvc(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray):
    """Train a fidelity quantum-kernel SVM.

    Preferred path: Qiskit Machine Learning `FidelityQuantumKernel` + QSVC.
    Reproducibility path: a NumPy statevector implementation of the same 4-qubit
    ZZ-style fidelity kernel. The fallback remains a quantum-kernel simulation;
    it never silently substitutes a polynomial/classical kernel.
    """
    reps = 1
    entanglement = "full"
    try:
        from qiskit.circuit.library import zz_feature_map
        from qiskit_machine_learning.kernels import FidelityQuantumKernel
        from qiskit_machine_learning.algorithms import QSVC

        feature_map = zz_feature_map(
            feature_dimension=x_train.shape[1], reps=reps, entanglement=entanglement
        )
        quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)
        model = QSVC(quantum_kernel=quantum_kernel, probability=True, C=2.0, random_state=7)
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        score = model.predict_proba(x_test)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(x_test)
        backend = "qiskit-fidelity-quantum-kernel-qsvc"
    except Exception as exc:
        k_train = pure_state_kernel(x_train, reps=reps, entanglement=entanglement)
        k_test = pure_state_kernel(x_test, x_train, reps=reps, entanglement=entanglement)
        svc = SVC(kernel="precomputed", probability=True, C=2.0, random_state=7)
        svc.fit(k_train, y_train)
        pred = svc.predict(k_test)
        score = svc.predict_proba(k_test)[:, 1]
        model = PrecomputedQuantumKernelModel(svc, x_train, reps=reps, entanglement=entanglement)
        backend = f"reference-quantum-kernel-numpy (Qiskit unavailable: {exc.__class__.__name__})"

    metrics = classification_metrics(y_test, pred, score)
    return model, pred, score, metrics, backend
