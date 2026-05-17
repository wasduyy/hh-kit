import json
import os
import sqlite3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_DIR = os.path.dirname(HARNESS_DIR)
CONTROL_DIR = os.path.join(PROJECT_DIR, ".control")

print("=== archAIHelper Diagnostics ===\n")

print("[1/5] Checking core files...")
for label, path in [
    ("harness.yml", os.path.join(CONTROL_DIR, "harness.yml")),
    ("state.json", os.path.join(CONTROL_DIR, "state.json")),
    ("activeContext.md", os.path.join(CONTROL_DIR, "memory-bank", "activeContext.md")),
]:
    if os.path.exists(path):
        print(f"  OK: {label}")
    else:
        print(f"  MISSING: {label} ({path})")

print("\n[2/5] Checking SQLite database...")
db_path = os.path.join(CONTROL_DIR, "trace.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM trace_nodes").fetchone()[0]
    conn.close()
    print(f"  OK: Database has {count} trace nodes")
else:
    print("  MISSING: trace.db (run .harness/scripts/setup-layer1.py)")

print("\n[3/5] Checking configuration...")
harness_path = os.path.join(CONTROL_DIR, "harness.yml")
if os.path.exists(harness_path):
    with open(harness_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "override:" in content:
        print("  INFO: override section found in harness.yml")
    else:
        print("  INFO: Using all framework defaults (no overrides)")
else:
    print("  MISSING: harness.yml")

print("\n[4/5] Checking Git hooks...")
git_hooks = os.path.join(PROJECT_DIR, ".git", "hooks")
for hook in ["pre-commit", "commit-msg"]:
    path = os.path.join(git_hooks, hook)
    if os.path.exists(path):
        print(f"  OK: {hook} installed")
    else:
        print(f"  MISSING: {hook} (run .harness/scripts/setup-layer1.py)")

print("\n[5/5] Checking trace integrity...")
db_path = os.path.join(CONTROL_DIR, "trace.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    sql_path = os.path.join(HARNESS_DIR, ".scaffold", "sql", "queries", "trace-completeness.sql")
    if os.path.exists(sql_path):
        with open(sql_path, "r", encoding="utf-8") as f:
            sql = f.read()
        rows = conn.execute(sql).fetchall()
        if len(rows) == 0:
            print("  OK: All trace chains complete")
        else:
            print(f"  WARN: {len(rows)} broken chain(s) detected")
    else:
        print("  SKIP: completeness query not found")
    conn.close()
else:
    print("  SKIP: No database to check")

print("\n" + "=" * 40)
print("All checks passed." if all([
    os.path.exists(os.path.join(CONTROL_DIR, "harness.yml")),
    os.path.exists(os.path.join(CONTROL_DIR, "state.json")),
    os.path.exists(db_path),
]) else "Some checks failed. See above for details.")
