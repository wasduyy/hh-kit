# Skill: Research and Plan

Research a problem space and produce a structured implementation plan.

## Phase 1: Research (Framework)

### Understand the Requirement
- Read the REQ node carefully
- Identify constraints, success criteria, and acceptance conditions
- Check if similar work exists: `trace_query` for related upstream/downstream nodes

### Investigate the Codebase
- Search for existing implementations that may be affected
- Identify integration points and dependencies
- Check for existing patterns to follow (or anti-patterns to avoid)

### Evaluate Options
For each viable approach, evaluate:
- **Feasibility**: Can it be done with current tech stack?
- **Complexity**: How many files/components affected?
- **Risk**: What could go wrong? What are the failure modes?
- **Alignment**: Does it match existing architecture decisions (DEC nodes)?

## Phase 2: Plan (Procedural)

### Step 1: Create Analysis Node
- `trace_next_id(type="analysis")` → ANA-NNN
- `trace_create_node(type="analysis", traces_from=["REQ-NNN"])`
- Document: key findings, feasibility assessment, risks

### Step 2: Create Decision Node (if a choice is needed)
- `trace_next_id(type="decision")` → DEC-NNN
- `trace_create_node(type="decision", traces_from=["ANA-NNN", "REQ-NNN"])`
- Document: context, options considered, decision, rationale, consequences

### Step 3: Create Task Node(s)
- `trace_next_id(type="task")` → TSK-NNN
- `trace_create_node(type="task", traces_from=["DEC-NNN"])`
- Document: goal, implementation steps, success criteria

### Step 4: Present Plan to User
```
━━━ Implementation Plan ━━━
REQ: {requirement title}
ANA: {analysis summary}
DEC: {decision summary}
TSK: {task title}
───────────────────────────
Files to modify: {list}
Estimated complexity: {low/medium/high}
Risks: {list}
Success criteria: {list}
Confirm? (yes/no)
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 5: Wait for Confirmation
- User confirms → proceed to implementation
- User requests changes → update plan and re-present
- User declines → archive plan with status `rejected`

## Decision Framework
When multiple approaches exist:
1. List all viable options (max 3)
2. For each: one paragraph pros, one paragraph cons
3. State your recommendation with rationale
4. Let user decide — do not pick silently
