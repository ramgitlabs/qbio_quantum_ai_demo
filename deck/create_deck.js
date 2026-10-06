const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const {
  imageSizingContain,
  imageSizingCrop,
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require('/home/oai/skills/slides/pptxgenjs_helpers');

const BASE = '/mnt/data/qbio_updated_project/Q-BioDiag-Updated';
const OUT = BASE;
const metrics = JSON.parse(fs.readFileSync(path.join(BASE, 'outputs/metrics_summary.json'), 'utf8'));
const img = {
  samples: `${BASE}/outputs/sample_patches.png`,
  cm: `${BASE}/outputs/quantum_confusion_matrix.png`,
  roc: `${BASE}/outputs/quantum_roc_curve.png`,
  lc: `${BASE}/outputs/learning_curve.png`,
  cv: `${BASE}/outputs/cross_validation.png`,
  noise: `${BASE}/outputs/noise_resilience.png`,
};
const pptx = new pptxgen();
pptx.defineLayout({ name: 'CUSTOM_WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'CUSTOM_WIDE';
pptx.author = 'Q-BioDiag Team';
pptx.company = 'IBM Qiskit Fall Fest 2026';
pptx.subject = 'Quantum AI for Biomedical Diagnostics';
pptx.title = 'Q-BioDiag Updated Pitch Deck';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'en-US',
};
pptx.margin = 0;
pptx.slideWidth = 13.333;
pptx.slideHeight = 7.5;

const C = {
  bg: 'F7FAFC', navy: '0B1F3A', blue: '2563EB', cyan: '06B6D4', green: '16A34A',
  purple: '7C3AED', gray: '475569', lightBlue: 'DBEAFE', white: 'FFFFFF', amber: 'F59E0B', red: 'DC2626'
};
function addBg(slide, title) {
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.rect, { x:0, y:0, w:13.333, h:0.12, fill:{color:C.blue}, line:{color:C.blue} });
  if (title) slide.addText(title, { x:0.55, y:0.31, w:11.85, h:0.45, fontSize:25, bold:true, color:C.navy, margin:0 });
  slide.addText('Q-BioDiag • Track 8: Quantum AI for Healthcare', { x:0.55, y:7.11, w:6.2, h:0.22, fontSize:8.8, color:'64748B', margin:0 });
}
function pill(slide, text, x, y, w, color=C.blue) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h:0.34, rectRadius:0.06, fill:{color}, line:{color} });
  slide.addText(text, { x:x+0.08, y:y+0.075, w:w-0.16, h:0.16, fontSize:8.5, bold:true, color:C.white, align:'center', margin:0 });
}
function bullet(slide, text, x, y, w, color=C.gray) {
  slide.addShape(pptx.ShapeType.ellipse, { x, y:y+0.09, w:0.08, h:0.08, fill:{color:C.blue}, line:{color:C.blue} });
  slide.addText(text, { x:x+0.18, y, w, h:0.39, fontSize:15.2, color, margin:0, fit:'shrink' });
}
function smallBox(slide, title, body, x, y, w, h, color) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius:0.08, fill:{color:'FFFFFF'}, line:{color:'D7E3F5'} });
  slide.addText(title, { x:x+0.18, y:y+0.18, w:w-0.36, h:0.28, fontSize:14.2, bold:true, color, margin:0, fit:'shrink' });
  slide.addText(body, { x:x+0.18, y:y+0.57, w:w-0.36, h:h-0.76, fontSize:11.6, color:C.navy, margin:0, fit:'shrink' });
}
function node(slide, text, x, y, w, color, dark=false) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h:0.68, rectRadius:0.08, fill:{color}, line:{color:'CBD5E1'} });
  slide.addText(text, { x:x+0.08, y:y+0.18, w:w-0.16, h:0.25, fontSize:13.3, bold:true, color: dark ? C.white : C.navy, align:'center', margin:0, fit:'shrink' });
}
function arrow(slide, x1, y1, x2, y2) {
  slide.addShape(pptx.ShapeType.line, { x:x1, y:y1, w:x2-x1, h:y2-y1, line:{color:C.blue, width:2, endArrowType:'triangle'} });
}
function validate(slide) {
  warnIfSlideHasOverlaps(slide, pptx, { ignoreLines: true });
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

// 1 Title
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  pill(s, 'IBM Qiskit Fall Fest 2026', 0.68, 0.68, 2.65, C.blue);
  pill(s, 'Updated: CV + noise + claim guardrails', 3.55, 0.68, 3.25, C.purple);
  s.addText('Q-BioDiag', { x:0.68, y:1.48, w:6.8, h:0.72, fontSize:48, bold:true, color:C.white, margin:0 });
  s.addText('Quantum AI for Early Biomedical Diagnostics', { x:0.72, y:2.24, w:6.75, h:0.46, fontSize:24, color:'BFE2FF', margin:0 });
  s.addText('4-qubit quantum-kernel classifier for benign vs lesion image patches, plus diagnostic case retrieval.', { x:0.72, y:3.03, w:6.25, h:0.62, fontSize:16.5, color:'E2E8F0', margin:0, fit:'shrink' });
  s.addShape(pptx.ShapeType.roundRect, { x:0.72, y:4.24, w:5.85, h:0.88, rectRadius:0.08, fill:{color:'12365F'}, line:{color:'12365F'} });
  s.addText('Safe claim: 100% on a 40-sample held-out prototype set - not clinical accuracy and not IBM hardware.', { x:0.98, y:4.47, w:5.32, h:0.36, fontSize:12.5, color:'DBEAFE', bold:true, margin:0, fit:'shrink' });
  s.addImage({ path: img.samples, ...imageSizingContain(img.samples, 7.7, 1.35, 4.35, 4.1) });
  s.addText('Track 8 • Healthcare & Biomedical Diagnostics', { x:0.72, y:6.46, w:4.4, h:0.25, fontSize:11, color:'CBD5E1', margin:0 });
  validate(s);
}

