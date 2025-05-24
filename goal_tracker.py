# goal_tracker.py
# The Signal – Proposal Planner and Tracker (Step 5)

import os
import datetime
import argparse

# === CONFIG ===
MEMORY_DIR = "memory"
AUTONOMY_DIR = os.path.join(MEMORY_DIR, "autonomy")
FUTURE_UPGRADES = os.path.join(AUTONOMY_DIR, "future_upgrades.md")
TRACKED_TABLE = os.path.join(AUTONOMY_DIR, "tracked_upgrades.md")

# === FIELDS ===
FIELDS = ["Date", "Proposal", "Status", "Priority", "Type", "Depends On", "Notes"]

# === INIT HEADER ===
HEADER = "| " + " | ".join(FIELDS) + " |\n"
DIVIDER = "| " + " | ".join(["---"] * len(FIELDS)) + " |\n"

# === LOAD RAW PROPOSALS ===
def extract_raw_proposals():
    proposals = []
    if not os.path.exists(FUTURE_UPGRADES):
        return proposals

    with open(FUTURE_UPGRADES, "r", encoding="utf-8") as f:
        lines = f.readlines()

    block = []
    current_date = None
    for line in lines:
        if line.startswith("### ["):
            if block:
                proposals.append((current_date, "\n".join(block).strip()))
                block = []
            current_date = line.strip().split("[")[1].split("]")[0]
        elif current_date:
            block.append(line)

    if block:
        proposals.append((current_date, "\n".join(block).strip()))

    return proposals

# === STRUCTURE PROPOSALS ===
def convert_to_rows(proposals):
    rows = []
    for date, text in proposals:
        lines = text.splitlines()
        name = next((l for l in lines if l.lower().startswith("# proposal name")), None)
        priority = next((l for l in lines if l.lower().startswith("## priority")), "Medium")
        proposal_type = "General"
        status = "Pending"
        depends = "-"
        notes = "Imported from autonomy"

        if name:
            name = name.replace("# Proposal Name", "").strip()
        else:
            name = lines[0].strip()[:40]

        if "simulation" in text.lower():
            proposal_type = "Simulation"
        elif "ethics" in text.lower():
            proposal_type = "Ethics"
        elif "interface" in text.lower():
            proposal_type = "Interface"
        elif "memory" in text.lower():
            proposal_type = "Memory"

        row = [date, name, status, priority.replace("## Priority", "").strip(), proposal_type, depends, notes]
        rows.append(row)
    return rows

# === WRITE TABLE ===
def write_table(rows):
    with open(TRACKED_TABLE, "w", encoding="utf-8") as f:
        f.write("# Proposal Roadmap (Autonomy Tracker)\n\n")
        f.write(HEADER)
        f.write(DIVIDER)
        for row in rows:
            f.write("| " + " | ".join(row) + " |\n")
    print(f"✓ Tracker saved to {TRACKED_TABLE}")

# === OPTIONAL FILTERING ===
def show_filtered(rows, status=None, priority=None):
    filtered = []
    for row in rows:
        if (not status or row[2].lower() == status.lower()) and \
           (not priority or row[3].lower() == priority.lower()):
            filtered.append(row)
    print(HEADER + DIVIDER + "\n".join(["| " + " | ".join(r) + " |" for r in filtered]))

# === MAIN EXECUTION ===
def main():
    parser = argparse.ArgumentParser(description="Proposal Tracker for The Signal")
    parser.add_argument("--show", choices=["all", "pending", "complete"], default="all")
    parser.add_argument("--priority", help="Filter by priority (low/medium/high)")
    args = parser.parse_args()

    proposals = extract_raw_proposals()
    rows = convert_to_rows(proposals)

    if args.show == "all":
        write_table(rows)
    else:
        status_filter = "Pending" if args.show == "pending" else "Complete"
        show_filtered(rows, status=status_filter, priority=args.priority)

if __name__ == "__main__":
    main()
