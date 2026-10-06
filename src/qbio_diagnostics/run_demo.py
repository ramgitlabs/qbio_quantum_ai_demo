from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.svm import SVC

from .data import generate_synthetic_biomedical_patches, save_montage
from .features import make_qubit_features
from .train_classical import train_classical_svm
from .train_qsvc import train_quantum_qsvc
from .metrics import save_confusion_matrix, save_roc_curve
from .quantum_reference import pure_state_kernel
from .noise_resilience import run_noise_classification_benchmark
from .validation import run_stratified_5fold_cv
from .pinecone_store import upsert_cases


def _learning_curve_plot(bundle, out_path: Path) -> dict:
    sizes = [20, 40, 80, min(120, len(bundle.x_train))]
    classical_scores = []
    quantum_scores = []
    y = bundle.y_train
    for n in sizes:
        if n >= len(y):
            idx = np.arange(len(y))
        else:
            splitter = StratifiedShuffleSplit(n_splits=1, train_size=n, random_state=7 + n)
            idx, _ = next(splitter.split(bundle.x_train, y))
        x = bundle.x_train[idx]
        yy = y[idx]
        classical = SVC(kernel="rbf", C=2.0, gamma="scale").fit(x, yy)
        classical_scores.append(float(classical.score(bundle.x_test, bundle.y_test)))

        k_train = pure_state_kernel(x, reps=1, entanglement="full")
        k_test = pure_state_kernel(bundle.x_test, x, reps=1, entanglement="full")
        quantum = SVC(kernel="precomputed", C=2.0).fit(k_train, yy)
        quantum_scores.append(float(quantum.score(k_test, bundle.y_test)))

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.plot(sizes, classical_scores, marker="o", label="Classical RBF SVM")
    ax.plot(sizes, quantum_scores, marker="o", label="4-qubit fidelity kernel")
    ax.set_xlabel("Training samples")
    ax.set_ylabel("Held-out accuracy")
    ax.set_ylim(0.5, 1.03)
    ax.set_title("Small-data learning curve")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return {"train_sizes": sizes, "classical_accuracy": classical_scores, "quantum_accuracy": quantum_scores}


def _cv_plot(cv: dict, out_path: Path) -> None:
    labels = ["Classical RBF\nSVM", "4-qubit quantum\nkernel"]
    means = [cv["classical_rbf_svm"]["mean_accuracy"], cv["reference_quantum_kernel_svm"]["mean_accuracy"]]
    stds = [cv["classical_rbf_svm"]["std_accuracy"], cv["reference_quantum_kernel_svm"]["std_accuracy"]]
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    ax.bar(labels, means, yerr=stds, capsize=6)
    ax.set_ylim(0.5, 1.03)
    ax.set_ylabel("Accuracy")
    ax.set_title("5-fold stratified cross-validation")
    ax.grid(axis="y", alpha=0.2)
    for i, m in enumerate(means):
        ax.text(i, m + 0.02, f"{m:.3f}", ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def _noise_plot(noise: dict, out_path: Path) -> None:
    labels = ["Ideal", "Noisy", "ZNE\nmitigated"]
    acc = [noise[k]["accuracy"] for k in ("ideal", "noisy", "zne_mitigated")]
    f1 = [noise[k]["macro_f1"] for k in ("ideal", "noisy", "zne_mitigated")]
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(6.3, 4.2))
    ax.bar(x - width / 2, acc, width, label="Accuracy")
    ax.bar(x + width / 2, f1, width, label="Macro-F1")
    ax.set_xticks(x, labels)
    ax.set_ylim(0.5, 1.03)
    ax.set_ylabel("Score")
    ax.set_title("Quantum-kernel resilience under depolarizing noise")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=160)
    parser.add_argument("--qubits", type=int, default=4)
    parser.add_argument("--use-pinecone", action="store_true")
    parser.add_argument("--skip-noise", action="store_true", help="Skip density-matrix noise benchmark for a faster smoke test")
    args = parser.parse_args()

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    dataset = generate_synthetic_biomedical_patches(n_samples=args.samples)
    save_montage(dataset, out_dir / "sample_patches.png")
    bundle = make_qubit_features(dataset.images, dataset.labels, qubits=args.qubits)

    _, c_pred, c_score, c_metrics = train_classical_svm(bundle.x_train, bundle.y_train, bundle.x_test, bundle.y_test)
    _, q_pred, q_score, q_metrics, q_backend = train_quantum_qsvc(bundle.x_train, bundle.y_train, bundle.x_test, bundle.y_test)

    save_confusion_matrix(bundle.y_test, q_pred, out_dir / "quantum_confusion_matrix.png", "4-Qubit Quantum-Kernel Confusion Matrix")
    save_roc_curve(bundle.y_test, q_score, out_dir / "quantum_roc_curve.png", "4-Qubit Quantum-Kernel ROC Curve")
    learning = _learning_curve_plot(bundle, out_dir / "learning_curve.png")

    cv = run_stratified_5fold_cv(dataset.images, dataset.labels, qubits=args.qubits)
    _cv_plot(cv, out_dir / "cross_validation.png")

    if args.skip_noise:
        noise = {"status": "skipped_by_cli"}
    else:
        noise = run_noise_classification_benchmark(bundle.x_train, bundle.y_train, bundle.x_test, bundle.y_test)
        _noise_plot(noise, out_dir / "noise_resilience.png")

    vector_status = upsert_cases(bundle.x_train, bundle.y_train, out_dir, use_pinecone=args.use_pinecone)

    hardware_path = out_dir / "ibm_hardware_metrics.json"
    hardware = json.loads(hardware_path.read_text()) if hardware_path.exists() else {
        "status": "not_run",
        "reason": "No IBM QPU job has been executed in this packaged run. Use `python -m qbio_diagnostics.ibm_hardware_benchmark` with an IBM Quantum account.",
    }

    summary = {
        "dataset": {
            "samples": int(args.samples),
            "held_out_test_samples": int(len(bundle.y_test)),
            "held_out_test_class_balance": {"benign": int((bundle.y_test == 0).sum()), "lesion": int((bundle.y_test == 1).sum())},
            "patch_size": "16x16",
            "qubits": int(args.qubits),
            "feature_names": bundle.feature_names,
            "source": "synthetic microscopy-style demonstration data",
        },
        "classical_baseline_held_out": c_metrics,
        "quantum_kernel_held_out": q_metrics,
        "quantum_execution_path": q_backend,
        "claim_guardrail": "Held-out metrics are prototype results on 40 synthetic samples, not clinical accuracy and not IBM Quantum hardware results.",
        "cross_validation_5fold": cv,
        "small_data_learning_curve": learning,
        "noise_resilience": noise,
        "ibm_quantum_hardware": hardware,
        "parameter_efficiency_note": "The quantum-kernel model learns an SVM boundary over circuit-derived similarities; it does not train a large deep CNN.",
        "vector_database": vector_status,
    }
    (out_dir / "metrics_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
