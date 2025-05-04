import os
import re
import json
import mistune

### --- Markdown Cleaner --- ###
def strip_markdown(md_text):
    markdown = mistune.create_markdown(renderer='ast')
    ast = markdown(md_text)

    def extract_text(nodes):
        parts = []
        for node in nodes:
            node_type = node.get('type')

            # Preserve headers with hashes
            if node_type == 'heading':
                level = node.get('level', 1)
                header_text = extract_text(node.get('children', []))
                parts.append(f"{'#' * level} {header_text}")

            elif 'raw' in node:
                parts.append(node['raw'])

            if 'children' in node:
                parts.append(extract_text(node['children']))

        return '\n'.join(parts)

    return extract_text(ast)


### --- Page ID Stripper --- ###
def strip_page_id(name):
    parts = name.rsplit(" ", 1)
    if len(parts) == 2 and len(parts[1]) == 32:
        return parts[0], parts[1]
    return name, None


### --- Batch Markdown Cleaner --- ###
def batch_clean_markdown(input_folder, output_folder):
    for root, _, files in os.walk(input_folder):
        for file in files:
            if not file.endswith(".md"):
                continue

            in_path = os.path.join(root, file)

            base_name = os.path.splitext(file)[0]
            page_name, page_id = strip_page_id(base_name)

            # Clean folder path
            rel_dir = os.path.relpath(root, input_folder)
            clean_parts = [strip_page_id(part)[0] for part in rel_dir.split(os.sep)]
            out_dir = os.path.join(output_folder, *clean_parts)
            os.makedirs(out_dir, exist_ok=True)

            out_path = os.path.join(out_dir, f"{page_name}.clean.txt")

            with open(in_path, "r", encoding="utf-8") as f:
                raw_md = f.read()

            cleaned = strip_markdown(raw_md)
            if page_id:
                cleaned = f"[page_id: {page_id}]\n\n" + cleaned

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned)


### --- Chunking Function --- ###
def chunk_clean_file(file_path, max_words=300):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    header = None
    current_chunk = []
    chunks = []
    word_count = 0
    chunk_id = 1
    page = os.path.splitext(os.path.basename(file_path))[0]

    def flush_chunk():
        nonlocal current_chunk, word_count, chunk_id
        if current_chunk:
            content = '\n'.join(current_chunk).strip()
            if content:
                chunks.append({
                    "page": page,
                    "chunk_id": chunk_id,
                    "header": header or "No Header",
                    "content": content
                })
                chunk_id += 1
            current_chunk = []
            word_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if re.match(r"^#{1,6} ", stripped):
            flush_chunk()
            header = stripped
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


### --- Save to JSONL --- ###
def save_chunks_to_jsonl(chunks, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")


### --- Run Single File Test --- ###
if __name__ == "__main__":
    file_path = "clean_txt/Workbook #3 Solution & Vision.clean.txt"
    chunks = chunk_clean_file(file_path)
    save_chunks_to_jsonl(chunks, "chunked_output.jsonl")
    print(f"✅ Saved {len(chunks)} chunks to 'chunked_output.jsonl'")
