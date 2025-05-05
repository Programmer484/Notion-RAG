from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from constants import *

def search(query_text, top_k=5):
    ix = open_dir(INDEX_DIR)
    with ix.searcher() as searcher:
        parser = QueryParser("bm25_text", schema=ix.schema)
        query = parser.parse(query_text)

        results = searcher.search(query, limit=top_k)
        for hit in results:
            print(f"📄 {hit['page']} [{hit['page_id']}]")
            print(f"🔹 Header: {hit['header_path']}")
            print(f"🔎 Chunk ID: {hit['chunk_id']}")
            print("—" * 40)

if __name__ == "__main__":
    search("autonomous underwater vehicle")
