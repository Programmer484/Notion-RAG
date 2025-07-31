import os
import re
import json
from constants import *


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def strip_page_id(name: str):
    """Extract page name and ID from filename (e.g. 'Page Name abc123' → ('Page Name', 'abc123'))."""
    parts = name.rsplit(" ", 1)
    if len(parts) == 2 and len(parts[1]) == 32:
        return parts[0], parts[1]
    return name, None


# =============================================================================
# CORE CHUNKING LOGIC
# =============================================================================

def chunk_md_file(file_path: str, max_words: int = 300):
    """
    Split a markdown file into semantic chunks while preserving header hierarchy.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    base = os.path.splitext(os.path.basename(file_path))[0]
    page, page_id = strip_page_id(base)

    lines = text.splitlines()
    header = None
    header_word_count = 0
    header_path = []
    current_chunk = []
    chunks = []
    word_count = 0
    chunk_id = 1

    def add_content_with_count(content: str):
        nonlocal word_count
        current_chunk.append(content)
        word_count += len(content.split())

    def flush_chunk():
        """Save current chunk to results and reset for next chunk."""
        nonlocal current_chunk, word_count, chunk_id
        content = "\n".join(current_chunk).strip()
        if content:
            chunks.append(
                {
                    "page": page,
                    "page_id": page_id,
                    "chunk_id": chunk_id,
                    "header_path": header_path.copy() if header_path else ["No Header"],
                    "content": content,
                }
            )
            chunk_id += 1
        current_chunk.clear()
        word_count = 0

    def start_new_chunk_with_header():
        """When a chunk flushes mid-section, start the next chunk with the current header for context."""
        nonlocal word_count
        if header:
            current_chunk.append(header)
            word_count = header_word_count

    # Iterate over each line
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        match = re.match(r"^(#{1,6}) (.+)", stripped)
        if match:
            # New header encountered
            flush_chunk()
            header = stripped
            header_word_count = len(stripped.split())

            level = len(match.group(1))
            header_text = match.group(2)

            header_path = header_path[: level - 1]  # truncate deeper levels
            header_path.append(header_text)         # append current level
            add_content_with_count(header)
        else:
            # Regular content
            add_content_with_count(stripped)
            if word_count >= max_words:
                flush_chunk()
                start_new_chunk_with_header()

    flush_chunk()  # flush remaining content
    return chunks


# =============================================================================
# BATCH PROCESSING FUNCTIONS
# =============================================================================

def chunk_all_md_files(input_folder: str, output_jsonl: str):
    """Process all markdown files in a folder and save chunks to JSONL."""
    all_chunks = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if not file.endswith(".md"):
                continue
            file_path = os.path.join(root, file)
            all_chunks.extend(chunk_md_file(file_path))

    save_chunks_to_jsonl(all_chunks, output_jsonl)
    print(f"✅ Saved {len(all_chunks)} total chunks to '{output_jsonl}'")


def save_chunks_to_jsonl(chunks, output_path: str):
    """Write chunks to a JSONL file (one JSON object per line)."""
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    chunk_all_md_files(INPUT_FOLDER, "chunks.jsonl")
