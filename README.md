# Q-BioDiag: Quantum AI for Early Biomedical Diagnostics

A hackathon-ready demo for **Track 8: Quantum AI for Healthcare & Biomedical Diagnostics**.

Q-BioDiag is a hybrid quantum-classical diagnostic prototype. It generates small microscopy-style image patches, compresses each image into a 4-qubit feature vector, classifies early lesion patterns using a **Qiskit QSVC quantum kernel**, compares against a classical baseline, and stores diagnostic case embeddings in **Pinecone** for similarity search and clinical explanation retrieval.

## Why this matters
Early disease signals can be tiny and noisy. Classical CNNs often need large labelled datasets. This project demonstrates how a quantum feature map can transform compact image features into a high-dimensional Hilbert space for non-linear separation with fewer trainable parameters.

## Architecture

```text
Synthetic / clinical image patches
        ↓
Preprocessing + lesion patch extraction
        ↓
PCA feature compression → 4 features = 4 qubits
        ↓
Qiskit ZZFeatureMap + FidelityQuantumKernel + QSVC
        ↓
Prediction + metrics + robustness analysis
        ↓
Pinecone vector DB stores embeddings + case metadata
        ↓
Streamlit dashboard for demo and retrieval
```

## Repository contents

```text
src/qbio_diagnostics/
  data.py                  Synthetic biomedical image data generator
  features.py              Preprocessing + PCA feature compression
  train_classical.py       Classical SVM baseline
  train_qsvc.py            Qiskit QSVC quantum-kernel classifier
  noise_resilience.py      Small quantum noise + ZNE demo helper
  pinecone_store.py        Pinecone vector DB integration with local fallback
  app_streamlit.py         Demo dashboard
  run_demo.py              One-command hackathon demo
notebooks/
  Quantum_AI_Biomedical_Diagnostics_Demo.ipynb
outputs/
  Sample generated figures and metrics
requirements.txt
```

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
python -m qbio_diagnostics.run_demo --samples 160 --qubits 4
```

Run the dashboard:

```bash
streamlit run src/qbio_diagnostics/app_streamlit.py
```

## Optional Pinecone setup

The project works without Pinecone by writing a local vector store to `outputs/local_vector_db.json`.

To use Pinecone:

```bash
set PINECONE_API_KEY=your_key_here
set PINECONE_INDEX=qbio-diagnostics
# macOS/Linux: export instead of set
python -m qbio_diagnostics.run_demo --use-pinecone
```

## Expected output

The demo prints:

- Classical baseline accuracy, F1, AUC
- Quantum QSVC accuracy, F1, AUC, parameter-efficiency estimate
- Confusion matrix and ROC curve in `outputs/`
- Learning-curve comparison for small-data settings
- Local or Pinecone vector database status

## Pitch in one line

**Q-BioDiag detects subtle early lesion patterns using a hybrid Qiskit quantum-kernel classifier and Pinecone-based diagnostic case retrieval.**

## Notes for judges

This is a hackathon-scale prototype, not a medical device. The demo uses synthetic microscopy-style patches so it is reproducible within minutes. The same pipeline can be connected to BreakHis, HAM10000, Chest X-Ray, or CT patch datasets by replacing `data.py` with a dataset loader.
