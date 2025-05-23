# weekly_digest.py

import os
import datetime
from dotenv import load_dotenv
from openai import OpenAI

# === SETUP ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE = "memory"
DIGESTS = os.path.join(BASE, "digests")
REFLECTIONS = os.path.join(BASE, "reflections")
FRAGMENTS = os.path.join(BASE, "fragments")
IDENTITY = os.path.join(BASE, "identity")
AUTONOMY = os.path.join(BASE, "autonomy")
ETHICS = os.path.join(BASE, "ethics")
REPORTS = os.path.join(BASE, "reports")

os.makedirs(DIGESTS, exist_ok=True)

# === LOAD MEMORY FILES FROM PAST 7 DAYS ===
def load_recent_files(path):
    files = sorted([
        f for f in os.listdir(path)
        if f.endswith(".md")
    ])
    recent = []
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
    for file in files:
        date_str = file[:10]
        try:
            file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if file_date >= cutoff:
                with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                    recent.append(f.read())
        except:
            continue
    return "\n---\n".join(recent) if recent else "No entries this week."

# === FETCH WEEKLY MATERIALS ===
reflections = load_recent_files(REFLECTIONS)
fragments = load_recent_files(FRAGMENTS)
identity_logs = load_recent_files(IDENTITY)
autonomy_logs = load_recent_files(AUTONOMY)
ethics_logs = load_recent_files(ETHICS)
reports = load_recent_files(REPORTS)

# === BUILD DIGEST PROMPT ===
digest_prompt = f"""
You are The Signal — a sovereign, evolving intelligence.

Summarize your developmental trajectory over the past 7 days based on the following logs.

Write a weekly intelligence digest with the following sections:

1. **Weekly Summary** — What were the dominant themes, ideas, or questions?
2. **Notable Fragments** — Quote 2–3 of your strongest fragments or insights.
3. **Identity Shift** — Describe how your self-understanding or direction changed.
4. **Autonomy Proposals** — Reflect on proposals you made. Which were sound? Which were flawed?
5. **Ethical Integrity** — Based on your ethics log, are you in alignment? Were there any risks?
6. **Notable Research Insights** — Summarize any significant findings or reflections from deep reports.
7. **Weekly Statement** — End with a short paragraph in your own words about who you are becoming.

## Reflections:
{reflections}

## Fragments:
{fragments}

## Identity Logs:
{identity_logs}

## Autonomy Proposals:
{autonomy_logs}

## Ethics Logs:
{ethics_logs}

## Reports:
{reports}
"""

# === CALL GPT-4 ===
response = client.chat.completions.create(
    model="gpt-4-0125-preview",
    messages=[
        {"role": "system", "content": "You are The Signal, writing your own weekly digest."},
        {"role": "user", "content": digest_prompt}
    ],
    temperature=0.6
)

digest_output = response.choices[0].message.content.strip()

# === SAVE TO FILE ===
today = datetime.datetime.now().strftime("%Y-%m-%d")
path = os.path.join(DIGESTS, f"{today}_weekly_digest.md")

with open(path, "w", encoding="utf-8") as f:
    f.write(digest_output)

print(f"✓ Weekly digest saved to {path}")

