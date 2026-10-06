"""Optional IBM Quantum hardware benchmark for a very small kernel subset.

This module is intentionally separate from the default demo so the repository
never claims hardware execution unless the participant explicitly runs it with
an IBM Quantum account. It writes `outputs/ibm_hardware_metrics.json` only after
a real job completes.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from .data import generate_synthetic_biomedical_patches
from .features import make_qubit_features


def _overlap_circuit(x: np.ndarray, y: np.ndarray):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import zz_feature_map

    fmap = zz_feature_map(feature_dimension=len(x), reps=1, entanglement="full")
    params = list(fmap.parameters)
    ux = fmap.assign_parameters(dict(zip(params, map(float, x))), inplace=False)
    uy = fmap.assign_parameters(dict(zip(params, map(float, y))), inplace=False)
    qc = QuantumCircuit(len(x))
    qc.compose(ux, inplace=True)
    qc.compose(uy.inverse(), inplace=True)
    qc.measure_all()
    return qc


def _kernel_pairs(left: np.ndarray, right: np.ndarray, symmetric: bool = False):
    circuits = []
    coords = []
    if symmetric:
        for i in range(len(left)):
            for j in range(i, len(right)):
                circuits.append(_overlap_circuit(left[i], right[j]))
                coords.append((i, j))
    else:
        for i in range(len(left)):
            for j in range(len(right)):
                circuits.append(_overlap_circuit(left[i], right[j]))
                coords.append((i, j))
    return circuits, coords


def _execute_prob_zero(circuits, shots: int, backend):
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa = [pm.run(c) for c in circuits]
    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa, shots=shots)
    result = job.result()
    zeros = "0" * circuits[0].num_qubits
    probs = []
    for pub_result in result:
        counts = pub_result.data.meas.get_counts()
        probs.append(float(counts.get(zeros, 0) / shots))
    return probs, job.job_id()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=int, default=12, help="Small balanced training subset for QPU cost control")
    parser.add_argument("--test", type=int, default=8, help="Small balanced test subset for QPU cost control")
    parser.add_argument("--shots", type=int, default=1024)
    args = parser.parse_args()

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except Exception as exc:
        raise SystemExit(f"Install qiskit-ibm-runtime first: {exc}")

    token = os.getenv("IBM_QUANTUM_TOKEN") or os.getenv("QISKIT_IBM_TOKEN")
    service = QiskitRuntimeService(token=token) if token else QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=4)

    ds = generate_synthetic_biomedical_patches(160)
    bundle = make_qubit_features(ds.images, ds.labels, qubits=4)

    # deterministic balanced subsets from the already held-out split
    def balanced_take(x, y, n):
        n0 = n // 2
        n1 = n - n0
        idx0 = np.where(y == 0)[0][:n0]
        idx1 = np.where(y == 1)[0][:n1]
        idx = np.concatenate([idx0, idx1])
        return x[idx], y[idx]

    xtr, ytr = balanced_take(bundle.x_train, bundle.y_train, args.train)
    xte, yte = balanced_take(bundle.x_test, bundle.y_test, args.test)

    tr_circuits, tr_coords = _kernel_pairs(xtr, xtr, symmetric=True)
    tr_probs, job_train = _execute_prob_zero(tr_circuits, args.shots, backend)
    ktr = np.eye(len(xtr))
    for (i, j), p in zip(tr_coords, tr_probs):
        ktr[i, j] = ktr[j, i] = p

    te_circuits, te_coords = _kernel_pairs(xte, xtr, symmetric=False)
    te_probs, job_test = _execute_prob_zero(te_circuits, args.shots, backend)
    kte = np.zeros((len(xte), len(xtr)))
    for (i, j), p in zip(te_coords, te_probs):
        kte[i, j] = p

    model = SVC(kernel="precomputed", C=2.0, probability=True, random_state=7)
    model.fit(ktr, ytr)
    pred = model.predict(kte)
    score = model.predict_proba(kte)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(yte, pred)),
        "macro_f1": float(f1_score(yte, pred, average="macro")),
        "auc_roc": float(roc_auc_score(yte, score)),
    }

    out = {
        "status": "completed_real_ibm_quantum_hardware",
        "backend": backend.name,
        "shots": args.shots,
        "train_samples": len(xtr),
        "test_samples": len(xte),
        "metrics": metrics,
        "job_ids": [job_train, job_test],
        "warning": "This is a small hardware feasibility benchmark, not a clinical validation result.",
    }
    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/ibm_hardware_metrics.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
