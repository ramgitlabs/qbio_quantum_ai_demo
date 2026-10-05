# 2–4 Minute Demo Video Script

## 0:00–0:20 — Opening
Hello judges, our project is **Q-BioDiag**, a hybrid quantum-classical diagnostic system for early biomedical disease detection.

## 0:20–0:55 — Problem
Early lesion signals in CT, MRI, and histopathology can be tiny, noisy, and hard to separate with limited labelled data. Classical deep models often need many parameters and large datasets.

## 0:55–1:35 — Solution architecture
We generate or load clinical image patches, preprocess them, compress each patch to four features, encode those features into a four-qubit Qiskit ZZFeatureMap, and train a QSVC with a fidelity quantum kernel. We compare this against a classical SVM baseline.

## 1:35–2:20 — Live execution
Show the terminal command:

```bash
python -m qbio_diagnostics.run_demo --samples 160 --qubits 4
```

Point out the metrics summary, confusion matrix, ROC curve, and learning curve generated in the outputs folder.

## 2:20–3:00 — Pinecone
Explain that compressed case embeddings are stored in Pinecone or a local vector database fallback. This supports similarity search: for a new patient patch, clinicians can retrieve similar historical cases and explanations.

## 3:00–3:40 — Quantum advantage and future scope
The advantage is parameter efficiency and expressive non-linear feature mapping in Hilbert space. The next step is replacing synthetic patches with BreakHis/HAM10000/Chest X-Ray data and running circuits on IBM Heron/Eagle backends with noise mitigation.
