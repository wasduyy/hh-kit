import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '.control', 'trace.db')
DB_PATH = os.path.normpath(DB_PATH)

print(f"Migrating: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("\n=== Before migration ===")
rows = conn.execute("SELECT id, type, status FROM trace_nodes ORDER BY id").fetchall()
for r in rows:
    print(f"  {r['id']:12s} type={r['type']:20s} status={r['status']}")

print("\n=== Migrating schema ===")
conn.executescript("""
CREATE TABLE IF NOT EXISTS trace_nodes_new (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL CHECK(type IN ('requirement','analysis','decision','task','implementation','fix','optimization','test','bug','review')),
    title       TEXT NOT NULL,
    status      TEXT DEFAULT 'draft',
    phase       TEXT,
    file_path   TEXT,
    commit_hash TEXT,
    metadata    TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

INSERT OR IGNORE INTO trace_nodes_new SELECT * FROM trace_nodes;

DROP TABLE IF EXISTS trace_nodes_old;
ALTER TABLE trace_nodes RENAME TO trace_nodes_old;
ALTER TABLE trace_nodes_new RENAME TO trace_nodes;
""")
conn.commit()

print("\n=== After migration ===")
rows = conn.execute("SELECT id, type, status FROM trace_nodes ORDER BY id").fetchall()
for r in rows:
    print(f"  {r[0]:12s} type={r[1]:20s} status={r[2]}")

total = conn.execute("SELECT COUNT(*) as c FROM trace_nodes").fetchone()[0]
print(f"\nTotal nodes: {total}")

conn.execute("DROP TABLE IF EXISTS trace_nodes_old")
conn.commit()
conn.close()

print("\nMigration complete.")
