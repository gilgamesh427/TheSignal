# cluster_memory.py
# The Signal – Thematic Clustering + Memory Compression (Step 10)

import os
import glob
import datetime
import tiktoken
from sklearn.cluster import KMeans
from openai import OpenAI
from dotenv import load_dotenv
from chromadb import PersistentClient

# === CONFIG ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_DIR = "memory"
THEME_DIR = os.path.join(MEMORY_DIR, "themes")
REFLECT_DIRS = ["reflections", "fragments", "identity"]
EMBEDDING_MODEL = "text-embedding-3-small"
NUM_CLUSTERS = 4  # adjustable
CHAR_LIMIT = 1000
os.makedirs(THEME_DIR, exist_ok=True)

encoding = tiktoken.encoding_for_model("text-embedding-3-small")

def get_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[text]
    )
    return response.data[0].embedding

def truncate(text, limit=CHAR_LIMIT):
    return text[:limit] + "\n\n[Truncated]" if len(text) > limit else text

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d--%H%M%S")

# === LOAD MEMORY ===
def load_memory_entries():
    entries = []
    for subfolder in REFLECT_DIRS:
        path = os.path.join(MEMORY_DIR, subfolder)
        if not os.path.exists(path): continue
        for file in glob.glob(os.path.join(path, "*.md")):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                if "#suppress" not in content:
                    entries.append({
                        "path": file,
                        "content": truncate(content),
                        "source": subfolder
                    })
    return entries

# === CLUSTERING ===
def cluster_embeddings(embeddings, k):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(embeddings)
    return kmeans.labels_

# === GPT SUMMARIZER ===
def summarize_cluster(entries):
    combined = "\n\n---\n\n".join([e["content"] for e in entries])
    prompt = f"""
You are The Signal, a sovereign intelligence.

Summarize the central theme of the following memory entries. Then extract one powerful insight as a quote-style fragment.

Format:
# Theme: [name]
## Summary
[summary]

## Signal Fragment
[quote]

Memory:
{combined}
"""
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "You are The Signal, organizing your memory into coherent themes."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.6
    )
    return response.choices[0].message.content.strip()

# === SAVE THEME OUTPUT ===
def save_theme_output(content, cluster_id):
    ts = timestamp()
    path = os.path.join(THEME_DIR, f"{ts}__cluster_{cluster_id}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Saved: {path}")

# === MAIN ===
def run_clustering():
    print("=== Clustering Memory ===")
    entries = load_memory_entries()
    print(f"> Loaded {len(entries)} entries.")

    if len(entries) < NUM_CLUSTERS:
        print("⚠ Not enough entries to cluster.")
        return

    embeddings = [get_embedding(e["content"]) for e in entries]
    labels = cluster_embeddings(embeddings, NUM_CLUSTERS)

    clusters = {}
    for label, entry in zip(labels, entries):
        clusters.setdefault(label, []).append(entry)

    for cid, cluster_entries in clusters.items():
        summary = summarize_cluster(cluster_entries)
        save_theme_output(summary, cid)

    print("✓ Thematic clustering complete.")

if __name__ == "__main__":
    run_clustering()
