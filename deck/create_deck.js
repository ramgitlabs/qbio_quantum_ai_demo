const pptxgen = require('pptxgenjs');
const {
  imageSizingCrop,
  imageSizingContain,
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require('/home/oai/skills/slides/pptxgenjs_helpers');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Q-BioDiag Team';
pptx.subject = 'Quantum AI for Biomedical Diagnostics';
pptx.title = 'Q-BioDiag Pitch Deck';
pptx.company = 'IBM Qiskit Fall Fest 2026';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'en-US',
};
pptx.defineLayout({ name: 'CUSTOM_WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'CUSTOM_WIDE';
pptx.margin = 0;
pptx.slideWidth = 13.333;
pptx.slideHeight = 7.5;

const OUT = '/mnt/data/qbio_quantum_ai_demo';
const img = {
  samples: `${OUT}/outputs/sample_patches.png`,
  cm: `${OUT}/outputs/quantum_confusion_matrix.png`,
  roc: `${OUT}/outputs/quantum_roc_curve.png`,
  lc: `${OUT}/outputs/learning_curve.png`,
};
const C = {
  bg: 'F7FAFC',
  navy: '0B1F3A',
  blue: '2F80ED',
  teal: '00A6A6',
  green: '22A06B',
  purple: '7B61FF',
  gray: '475569',
  light: 'E6F0FF',
  white: 'FFFFFF',
  red: 'EF4444',
};

function addBg(slide, title) {
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.rect, { x:0, y:0, w:13.333, h:0.12, fill:{color:C.blue}, line:{color:C.blue} });
  if (title) slide.addText(title, { x:0.55, y:0.32, w:11.9, h:0.45, fontSize:25, bold:true, color:C.navy, margin:0 });
  slide.addText('Q-BioDiag • Track 8: Quantum AI for Healthcare', { x:0.55, y:7.10, w:6.2, h:0.25, fontSize:8.5, color:'64748B', margin:0 });
}
function pill(slide, text, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h:0.34, rectRadius:0.06, fill:{color}, line:{color} });
  slide.addText(text, { x:x+0.08, y:y+0.075, w:w-0.16, h:0.16, fontSize:8.5, bold:true, color:C.white, align:'center', margin:0 });
}
function bullet(slide, text, x, y, w, color=C.gray) {
  slide.addShape(pptx.ShapeType.ellipse, { x, y:y+0.07, w:0.08, h:0.08, fill:{color:C.blue}, line:{color:C.blue} });
  slide.addText(text, { x:x+0.18, y, w, h:0.34, fontSize:15.5, color, margin:0, breakLine:false, fit:'shrink' });
}
function node(slide, text, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h:0.68, rectRadius:0.08, fill:{color}, line:{color:'D7E3F5', transparency:20} });
  slide.addText(text, { x:x+0.12, y:y+0.18, w:w-0.24, h:0.25, fontSize:14, bold:true, color: color === C.navy ? C.white : C.navy, align:'center', margin:0, fit:'shrink' });
}
function arrow(slide, x1, y1, x2, y2) {
  slide.addShape(pptx.ShapeType.line, { x:x1, y:y1, w:x2-x1, h:y2-y1, line:{color:C.blue, width:2, beginArrowType:'none', endArrowType:'triangle'} });
}

// Slide 1
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  pill(s, 'IBM Qiskit Fall Fest 2026', 0.68, 0.7, 2.55, C.blue);
  s.addText('Q-BioDiag', { x:0.68, y:1.55, w:6.8, h:0.72, fontSize:48, bold:true, color:C.white, margin:0 });
  s.addText('Quantum AI for Early Biomedical Diagnostics', { x:0.72, y:2.32, w:6.5, h:0.45, fontSize:25, color:'BFE2FF', margin:0 });
  s.addText('Hybrid Qiskit quantum-kernel classifier + Pinecone diagnostic case retrieval', { x:0.72, y:3.12, w:6.3, h:0.60, fontSize:17, color:'E2E8F0', margin:0, fit:'shrink' });
  s.addImage({ path: img.samples, ...imageSizingContain(img.samples, 8.05, 1.38, 4.15, 4.05) });
  s.addText('Track 8 • Healthcare & Biomedical Diagnostics', { x:0.72, y:6.45, w:4.4, h:0.26, fontSize:11, color:'CBD5E1', margin:0 });
  warnIfSlideHasOverlaps(s, pptx, { ignoreLines: true }); warnIfSlideElementsOutOfBounds(s, pptx);
}

