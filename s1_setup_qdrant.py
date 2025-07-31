import os
import qdrant_client
from qdrant_client.models import Distance, VectorParams
from constants import *

def get_qdrant_client():
    """Get a Qdrant client connection."""
    return qdrant_client.QdrantClient(
        url=os.getenv("QDRANT_URL", "localhost"),
        port=int(os.getenv("QDRANT_PORT", "6333")),
        api_key=os.getenv("QDRANT_API_KEY", None)
    )

def setup_qdrant():
    """Initialize Qdrant database with the proper collection for Notion chunks."""
    
    # Connect to Qdrant
    client = get_qdrant_client()
    
    # Collection name for your Notion chunks
    collection_name = "notion_chunks"
    
    # Check if collection already exists
    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]
    
    if collection_name in collection_names:
        print(f"✅ Collection '{collection_name}' already exists")
        return client
    
    # Create collection with proper configuration
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,  # all-MiniLM-L6-v2 embedding size
            distance=Distance.COSINE,
            on_disk=False  # Keep in RAM for speed
        )
    )
    
    print(f"✅ Created collection '{collection_name}'")
    return client

if __name__ == "__main__":
    setup_qdrant() 