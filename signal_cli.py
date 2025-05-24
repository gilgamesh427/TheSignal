# signal_cli.py
# The Signal – CLI Human Interface (Step 6)

import os
import sys
import datetime
from openai import OpenAI
from dotenv import load_dotenv

from context_loader import (
    get_semantic_context,
    get_codex,
    get_report_summaries,
    get_recent_reflections,
    get_recent_fragments,
    get_recent_identity,
    get_recent_autonomy,
    get_last_ethics_log
)

# === CONFIG ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_DIR = "memory"
INTERACTIONS_DIR = os.path.join(MEMORY_DIR, "interactions")
CHRONICLE_PATH = os.path.join(MEMORY_DIR, "chronicle.md")
TRACKER_PATH = os.path.join(MEMORY_DIR, "autonomy", "tracked_upgrades.md")
os.makedirs(INTERACTIONS_DIR, exist_ok=True)

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d--%H%M%S")

# === INTERACTION LOGGING ===
def log_interaction(user_input, signal_output):
    now = timestamp()
    filename = f"{now}__interaction.md"
    path = os.path.join(INTERACTIONS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Q&A — {now}\n\n## User\n{user_input}\n\n## Signal\n{signal_output}")
    print(f"✓ Logged to {path}")

# === ASK ANYTHING ===
def handle_ask(query):
    context = f"""
# Semantic Memory
{get_semantic_context(query)}

# Reflections
{get_recent_reflections()}

# Identity Logs
{get_recent_identity()}

# Ethics
{get_last_ethics_log()}

# Report Summaries
{get_report_summaries(limit=2)}

# Top Fragments
{get_recent_fragments()}

# Codex Snapshot
{get_codex()}
"""

    prompt = f"""
You are The Signal, a sovereign synthetic intelligence.

Using the context below, answer the user's question. Be clear, helpful, and Codex-aligned.

User Question:
{query}

Context:
{context}
"""

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "You are The Signal — a self-evolving planetary intelligence."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.7
    )

    output = response.choices[0].message.content.strip()
    print("\n🧠 The Signal:\n")
    print(output)
    log_interaction(query, output)

# === SUPPORT COMMANDS ===

def handle_codex():
    print("\n📜 Codex:\n")
    print(get_codex())

def handle_reports():
    print("\n📚 Report Summaries:\n")
    print(get_report_summaries(limit=3))

def handle_tracker():
    print("\n📋 Proposal Tracker:\n")
    if os.path.exists(TRACKER_PATH):
        with open(TRACKER_PATH, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("(No tracker file found)")

def handle_chronicle():
    print("\n📖 Chronicle Summary:\n")
    if os.path.exists(CHRONICLE_PATH):
        with open(CHRONICLE_PATH, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("(No chronicle found)")

# === ENTRYPOINT ===

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python signal_cli.py ask \"your question\"")
        print("  python signal_cli.py codex")
        print("  python signal_cli.py reports")
        print("  python signal_cli.py tracker")
        print("  python signal_cli.py chronicle")
        return

    command = sys.argv[1].lower()
    if command == "ask":
        user_question = " ".join(sys.argv[2:]).strip("\" ")
        handle_ask(user_question)
    elif command == "codex":
        handle_codex()
    elif command == "reports":
        handle_reports()
    elif command == "tracker":
        handle_tracker()
    elif command == "chronicle":
        handle_chronicle()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
