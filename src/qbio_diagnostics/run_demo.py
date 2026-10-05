from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from .data import generate_synthetic_biomedical_patches, save_montage
from .features import make_qubit_features
from .train_classical import train_classical_svm
from .train_qsvc import train_quantum_qsvc
from .metrics import save_confusion_matrix, save_roc_curve
from .noise_resilience import run_zne_feature_map_demo
from .pinecone_store import upsert_cases


def _learning_curve_plot(bundle, out_path: Path) -> None:
    from sklearn.svm import SVC
    sizes = [20, 40, 80, min(120, len(bundle.x_train))]
    classical_scores = []
    quantum_like_scores = []
    for n in sizes:
        x = bundle.x_train[:n]
        y = bundle.y_train[:n]
        classical = SVC(kernel="rbf", C=2.0, gamma="scale").fit(x, y)
        quantum_like = SVC(kernel="poly", degree=2, C=2.0).fit(x, y)
        classical_scores.append(classical.score(bundle.x_test, bundle.y_test))
        quantum_like_scores.append(quantum_like.score(bundle.x_test, bundle.y_test))
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.plot(sizes, classical_scores, marker="o", label="Classical RBF SVM")
    ax.plot(sizes, quantum_like_scores, marker="o", label="Quantum-kernel proxy / QSVC fallback")
    ax.set_xlabel("Training samples")
    ax.set_ylabel("Accuracy")
    ax.set_title("Small-data learning curve")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=160)
    parser.add_argument("--qubits", type=int, default=4)
    parser.add_argument("--use-pinecone", action="store_true")
    args = parser.parse_args()

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    dataset = generate_synthetic_biomedical_patches(n_samples=args.samples)
    save_montage(dataset, out_dir / "sample_patches.png")
    bundle = make_qubit_features(dataset.images, dataset.labels, qubits=args.qubits)

    classical_model, c_pred, c_score, c_metrics = train_classical_svm(bundle.x_train, bundle.y_train, bundle.x_test, bundle.y_test)
    q_model, q_pred, q_score, q_metrics, q_backend = train_quantum_qsvc(bundle.x_train, bundle.y_train, bundle.x_test, bundle.y_test)

    save_confusion_matrix(bundle.y_test, q_pred, out_dir / "quantum_confusion_matrix.png", "Q-BioDiag QSVC Confusion Matrix")
    save_roc_curve(bundle.y_test, q_score, out_dir / "quantum_roc_curve.png", "Q-BioDiag QSVC ROC Curve")
    _learning_curve_plot(bundle, out_dir / "learning_curve.png")

    zne = run_zne_feature_map_demo(bundle.x_test[0])
    vector_status = upsert_cases(bundle.x_train, bundle.y_train, out_dir, use_pinecone=args.use_pinecone)

    summary = {
        "dataset": {"samples": int(args.samples), "patch_size": "16x16", "qubits": int(args.qubits)},
        "classical_baseline": c_metrics,
        "quantum_qsvc": q_metrics,
        "quantum_backend": q_backend,
        "parameter_efficiency_note": "QSVC optimizes support vectors/kernel boundary, not a deep CNN with thousands of trainable weights.",
        "noise_zne_demo": zne,
        "vector_database": vector_status,
    }
    (out_dir / "metrics_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