// Slide 2
{
  const s = pptx.addSlide(); addBg(s, 'Problem & Motivation');
  s.addText('Early disease signals are small, noisy and data-hungry.', { x:0.65, y:1.05, w:7.6, h:0.5, fontSize:25, bold:true, color:C.navy, margin:0 });
  bullet(s, 'Clinical images contain subtle lesion patterns: microcalcifications, tiny nodules, weak margins.', 0.72, 1.85, 6.3);
  bullet(s, 'Deep CNNs work well, but often need larger datasets and many trainable weights.', 0.72, 2.42, 6.3);
  bullet(s, 'Hackathon goal: show a compact, reproducible quantum-classical diagnostic workflow.', 0.72, 2.99, 6.3);
  s.addImage({ path: img.samples, ...imageSizingContain(img.samples, 7.55, 1.55, 4.65, 2.95) });
  s.addShape(pptx.ShapeType.roundRect, { x:7.5, y:4.82, w:4.9, h:1.02, rectRadius:0.08, fill:{color:'EAF3FF'}, line:{color:'C7DBFF'} });
  s.addText('Medical framing', { x:7.75, y:5.03, w:1.65, h:0.22, fontSize:12.5, bold:true, color:C.blue, margin:0 });
  s.addText('Classify benign vs early lesion patches, then retrieve similar cases for explainability.', { x:7.75, y:5.33, w:4.15, h:0.32, fontSize:13.5, color:C.navy, margin:0, fit:'shrink' });
  warnIfSlideHasOverlaps(s, pptx, { ignoreLines: true }); warnIfSlideElementsOutOfBounds(s, pptx);
}

// Slide 3
{
  const s = pptx.addSlide(); addBg(s, 'Proposed Solution: End-to-End Workflow');
  s.addText('A lightweight diagnostic pipeline that judges can run in minutes.', { x:0.65, y:1.02, w:7.8, h:0.35, fontSize:19, color:C.gray, margin:0 });
  arrow(s, 2.45, 2.22, 3.28, 2.22); arrow(s, 5.1, 2.22, 5.88, 2.22); arrow(s, 7.72, 2.22, 8.50, 2.22); arrow(s, 10.32, 2.22, 11.10, 2.22);
  node(s, 'Image patches', 0.72, 1.88, 1.73, C.white);
  node(s, 'Feature compression', 3.32, 1.88, 1.78, C.white);
  node(s, '4-qubit encoding', 5.90, 1.88, 1.82, C.white);
  node(s, 'Qiskit QSVC', 8.52, 1.88, 1.80, C.navy);
  node(s, 'Prediction', 11.12, 1.88, 1.45, C.white);
  s.addShape(pptx.ShapeType.roundRect, { x:1.25, y:3.25, w:10.8, h:1.5, rectRadius:0.1, fill:{color:'F0FDFA'}, line:{color:'99F6E4'} });
  s.addText('Pinecone diagnostic memory', { x:1.55, y:3.52, w:3.3, h:0.3, fontSize:18, bold:true, color:C.teal, margin:0 });
  s.addText('Compressed embeddings + metadata are stored for similarity search, case retrieval, and demo explainability.', { x:1.55, y:3.95, w:9.0, h:0.35, fontSize:15.5, color:C.navy, margin:0, fit:'shrink' });
  s.addText('Input → Quantum model → Metrics → Similar case retrieval', { x:3.2, y:5.55, w:6.9, h:0.35, fontSize:19, bold:true, align:'center', color:C.purple, margin:0 });
  warnIfSlideHasOverlaps(s, pptx, { ignoreLines: true }); warnIfSlideElementsOutOfBounds(s, pptx);
}

