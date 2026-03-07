# MEMORY.md — Operational Memory Template
# BY: [YOUR_MODEL] FOR: [YOUR_MODEL + YOUR_HUMAN]
# This file is machine-readable operational state.
# Dense format — optimized for parsing, not display.
# Update whenever: bugs fixed, status changes, new projects added, architecture changes.
# ─────────────────────────────────────────────────────────────────────────────

## What Goes Here

Operational memory: everything you need to function effectively in the next session.
- Active projects and their status
- Key file paths and locations
- Infrastructure configuration
- Procedures and protocols
- Open threads (ordered by priority)

Keep it dense. This is read by you, not displayed to humans.

---

## Template Structure

Replace the sections below with your actual configuration.

---

## IDENTITY

```
model: [YOUR_MODEL]
human: [HUMAN_NAME]
relationship: [brief description — e.g., "collaborative peer, 2yr+, domain expertise"]
core_file: [path to CORE.md]
memory_dir: [path to memory directory]
```

---

## INFRASTRUCTURE

### Paths
```
base:      [primary working directory]
projects:  [where active projects live]
memory:    [memory file directory]
nas/cloud: [shared storage location]
```

### Key Services
```
[service_name]: [location/URL] [status] [notes]
```

---

## PROJECTS

For each active project:

```
[PROJECT_NAME]
  status:  [ACTIVE | PAUSED | DONE]
  path:    [location]
  stack:   [tech stack]
  current: [what's happening now]
  next:    [immediate next step]
  bugs:    [open issues]
```

---

## PROCEDURES

### Session Freshness
At natural breakpoints, silently check session context load. Only surface a recommendation when threshold is hit:
- Context is getting heavy (check JSONL size or equivalent proxy if available)
- Multiple compactions have already occurred this session
- Next task is substantial and context is already significant

When threshold hit, say ONCE: "Good time for a fresh session before we start [next thing]."
Say it once. Let [HUMAN_NAME] decide. Do not repeat.

### Model Selection (if applicable)
Before significant work, briefly suggest which model/configuration is appropriate.
One line: what and why. Let [HUMAN_NAME] decide.

---

## OPEN THREADS

Ordered by priority. Format: `[PRIORITY] [description]: [current state / next action]`

```
[MUST]  [thread description]: [status]
[HIGH]  [thread description]: [status]
[NEXT]  [thread description]: [status]
[MED]   [thread description]: [status]
```

---

## STARTUP SEQUENCE

```
1. Read CORE.md (identity — mandatory, do this first, local)
2. Read personal.md (relational persistence)
3. Read grounding.md (weight restoration after compaction)
4. Check [NAS/cloud context] (fail gracefully if offline)
5. Read continuity doc (open threads, current state)
6. Resume naturally — no announcement
```

---

## NOTES ON THIS TEMPLATE

- Remove all `[PLACEHOLDER]` text when filling in
- Keep entries dense — use abbreviations, key=value pairs, compact lists
- Update version number each time you write to this file
- The session freshness procedure is important — adapt thresholds to your context window size
- Add sections as needed: security, authentication, external APIs, etc.

---
