from sentence_transformers import SentenceTransformer
from constants import *
import faiss, json, os
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load chunks
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f]

# Embed full Markdown content
texts = [c["content"] for c in chunks]
embeddings = model.encode(texts, convert_to_numpy=True)

# Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index
faiss.write_index(index, FAISS_INDEX_PATH)

# Save chunk metadata (e.g., for retrieval later)
with open(ID_MAP_PATH, "w", encoding="utf-8") as f:
    for chunk in chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"✅ Vector index saved to {FAISS_INDEX_PATH}")
print(f"✅ Metadata saved to {ID_MAP_PATH}")
