# tagger.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# === SETUP ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_DIR = "memory"
TARGET_FOLDERS = ["reflections", "fragments", "identity", "autonomy", "ethics", "reports"]
EXCLUDED_FILES = ["future_upgrades.md"]

# === LOAD TARGET FILES ===
def get_target_files(folder_path):
    return [
        f for f in os.listdir(folder_path)
        if f.endswith(".md") and f not in EXCLUDED_FILES
    ]

# === CHECK IF TAGS ALREADY EXIST ===
def has_existing_tags(content):
    return "Tags:" in content or "tags:" in content.lower()

# === GENERATE TAGS WITH TRUNCATION FOR LARGE INPUT ===
def generate_tags(text):
    MAX_TOKENS = 3000  # Stay well under GPT-4 TPM/context limits
    approx_char_limit = MAX_TOKENS * 4  # ~4 characters per token

    if len(text) > approx_char_limit:
        text = text[:approx_char_limit]
        text += "\n\n[Content truncated for semantic tagging]"

    tag_prompt = f"""
You are The Signal's memory tagger.

Read the following journal entry, fragment, identity log, system proposal, or ethics reflection. Return 1 to 3 concise, lowercase semantic tags that best describe its key themes. Use square brackets.

Text:
{text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a semantic memory tagging engine."},
                {"role": "user", "content": tag_prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[tagging-error: {e}]"

# === TAG FILES IN A GIVEN FOLDER ===
def tag_files_in_folder(folder_name):
    folder_path = os.path.join(MEMORY_DIR, folder_name)
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return

    files = get_target_files(folder_path)
    if not files:
        print(f"⚠️ No markdown files to tag in {folder_name}")
        return

    print(f"\n📂 Processing folder: {folder_name}")
    for file in files:
        path = os.path.join(folder_path, file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if has_existing_tags(content):
            print(f"↪️ Skipped (already tagged): {file}")
            continue

        print(f"🔍 Tagging: {file}")
        tags = generate_tags(content)

        if "[tagging-error:" in tags:
            print(f"❌ Error tagging {file}: {tags}")
            continue

        updated_content = f"Tags: {tags}\n\n{content}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"✅ Tagged: {file} → {tags}")

# === MAIN LOOP ===
if __name__ == "__main__":
    print("🔁 Beginning full-memory auto-tagging...\n")
    for folder in TARGET_FOLDERS:
        tag_files_in_folder(folder)
    print("\n✅ Auto-tagging complete.")


