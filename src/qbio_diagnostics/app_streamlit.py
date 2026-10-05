from __future__ import annotations

from pathlib import Path
import json
import streamlit as st

st.set_page_config(page_title="Q-BioDiag", layout="wide")
st.title("Q-BioDiag: Quantum AI Biomedical Diagnostics")
st.caption("Hybrid Qiskit quantum-kernel classifier + Pinecone diagnostic case retrieval")

summary_path = Path("outputs/metrics_summary.json")
if not summary_path.exists():
    st.warning("Run `python -m qbio_diagnostics.run_demo` first to generate outputs.")
    st.stop()

summary = json.loads(summary_path.read_text())
col1, col2, col3 = st.columns(3)
col1.metric("Quantum Accuracy", f"{summary['quantum_qsvc'].get('accuracy', 0):.2f}")
col2.metric("Quantum Macro-F1", f"{summary['quantum_qsvc'].get('macro_f1', 0):.2f}")
col3.metric("AUC-ROC", f"{summary['quantum_qsvc'].get('auc_roc', 0):.2f}")

st.subheader("Biomedical patch examples")
st.image("outputs/sample_patches.png", use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("QSVC Confusion Matrix")
    st.image("outputs/quantum_confusion_matrix.png", use_container_width=True)
with right:
    st.subheader("QSVC ROC Curve")
    st.image("outputs/quantum_roc_curve.png", use_container_width=True)

st.subheader("Small-data learning curve")
st.image("outputs/learning_curve.png", use_container_width=True)

st.subheader("Pinecone / Vector DB status")
st.json(summary["vector_database"])

st.subheader("Noise resilience demo")
st.json(summary["noise_zne_demo"])