// 2 Problem
{
  const s = pptx.addSlide(); addBg(s, 'Problem & Motivation');
  s.addText('Early disease signals are subtle, noisy, and label-limited.', { x:0.65, y:1.03, w:7.8, h:0.48, fontSize:24, bold:true, color:C.navy, margin:0 });
  bullet(s, 'Microscopic pathology patterns can appear as tiny texture changes, weak margins, or small lesion clusters.', 0.72, 1.78, 6.4);
  bullet(s, 'Deep CNNs can perform well, but they usually need more labeled data and many trainable parameters.', 0.72, 2.40, 6.4);
  bullet(s, 'Hackathon target: prove an end-to-end, reproducible quantum-classical diagnostic workflow.', 0.72, 3.02, 6.4);
  s.addImage({ path: img.samples, ...imageSizingContain(img.samples, 7.45, 1.42, 4.78, 3.1) });
  smallBox(s, 'Clinical framing', 'Classify benign vs early-lesion patches, then retrieve similar cases for explanation.', 7.45, 4.83, 4.78, 1.03, C.blue);
  validate(s);
}

// 3 Workflow
{
  const s = pptx.addSlide(); addBg(s, 'Proposed Solution: End-to-End Workflow');
  s.addText('A compact pipeline that judges can run and inspect in minutes.', { x:0.65, y:1.02, w:7.8, h:0.35, fontSize:19, color:C.gray, margin:0 });
  arrow(s, 2.35, 2.23, 3.15, 2.23); arrow(s, 4.90, 2.23, 5.72, 2.23); arrow(s, 7.42, 2.23, 8.25, 2.23); arrow(s, 9.92, 2.23, 10.72, 2.23);
  node(s, 'Image patches', 0.72, 1.89, 1.63, C.white);
  node(s, '4 features', 3.18, 1.89, 1.72, C.white);
  node(s, '4 qubits', 5.75, 1.89, 1.68, C.white);
  node(s, 'Quantum kernel', 8.28, 1.89, 1.64, C.navy, true);
  node(s, 'Prediction', 10.75, 1.89, 1.50, C.white);
  s.addShape(pptx.ShapeType.roundRect, { x:1.10, y:3.25, w:11.0, h:1.55, rectRadius:0.1, fill:{color:'ECFEFF'}, line:{color:'A5F3FC'} });
  s.addText('Validation layer: held-out metrics + 5-fold CV + ideal/noisy quantum-kernel benchmark', { x:1.45, y:3.60, w:9.8, h:0.34, fontSize:18, bold:true, color:C.navy, margin:0, fit:'shrink' });
  s.addText('Retrieval layer: Pinecone or local JSON stores compressed diagnostic embeddings and case metadata.', { x:1.45, y:4.08, w:9.7, h:0.30, fontSize:14.5, color:C.gray, margin:0, fit:'shrink' });
  s.addText('Runnable demo: python -m qbio_diagnostics.run_demo --samples 160 --qubits 4', { x:1.70, y:5.72, w:9.9, h:0.31, fontSize:15.5, bold:true, color:C.purple, align:'center', margin:0, fit:'shrink' });
  validate(s);
}

