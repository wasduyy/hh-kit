# T-005: Trace Integrity Issues

## Symptom
`trace_validate` returns broken chains, or `diagnose.py` reports issues.

## Cause
- Requirements without decisions (REQ -> DEC link missing)
- Decisions without implementations (DEC -> IMP link missing)
- Implementations without tests (IMP -> TST link missing)
- Bugs without fixes (BUG -> IMP fix link missing)

## Solution

### Automatic repair
```bash
python scripts/rebuild-trace-db.py
```
This rebuilds the database from .md files, fixing any database-level inconsistencies.

### Manual repair
1. Run diagnostics: `python scripts/diagnose.py`
2. Identify broken chains from the output
3. For each broken chain:
   - Create the missing node (e.g., add a decision for an orphaned requirement)
   - Or add the missing `traces_to` / `traces_from` in existing .md files
   - Or create a trace edge if the nodes exist but the link is missing
4. Rebuild: `python scripts/rebuild-trace-db.py`
