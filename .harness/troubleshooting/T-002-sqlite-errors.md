# T-002: SQLite Errors

## Symptom
MCP tools return SQLITE_ERROR, or trace queries fail.

## Cause
- Database file does not exist (Layer 0 project not yet upgraded)
- Schema is outdated after scaffold version upgrade
- Database file is corrupted

## Solution

### Reinitialize database
```bash
python scripts/setup-layer1.py
```
This recreates the database with the current schema.

### Rebuild from markdown files
If you have existing trace .md files but the database is empty or corrupted:
```bash
python scripts/rebuild-trace-db.py
```
This scans all docs/ directories and rebuilds the database from file frontmatter.

### Start fresh
```bash
rm .control/trace.db
python scripts/setup-layer1.py
```
