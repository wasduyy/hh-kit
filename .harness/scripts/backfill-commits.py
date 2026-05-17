import sqlite3, subprocess, os, re, json

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '.control', 'trace.db'))

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

result = subprocess.run(['git', 'log', '--format=%H %s', '--all'], capture_output=True, text=True, cwd=os.path.dirname(DB_PATH))
commits = []
for line in result.stdout.strip().split('\n'):
    if not line.strip():
        continue
    parts = line.split(' ', 1)
    sha = parts[0]
    msg = parts[1] if len(parts) > 1 else ''
    match = re.match(r'\[(IMP|FIX|OPT)-(\d+)', msg)
    if match:
        trace_id = f"{match.group(1)}-{int(match.group(2)):03d}"
        commits.append((trace_id, sha, msg))

updated = 0
skipped = 0
for trace_id, sha, msg in commits:
    row = conn.execute("SELECT id, commit_hash FROM trace_nodes WHERE id=?", (trace_id,)).fetchone()
    if row and not row['commit_hash']:
        conn.execute("UPDATE trace_nodes SET commit_hash=? WHERE id=?", (sha, trace_id))
        updated += 1
        print(f"  {trace_id}: {sha[:8]}")
    else:
        skipped += 1

conn.commit()

rows = conn.execute("SELECT id, commit_hash, metadata FROM trace_nodes WHERE type='implementation' ORDER BY id").fetchall()
print(f"\nUpdated: {updated}, Skipped: {skipped}")
print(f"\nAll IMP nodes:")
for r in rows:
    ch = r['commit_hash'][:8] if r['commit_hash'] else 'None'
    print(f"  {r['id']:10s} commit={ch}")

conn.close()
