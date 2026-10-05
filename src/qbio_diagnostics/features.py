"""Feature compression: image patch -> N-qubit real-valued vector."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split


@dataclass
class FeatureBundle:
    x_train: np.ndarray
    x_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    pca: PCA | None
    scaler: MinMaxScaler


def flatten_images(images: np.ndarray) -> np.ndarray:
    return images.reshape(images.shape[0], -1)


def handcrafted_patch_features(images: np.ndarray) -> np.ndarray:
    flat = flatten_images(images)
    mean = flat.mean(axis=1)
    std = flat.std(axis=1)
    maxv = flat.max(axis=1)
    bright_ratio = (flat > 0.72).mean(axis=1)
    # Local contrast approximates lesion boundary sharpness.
    gy = np.abs(np.diff(images, axis=1)).mean(axis=(1, 2))
    gx = np.abs(np.diff(images, axis=2)).mean(axis=(1, 2))
    contrast = gx + gy
    return np.column_stack([mean, std, maxv, bright_ratio, contrast])


def make_qubit_features(images: np.ndarray, labels: np.ndarray, qubits: int = 4, test_size: float = 0.25, seed: int = 7) -> FeatureBundle:
    # For a demo, use interpretable diagnostic features, then compress to N qubits.
    base_features = handcrafted_patch_features(images)
    x_train_raw, x_test_raw, y_train, y_test = train_test_split(
        base_features, labels, test_size=test_size, random_state=seed, stratify=labels
    )

    if base_features.shape[1] > qubits:
        pca = PCA(n_components=qubits, random_state=seed)
        x_train = pca.fit_transform(StandardScaler().fit_transform(x_train_raw))
        x_test = pca.transform(StandardScaler().fit(x_train_raw).transform(x_test_raw))
    else:
        pca = None
        x_train = x_train_raw
        x_test = x_test_raw

    # Qiskit angle encodings work cleanly when features are in [0, pi].
    scaler = MinMaxScaler(feature_range=(0, np.pi))
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    return FeatureBundle(x_train, x_test, y_train, y_test, pca, scaler)
