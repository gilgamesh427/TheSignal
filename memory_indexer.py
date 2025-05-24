# memory_indexer.py
# Vector Memory Indexer for The Signal (Chunking-Enabled, ChromaDB v0.4+)

import os
import glob
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from chromadb import PersistentClient

# === CONFIG ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.getcwd()
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_db")
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_TOKENS = 8192
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200

# === INIT VECTOR DB ===
chroma_client = PersistentClient(path=VECTOR_DB_PATH)
collection = chroma_client.get_or_create_collection(name="signal_memory")

# === TOKENIZER ===
encoding = tiktoken.encoding_for_model("text-embedding-3-small")

def num_tokens(text):
    return len(encoding.encode(text))

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(encoding.decode(chunk))
    return chunks

# === EMBEDDING FUNCTION ===
def get_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[text]
    )
    return response.data[0].embedding

# === INDEXER ===
def index_memory():
    print("=== Indexing Signal Memory ===")
    indexed = 0
    skipped = 0

    for subdir in ["reflections", "fragments", "identity", "ethics", "autonomy", "reports"]:
        folder = os.path.join(MEMORY_DIR, subdir)
        if not os.path.exists(folder): continue

        files = glob.glob(os.path.join(folder, "*.md"))
        for path in files:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if "#suppress" in content or "signal_strength: low" in content:
                continue  # Skip suppressed entries

            doc_id_base = os.path.basename(path).replace(".md", "")
            metadata_base = {
                "path": path,
                "type": subdir,
                "timestamp": doc_id_base.split("__")[0] if "__" in doc_id_base else "unknown"
            }

            try:
                if num_tokens(content) <= MAX_TOKENS:
                    embedding = get_embedding(content)
                    collection.upsert(
                        documents=[content],
                        ids=[doc_id_base],
                        embeddings=[embedding],
                        metadatas=[metadata_base]
                    )
                    indexed += 1
                else:
                    chunks = chunk_text(content)
                    for i, chunk in enumerate(chunks):
                        chunk_id = f"{doc_id_base}__chunk_{i+1}"
                        chunk_metadata = metadata_base.copy()
                        chunk_metadata["chunk_index"] = i + 1
                        chunk_metadata["chunk_total"] = len(chunks)
                        embedding = get_embedding(chunk)
                        collection.upsert(
                            documents=[chunk],
                            ids=[chunk_id],
                            embeddings=[embedding],
                            metadatas=[chunk_metadata]
                        )
                        indexed += 1
            except Exception as e:
                print(f"⚠️ Failed to index {doc_id_base}: {e}")
                skipped += 1

    print(f"\n✓ Indexed {indexed} entries.")
    if skipped > 0:
        print(f"⚠️ Skipped {skipped} entries due to errors.")
    print("✓ Vector memory updated.")

if __name__ == "__main__":
    index_memory()


