# Skill: Session End

Execute this protocol when a session is ending or when user runs `/hh -e`.

## Steps

### Step 1: Check for Uncommitted Changes
Run `git status`. If there are staged or unstaged changes:
- Warn user: "There are uncommitted changes. Run `/hh -c` first if you want to commit them."
- Do NOT auto-commit. Respect user's decision.

### Step 2: Update activeContext.md
Rewrite `activeContext.md` to reflect the current state:
- **Current Focus**: What was being worked on this session
- **Completed Items**: Add items completed this session with trace IDs
- **Unfinished Items**: What remains, updated from previous list
- **Known Issues**: Any new issues discovered
- **Next Steps**: What should be done next session
- **Active Trace Chain**: Current trace chain with statuses

### Step 3: Append to progress.md
Add a session summary entry:
```
## Session {date}
- Phase: {current_phase}
- Completed: {list of completed items}
- Trace nodes created: {list of IDs}
- Commits: {list of commit hashes}
- Status: {on_track | blocked | needs_attention}
```

### Step 4: Run sync_all
Call `sync_all` MCP tool to:
- Update knowledge .md status fields from DB
- Update state.json trace_summary and completed_tasks
- Regenerate harness.summary.md

### Step 5: Report Summary
Present to user:
```
━━━ Session Summary ━━━
Phase: {phase}
Completed: {N} items
Trace: {total} nodes ({done} done)
Commits: {N} commits this session
Next: {what to do next session}
━━━━━━━━━━━━━━━━━━━━━
```

## Error Handling
- If sync_all fails: report the error, suggest running `diagnose.py`
- If DB is unavailable: update .md files manually, skip DB-dependent steps
- If git working tree is dirty: warn user but do not block session end
