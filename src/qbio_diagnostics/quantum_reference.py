"""Small reference simulator for the 4-qubit ZZ-style feature map used by Q-BioDiag.

This module exists for reproducibility on machines where Qiskit is not installed.
It does NOT claim IBM Quantum hardware execution. When Qiskit is available, the
main classifier uses Qiskit's zz_feature_map + FidelityQuantumKernel instead.

For ideal pure states the kernel is |<phi(x)|phi(y)>|^2. For the noise study we
propagate density matrices through depolarizing channels and use the
Hilbert-Schmidt overlap Tr(rho_x rho_y), which remains a positive-semidefinite
similarity kernel because it is an inner product in operator space.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product
import numpy as np

_I2 = np.eye(2, dtype=complex)
_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_PAULIS = (_I2, _X, _Y, _Z)


def _phase(theta: float) -> np.ndarray:
    return np.array([[1.0, 0.0], [0.0, np.exp(1j * theta)]], dtype=complex)


def _kron_all(mats: list[np.ndarray]) -> np.ndarray:
    out = mats[0]
    for mat in mats[1:]:
        out = np.kron(out, mat)
    return out


@lru_cache(maxsize=None)
def _single_qubit_operator_cached(n: int, q: int, gate_key: str, theta_key: float = 0.0) -> np.ndarray:
    if gate_key == "H":
        gate = _H
    elif gate_key == "P":
        gate = _phase(theta_key)
    elif gate_key == "X":
        gate = _X
    elif gate_key == "Y":
        gate = _Y
    elif gate_key == "Z":
        gate = _Z
    else:
        raise ValueError(gate_key)
    # Qiskit-style little-endian indexing: q0 is the right-most tensor factor.
    mats = [_I2.copy() for _ in range(n)]
    mats[n - 1 - q] = gate
    return _kron_all(mats)


def _single_qubit_operator(gate: np.ndarray, q: int, n: int) -> np.ndarray:
    mats = [_I2 for _ in range(n)]
    mats[n - 1 - q] = gate
    return _kron_all(mats)


@lru_cache(maxsize=None)
def _cx_operator(n: int, control: int, target: int) -> np.ndarray:
    dim = 2**n
    op = np.zeros((dim, dim), dtype=complex)
    for basis in range(dim):
        mapped = basis ^ (1 << target) if ((basis >> control) & 1) else basis
        op[mapped, basis] = 1.0
    return op


def _feature_operations(x: np.ndarray, reps: int = 1, entanglement: str = "full"):
    n = len(x)
    if entanglement == "linear":
        pairs = [(i, i + 1) for i in range(n - 1)]
    elif entanglement == "full":
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    else:
        raise ValueError("entanglement must be 'linear' or 'full'")

    for _ in range(reps):
        for q in range(n):
            yield ("1q", q, _H)
        for q in range(n):
            yield ("1q", q, _phase(2.0 * float(x[q])))
        for a, b in pairs:
            yield ("2q", (a, b), _cx_operator(n, a, b))
            zz_angle = 2.0 * (np.pi - float(x[a])) * (np.pi - float(x[b]))
            yield ("1q", b, _phase(zz_angle))
            yield ("2q", (a, b), _cx_operator(n, a, b))


def feature_state(x: np.ndarray, reps: int = 1, entanglement: str = "full") -> np.ndarray:
    x = np.asarray(x, dtype=float)
    n = len(x)
    psi = np.zeros(2**n, dtype=complex)
    psi[0] = 1.0
    for kind, loc, gate in _feature_operations(x, reps=reps, entanglement=entanglement):
        if kind == "1q":
            psi = _single_qubit_operator(gate, int(loc), n) @ psi
        else:
            psi = gate @ psi
    return psi


def state_matrix(x: np.ndarray, reps: int = 1, entanglement: str = "full") -> np.ndarray:
    return np.vstack([feature_state(row, reps=reps, entanglement=entanglement) for row in np.asarray(x)])


def pure_state_kernel(x_left: np.ndarray, x_right: np.ndarray | None = None, reps: int = 1, entanglement: str = "full") -> np.ndarray:
    left_states = state_matrix(x_left, reps=reps, entanglement=entanglement)
    right_states = left_states if x_right is None else state_matrix(x_right, reps=reps, entanglement=entanglement)
    return np.abs(left_states @ right_states.conj().T) ** 2


def _apply_depolarizing_1q(rho: np.ndarray, q: int, n: int, p: float) -> np.ndarray:
    if p <= 0:
        return rho
    accum = np.zeros_like(rho)
    for pauli in (_X, _Y, _Z):
        op = _single_qubit_operator(pauli, q, n)
        accum += op @ rho @ op.conj().T
    return (1.0 - p) * rho + (p / 3.0) * accum


@lru_cache(maxsize=None)
def _two_qubit_pauli_operator(n: int, a: int, b: int, ia: int, ib: int) -> np.ndarray:
    mats = [_I2 for _ in range(n)]
    mats[n - 1 - a] = _PAULIS[ia]
    mats[n - 1 - b] = _PAULIS[ib]
    return _kron_all(mats)


def _apply_depolarizing_2q(rho: np.ndarray, a: int, b: int, n: int, p: float) -> np.ndarray:
    if p <= 0:
        return rho
    accum = np.zeros_like(rho)
    for ia, ib in product(range(4), repeat=2):
        if ia == 0 and ib == 0:
            continue
        op = _two_qubit_pauli_operator(n, a, b, ia, ib)
        accum += op @ rho @ op.conj().T
    return (1.0 - p) * rho + (p / 15.0) * accum


def noisy_feature_density(
    x: np.ndarray,
    p1: float = 0.003,
    p2: float = 0.015,
    noise_scale: float = 1.0,
    reps: int = 1,
    entanglement: str = "full",
) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    n = len(x)
    psi0 = np.zeros(2**n, dtype=complex)
    psi0[0] = 1.0
    rho = np.outer(psi0, psi0.conj())
    p1s = min(float(p1) * float(noise_scale), 0.95)
    p2s = min(float(p2) * float(noise_scale), 0.95)

    for kind, loc, gate in _feature_operations(x, reps=reps, entanglement=entanglement):
        if kind == "1q":
            op = _single_qubit_operator(gate, int(loc), n)
            rho = op @ rho @ op.conj().T
            rho = _apply_depolarizing_1q(rho, int(loc), n, p1s)
        else:
            rho = gate @ rho @ gate.conj().T
            a, b = loc
            rho = _apply_depolarizing_2q(rho, int(a), int(b), n, p2s)
    return rho


def density_matrix_stack(
    x: np.ndarray,
    p1: float = 0.003,
    p2: float = 0.015,
    noise_scale: float = 1.0,
    reps: int = 1,
    entanglement: str = "full",
) -> np.ndarray:
    return np.stack([
        noisy_feature_density(row, p1=p1, p2=p2, noise_scale=noise_scale, reps=reps, entanglement=entanglement)
        for row in np.asarray(x)
    ])


def density_overlap_kernel(rho_left: np.ndarray, rho_right: np.ndarray | None = None) -> np.ndarray:
    right = rho_left if rho_right is None else rho_right
    # Tr(A B) = sum_ij A_ij * B_ji. einsum vectorizes all pairwise overlaps.
    k = np.einsum("aij,bji->ab", rho_left, right, optimize=True).real
    return np.clip(k, 0.0, 1.0)


def nearest_psd_correlation(kernel: np.ndarray) -> np.ndarray:
    k = (np.asarray(kernel, dtype=float) + np.asarray(kernel, dtype=float).T) / 2.0
    vals, vecs = np.linalg.eigh(k)
    vals = np.clip(vals, 1e-9, None)
    k = (vecs * vals) @ vecs.T
    diag = np.sqrt(np.clip(np.diag(k), 1e-12, None))
    k = k / np.outer(diag, diag)
    return np.clip((k + k.T) / 2.0, 0.0, 1.0)


def zne_extrapolate_kernels(kernels: list[np.ndarray], scale_factors: list[float]) -> np.ndarray:
    stack = np.stack(kernels, axis=0)
    scales = np.asarray(scale_factors, dtype=float)
    # Linear fit per kernel element. intercept at scale=0 is the ZNE estimate.
    xbar = scales.mean()
    ybar = stack.mean(axis=0)
    slope = np.sum((scales - xbar)[:, None, None] * (stack - ybar), axis=0) / np.sum((scales - xbar) ** 2)
    intercept = ybar - slope * xbar
    intercept = np.clip(intercept, 0.0, 1.0)
    if intercept.shape[0] == intercept.shape[1]:
        return nearest_psd_correlation(intercept)
    return intercept
