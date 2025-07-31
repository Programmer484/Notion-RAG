# Notion RAG System

A simple RAG (Retrieval-Augmented Generation) system for searching through Notion exports using Qdrant vector database.

## Quick Start

### 1. Setup Everything
```bash
# Start Qdrant locally
docker compose up -d

# Run complete setup pipeline
python main.py setup
```

### 2. Search Your Data
```bash
# Interactive search mode
python main.py search

# Single query
python main.py query "your search query here"

# With filters
python main.py query "AI research" --page "Research Notes" --header "Technology"
```

## Manual Step-by-Step (Alternative)

### 1. Setup Qdrant
```bash
# Start Qdrant locally
docker compose up -d

# Setup collection
python s1_setup_qdrant.py
```

### 2. Process Notion Data
```bash
# Process markdown files into chunks
python s2_chunk_pages.py
```

### 3. Load Data into Qdrant
```bash
# Load chunks with embeddings into Qdrant
python s3_load_to_qdrant.py
```

### 4. Search
```bash
# Search your Notion data
python s4_search_qdrant.py
```

## Usage Examples

### Interactive Search
```bash
python main.py search
```
- Type queries and see results
- Use `/page` to filter by page name
- Use `/header` to filter by section header
- Use `/clear` to remove filters

### Single Queries
```bash
# Basic search
python main.py query "machine learning"

# With page filter
python main.py query "conference dates" --page "Conferences"

# With header filter
python main.py query "maritime technology" --header "Technology"

# Multiple results
python main.py query "AI research" --top-k 10
```

## Files
- `main.py` - **Main entry point** - Orchestrates the entire pipeline
- `s1_setup_qdrant.py` - Setup Qdrant collection
- `s2_chunk_pages.py` - Process Notion markdown into chunks
- `s3_load_to_qdrant.py` - Load chunks into Qdrant with embeddings
- `s4_search_qdrant.py` - Search the Qdrant database
- `constants.py` - Configuration
- `docker-compose.yml` - Qdrant container setup
- `chunks.jsonl` - Processed chunks data
- `resources/` - Source Notion markdown files 