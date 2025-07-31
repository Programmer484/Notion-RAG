import json
from sentence_transformers import SentenceTransformer
from s1_setup_qdrant import get_qdrant_client
from constants import *

def search_qdrant(query, top_k=5, page_filter=None, header_filter=None):
    """
    Search Qdrant for similar chunks with optional filtering.
    
    Args:
        query (str): Search query
        top_k (int): Number of results to return
        page_filter (str, optional): Filter by page name
        header_filter (str, optional): Filter by header text
        
    Returns:
        list: Search results from Qdrant
    """
    
    # Get Qdrant client
    client = get_qdrant_client()
    
    # Load embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Generate query embedding
    query_embedding = model.encode(query).tolist()
    
    # Build filter
    search_filter = None
    if page_filter or header_filter:
        search_filter = {}
        
        if page_filter:
            search_filter["must"] = [{"key": "page", "match": {"value": page_filter}}]
        
        if header_filter:
            if "must" not in search_filter:
                search_filter["must"] = []
            search_filter["must"].append({
                "key": "header_path", 
                "match": {"text": header_filter}
            })
    
    # Search
    results = client.search(
        collection_name="notion_chunks",
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=top_k,
        with_payload=True
    )
    
    return results


def display_search_results(results, query, top_k=5, page_filter=None, header_filter=None):
    """
    Display search results in a formatted way.
    
    Args:
        results: Search results from search_qdrant()
        query (str): Original search query
        top_k (int): Number of results requested
        page_filter (str, optional): Page filter used
        header_filter (str, optional): Header filter used
    """
    print(f"🔎 Top {top_k} results for: '{query}'")
    if page_filter:
        print(f"📄 Filtered by page: {page_filter}")
    if header_filter:
        print(f"🔹 Filtered by header: {header_filter}")
    print()
    
    # Load content from JSONL for display
    content_cache = {}
    try:
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                chunk = json.loads(line)
                content_cache[chunk["chunk_id"]] = chunk["content"]
    except FileNotFoundError:
        print("⚠️  Warning: Could not load content from chunks file")
    
    for i, result in enumerate(results):
        payload = result.payload
        chunk_id = result.id
        
        # Get content from cache
        content = content_cache.get(chunk_id, "Content not available")
        
        print(f"#{i+1}: {payload['page']} > {' > '.join(payload['header_path'])}")
        print(f"Chunk ID: {chunk_id} | Similarity: {result.score:.3f}")
        print(f"Content: {content[:200].strip()}...")
        print("—" * 40)


def search_and_display(query, top_k=5, page_filter=None, header_filter=None):
    """
    Perform search and display results in one function.
    
    Args:
        query (str): Search query
        top_k (int): Number of results to return
        page_filter (str, optional): Filter by page name
        header_filter (str, optional): Filter by header text
    """
    results = search_qdrant(query, top_k, page_filter, header_filter)
    display_search_results(results, query, top_k, page_filter, header_filter)
    return results


if __name__ == "__main__":
    # Simple example usage
    print("🔍 Notion RAG Search - Example Queries")
    print("=" * 50)
    
    # Example 1: Basic search
    search_and_display("Impact of biofouling on ship propulsion efficiency")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Search with page filter
    search_and_display("conference dates", page_filter="Conferences to attend")
    
    print("\n" + "="*60 + "\n")
    
    # Example 3: Search with header filter
    search_and_display("maritime technology", header_filter="Technology") 