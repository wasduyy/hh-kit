# Claude Code Adapter

## Rules Generation

Claude Code reads `CLAUDE.md` from the project root. The adapter generates this file by merging:
1. `.scaffold/defaults/coding-principles.md` (if exists)
2. Starter template conventions
3. Project-specific rules from `harness.yml`

## MCP Server Configuration

Claude Code uses `.mcp.json` in the project root.

Generated configuration:
```json
{
  "mcpServers": {
    "harness": {
      "command": "python",
      "args": [".scaffold/mcp-server/server.py"],
      "cwd": "${projectRoot}"
    }
  }
}
```

## Setup

1. Copy `.scaffold/adapters/claude-code/claude-md-template.md` → `CLAUDE.md`
2. Copy `.scaffold/adapters/claude-code/mcp-template.json` → `.mcp.json` (if Layer 1+)
3. Restart Claude Code session
