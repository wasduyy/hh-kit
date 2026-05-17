# Skill: Code Review

Systematic code review framework. Use as a decision guide, not a rigid checklist.

## Review Dimensions

### 1. Traceability Alignment
Before reviewing code, check context:
- Call `trace_report` for the associated task/implementation node
- Verify: does this code change trace back to a requirement?
- If no upstream trace exists: flag as "orphan change"

### 2. Correctness
- Does the code do what the requirement/task says?
- Are edge cases handled?
- Are there off-by-one errors, null/undefined risks?
- Do algorithms match the documented intent?

### 3. Security
- No hardcoded secrets, API keys, or credentials
- No SQL injection, XSS, or command injection vectors
- Input validation on all external inputs
- Proper error handling (no stack traces leaked to users)

### 4. Performance
- No N+1 queries or unnecessary loops
- Appropriate data structures used
- No memory leaks (event listeners cleaned up, connections closed)
- Large datasets handled efficiently (pagination, streaming)

### 5. Maintainability
- Functions/methods are focused (single responsibility)
- Naming is clear and consistent with codebase conventions
- No magic numbers — use named constants
- Code follows existing patterns in the project

### 6. Surgical Changes
- Only files related to the task were modified
- No unrelated refactoring mixed in
- No speculative features added
- If shared logic was changed: all references updated

## Review Output Format

```
━━━ Code Review ━━━
Trace: {upstream chain}
Files: {changed files}
────────────────────
✅ Passed:
  - {dimension}: {note}

⚠️ Warnings:
  - {dimension}: {issue} — {suggestion}

❌ Blocking:
  - {dimension}: {issue} — must fix before merge

━━━━━━━━━━━━━━━━━━━
Verdict: APPROVE | REQUEST_CHANGES | BLOCK
```

## Decision Criteria

| Verdict | Condition |
|---------|-----------|
| APPROVE | Zero blocking issues, ≤2 warnings |
| REQUEST_CHANGES | Zero blocking, >2 warnings |
| BLOCK | Any blocking issue |

## Integration with Trace System
If user wants a formal review record:
- Create REV-* node via `trace_create_node`
- Link to the implementation being reviewed
- Store review findings in metadata summary
