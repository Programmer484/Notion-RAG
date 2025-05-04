import os
import re
import json
import mistune

INPUT_FOLDER = "notion_export"
OUTPUT_FOLDER = "clean_txt"


### --- Markdown Cleaner --- ###
def strip_markdown(md_text):
    markdown = mistune.create_markdown(renderer='ast')
    ast = markdown(md_text)

    def extract_text(nodes):
        parts = []
        for node in nodes:
            node_type = node.get('type')

            if node_type == 'heading':
                level = node.get('attrs').get('level', 1)
                header_text = extract_text(node.get('children', []))
                parts.append(f"{'#' * level} {header_text}")
            elif 'raw' in node:
                parts.append(node['raw'])
            elif 'children' in node:
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

            rel_dir = os.path.relpath(root, input_folder)
            clean_parts = [strip_page_id(part)[0] for part in rel_dir.split(os.sep)]
            out_dir = os.path.join(output_folder, *clean_parts)
            os.makedirs(out_dir, exist_ok=True)

            out_path = os.path.join(out_dir, f"{page_name}.clean.txt")

            with open(in_path, "r", encoding="utf-8") as f:
                raw_md = f.read()

            cleaned = strip_markdown(raw_md)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            # Save optional page_id metadata
            if page_id:
                with open(out_path.replace(".clean.txt", ".meta.json"), "w", encoding="utf-8") as f:
                    json.dump({"page_id": page_id}, f)


### --- Chunking Function --- ###
def chunk_clean_file(file_path, max_words=300):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    meta_path = file_path.replace(".clean.txt", ".meta.json")
    page_id = None
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            page_id = json.load(f).get("page_id")

    lines = text.splitlines()
    header = None
    header_path = []
    current_chunk = []
    chunks = []
    word_count = 0
    chunk_id = 1
    page = os.path.splitext(os.path.basename(file_path))[0]

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
                "content": content
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

            # Update header path: truncate to one level above, then set new level
            header_path = header_path[:level - 1]  # truncate deeper levels
            if len(header_path) < level:
                header_path.append(header_text)
            else:
                header_path[level - 1] = header_text

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

def chunk_all_clean_files(clean_folder, output_jsonl):
    all_chunks = []
    for root, _, files in os.walk(clean_folder):
        for file in files:
            if not file.endswith(".clean.txt"):
                continue
            file_path = os.path.join(root, file)
            chunks = chunk_clean_file(file_path)
            all_chunks.extend(chunks)

    save_chunks_to_jsonl(all_chunks, output_jsonl)
    print(f"✅ Saved {len(all_chunks)} total chunks to '{output_jsonl}'")

### --- Save to JSONL --- ###
def save_chunks_to_jsonl(chunks, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")


### --- Run Single File Test --- ###
if __name__ == "__main__":
    # Clean a single file
    with open("Test.md", "r", encoding="utf-8") as f:
        test_md = f.read()
    cleaned_test = strip_markdown(test_md)
    # save cleaned test to a file
    with open("Test.clean.txt", "w", encoding="utf-8") as f:
        f.write(cleaned_test)