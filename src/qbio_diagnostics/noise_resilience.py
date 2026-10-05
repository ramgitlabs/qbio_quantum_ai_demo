"""Small Qiskit Aer noise and zero-noise extrapolation demo.

This is intentionally lightweight for hackathon demos. It shows how the encoded
quantum feature-map expectation can be evaluated under depolarizing noise and then
linearly extrapolated toward the zero-noise limit.
"""
from __future__ import annotations

from typing import Dict, List
import numpy as np


def run_zne_feature_map_demo(feature_vector: np.ndarray, shots: int = 512) -> Dict[str, object]:
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, depolarizing_error
    except Exception as exc:  # fallback keeps repo runnable
        return {
            "available": False,
            "reason": f"Qiskit Aer unavailable: {exc.__class__.__name__}",
            "zne_estimate": None,
            "noisy_expectations": [],
        }

    n = len(feature_vector)
    qc = QuantumCircuit(n, n)
    for i, angle in enumerate(feature_vector):
        qc.ry(float(angle), i)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure(range(n), range(n))

    scale_factors = [1.0, 2.0, 3.0]
    expectations: List[float] = []
    for scale in scale_factors:
        noise = NoiseModel()
        noise.add_all_qubit_quantum_error(depolarizing_error(0.01 * scale, 1), ["ry"])
        noise.add_all_qubit_quantum_error(depolarizing_error(0.02 * scale, 2), ["cx"])
        sim = AerSimulator(noise_model=noise)
        tqc = transpile(qc, sim)
        counts = sim.run(tqc, shots=shots).result().get_counts()
        # Z expectation on first qubit from measured bitstrings.
        exp_z = 0.0
        for bitstr, count in counts.items():
            first = bitstr[-1]
            exp_z += (1 if first == "0" else -1) * count / shots
        expectations.append(float(exp_z))

    coeffs = np.polyfit(scale_factors, expectations, deg=1)
    zne_estimate = float(np.polyval(coeffs, 0.0))
    return {
        "available": True,
        "scale_factors": scale_factors,
        "noisy_expectations": expectations,
        "zne_estimate": zne_estimate,
    }
