"""Synthetic biomedical image data for hackathon reproducibility.

Class 0: benign tissue-like texture.
Class 1: early lesion / microcalcification-like bright clusters.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class Dataset:
    images: np.ndarray  # (n, h, w)
    labels: np.ndarray  # (n,)


def _gaussian_blob(h: int, w: int, cy: float, cx: float, sigma: float) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    return np.exp(-((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * sigma**2))


def generate_synthetic_biomedical_patches(
    n_samples: int = 160,
    size: int = 16,
    seed: int = 7,
) -> Dataset:
    rng = np.random.default_rng(seed)
    images = []
    labels = []

    for i in range(n_samples):
        label = i % 2
        base = rng.normal(0.24, 0.06, (size, size))

        # tissue-like soft structures common to both classes
        for _ in range(rng.integers(2, 5)):
            blob = _gaussian_blob(
                size,
                size,
                cy=rng.uniform(2, size - 2),
                cx=rng.uniform(2, size - 2),
                sigma=rng.uniform(1.2, 3.5),
            )
            base += rng.uniform(0.05, 0.16) * blob

        if label == 1:
            # early disease signal: tiny high-intensity lesions / calcification clusters
            for _ in range(rng.integers(3, 6)):
                y = rng.integers(2, size - 2)
                x = rng.integers(2, size - 2)
                base += rng.uniform(0.45, 0.70) * _gaussian_blob(size, size, y, x, rng.uniform(0.45, 0.9))
        else:
            # benign: smoother, less clustered bright regions
            base += 0.08 * _gaussian_blob(
                size, size, rng.uniform(4, 12), rng.uniform(4, 12), rng.uniform(3.5, 5.0)
            )

        img = np.clip(base, 0, 1)
        images.append(img)
        labels.append(label)

    return Dataset(images=np.asarray(images, dtype=np.float32), labels=np.asarray(labels, dtype=int))


def save_montage(dataset: Dataset, out_path: str | Path, n: int = 12) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    idx = np.arange(min(n, len(dataset.images)))
    cols = 6
    rows = int(np.ceil(len(idx) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.8, rows * 1.8))
    axes = np.ravel(axes)
    for ax_i, sample_i in enumerate(idx):
        ax = axes[ax_i]
        ax.imshow(dataset.images[sample_i], cmap="gray", vmin=0, vmax=1)
        ax.set_title("lesion" if dataset.labels[sample_i] else "benign", fontsize=9)
        ax.axis("off")
    for ax in axes[len(idx):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
