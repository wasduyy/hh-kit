# Skill: Session Start

Execute this protocol at the beginning of every new session.

## Steps

### Step 1: Read Project State
Read `.control/state.json` to determine:
- Current phase and its status
- Completed phases
- Remaining tasks for current phase

### Step 2: Read Session Memory
Read `memory-bank/activeContext.md` to determine:
- What was being worked on last session
- Unfinished items
- Known issues
- Planned next steps

### Step 3: Read Configuration
Read `harness.summary.md` to understand:
- Which starter is in use
- What has been overridden from defaults
- Current dependency layer

### Step 4: Report to User
Present a summary in this format:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: {project_name}
Starter: {starter_name}
Phase:   {current_phase} ({status})

Last session focus: {active_context_summary}
Unfinished: {unfinished_items}

Config overrides: {list overrides, or "none"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 5: Continue Work
Based on the current phase, active context, and unfinished items:
- If there are unfinished tasks from last session, ask user: "Continue with {unfinished_task}?"
- If current phase is complete, suggest advancing to next phase
- If user provides new instructions, follow them

## Error Handling
- If `.control/state.json` does not exist: inform user that the project is not initialized. Suggest copying from `templates/_blank/state.json`
- If `memory-bank/activeContext.md` does not exist: treat as a fresh project. Ask user what they want to work on
- If `harness.summary.md` does not exist: note it as missing, proceed with reading `harness.yml` directly