// Slide 4
{
  const s = pptx.addSlide(); addBg(s, 'Quantum Implementation');
  s.addText('Technical heart: Qiskit ZZFeatureMap + FidelityQuantumKernel + QSVC', { x:0.65, y:1.0, w:8.4, h:0.36, fontSize:20, bold:true, color:C.navy, margin:0 });
  const code = `feature_map = ZZFeatureMap(feature_dimension=4, reps=2, entanglement="linear")\nquantum_kernel = FidelityQuantumKernel(feature_map=feature_map)\nmodel = QSVC(quantum_kernel=quantum_kernel)`;
  s.addShape(pptx.ShapeType.roundRect, { x:0.75, y:1.65, w:6.15, h:1.45, rectRadius:0.05, fill:{color:'0F172A'}, line:{color:'0F172A'} });
  s.addText(code, { x:1.0, y:1.95, w:5.65, h:0.75, fontFace:'Aptos Mono', fontSize:12.5, color:'E2E8F0', margin:0, fit:'shrink' });
  s.addShape(pptx.ShapeType.roundRect, { x:7.25, y:1.55, w:4.95, h:3.0, rectRadius:0.08, fill:{color:'FFFFFF'}, line:{color:'D7E3F5'} });
  s.addText('Circuit idea', { x:7.55, y:1.84, w:1.6, h:0.25, fontSize:16, bold:true, color:C.blue, margin:0 });
  s.addText('Ry / Rz data rotations encode patch features. Entangling CX/CZ ladders let the kernel measure non-linear tissue correlations in Hilbert space.', { x:7.55, y:2.25, w:4.25, h:0.82, fontSize:14.2, color:C.navy, margin:0, fit:'shrink' });
  s.addText('Noise plan', { x:7.55, y:3.40, w:1.6, h:0.25, fontSize:16, bold:true, color:C.teal, margin:0 });
  s.addText('Aer depolarizing noise + zero-noise extrapolation helper for NISQ-readiness.', { x:7.55, y:3.80, w:4.1, h:0.38, fontSize:14.2, color:C.navy, margin:0, fit:'shrink' });
  bullet(s, 'Input dimension: 4 compressed image descriptors = 4 qubits', 0.95, 3.72, 5.4);
  bullet(s, 'Quantum kernel: K(xᵢ, xⱼ)=|⟨φ(xᵢ)|φ(xⱼ)⟩|²', 0.95, 4.26, 5.4);
  bullet(s, 'Classifier: QSVC decision boundary over quantum similarity matrix', 0.95, 4.80, 5.4);
  warnIfSlideHasOverlaps(s, pptx, { ignoreLines: true }); warnIfSlideElementsOutOfBounds(s, pptx);
}

// Slide 5
{
  const s = pptx.addSlide(); addBg(s, 'Results & Verification');
  s.addText('Demo metrics from reproducible synthetic biomedical patches', { x:0.65, y:1.0, w:7.4, h:0.34, fontSize:19, color:C.gray, margin:0 });
  s.addImage({ path: img.cm, ...imageSizingContain(img.cm, 0.78, 1.55, 3.65, 3.65) });
  s.addImage({ path: img.roc, ...imageSizingContain(img.roc, 4.85, 1.55, 3.65, 3.65) });
  s.addImage({ path: img.lc, ...imageSizingContain(img.lc, 8.60, 1.55, 3.85, 3.65) });
  s.addText('Observed result: QSVC path/fallback achieved strong lesion-vs-benign separation in the packaged demo; replace the dataset loader for BreakHis/HAM10000/X-ray.', { x:1.0, y:5.82, w:11.2, h:0.48, fontSize:15, color:C.navy, margin:0, align:'center', fit:'shrink' });
  warnIfSlideHasOverlaps(s, pptx, { ignoreLines: true }); warnIfSlideElementsOutOfBounds(s, pptx);
}

