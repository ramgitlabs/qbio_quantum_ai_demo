# Q-BioDiag: Quantum AI for Early Biomedical Diagnostics

Hackathon-ready project for **IBM Qiskit Fall Fest 2026 - Track 8: Quantum AI for Healthcare & Biomedical Diagnostics**.

Q-BioDiag is a hybrid quantum-classical diagnostic prototype. It generates reproducible 16x16 microscopy-style biomedical patches, compresses each image into a 4-feature / 4-qubit representation, compares a classical RBF-SVM baseline with a quantum-kernel SVM, runs 5-fold validation, evaluates classifier-level noise resilience, and stores case embeddings in a Pinecone-compatible diagnostic memory.

## Important claim guardrail

Do **not** say this project proves clinical accuracy or that IBM Quantum hardware achieved 100% accuracy.

Correct wording for the pitch:

> QSVC / quantum-kernel evaluation achieved 100% accuracy on the 40-sample held-out evaluation set in the current reproducible demo pipeline. A 5-fold stratified CV check and a noise-resilience benchmark are included. IBM Quantum hardware execution is prepared as an optional next step, but no IBM QPU result is claimed in this packaged run.

## What changed in this updated version

- Removed the misleading classical polynomial-SVM fallback.
- Added a NumPy reference implementation of the 4-qubit ZZ-style fidelity kernel for environments where Qiskit is missing.
- Added leakage-safe **5-fold stratified cross-validation**.
- Added classifier-level **ideal vs noisy vs ZNE** quantum-kernel robustness experiment.
- Added explicit **IBM hardware: not run** status to avoid false claims.
- Updated the deck, metrics JSON, demo script, and notebook wording.

## Architecture

```text
Synthetic / clinical image patches
        ↓
Preprocessing + diagnostic feature extraction
        ↓
4 compact features = 4 qubits
        ↓
Qiskit ZZFeatureMap + FidelityQuantumKernel + QSVC
(or equivalent reference quantum-kernel simulator when Qiskit is unavailable)
        ↓
Prediction + confusion matrix + ROC + learning curve
        ↓
5-fold validation + quantum noise-resilience benchmark
        ↓
Pinecone/local vector DB for similar-case retrieval
```

## Repository contents

```text
src/qbio_diagnostics/
  data.py                         Synthetic biomedical patch generator
  features.py                     Image feature extraction + leakage-safe fold transforms
  quantum_reference.py            4-qubit ZZ-style quantum-kernel reference simulator
  train_classical.py              Classical RBF-SVM baseline
  train_qsvc.py                   Qiskit QSVC path + reference quantum-kernel fallback
  validation.py                   5-fold stratified cross-validation
  noise_resilience.py             Ideal/noisy/ZNE classifier-level robustness benchmark
  ibm_hardware_benchmark.py       Optional IBM Quantum execution starter
  pinecone_store.py               Pinecone integration with local JSON fallback
  run_demo.py                     One-command demo
  app_streamlit.py                Simple dashboard
notebooks/
  Quantum_AI_Biomedical_Diagnostics_Demo.ipynb
outputs/
  Generated figures and metrics_summary.json
docs/
  demo_video_script.md
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

## Key outputs

After running the demo, check `outputs/metrics_summary.json` and these figures:

- `quantum_confusion_matrix.png`
- `quantum_roc_curve.png`
- `learning_curve.png`
- `cross_validation.png`
- `noise_resilience.png`

Expected packaged result summary:

- Dataset: 160 synthetic microscopy-style patches
- Held-out test set: 40 samples, balanced 20 benign / 20 lesion
- Quantum-kernel held-out result: 100% accuracy on this small prototype set
- 5-fold quantum-kernel CV: around 0.994 mean accuracy in the packaged run
- Noise benchmark: reports ideal, noisy, and ZNE scores using a reference 4-qubit density-matrix simulator
- IBM Quantum hardware: **not run** in the package; use `ibm_hardware_benchmark.py` only with your own IBM Quantum account/token

## Optional Pinecone setup

The project works without Pinecone by writing a local vector store to `outputs/local_vector_db.json`.

To use Pinecone:

```bash
set PINECONE_API_KEY=your_key_here
set PINECONE_INDEX=qbio-diagnostics
# macOS/Linux: export instead of set
python -m qbio_diagnostics.run_demo --use-pinecone
```

## Optional IBM Quantum execution

The packaged result does not claim IBM hardware execution. To add it later:

```bash
set IBM_QUANTUM_TOKEN=your_ibm_quantum_token
python -m qbio_diagnostics.ibm_hardware_benchmark
```

`QISKIT_IBM_TOKEN` is also accepted if that is how your environment is configured. Use hardware results only if the job actually completes and produces saved metrics.

## 2-4 minute video flow

1. Show the problem: subtle benign vs lesion biomedical patches.
2. Run `python -m qbio_diagnostics.run_demo --samples 160 --qubits 4`.
3. Open `outputs/metrics_summary.json` and say the exact claim guardrail.
4. Show confusion matrix, ROC, cross-validation, and noise-resilience chart.
5. Mention IBM hardware is prepared but not claimed in the packaged run.

## Final pitch line

**Q-BioDiag turns tiny biomedical image signals into quantum-kernel similarity patterns, tests robustness under noise, and retrieves explainable diagnostic cases for a clinically inspired workflow.**
