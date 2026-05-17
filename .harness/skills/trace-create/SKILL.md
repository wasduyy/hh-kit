# Skill: Trace Create

Create a traceability node that links to the upstream causal chain.

## Steps

### Step 1: Determine Node Details
Before creating, determine:
- **type**: requirement | analysis | decision | task | implementation | test | bug | review
- **title**: concise description
- **traces_from**: list of upstream node IDs that this node traces from

### Step 2: Generate Node ID
ID format: `{TYPE_PREFIX}-{NNN}` where NNN is zero-padded to 3 digits.

Type prefixes: REQ(requirement) ANA(analysis) DEC(decision) TSK(task) IMP(implementation) TST(test) BUG(bug) REV(review)

To find the next available number:
- If MCP available: call `trace_next_id(type)` tool
- If MCP not available: scan `docs/{type}s/` directory for existing files and increment

### Step 3: Create Node

#### If MCP tools available:
Call `trace_create_node(id, type, title, traces_from)` and follow the result:
- `success: true` -> node created, proceed to Step 4
- `DUPLICATE_ID` -> use next available number and retry
- `BROKEN_REFERENCE` -> create upstream nodes first
- `NO_DATABASE` -> fall through to manual mode below

#### If MCP tools NOT available (Layer 0):
Create the file manually:

File path: `docs/{type}s/{ID}-{slug}.md`

File content must include YAML frontmatter:
```markdown
---
id: {ID}
type: {type}
title: {title}
traces_from:
{yaml_list_of_traces_from}
traces_to: []
status: draft
created: {YYYY-MM-DD}
---

# {ID}: {title}

## Context
(Why this node exists)

## Details
(Specific content depends on type)
```

### Step 4: Update Upstream Links
For each node listed in `traces_from`:
- Open the upstream node's .md file
- Add this node's ID to its `traces_to` list in the YAML frontmatter
- If MCP available: call `trace_create_edge(from_id, to_id, relation)`

### Step 5: Verify
Confirm the node was created:
- File exists at the expected path
- YAML frontmatter is valid
- Upstream links are bidirectional

### Step 6: Report
Tell the user:
"Created {ID}: {title}
Traces from: {traces_from}
File: {file_path}"

## Common Relations
| From Type | To Type | Relation |
|-----------|---------|----------|
| REQ | ANA | triggered_analysis |
| REQ | DEC | informed_decision |
| ANA | DEC | concluded |
| DEC | TSK | decomposed_to_task |
| TSK | IMP | implemented_by |
| IMP | TST | verified_by |
| TST | BUG | discovered |
| BUG | IMP | fixed_by |
| IMP | TST | regression_verified_by |

## Error Handling
- MCP tool returns error with `fix` field -> present the fix suggestion to user
- File already exists -> use a different ID number
- Upstream node not found -> ask user if upstream should be created first
