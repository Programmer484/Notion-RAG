import os
import re
import json
import mistune
from constants import *


def strip_markdown(md_text):
    markdown = mistune.create_markdown(renderer='ast')
    ast = markdown(md_text)

    def extract_text(nodes):
        parts = []
        for node in nodes:
            if "children" in node:
                parts.append(extract_text(node["children"]))
            elif "raw" in node:
                parts.append(node["raw"])

        combined = ' '.join(parts)
        combined = combined.replace("[  ]", "").replace("[ x]", "")
        return combined.strip()

    return extract_text(ast)

def strip_page_id(name):
    parts = name.rsplit(" ", 1)
    if len(parts) == 2 and len(parts[1]) == 32:
        return parts[0], parts[1]
    return name, None

def chunk_md_file(file_path, max_words=300):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    base = os.path.splitext(os.path.basename(file_path))[0]
    page, page_id = strip_page_id(base)

    lines = text.splitlines()
    header = None
    header_path = []
    current_chunk = []
    chunks = []
    word_count = 0
    chunk_id = 1

    def flush_chunk():
        nonlocal current_chunk, word_count, chunk_id
        content = '\n'.join(current_chunk).strip()
        if content:
            chunks.append({
                "page": page,
                "page_id": page_id,
                "chunk_id": chunk_id,
                "header": header or "No Header",
                "header_path": header_path.copy(),
                "content": content,
                "bm25_text": strip_markdown(content)
            })
            chunk_id += 1
        current_chunk.clear()
        word_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        match = re.match(r"^(#{1,6}) (.+)", stripped)
        if match:
            flush_chunk()
            header = stripped
            level = len(match.group(1))
            header_text = match.group(2)

            header_path = header_path[:level - 1]  # always truncate deeper levels
            header_path.append(header_text)        # always append current level

            current_chunk.append(header)
            word_count += len(stripped.split())
        else:
            current_chunk.append(stripped)
            word_count += len(stripped.split())
            if word_count >= max_words:
                flush_chunk()
                if header:
                    current_chunk.append(header)
                    word_count += len(header.split())

    flush_chunk()
    return chunks

def chunk_all_md_files(input_folder, output_jsonl):
    all_chunks = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if not file.endswith(".md"):
                continue
            file_path = os.path.join(root, file)
            chunks = chunk_md_file(file_path)
            all_chunks.extend(chunks)

    save_chunks_to_jsonl(all_chunks, output_jsonl)
    print(f"✅ Saved {len(all_chunks)} total chunks to '{output_jsonl}'")

def save_chunks_to_jsonl(chunks, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    chunk_all_md_files(INPUT_FOLDER, "chunks.jsonl")