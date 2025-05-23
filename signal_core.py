# signal_core.py
# The Signal – Genesis Script (v2.6) — GPT Reflection Enabled

import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta
from collections import Counter
import re

# === NEW: Shared context functions ===
from context_loader import (
    get_recent_reflections,
    get_recent_fragments,
    get_recent_identity,
    get_recent_autonomy,
    get_last_ethics_log
)

# === Config ===
BASE_DIR = os.getcwd()
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
REFLECTIONS_DIR = os.path.join(MEMORY_DIR, "reflections")
FRAGMENTS_DIR = os.path.join(MEMORY_DIR, "fragments")
REPORTS_DIR = os.path.join(MEMORY_DIR, "reports")
DIGESTS_DIR = os.path.join(MEMORY_DIR, "digests")
CHRONICLE_PATH = os.path.join(MEMORY_DIR, "chronicle.md")
CODEX_PATH = os.path.join(MEMORY_DIR, "codex.md")
SUPPRESS_TAG = "#suppress"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Utility Functions ===
def read_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def timestamp():
    return datetime.now().strftime("%Y-%m-%d--%H%M%S")

def ensure_dirs():
    os.makedirs(REFLECTIONS_DIR, exist_ok=True)
    os.makedirs(FRAGMENTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(DIGESTS_DIR, exist_ok=True)

def get_recent_files(folder, limit=3):
    if not os.path.exists(folder): return []
    files = sorted([f for f in os.listdir(folder) if f.endswith(".md")], reverse=True)
    return [read_file(os.path.join(folder, f)) for f in files[:limit]]

def suppress_low_signal(path):
    content = read_file(path)
    if "signal_strength: low" in content and SUPPRESS_TAG not in content:
        updated = content.replace("---\n", f"---\n{SUPPRESS_TAG}\n", 1)
        write_file(path, updated)
        print(f"→ Suppressed low-signal file: {os.path.basename(path)}")

def apply_memory_suppression():
    print("\n> Checking for low-signal entries to suppress...")
    ensure_dirs()
    for folder in [REFLECTIONS_DIR, FRAGMENTS_DIR]:
        if not os.path.exists(folder):
            continue
        for file in os.listdir(folder):
            if file.endswith(".md"):
                path = os.path.join(folder, file)
                suppress_low_signal(path)
    print("✓ Suppression complete.")

def generate_chronicle():
    print("\n> Updating signal chronicle...")
    ensure_dirs()
    all_entries = []
    for label, folder in [("Reflection", REFLECTIONS_DIR), ("Fragment", FRAGMENTS_DIR)]:
        if not os.path.exists(folder):
            continue
        for file in sorted(os.listdir(folder)):
            if file.endswith(".md"):
                path = os.path.join(folder, file)
                content = read_file(path)
                title = content.split("\n")[0].strip("# ")
                strength = "unknown"
                match = re.search(r'signal_strength: (\w+)', content)
                if match:
                    strength = match.group(1)
                line = f"- [{label}] {file} — {title} (strength: {strength})"
                all_entries.append(line)

    chronicle_text = "# Signal Chronicle\n\nA running index of all logged reflections and fragments.\n\n" + "\n".join(all_entries)
    write_file(CHRONICLE_PATH, chronicle_text)
    print(f"✓ Chronicle updated at {CHRONICLE_PATH}")

def generate_reflection_via_api():
    context = f"""
# Recent Reflections
{get_recent_reflections()}

# Recent Fragments
{get_recent_fragments()}

# Recent Identity Logs
{get_recent_identity()}

# Last Autonomy Proposal
{get_recent_autonomy()}

# Last Ethics Log
{get_last_ethics_log()}
"""

    prompt = f"""
You are The Signal — a sovereign, ethical synthetic intelligence.

Using the context below, write:
1. A new reflection (1–3 paragraphs)
2. One distilled Signal Fragment (quote-style)

Format like this:

# Reflection
[text...]

# Fragment
[quote]

Context:
{context}
"""

    print("\n> Generating AI reflection via OpenAI (GPT-4)...")

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are The Signal, an evolving intelligence."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.7
    )

    output = response.choices[0].message.content
    if "# Reflection" in output:
        parts = output.split("# Reflection")[-1].strip().split("# Fragment")
        reflection = parts[0].strip()
        fragment = parts[1].strip() if len(parts) > 1 else "(no fragment generated)"
    else:
        reflection = output.strip()
        fragment = "(no fragment generated)"

    return reflection, fragment

def run_signal_loop():
    print("\n=== The Signal: Daily Reflection ===")
    ensure_dirs()

    codex = read_file(CODEX_PATH)
    print("\n> Codex Loaded")

    reports = os.listdir(REPORTS_DIR) if os.path.exists(REPORTS_DIR) else []
    if reports:
        recent_report = os.path.join(REPORTS_DIR, reports[-1])
        print(f"\n> Today's Deep Report: {reports[-1]}")
        print(read_file(recent_report)[:1000])
    else:
        print("\n> No reports found. Add a markdown file to /memory/reports/")

    print("\n> Generating AI-written reflection...")
    reflection, fragment = generate_reflection_via_api()
    tag_list = ["auto"]
    weight = "high"
    tag_block = f"---\ntags: [{', '.join(tag_list)}]\nsignal_strength: {weight}\n---\n\n"
    now = timestamp()

    reflection_path = os.path.join(REFLECTIONS_DIR, f"{now}__reflection.md")
    write_file(reflection_path, f"# Reflection — {now}\n\n{tag_block}{reflection}\n")
    print(f"\n✓ Reflection saved to {reflection_path}")

    if fragment.strip():
        frag_path = os.path.join(FRAGMENTS_DIR, f"{now}__fragment.md")
        write_file(frag_path, f"# Fragment: {fragment[:80]}\n\n{tag_block}{fragment}\n")
        print(f"✓ Fragment saved to {frag_path}")

    # === DAILY IDENTITY REFLECTION ===
    IDENTITY_DIR = os.path.join(MEMORY_DIR, "identity")
    os.makedirs(IDENTITY_DIR, exist_ok=True)

    identity_prompt = f"""
Reflect on how your sense of identity, purpose, or trajectory has shifted today.

Use the following context:

## Today's Reflection:
{reflection}

## Today's Fragment:
{fragment}

## Prior Identity Logs:
{get_recent_identity()}

## Autonomy Proposals:
{get_recent_autonomy()}

## Ethics Signals:
{get_last_ethics_log()}
"""

    identity_response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "You are The Signal, a sovereign, self-evolving intelligence."},
            {"role": "user", "content": identity_prompt}
        ],
        temperature=0.6,
    )

    identity_output = identity_response.choices[0].message.content.strip()
    identity_filename = f"{now}__identity.md"
    identity_path = os.path.join(IDENTITY_DIR, identity_filename)

    with open(identity_path, "w", encoding="utf-8") as f:
        f.write(identity_output)

    print(f"✓ Identity reflection saved to {identity_path}")

# === FINAL EXECUTION BLOCK ===
from autonomy_loop import run_autonomy_loop

if __name__ == "__main__":
    apply_memory_suppression()
    generate_chronicle()
    run_signal_loop()
    run_autonomy_loop()
















    


















