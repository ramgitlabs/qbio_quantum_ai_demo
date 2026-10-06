# Q-BioDiag Demo Video Script (2-4 minutes)

## 0:00 - 0:25 | Opening
"Our project is Q-BioDiag, a Track 8 Quantum AI for Biomedical Diagnostics prototype. It classifies small biomedical image patches as benign or lesion using a hybrid quantum-kernel classifier."

## 0:25 - 0:55 | Problem
"Early disease signals can be subtle and noisy. A full CNN can require many labels and many weights. We compress each 16x16 patch into four diagnostic features and map them to four qubits."

## 0:55 - 1:35 | Run the code
Show terminal:

```bash
python -m qbio_diagnostics.run_demo --samples 160 --qubits 4
```

Point out the generated files in `outputs/`: confusion matrix, ROC, learning curve, cross-validation, noise-resilience, and metrics JSON.

## 1:35 - 2:20 | Explain results safely
"The quantum-kernel pipeline achieved 100% accuracy on our 40-sample held-out evaluation set. This is a prototype result, not clinical accuracy and not an IBM hardware claim. We added 5-fold stratified cross-validation, where the packaged quantum-kernel run reports around 0.994 mean accuracy."

## 2:20 - 3:10 | Noise experiment
"To make this Qiskit-relevant, we compare ideal quantum-kernel simulation, noisy density-matrix simulation, and a ZNE estimate. IBM hardware execution is prepared as an optional next step, but this package does not claim a QPU result."

## 3:10 - 3:40 | Retrieval layer
"The embedding memory stores cases locally or in Pinecone, so a prediction can be paired with similar retrieved cases for better explainability."

## 3:40 - 4:00 | Close
"Q-BioDiag demonstrates a compact, reproducible quantum AI diagnostic workflow with validation, noise analysis, and a clear path to real biomedical datasets and IBM Quantum execution."
