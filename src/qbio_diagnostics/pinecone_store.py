from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Dict, Any
import numpy as np


def upsert_cases(vectors: np.ndarray, labels: np.ndarray, out_dir: str | Path = "outputs", use_pinecone: bool = False) -> Dict[str, Any]:
    """Upsert diagnostic embeddings to Pinecone or a local JSON fallback."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for i, (vec, label) in enumerate(zip(vectors, labels)):
        records.append(
            {
                "id": f"case-{i:04d}",
                "values": [float(v) for v in vec],
                "metadata": {
                    "diagnosis": "early_lesion" if int(label) == 1 else "benign",
                    "modality": "synthetic_histopathology_patch",
                    "explanation": "Small bright clustered regions suggest early lesion signal." if int(label) == 1 else "Smooth low-intensity texture resembles benign patch.",
                },
            }
        )

    if use_pinecone and os.getenv("PINECONE_API_KEY"):
        from pinecone import Pinecone, ServerlessSpec

        index_name = os.getenv("PINECONE_INDEX", "qbio-diagnostics")
        pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        existing = [idx.name for idx in pc.list_indexes()]
        if index_name not in existing:
            pc.create_index(
                name=index_name,
                dimension=vectors.shape[1],
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        index = pc.Index(index_name)
        index.upsert(vectors=[(r["id"], r["values"], r["metadata"]) for r in records])
        return {"mode": "pinecone", "index": index_name, "count": len(records)}

    path = out_dir / "local_vector_db.json"
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return {"mode": "local-json", "path": str(path), "count": len(records)}
