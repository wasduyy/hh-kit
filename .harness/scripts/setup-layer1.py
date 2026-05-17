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
HARNESS_YML = os.path.join(CONTROL_DIR, "harness.yml")

print("=== hh-kit Layer 1 Setup ===\n")

print("[0/4] Configuring project name...")
project_name = ""
if os.path.exists(HARNESS_YML):
    with open(HARNESS_YML, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("name:"):
                project_name = line.split(":", 1)[1].strip().strip('"').strip("'")
                break

if not project_name:
    default_name = os.path.basename(PROJECT_DIR)
    raw = input(f"  Enter project name [{default_name}]: ").strip()
    project_name = raw if raw else default_name

    if os.path.exists(HARNESS_YML):
        with open(HARNESS_YML, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace('name: ""', f'name: "{project_name}"')
        with open(HARNESS_YML, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(HARNESS_YML, "w", encoding="utf-8") as f:
            f.write(f'project:\n  name: "{project_name}"\n  starter: _blank\n')
    print(f"  [OK] Project name: {project_name}")
else:
    print(f"  [OK] Project name already set: {project_name}")

mcp_name = f"hh-kit--{project_name}"
print(f"  MCP server will register as: {mcp_name}")

print("\n[1/4] Initializing SQLite database...")
db_path = os.path.join(CONTROL_DIR, "trace.db")
os.makedirs(CONTROL_DIR, exist_ok=True)
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    sql = f.read()
conn = sqlite3.connect(db_path)
conn.executescript(sql)
conn.close()
print(f"  [OK] SQLite database initialized: {db_path}")

print("\n[2/4] Installing Git hooks...")
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

print("\n[3/4] Checking state file...")
state_path = os.path.join(CONTROL_DIR, "state.json")
if os.path.exists(state_path):
    print("  [SKIP] state.json already exists")
elif os.path.exists(STATE_SRC):
    shutil.copy2(STATE_SRC, state_path)
    print(f"  [OK] Created state.json from template")
else:
    print("  [WARN] No state.json template found")

print("\n[4/4] Checking README...")
readme = os.path.join(PROJECT_DIR, "README.md")
if os.path.exists(readme):
    print("  [SKIP] README.md already exists")
else:
    with open(readme, "w", encoding="utf-8") as f:
        f.write(f"# {project_name}\n")
    print(f"  [OK] Created README.md")

print("\nSetup complete. Next steps:")
print("  1. Run: .harness/scripts/init-venv.ps1")
print("  2. Restart your AI IDE")
print(f"  3. MCP server name: {mcp_name}")
