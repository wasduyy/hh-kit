# Skill: Bug Fix

Full defect fix workflow with traceability. Follow these steps in order.

## Steps

### Step 1: Record the Bug
Create a BUG trace node:
- Call `trace_next_id(type="bug")` to get BUG-NNN
- Call `trace_create_node(id, type="bug", title, traces_from=[related_REQ_or_IMP])`
- Status: `draft`

### Step 2: Reproduce and Diagnose
- Reproduce the bug reliably
- Identify root cause
- Determine scope: which files/modules are affected
- Check if the bug traces back to a specific implementation (IMP-*)

### Step 3: Plan the Fix
Before coding:
- State the fix strategy clearly
- Identify all files that need to change
- Consider side effects: will this fix break anything else?
- If fix is non-trivial (>1 file): present plan to user and wait for confirmation

### Step 4: Implement the Fix
- Create FIX trace node: `trace_next_id(type="fix")` → `trace_create_node(type="fix", traces_from=["BUG-NNN"])`
- Make surgical changes — only fix the bug, no refactoring
- Add the minimum necessary code to fix the issue

### Step 5: Verify the Fix
- Confirm the original bug is resolved
- Check for regressions in related functionality
- Run existing tests if available

### Step 6: Commit and Close
- Commit with format: `[FIX-NNN|TSK-xxx] Fix: {description}`
- Call `trace_update_node(node_id="FIX-NNN", status="done", commit_hash=..., files_changed=[...])`
- Call `trace_update_node(node_id="BUG-NNN", status="resolved")`
- Call `sync_all` to update status

## Trace Chain Template
```
REQ-001 → ... → IMP-003 → BUG-001 → FIX-001 (commit abc1234)
```

## Error Handling
- If bug cannot be reproduced: document conditions, set BUG status to `in_progress`, ask user for details
- If fix is complex: break into multiple FIX nodes
- If fix introduces new issues: create additional BUG nodes
