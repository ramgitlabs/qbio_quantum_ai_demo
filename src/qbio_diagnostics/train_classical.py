from __future__ import annotations

import numpy as np
from sklearn.svm import SVC
from .metrics import classification_metrics


def train_classical_svm(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray):
    model = SVC(kernel="rbf", probability=True, C=2.0, gamma="scale", random_state=7)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    score = model.predict_proba(x_test)[:, 1]
    metrics = classification_metrics(y_test, pred, score)
    return model, pred, score, metrics
