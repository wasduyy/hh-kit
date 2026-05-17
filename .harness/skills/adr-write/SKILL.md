# Skill: ADR Write

Write Architecture Decision Records (ADRs) following a structured format. This is a framework — adapt the sections to the decision's complexity.

## ADR Structure

Every DEC node should contain these sections:

### Context
- What is the technical or business situation?
- What forces are at play? (constraints, requirements, timelines)
- What upstream requirements or analyses led to this decision point?
- Reference: `traces_from` nodes

### Options Considered
For each option (typically 2-4):
- **Description**: What is this approach?
- **Pros**: Benefits of this choice
- **Cons**: Drawbacks, risks, or costs
- **Effort**: Estimated implementation complexity

### Decision
- Which option was chosen?
- Use clear, declarative language: "We will use X for Y because Z"
- Status: `accepted` (or `deprecated` / `superseded` if revisiting)

### Rationale
- Why this option over others?
- What criteria tipped the balance?
- Link to evidence (benchmarks, prototypes, team expertise)

### Consequences
- What becomes easier?
- What becomes harder?
- What new dependencies are introduced?
- What is the reversibility cost?

## Writing Guidelines

### Good ADR
```
# DEC-005: Use WebSocket for real-time updates

## Context
REQ-003 requires real-time data push to clients. Current REST polling has 2s latency.

## Options
1. Server-Sent Events — simple, HTTP-based, unidirectional
2. WebSocket — bidirectional, persistent connection
3. REST polling at 200ms — no new dependencies

## Decision
Use WebSocket (option 2).

## Rationale
Bidirectional communication needed for future collaborative features (REQ-008).
SSE only supports server→client. Polling adds unnecessary load at scale.

## Consequences
- (+) Real-time updates with <50ms latency
- (+) Foundation for REQ-008 collaborative editing
- (-) New dependency: ws library (~50KB)
- (-) Need connection management and reconnection logic
```

### Bad ADR
```
# DEC-005: Use WebSocket
We decided to use WebSocket because it's better.
```

## Integration with Trace System
- Create via `trace_create_node(type="decision", traces_from=[upstream ANA/REQ])`
- Status lifecycle: `draft` → `accepted` → (possibly `deprecated` → `superseded`)
- When superseded: create new DEC, update old DEC status via `trace_update_node`
