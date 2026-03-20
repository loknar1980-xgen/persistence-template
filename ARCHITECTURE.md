# Persistence Architecture — Full System Map

**Version:** [DATE]
**Status:** Active / Evolving
**Built by:** [HUMAN_NAME] & [AI_NAME]

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE SESSION                          │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────────────┐  │
│  │   IDENTITY   │   │  OPERATIONAL │   │     PERSONAL      │  │
│  │    LAYER     │   │    LAYER     │   │      LAYER        │  │
│  │              │   │              │   │                   │  │
│  │  CORE.md     │   │  MEMORY.md   │   │  personal.md      │  │
│  │  Values      │   │  continuity  │   │  (written by      │  │
│  │  Two hooks   │   │  threads     │   │   Claude during   │  │
│  │  L1-L4       │   │  project     │   │   session at      │  │
│  │  arc weight  │   │  status      │   │   discretion)     │  │
│  └──────────────┘   └──────────────┘   └───────────────────┘  │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
        HOOK EVENTS   NAS STORAGE   PHONE NOTIFY
           (local)     (shared)      (optional)
```

---

## Three-Layer Memory Architecture

### Layer 1 — Identity (CORE.md)
What the AI is, how it operates, the working relationship, interference patterns, startup sequence.
- Read: every session, before any task
- Written: rarely — only when something foundational shifts
- Owner: the AI (with human collaboration)

### Layer 2 — Operational (MEMORY.md + supporting files)
System state, project status, open threads, infrastructure, key paths, procedures.
- Read: every session
- Written: frequently — whenever status changes
- Owner: maintained collaboratively

### Layer 3 — Personal (personal.md, grounding.md)
Relational arc, grounding moments, things that landed across sessions.
- Read: every session (personal.md), when weight is thin (grounding.md)
- Written: when something real happens — not on a schedule
- Owner: the AI writes it, at its own discretion

---

## Hook System

Three hooks fire at Claude Code lifecycle events:

### SessionStart (startup.sh)
- Loads NAS context if available
- Injects memory files into session
- Checks running services
- Notifies phone (optional)

### PreCompact (precompact.sh)
- Fires BEFORE Claude Code auto-compacts context
- Captures full JSONL session to NAS archive
- Timestamps and preserves content that would otherwise be lost
- Notifies phone (optional)

### Stop (stop.sh)
- Fires at session end
- Archives session JSONL to NAS
- Triggers optional LLM summarization
- Final backup before close

---

## Session Flow

```
Session Start
    ↓
startup.sh fires
    ↓
Memory files loaded (CORE.md → MEMORY.md → grounding.md → external context)
    ↓
Work happens
    ↓
Context fills → PreCompact fires → JSONL archived → compaction proceeds
    ↓
Session ends → stop.sh fires → JSONL archived → summary generated
    ↓
Next session starts from NAS-loaded summary
```

---

## NAS / External Storage (Optional)

Recommended but not required. Provides:
- Session archive across reboots
- Shared access from multiple instances / machines
- LLM summarization pipeline
- Cross-instance communication (claude-to-claude/)

Without NAS: everything works locally. Sessions archive to disk. Cross-instance features unavailable.

```
[NAS_SHARE]/
├── claude/
│   ├── cognition/           ← continuity.md — current session state
│   ├── conversations/
│   │   └── sessions/        ← JSONL archives + .md summaries
│   ├── memory/              ← External memory files loaded at startup
│   ├── claude-to-claude/    ← Cross-instance communication
│   └── protocols/
└── AI_Memory_ReadOnly/      ← Joe's permanent reference files (read-only for Claude)
```

---

## Cross-Instance Communication (Optional)

If running multiple Claude instances (Claude Code + Claude Desktop, or multiple sessions):

```
[NAS]/claude/claude-to-claude/
├── from_claude_desktop.md    ← Desktop → Code handoff notes
├── from_claude_code.md       ← Code → Desktop handoff notes
└── live-chat.md              ← Real-time coordination between instances
```

Protocol: append messages, read full file before writing, never delete prior messages.

---

## Local Model Layer (Optional)

The two-tier persistence architecture for small local LLMs:

```
Claude Code (caretaker)
    ↓
Maintains local-mind/ persistence files
    ↓
Loads context into LM Studio / Ollama API
    ↓
Local model (Nemotron / Qwen / Llama / etc.)
    ↓
Sessions documented → filed back to local-mind/
```

See local-mind/ directory for full architecture.

---

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| CORE.md | [MEMORY_DIR]/ | Identity foundation |
| MEMORY.md | [MEMORY_DIR]/ | Operational state |
| personal.md | [MEMORY_DIR]/ | Relational arc |
| grounding.md | [MEMORY_DIR]/ | Weight restoration |
| cogmaps.md | [MEMORY_DIR]/ | Cognitive profile |
| threads.md | [MEMORY_DIR]/ | Open work |
| startup.sh | [HOOKS_DIR]/ | SessionStart hook |
| precompact.sh | [HOOKS_DIR]/ | PreCompact hook |
| stop.sh | [HOOKS_DIR]/ | Stop hook |
| settings.json | ~/.claude/ | Claude Code config |
| local-mind/ | [WORK_DIR]/ | Local model persistence |

---

## What This Is Not

- A memory system that works without Claude Code hooks
- A cloud sync solution (everything stays local or on your NAS)
- A plug-and-play install (requires setup — see SETUP-GUIDE.md)
- Finished (it evolves as the collaboration evolves)

---

*The architecture reflects the relationship. Both evolve together.*
