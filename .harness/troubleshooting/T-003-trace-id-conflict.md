# T-003: Trace ID Conflict

## Symptom
`trace_create_node` returns DUPLICATE_ID error.

## Cause
- AI forgot a previously used ID
- Multiple sessions created the same ID concurrently

## Solution

### Find next available ID
If using MCP: call `trace_next_id(type)` to get the next available number.

### Manual check
```bash
python -c "
import sqlite3, sys
conn = sqlite3.connect('.control/trace.db')
rows = conn.execute('SELECT id FROM trace_nodes WHERE type=? ORDER BY id', (sys.argv[1],)).fetchall()
used = [r[0] for r in rows]
print('Used:', used)
conn.close()
" requirement
```

### Fix existing conflict
1. Find the two nodes with the same ID
2. Rename the later one to a new ID
3. Update all trace_edges references
4. Update the .md file's frontmatter
