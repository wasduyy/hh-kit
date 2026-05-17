import os
import sqlite3
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_DIR = os.path.dirname(HARNESS_DIR)
CONTROL_DIR = os.path.join(PROJECT_DIR, ".control")

SCHEMA_PATH = os.path.join(HARNESS_DIR, ".scaffold", "sql", "init-trace.sql")
HOOKS_DIR = os.path.join(HARNESS_DIR, ".scaffold", "hooks")
STATE_SRC = os.path.join(HARNESS_DIR, "templates", "_blank", "state.json")

print("=== archAIHelper Layer 1 Setup ===\n")

print("[1/3] Initializing SQLite database...")
db_path = os.path.join(CONTROL_DIR, "trace.db")
os.makedirs(CONTROL_DIR, exist_ok=True)
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    sql = f.read()
conn = sqlite3.connect(db_path)
conn.executescript(sql)
conn.close()
print(f"  [OK] SQLite database initialized: {db_path}")

print("\n[2/3] Installing Git hooks...")
git_hooks = os.path.join(PROJECT_DIR, ".git", "hooks")
if os.path.exists(git_hooks):
    for hook in ["pre-commit", "commit-msg"]:
        src = os.path.join(HOOKS_DIR, hook)
        dst = os.path.join(git_hooks, hook)
        shutil.copy2(src, dst)
        os.chmod(dst, 0o755)
        print(f"  [OK] Installed hook: {hook}")
else:
    print("  [SKIP] .git/hooks not found (not a git repo?)")

print("\n[3/3] Checking state file...")
state_path = os.path.join(CONTROL_DIR, "state.json")
if os.path.exists(state_path):
    print("  [SKIP] state.json already exists")
elif os.path.exists(STATE_SRC):
    shutil.copy2(STATE_SRC, state_path)
    print(f"  [OK] Created state.json from template")
else:
    print("  [WARN] No state.json template found")

print("\nSetup complete. Next steps:")
print("  1. Run: .harness/scripts/init-venv.ps1")
print("  2. Restart your AI IDE")
