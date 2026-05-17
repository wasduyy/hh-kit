# Skill: Stage Advance

Advance to the next project phase after validating gate checks and getting user confirmation.

## Steps

### Step 1: Validate Trace Integrity
Call `trace_validate`. If there are broken chains:
- Report each broken chain to user
- STOP. Do not advance until all chains are fixed.
- Suggest: "Fix broken chains first, then retry."

### Step 2: Run Gate Checks
Call `gate_check` for the current phase. Review results:
- If `can_advance: false`: report blocking checks and STOP
- If `can_advance: true`: proceed to Step 3

### Step 3: Present Summary to User
Show phase completion summary:
```
━━━ Phase: {current_phase} ━━━
Gate Checks: ALL PASSED
Trace: {total} nodes, 0 broken chains
Completed Tasks: {list}
───────────────────────────
Ready to advance to: {next_phase}
Confirm? (yes/no)
```

### Step 4: Wait for User Confirmation
- If user confirms: proceed to Step 5
- If user declines: abort, stay in current phase
- If user requests fixes: address issues, then retry from Step 1

### Step 5: Execute Advance
Call `state_advance(phase_name="{next_phase}", validation_log="{summary of gate results}")`.
On success:
- Report: "Advanced to phase {next_phase}"
- Call `sync_all` to update all status files

### Step 6: Update Memory
Update `activeContext.md`:
- Move current phase items to "Completed Items"
- Set "Current Focus" to new phase
- List new phase's tasks in "Next Steps"

## Gate Check Reference

| Phase | Required Gates |
|-------|---------------|
| scaffold | trace_completeness |
| implement | trace_completeness, requirements_traced, requirements_implemented |
| verify | trace_completeness, requirements_implemented, tasks_completion |
| acceptance | trace_completeness, requirements_implemented, tasks_completion |

## Error Handling
- `GATE_BLOCKED`: Show blocking checks, suggest fixes
- `ALREADY_IN_PHASE`: Inform user they're already in that phase
- `NO_DATABASE`: Fall back to manual checklist review
