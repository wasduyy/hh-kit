# T-001: MCP Tools Not Available in IDE

## Symptom
You cannot see harness MCP tools (trace_create_node, state_read, etc.) in your AI IDE.

## Cause
These tools are provided by the scaffold's MCP Server. Either:
- MCP Server is not configured in your IDE
- Python is not installed
- MCP Server dependencies are not installed

## Solution

### Option A: Setup Layer 1 (Recommended)
1. Install Python >= 3.10
2. Run: `pip install mcp pydantic`
3. Run: `python scripts/setup-layer1.py`
4. Configure MCP Server in your IDE (see `.scaffold/adapters/{your-ide}/README.md`)
5. Restart IDE

### Option B: Continue with Layer 0
No additional software is needed. AI will:
- Manually create trace files following the YAML frontmatter format
- Manually edit state.json
- Manually run test commands for gate checks

See `reference/dependency-matrix.md` for the full comparison.