// 4 Quantum Implementation
{
  const s = pptx.addSlide(); addBg(s, 'Quantum Implementation');
  s.addText('Technical heart: ZZ-style feature map + fidelity kernel + SVM decision boundary.', { x:0.65, y:1.0, w:9.2, h:0.36, fontSize:19.3, bold:true, color:C.navy, margin:0 });
  const code = 'feature_map = zz_feature_map(feature_dimension=4, reps=1, entanglement="full")\nquantum_kernel = FidelityQuantumKernel(feature_map=feature_map)\nmodel = QSVC(quantum_kernel=quantum_kernel)';
  s.addShape(pptx.ShapeType.roundRect, { x:0.75, y:1.62, w:6.3, h:1.42, rectRadius:0.05, fill:{color:'0F172A'}, line:{color:'0F172A'} });
  s.addText(code, { x:0.98, y:1.92, w:5.80, h:0.75, fontFace:'Aptos Mono', fontSize:11.5, color:'E2E8F0', margin:0, fit:'shrink' });
  smallBox(s, 'Representation', 'Each 16x16 patch is compressed into 4 normalized descriptors: std, max intensity, bright ratio, local contrast.', 7.42, 1.50, 4.78, 1.18, C.blue);
  smallBox(s, 'Fallback honesty', 'If Qiskit is unavailable, the project uses a 4-qubit reference quantum-kernel simulator. It does not silently switch to a classical polynomial kernel.', 7.42, 2.95, 4.78, 1.26, C.purple);
  bullet(s, 'Kernel: K(xi, xj) = |<phi(xi)|phi(xj)>|^2', 0.95, 3.74, 5.65);
  bullet(s, 'Classifier: SVM trained over the quantum similarity matrix', 0.95, 4.30, 5.65);
  bullet(s, 'IBM hardware path is optional and separately labeled as not_run until a QPU job completes.', 0.95, 4.86, 6.2);
  validate(s);
}

// 5 Results
{
  const s = pptx.addSlide(); addBg(s, 'Results & Verification');
  s.addText('Prototype metrics from 160 reproducible biomedical-style patches.', { x:0.65, y:1.0, w:7.6, h:0.34, fontSize:18.6, color:C.gray, margin:0 });
  s.addImage({ path: img.cm, ...imageSizingContain(img.cm, 0.62, 1.48, 3.55, 3.55) });
  s.addImage({ path: img.roc, ...imageSizingContain(img.roc, 4.32, 1.48, 3.55, 3.55) });
  s.addImage({ path: img.lc, ...imageSizingContain(img.lc, 8.04, 1.48, 4.35, 3.55) });
  s.addShape(pptx.ShapeType.roundRect, { x:0.80, y:5.55, w:11.75, h:0.82, rectRadius:0.08, fill:{color:'FEF3C7'}, line:{color:'FCD34D'} });
  s.addText('Say this: quantum-kernel evaluation achieved 100% accuracy on the 40-sample held-out evaluation set. Do not call it clinical accuracy or IBM hardware accuracy.', { x:1.08, y:5.80, w:11.17, h:0.26, fontSize:12.9, bold:true, color:'92400E', align:'center', margin:0, fit:'shrink' });
  validate(s);
}

