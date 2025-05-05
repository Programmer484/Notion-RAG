from sentence_transformers import SentenceTransformer
import faiss, json, os
import numpy as np
from sklearn.preprocessing import normalize
from constants import *


model = SentenceTransformer("all-MiniLM-L6-v2")

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f]

texts = [c["content"] for c in chunks]
embeddings = model.encode(texts, convert_to_numpy=True)
embeddings = normalize(embeddings)  # 🔁 normalize for cosine

# Cosine = use Inner Product + normalized vectors
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

faiss.write_index(index, FAISS_INDEX_PATH)

print("✅ Cosine index + metadata saved")
