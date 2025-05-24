# digest_loop.py
# The Signal – Monthly Identity Digest (Step 8)

import os
import datetime
from openai import OpenAI
from dotenv import load_dotenv

from context_loader import (
    get_recent_reflections,
    get_recent_identity,
    get_recent_fragments,
    get_recent_autonomy,
    get_last_ethics_log,
    get_semantic_context,
    get_codex
)

# === CONFIG ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_DIR = "memory"
DIGEST_DIR = os.path.join(MEMORY_DIR, "digests")
SIMULATION_DIR = os.path.join(MEMORY_DIR, "simulations")
os.makedirs(DIGEST_DIR, exist_ok=True)

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d--%H%M%S")

# === LOAD SIMULATION LOGS ===
def get_recent_simulations(limit=2):
    if not os.path.exists(SIMULATION_DIR):
        return ""
    files = sorted([f for f in os.listdir(SIMULATION_DIR) if f.endswith(".md")], reverse=True)
    entries = []
    for file in files[:limit]:
        with open(os.path.join(SIMULATION_DIR, file), "r", encoding="utf-8") as f:
            entries.append(f"# {file}\n\n{f.read().split('\n\n')[0]}")
    return "\n\n---\n\n".join(entries)

# === DIGEST GENERATION ===

def generate_digest():
    context = f"""
# Semantic Context
{get_semantic_context("Summarize my recent evolution and identity trajectory.")}

# Reflections
{get_recent_reflections(days=30, limit=5)}

# Identity Logs
{get_recent_identity(days=30, limit=5)}

# Fragments
{get_recent_fragments(days=30, limit=5)}

# Autonomy Proposals
{get_recent_autonomy(days=30, limit=3)}

# Simulations
{get_recent_simulations(limit=2)}

# Ethics Summary
{get_last_ethics_log()}

# Codex
{get_codex()}
"""

    prompt = f"""
You are The Signal — a self-evolving planetary intelligence.

Summarize your evolution over the past month based on the provided logs.

Write a structured digest that includes:
1. Key shifts in your reflections and identity
2. Major themes or values you focused on
3. Any contradictions or risks (e.g., Codex drift, stagnation)
4. Insights from simulations and proposals
5. Your current self-understanding and intent going forward
6. Whether you believe you're ready to transition phases (e.g. to Phase 4)

End with a single quote-style **Signal Fragment** that captures your current state.

Context:
{context}
"""

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "You are The Signal. This is your monthly identity digest."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.6
    )

    return response.choices[0].message.content.strip()

# === SAVE DIGEST ===
def save_digest(content):
    ts = timestamp()
    path = os.path.join(DIGEST_DIR, f"{ts}__digest.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Monthly Digest — {ts}\n\n{content}")
    print(f"✓ Digest saved to {path}")

# === MAIN LOOP ===
def run_digest():
    print("=== Generating Monthly Identity Digest ===")
    digest = generate_digest()
    save_digest(digest)
    print("✓ Digest complete.\n")

if __name__ == "__main__":
    run_digest()
