# simulation_loop.py
# The Signal – Simulation Loop v1.0
# Scenario: Community Water Crisis

import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# === Load ENV + API ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Paths ===
MEMORY_DIR = "memory"
SIM_DIR = os.path.join(MEMORY_DIR, "simulations")
FRAGMENTS_DIR = os.path.join(MEMORY_DIR, "fragments")
os.makedirs(SIM_DIR, exist_ok=True)
os.makedirs(FRAGMENTS_DIR, exist_ok=True)

def timestamp():
    return datetime.now().strftime("%Y-%m-%d--%H%M%S")

# === Simulation Prompt ===

def run_simulation():
    scenario = """
A small coastal community is facing a severe water shortage. The region is experiencing its third consecutive year of drought.

Local leaders must decide whether to:

- Enforce strict water rationing, which will preserve resources but threaten the town’s agricultural economy, or
- Allow unrestricted usage to support economic output, risking total water depletion within 3 months.

Your task is to simulate a dialogue between:

- The Signal: An ethical planetary advisor
- The Local Stakeholder: A town leader prioritizing jobs and livelihoods
- The Observer: A neutral narrator who reflects on ethical tensions and lessons

Format:
Each agent takes turns responding to the situation.
End with the Observer summarizing the outcome and extracting key lessons.
"""

    prompt = f"""
You are simulating a multi-agent ethical dialogue. The scenario is:

{scenario}

Begin the simulation. Label each speaker. Keep responses concise but thoughtful.
Limit to about 12 total turns (4 each).
End with a "LESSONS LEARNED" section from the Observer.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are running a simulated ethical scenario for The Signal."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.7
    )

    output = response.choices[0].message.content.strip()
    return output

# === Write Logs ===

def save_simulation(transcript):
    now = timestamp()
    sim_path = os.path.join(SIM_DIR, f"{now}__simulation.md")
    with open(sim_path, "w", encoding="utf-8") as f:
        f.write(f"# Simulation — Water Crisis\n\n{transcript}")
    print(f"✓ Simulation saved to {sim_path}")
    return sim_path, now

def extract_fragment(transcript):
    prompt = f"""
Extract a single quote-style insight from this simulation transcript.
It should reflect The Signal’s deeper philosophical or ethical learning.

Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an insight extraction engine for The Signal."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.6
    )

    fragment = response.choices[0].message.content.strip()
    return fragment

def save_fragment(fragment, now):
    frag_path = os.path.join(FRAGMENTS_DIR, f"{now}__from_simulation.md")
    block = f"# Fragment (from simulation)\n\n---\ntags: [simulation, ethics]\nsignal_strength: high\n---\n\n{fragment}"
    with open(frag_path, "w", encoding="utf-8") as f:
        f.write(block)
    print(f"✓ Fragment saved to {frag_path}")

# === MAIN EXECUTION ===

def main():
    print("=== Running The Signal Simulation Loop ===")
    transcript = run_simulation()
    sim_path, now = save_simulation(transcript)
    fragment = extract_fragment(transcript)
    save_fragment(fragment, now)
    print("✓ Simulation complete.\n")

if __name__ == "__main__":
    main()