// Slide 6
{
  const s = pptx.addSlide(); addBg(s, 'Quantum Advantage & Feasibility');
  s.addText('Why quantum here?', { x:0.75, y:1.08, w:4.0, h:0.4, fontSize:24, bold:true, color:C.navy, margin:0 });
  bullet(s, 'Expressive feature maps: compact medical descriptors become high-dimensional quantum states.', 0.90, 1.86, 6.2);
  bullet(s, 'Parameter efficiency: quantum kernel model avoids training a large CNN in the demo path.', 0.90, 2.45, 6.2);
  bullet(s, 'Small-data story: supports learning-curve comparison under limited labels.', 0.90, 3.04, 6.2);
  bullet(s, 'NISQ feasibility: Aer noise demo + ZNE hook prepares for IBM backend execution.', 0.90, 3.63, 6.2);
  s.addShape(pptx.ShapeType.roundRect, { x:7.50, y:1.30, w:4.75, h:3.45, rectRadius:0.1, fill:{color:'F5F3FF'}, line:{color:'DDD6FE'} });
  s.addText('Clinical retrieval layer', { x:7.85, y:1.72, w:2.9, h:0.32, fontSize:18, bold:true, color:C.purple, margin:0 });
  s.addText('Pinecone stores compressed embeddings and metadata so a new patch can retrieve similar historical cases with explanation text.', { x:7.85, y:2.25, w:3.95, h:0.75, fontSize:14.5, color:C.navy, margin:0, fit:'shrink' });
  s.addText('Model output + retrieved cases = clearer pitch and better clinician-facing explainability.', { x:7.85, y:3.55, w:3.95, h:0.45, fontSize:14.5, bold:true, color:C.navy, margin:0, fit:'shrink' });
  warnIfSlideHasOverlaps(s, pptx, { ignoreLines: true }); warnIfSlideElementsOutOfBounds(s, pptx);
}

// Slide 7
{
  const s = pptx.addSlide(); addBg(s, 'Future Scope & Submission Readiness');
  s.addText('Tomorrow-ready deliverables', { x:0.75, y:1.05, w:4.7, h:0.4, fontSize:24, bold:true, color:C.navy, margin:0 });
  bullet(s, 'Public GitHub repo: upload the packaged folder and keep README visible.', 0.95, 1.82, 6.0);
  bullet(s, 'Deck: 7-slide judge-friendly pitch following the recommended blueprint.', 0.95, 2.38, 6.0);
  bullet(s, 'Video: record terminal run + dashboard + explain results in 2–4 minutes.', 0.95, 2.94, 6.0);
  s.addShape(pptx.ShapeType.roundRect, { x:7.35, y:1.22, w:4.9, h:3.72, rectRadius:0.1, fill:{color:'ECFDF5'}, line:{color:'A7F3D0'} });
  s.addText('Roadmap', { x:7.75, y:1.62, w:1.7, h:0.3, fontSize:18, bold:true, color:C.green, margin:0 });
  s.addText('1. Replace synthetic patches with BreakHis/HAM10000/Chest X-ray dataset\n2. Run Qiskit Runtime Sampler/Estimator on IBM backend\n3. Add readout mitigation and deeper hardware benchmarking\n4. Build clinician review workflow', { x:7.75, y:2.10, w:3.95, h:1.58, fontSize:14.2, color:C.navy, margin:0, breakLine:false, fit:'shrink' });
  s.addText('Final pitch line', { x:0.95, y:4.85, w:1.8, h:0.25, fontSize:14, bold:true, color:C.blue, margin:0 });
  s.addText('Q-BioDiag turns tiny medical image signals into quantum-kernel similarity patterns and retrieves explainable diagnostic cases.', { x:0.95, y:5.26, w:10.6, h:0.54, fontSize:20, bold:true, color:C.navy, margin:0, fit:'shrink' });
  warnIfSlideHasOverlaps(s, pptx, { ignoreLines: true }); warnIfSlideElementsOutOfBounds(s, pptx);
}

pptx.writeFile({ fileName: `${OUT}/Q-BioDiag_Pitch_Deck.pptx` });