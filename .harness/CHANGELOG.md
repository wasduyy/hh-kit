# Changelog

All notable changes to the archAIHelper scaffold will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-05-14

### Added
- Initial scaffold structure with 5-layer architecture
- `.scaffold/defaults/` - framework default configurations
- `.scaffold/schemas/` - JSON Schema definitions (harness, state, trace-node)
- `.scaffold/sql/` - SQLite schema and query templates
- `.scaffold/hooks/` - Git hook templates (pre-commit, commit-msg)
- `.scaffold/adapters/` - Platform adapters (Trae, Claude Code, Cursor, Copilot)
- `templates/_blank/` - Blank starter template
- `scripts/` - Setup, rebuild, and diagnostic tools
- `skills/` - Skill directory structure (10 skills)
- `personas/` - Persona directory structure
- `troubleshooting/` - FAQ directory
- `docs/` - Documentation directory structure
- 8 core design principles documented in README.md
- 4-layer dependency model (L0 zero-dep to L3 enterprise)
- Traceability system with SQLite backend and recursive CTE queries
- Configuration transparency via harness.summary.md
- Three-tier configuration priority (project > starter > framework)
