# context_loader.py

import os
import datetime

MEMORY_DIR = "memory"
CHAR_LIMIT = 3000  # Soft cap per block for GPT safety

FOLDERS = {
    "reflections": os.path.join(MEMORY_DIR, "reflections"),
    "fragments": os.path.join(MEMORY_DIR, "fragments"),
    "identity": os.path.join(MEMORY_DIR, "identity"),
    "autonomy": os.path.join(MEMORY_DIR, "autonomy"),
    "ethics": os.path.join(MEMORY_DIR, "ethics"),
    "reports": os.path.join(MEMORY_DIR, "reports"),
}

def load_recent_files(folder, days=7, limit=None):
    folder_path = FOLDERS.get(folder)
    if not folder_path or not os.path.exists(folder_path):
        return ""

    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".md")])
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    recent = []

    for file in reversed(files):  # most recent first
        try:
            date_str = file[:10]
            file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if file_date >= cutoff:
                with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    recent.append(content)
        except Exception:
            continue

        if limit and len(recent) >= limit:
            break

    return "\n---\n".join(recent[:limit]) if recent else ""

def truncate(text, char_limit=CHAR_LIMIT):
    return text[:char_limit] + "\n\n[Truncated]" if len(text) > char_limit else text

# === Public Functions ===

def get_recent_reflections(days=5, limit=3):
    return truncate(load_recent_files("reflections", days, limit))

def get_recent_fragments(days=7, limit=3):
    return truncate(load_recent_files("fragments", days, limit))

def get_recent_identity(days=5, limit=2):
    return truncate(load_recent_files("identity", days, limit))

def get_recent_autonomy(days=5, limit=2):
    return truncate(load_recent_files("autonomy", days, limit))

def get_last_ethics_log():
    logs = load_recent_files("ethics", days=14, limit=1)
    return truncate(logs)

def get_recent_reports(days=14, limit=1):
    return truncate(load_recent_files("reports", days, limit))
