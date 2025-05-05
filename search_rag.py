import faiss, json
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from constants import *
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(FAISS_INDEX_PATH)

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    id_map = [json.loads(line) for line in f]

def search(query, top_k=5):
    q = model.encode([query], convert_to_numpy=True)
    q = normalize(q)

    D, I = index.search(q, top_k)

    print(f"🔎 Top {top_k} for: '{query}'\n")
    for rank, i in enumerate(I[0]):
        chunk = id_map[i]
        print(f"#{rank+1}: {chunk['page']} > {' > '.join(chunk['header_path'])}")
        print(f"Chunk ID: {chunk['chunk_id']} | Cosine Sim: {D[0][rank]:.3f}")
        print(chunk['content'][:200].strip() + "...\n" + "—" * 40)

if __name__ == "__main__":
    search("Impact of biofouling on ship propulsion efficiency")