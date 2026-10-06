from __future__ import annotations

import numpy as np
import pytest

from qbio_diagnostics.data import generate_synthetic_biomedical_patches
from qbio_diagnostics.features import make_qubit_features
from qbio_diagnostics.metrics import classification_metrics


def test_generate_synthetic_biomedical_patches_creates_balanced_dataset() -> None:
    dataset = generate_synthetic_biomedical_patches(n_samples=40, seed=7)

    assert dataset.images.shape == (40, 16, 16)
    assert dataset.labels.shape == (40,)
    assert set(np.unique(dataset.labels)).issubset({0, 1})
    assert dataset.images.dtype == np.float32
    assert dataset.labels.dtype == np.int64


def test_make_qubit_features_produces_expected_shapes() -> None:
    dataset = generate_synthetic_biomedical_patches(n_samples=80, seed=11)
    bundle = make_qubit_features(dataset.images, dataset.labels, qubits=4, seed=9)

    assert bundle.x_train.shape[1] == 4
    assert bundle.x_test.shape[1] == 4
    assert bundle.x_train.shape[0] == len(bundle.y_train)
    assert bundle.x_test.shape[0] == len(bundle.y_test)
    assert bundle.x_train.min() >= 0.0
    assert bundle.x_test.max() <= np.pi


def test_classification_metrics_compute_standard_scores() -> None:
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    y_score = np.array([0.1, 0.6, 0.8, 0.9])

    metrics = classification_metrics(y_true, y_pred, y_score)

    assert metrics["accuracy"] == pytest.approx(0.75)
    assert metrics["macro_f1"] == pytest.approx(0.7333333333333334)
    assert metrics["auc_roc"] == pytest.approx(1.0)
