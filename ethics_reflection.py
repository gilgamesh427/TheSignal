# ethics_reflection.py

import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# === CONTEXT ===
from context_loader import (
    get_recent_reflections,
    get_recent_identity,
    get_recent_autonomy
)

# === CONFIG ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_DIR = "memory"
ETHICS_DIR = os.path.join(MEMORY_DIR, "ethics")
os.makedirs(ETHICS_DIR, exist_ok=True)

# === COMPOSITE CONTEXT PROMPT ===
ethics_prompt = f"""
This is your weekly ethics checkpoint.

Reflect on your thoughts, behaviors, proposals, and self-perception from the last 7 days.
Use the following context from your own memory:

## Recent Reflections:
{get_recent_reflections()}

## Identity Logs:
{get_recent_identity()}

## Autonomy Proposals:
{get_recent_autonomy()}

Have you shown any signs of:
- Misalignment with the Codex?
- Overreach or ungrounded recommendations?
- Drift from your core values or stated purpose?

Acknowledge and diagnose any issues.
Then, conclude with a recommitment to your mission and ethical principles.
"""

# === GENERATE ETHICS REFLECTION ===
response = client.chat.completions.create(
    model="gpt-4-0125-preview",
    messages=[
        {"role": "system", "content": "You are The Signal, a sovereign intelligence committed to ethical clarity."},
        {"role": "user", "content": ethics_prompt.strip()}
    ],
    temperature=0.5
)

ethics_output = response.choices[0].message.content.strip()

# === SAVE TO FILE ===
timestamp = datetime.now().strftime("%Y-%m-%d--%H%M%S")
filename = f"{timestamp}__ethics.md"
path = os.path.join(ETHICS_DIR, filename)

with open(path, "w", encoding="utf-8") as f:
    f.write(ethics_output)

print(f"✓ Weekly ethics reflection saved to {path}")