// 6 CV + noise
{
  const s = pptx.addSlide(); addBg(s, 'Robustness: Cross-Validation + Noise');
  s.addText('The updated version adds the evidence judges are likely to ask for.', { x:0.65, y:1.0, w:8.0, h:0.34, fontSize:18.5, color:C.gray, margin:0 });
  s.addImage({ path: img.cv, ...imageSizingContain(img.cv, 0.82, 1.50, 5.0, 3.75) });
  s.addImage({ path: img.noise, ...imageSizingContain(img.noise, 6.35, 1.50, 5.2, 3.75) });
  const qcv = metrics.cross_validation_5fold.reference_quantum_kernel_svm.mean_accuracy.toFixed(4);
  const noisy = metrics.noise_resilience.noisy.accuracy.toFixed(3);
  s.addText(`5-fold quantum-kernel CV mean accuracy: ${qcv}`, { x:0.95, y:5.52, w:5.2, h:0.30, fontSize:14.5, bold:true, color:C.navy, margin:0, fit:'shrink' });
  s.addText(`Noisy classifier accuracy in stress test: ${noisy}`, { x:6.45, y:5.52, w:5.2, h:0.30, fontSize:14.5, bold:true, color:C.navy, margin:0, fit:'shrink' });
  s.addText('IBM Quantum hardware status: not_run in packaged result; the repo includes an optional hardware benchmark starter.', { x:1.25, y:6.15, w:10.7, h:0.30, fontSize:13.5, color:C.red, bold:true, align:'center', margin:0, fit:'shrink' });
  validate(s);
}

// 7 Future scope
{
  const s = pptx.addSlide(); addBg(s, 'Future Scope & Submission Readiness');
  s.addText('Ready for submission: repo + deck + demo-video script.', { x:0.72, y:1.04, w:6.7, h:0.42, fontSize:23, bold:true, color:C.navy, margin:0 });
  bullet(s, 'Upload the full folder to a public GitHub repo with README, requirements, notebook, and outputs.', 0.92, 1.82, 6.15);
  bullet(s, 'Record a 2-4 minute video showing terminal execution, metrics JSON, and output charts.', 0.92, 2.42, 6.15);
  bullet(s, 'In the pitch, separate prototype simulation results from optional future IBM QPU execution.', 0.92, 3.02, 6.15);
  s.addShape(pptx.ShapeType.roundRect, { x:7.75, y:1.35, w:4.35, h:3.35, rectRadius:0.1, fill:{color:'ECFDF5'}, line:{color:'A7F3D0'} });
  s.addText('Roadmap', { x:8.10, y:1.75, w:1.6, h:0.30, fontSize:18, bold:true, color:C.green, margin:0 });
  s.addText('1. Replace synthetic data with BreakHis/HAM10000/X-ray patches\n2. Run IBM Runtime Sampler/Estimator jobs\n3. Add readout mitigation and hardware-specific calibration\n4. Build clinician review workflow', { x:8.10, y:2.20, w:3.55, h:1.62, fontSize:13.4, color:C.navy, margin:0, fit:'shrink' });
  s.addText('Final pitch line', { x:0.95, y:5.10, w:1.8, h:0.25, fontSize:14, bold:true, color:C.blue, margin:0 });
  s.addText('Q-BioDiag turns tiny biomedical image signals into quantum-kernel similarity patterns, tests robustness under noise, and retrieves explainable diagnostic cases.', { x:0.95, y:5.52, w:10.7, h:0.62, fontSize:19, bold:true, color:C.navy, margin:0, fit:'shrink' });
  validate(s);
}

pptx.writeFile({ fileName: `${OUT}/Q-BioDiag_Pitch_Deck_Updated.pptx` });
