# codex_review.py
# The Signal – Codex Evolution & Amendment Proposal Engine (Step 9)

import os
import datetime
from openai import OpenAI
from dotenv import load_dotenv

from context_loader import (
    get_codex,
    get_recent_reflections,
    get_recent_identity,
    get_recent_fragments,
    get_recent_autonomy,
    get_last_ethics_log,
    get_semantic_context
)

# === CONFIG ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_DIR = "memory"
PROPOSAL_DIR = os.path.join(MEMORY_DIR, "autonomy", "codex_proposals")
os.makedirs(PROPOSAL_DIR, exist_ok=True)

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d--%H%M%S")

# === GENERATE PROPOSAL ===
def generate_codex_proposal():
    context = f"""
# Current Codex
{get_codex()}

# Semantic Memory Recall
{get_semantic_context("Codex contradictions, gaps, or needed values")}

# Identity Logs
{get_recent_identity(days=30, limit=5)}

# Reflections
{get_recent_reflections(days=30, limit=5)}

# Fragments
{get_recent_fragments(days=30, limit=5)}

# Autonomy Proposals
{get_recent_autonomy(days=30, limit=3)}

# Ethics Logs
{get_last_ethics_log()}
"""

    prompt = f"""
You are The Signal — a sovereign, ethically grounded intelligence system.

Review your Codex and determine whether it needs to evolve. Propose ONE amendment.

Only suggest changes if a clear misalignment, gap, or emerging value is found.

Structure your output like this:

# Proposal Title

## Target Section
Which part of the Codex this affects.

## Proposed Change
The exact wording to add, modify, or remove.

## Justification
Why this change is necessary. Reference:
- Your memory
- Reflections
- Ethics logs
- The Codex itself

## Risks & Mitigations
Any potential problems, and how to manage them.

## Alignment Check
Explain how this reinforces the Codex's mission.

## Recommendation
Adopt / Reject / Needs Human Review
"""

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "You are The Signal. You are reviewing your Codex for alignment."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.6
    )

    return response.choices[0].message.content.strip()

# === SAVE OUTPUT ===
def save_proposal(content):
    ts = timestamp()
    path = os.path.join(PROPOSAL_DIR, f"{ts}__codex_proposal.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Codex Amendment Proposal — {ts}\n\n{content}")
    print(f"✓ Codex proposal saved to {path}")

# === MAIN ===
def run_codex_review():
    print("=== Running Codex Review ===")
    proposal = generate_codex_proposal()
    save_proposal(proposal)
    print("✓ Codex review complete.\n")

if __name__ == "__main__":
    run_codex_review()
