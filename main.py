#!/usr/bin/env python3
"""
Notion RAG Pipeline - Main Entry Point

This script orchestrates the entire Notion RAG pipeline:
1. Setup Qdrant database
2. Chunk Notion pages
3. Load chunks to Qdrant with embeddings
4. Provide interactive search interface

Usage:
    python main.py setup    # Run full setup pipeline
    python main.py search   # Interactive search mode
    python main.py query "your query here"  # Single query
"""

import os
import sys
import argparse
from pathlib import Path

# Import our pipeline modules
from s1_setup_qdrant import setup_qdrant
from s2_chunk_pages import chunk_all_md_files
from s3_load_to_qdrant import load_chunks_to_qdrant
from s4_search_qdrant import search_and_display
from constants import *


def run_full_setup():
    """Run the complete setup pipeline."""
    print("🚀 Starting Notion RAG Pipeline Setup")
    print("=" * 50)
    
    # Step 1: Setup Qdrant
    print("\n📊 Step 1: Setting up Qdrant database...")
    client = setup_qdrant()
    
    # Step 2: Check if chunks already exist
    if os.path.exists(CHUNKS_PATH):
        print(f"\n📄 Step 2: Chunks file already exists at {CHUNKS_PATH}")
        print("   Skipping chunking step...")
    else:
        print(f"\n✂️  Step 2: Chunking Notion pages from {INPUT_FOLDER}...")
        if not os.path.exists(INPUT_FOLDER):
            print(f"❌ Error: Input folder '{INPUT_FOLDER}' not found!")
            print("   Please export your Notion pages to this folder.")
            return False
        
        chunk_all_md_files(INPUT_FOLDER, CHUNKS_PATH)
    
    # Step 3: Load to Qdrant
    print(f"\n🧠 Step 3: Loading chunks to Qdrant...")
    load_chunks_to_qdrant()
    
    print("\n✅ Setup complete! You can now run searches.")
    return True


def interactive_search():
    """Interactive search interface."""
    print("🔍 Notion RAG Interactive Search")
    print("=" * 40)
    print("Commands:")
    print("  /help     - Show this help")
    print("  /page     - Filter by page name")
    print("  /header   - Filter by header")
    print("  /clear    - Clear filters")
    print("  /quit     - Exit")
    print("  /exit     - Exit")
    print("-" * 40)
    
    page_filter = None
    header_filter = None
    
    while True:
        try:
            query = input("\n🔎 Enter your search query: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['/quit', '/exit']:
                print("👋 Goodbye!")
                break
            elif query.lower() == '/help':
                print("Commands:")
                print("  /help     - Show this help")
                print("  /page     - Filter by page name")
                print("  /header   - Filter by header")
                print("  /clear    - Clear filters")
                print("  /quit     - Exit")
                print("  /exit     - Exit")
                continue
            elif query.lower() == '/page':
                page_filter = input("Enter page name to filter by: ").strip()
                print(f"📄 Page filter set to: {page_filter}")
                continue
            elif query.lower() == '/header':
                header_filter = input("Enter header to filter by: ").strip()
                print(f"🔹 Header filter set to: {header_filter}")
                continue
            elif query.lower() == '/clear':
                page_filter = None
                header_filter = None
                print("🧹 Filters cleared")
                continue
            
            # Perform search
            search_and_display(query, top_k=5, page_filter=page_filter, header_filter=header_filter)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def single_query(query, top_k=5, page_filter=None, header_filter=None):
    """Perform a single search query."""
    search_and_display(query, top_k=top_k, page_filter=page_filter, header_filter=header_filter)


def main():
    parser = argparse.ArgumentParser(description="Notion RAG Pipeline")
    parser.add_argument("mode", choices=["setup", "search", "query"], 
                       help="Mode to run: setup, search, or query")
    parser.add_argument("--query", "-q", help="Search query (for query mode)")
    parser.add_argument("--top-k", "-k", type=int, default=5, 
                       help="Number of results to return (default: 5)")
    parser.add_argument("--page", "-p", help="Filter by page name")
    parser.add_argument("--header", "-h", help="Filter by header")
    
    args = parser.parse_args()
    
    if args.mode == "setup":
        success = run_full_setup()
        sys.exit(0 if success else 1)
        
    elif args.mode == "search":
        interactive_search()
        
    elif args.mode == "query":
        if not args.query:
            print("❌ Error: Query mode requires a --query argument")
            sys.exit(1)
        single_query(args.query, args.top_k, args.page, args.header)


if __name__ == "__main__":
    main() 