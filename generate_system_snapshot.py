# generate_system_snapshot.py
# The Signal – System File Walker for Snapshot Overview

import os
import datetime

BASE_DIR = os.getcwd()
OUTPUT_FILE = "SYSTEM_SNAPSHOT.md"
INCLUDE_EXTENSIONS = [".py", ".md", ".yaml", ".yml"]

def is_code_or_text_file(filename):
    return any(filename.endswith(ext) for ext in INCLUDE_EXTENSIONS)

def get_file_head(path, lines=20):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.readlines()
            return "".join(content[:lines])
    except Exception as e:
        return f"[Error reading file: {e}]"

def walk_and_capture():
    snapshot = []
    snapshot.append(f"# SYSTEM SNAPSHOT — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    snapshot.append("This is an auto-generated index of all files in The Signal, with short previews.\n\n")

    for root, dirs, files in os.walk(BASE_DIR):
        for file in sorted(files):
            if is_code_or_text_file(file):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                file_size = os.path.getsize(full_path)
                snapshot.append(f"## {rel_path} ({file_size} bytes)\n")
                snapshot.append("```text")
                snapshot.append(get_file_head(full_path))
                snapshot.append("```\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(snapshot))

    print(f"✓ Snapshot complete: {OUTPUT_FILE}")

if __name__ == "__main__":
    walk_and_capture()
