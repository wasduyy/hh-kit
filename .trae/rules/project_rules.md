# hh-kit

## `/hh` Commands — EXECUTE IMMEDIATELY when user input starts with `/hh`

| Input | Action |
|-------|--------|
| `/hh` or `/hh -s` | Read `.control/state.json` + `.control/memory-bank/activeContext.md` + `.control/harness.summary.md`, then report status |
| `/hh -n` | Read `.control/memory-bank/activeContext.md`, find next unfinished item |
| `/hh -c [msg]` | **4-step commit flow**: (1) `git add -A` (2) `trace_next_id` → get ID (3) `git commit -m [ID\|TSK-xxx] msg` (4) `trace_create_node` with `commit_hash`, `files_changed`, `summary` |
| `/hh -t <ID>` | Call `trace_report` for node `<ID>` — shows node info + upstream/downstream chain + files changed + commit |
| `/hh -v` | Run `trace_validate` |
| `/hh -d` | Run `python .harness/scripts/diagnose.py` for checks, then call `sync_all` to fix status inconsistencies |
| `/hh -e` | Call `sync_all` MCP tool — syncs knowledge .md status + state.json + harness.summary.md from DB. Optionally pass `active_context` and `progress_entry` |

## Mandatory Behaviors

1. **New session**: automatically execute `/hh` before doing anything else
2. **After each unit of work**: check `git status`, if changes exist → execute `/hh -c`
3. **After completing a task**: execute `/hh -e` to sync status + refresh summary
4. **Before creating trace nodes**: use MCP tool `trace_create_node`, or create .md file in `knowledge/{type}s/`
5. **Commit format**: `[{TRACE_ID}|{TASK_ID}] {title}` with `Traces: {ids}` line
6. **DB is source of truth**: always use `trace_next_id` to get new IDs, never guess or reuse
7. **Confirm before building**: before implementing any non-trivial change (> 1 file, or new feature), present the plan and wait for user confirmation. Do not assume approval.

## Coding Constraints

- **Think Before Coding**: if uncertain, ask. If multiple approaches exist, present them. Do not pick silently.
- **Simplicity First**: no features beyond what was asked. No speculative code. If 50 lines suffice, do not write 200.
- **Surgical Changes**: touch only what you must. Every changed line must trace to the user's request. When modifying shared logic, update ALL references (rules, templates, scripts, tests) in the same commit.
- **Goal-Driven**: state success criteria before starting. Verify after completing.
- **No Bypass**: if an MCP tool is unavailable, STOP and tell the user to restart the IDE. Do NOT write workaround scripts, do NOT operate the database directly, do NOT duplicate existing logic.

## Key Paths

| Zone | Path | Content |
|------|------|---------|
| Control | `.control/` | state.json, harness.yml, trace.db, memory-bank/ |
| Knowledge | `knowledge/` | requirements/, decisions/, tasks/, implementations/, fixes/, optimizations/, tests/, bugs/ |
| Project | `project/` | src/, tests/, acceptance/ |
| Framework | `.harness/` | .scaffold/, skills/, scripts/ |

## Trace IDs

`REQ` `ANA` `DEC` `TSK` `IMP` `FIX` `OPT` `TST` `BUG` `REV` + `-NNN` (e.g. REQ-001, IMP-012, FIX-003)

- **IMP** — implementation (from task/decision)
- **FIX** — bug fix (from BUG)
- **OPT** — optimization (from REQ/IMP, or self-initiated improvement)
