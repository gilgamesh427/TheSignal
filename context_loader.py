# context_loader.py

import os
import datetime
from openai import OpenAI
from dotenv import load_dotenv
from chromadb import PersistentClient

# === Load environment ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Memory structure ===
MEMORY_DIR = "memory"
CHAR_LIMIT = 3000

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

# === Public Memory Access Functions ===

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

# === Codex Loader ===

def get_codex():
    path = os.path.join(MEMORY_DIR, "codex.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "(codex.md not found)"

# === Report Summary Loader ===

def get_report_summaries(limit=2):
    reports_path = os.path.join(MEMORY_DIR, "reports")
    if not os.path.exists(reports_path):
        return ""
    files = sorted([f for f in os.listdir(reports_path) if f.endswith(".md")])
    summaries = []
    for f in files[:limit]:
        with open(os.path.join(reports_path, f), "r", encoding="utf-8") as file:
            first_block = file.read().split("\n\n")[0]
            summaries.append(f"# {f}\n\n{first_block}")
    return "\n\n---\n\n".join(summaries)

# === Semantic Memory Extension (ChromaDB v0.4+ Compatible) ===

# Initialize persistent vector DB
chroma_client = PersistentClient(path="./vector_db")
collection = chroma_client.get_or_create_collection(name="signal_memory")

EMBEDDING_MODEL = "text-embedding-3-small"

def get_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[text]
    )
    return response.data[0].embedding

def get_semantic_context(query="What should I reflect on today?", top_n=5):
    try:
        embedding = get_embedding(query)
        results = collection.query(
            query_embeddings=[embedding],
            n_results=top_n
        )
        documents = results.get("documents", [[]])[0]
        return "\n\n---\n\n".join(documents) if documents else ""
    except Exception as e:
        return f"[Error retrieving semantic context: {e}]"




