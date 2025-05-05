from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from constants import *
import os, json

schema = Schema(
    chunk_id=ID(stored=True, unique=True),
    page_id=ID(stored=True),
    page=TEXT(stored=True),
    header_path=TEXT(stored=True),
    bm25_text=TEXT,
)

def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)
    if not index.exists_in(INDEX_DIR):
        ix = index.create_in(INDEX_DIR, schema)
    else:
        ix = index.open_dir(INDEX_DIR)

    writer = ix.writer()
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunk = json.loads(line)
            writer.update_document(
                chunk_id=str(chunk["chunk_id"]),
                page_id=chunk["page_id"] or "",
                page=chunk["page"],
                header_path=" > ".join(chunk["header_path"]),
                bm25_text=chunk["bm25_text"]
            )
    writer.commit()
    print("✅ BM25 index built.")

if __name__ == "__main__":
    build_index()
