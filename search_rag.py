from sentence_transformers import SentenceTransformer
from constants import *
import faiss, json, numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")

# Load index
index = faiss.read_index(FAISS_INDEX_PATH)

# Load metadata mapping
with open(ID_MAP_PATH, "r", encoding="utf-8") as f:
    id_map = [json.loads(line) for line in f]

def search(query, top_k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, top_k)

    print(f"🔎 Top {top_k} results for: '{query}'\n")
    for rank, i in enumerate(I[0]):
        chunk = id_map[i]
        print(f"#{rank+1}: {chunk['page']} > {' > '.join(chunk['header_path'])}")
        print(f"Chunk ID: {chunk['chunk_id']} | Score: {D[0][rank]:.2f}")
        print(chunk['content'][:200].strip() + "...\n" + "—" * 40)

if __name__ == "__main__":
    search("autonomous underwater navigation system")
