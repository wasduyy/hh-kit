# T-006: Upgrading from Layer 0 to Layer 1

## What you get with Layer 1
- Automatic trace node creation (MCP tool: trace_create_node)
- Graph queries on trace data (MCP tool: trace_query)
- Trace integrity validation (MCP tool: trace_validate)
- Gate check automation (MCP tool: gate_check)
- State management automation (MCP tools: state_read, state_advance)
- Configuration merging (MCP tools: config_read, config_summary)
- Git hook enforcement of commit message format

## Prerequisites
- Python >= 3.10
- pip install mcp pydantic

## Steps

### 1. Run setup
```bash
python scripts/setup-layer1.py
```
This will:
- Initialize SQLite database at .control/trace.db
- Install Git hooks (pre-commit, commit-msg)
- Create default state.json if not present

### 2. If you have existing trace .md files
```bash
python scripts/rebuild-trace-db.py
```
This scans all docs/ directories and populates the database.

### 3. Configure MCP Server in your IDE
See `.scaffold/adapters/{your-ide}/README.md` for platform-specific instructions.

### 4. Restart your IDE
The MCP Server should now be available.

### 5. Verify
```bash
python scripts/diagnose.py
```
All checks should pass.
