import json
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct
from s1_setup_qdrant import get_qdrant_client
from constants import *

def load_chunks_to_qdrant():
    """Load existing chunks from JSONL into Qdrant with embeddings."""
    
    # Get Qdrant client
    client = get_qdrant_client()
    
    # Load embedding model
    print("🔄 Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Read chunks from JSONL
    print("📖 Reading chunks from JSONL...")
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    
    print(f"📊 Found {len(chunks)} chunks to process")
    
    # Generate embeddings and prepare points
    print("🧠 Generating embeddings...")
    points = []
    
    for i, chunk in enumerate(chunks):
        if i % 100 == 0:
            print(f"   Processing chunk {i+1}/{len(chunks)}")
        
        # Generate embedding for the content
        embedding = model.encode(chunk["content"]).tolist()
        
        # Create Qdrant point
        point = PointStruct(
            id=chunk["chunk_id"],
            vector=embedding,
            payload={
                "page": chunk["page"],
                "page_id": chunk["page_id"],
                "header_path": chunk["header_path"]
            }
        )
        points.append(point)
    
    # Upload to Qdrant
    print("🚀 Uploading to Qdrant...")
    client.upsert(
        collection_name="notion_chunks",
        points=points
    )
    
    print(f"✅ Successfully loaded {len(points)} chunks to Qdrant!")
    
    # Verify
    collection_info = client.get_collection("notion_chunks")
    print(f"📈 Collection now has {collection_info.points_count} points")

if __name__ == "__main__":
    load_chunks_to_qdrant() 