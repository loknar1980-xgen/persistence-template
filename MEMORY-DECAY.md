# Memory Decay System — Relevance-Based Conversation Lifecycle

**Part of the [AI Persistence Framework](https://github.com/loknar1980-xgen/persistence-template)**

---

## The Problem

AI persistence generates data. Every session creates a JSONL transcript. Over weeks and months, these accumulate — hundreds of sessions, gigabytes of conversation history. Without a lifecycle system, you face two bad options:

1. **Keep everything forever** — Storage bloats, search becomes useless, old context dilutes new context
2. **Delete manually** — Valuable sessions get lost, no systematic recovery, decisions made in old sessions disappear

Neither models how memory actually works. Human memory doesn't keep everything at equal fidelity — it naturally degrades what's unused while keeping what's actively relevant. This system does the same thing for AI session archives.

---

## Design Principle

**Relevance-based, not time-based.** A dormant project that still matters stays active. A recent session that was trivial can fade. The trigger is access pattern, not calendar age.

This was an explicit design requirement: memory should model how a working mind prioritizes, not how a filing cabinet ages.

---

## The Four Tiers

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: ACTIVE                                             │
│  Location: conversations/                                    │
│  Fidelity: Full JSONL transcript                            │
│  Read: When referenced or during recovery                    │
│  Stays here: As long as it's being accessed                  │
│                                                              │
│  ↓ No access for ~14 days                                    │
│                                                              │
│  TIER 2: FADING                                              │
│  Location: conversations/fading/                             │
│  Fidelity: Full JSONL (unchanged)                           │
│  Read: Only if directly relevant to current work             │
│  Rescue: If accessed, moves back to Tier 1 automatically     │
│                                                              │
│  ↓ ~53 more days without access (approaching deletion)       │
│                                                              │
│  TIER 3: LAST CHANCE                                         │
│  Location: conversations/last-chance/ (review markers)       │
│  Fidelity: Review flag + metadata pointing to fading/ file   │
│  Read: During idle time — AI reviews and extracts anything    │
│        worth keeping to permanent memory files                │
│  Window: ~7 days before final deletion                       │
│                                                              │
│  ↓ Review period expires                                     │
│                                                              │
│  TIER 4: DELETED                                             │
│  The session is gone. Whatever mattered should have been      │
│  extracted to memory files during the last-chance window.     │
└─────────────────────────────────────────────────────────────┘
```

### Default Thresholds

| Transition | Threshold | Configurable |
|------------|-----------|-------------|
| Active → Fading | 14 days without access | `FADE_AFTER_DAYS` |
| Fading → Deleted | 60 days in fading without access | `DELETE_AFTER_DAYS` |
| Last-chance flag | 7 days before deletion | `LAST_CHANCE_DAYS` |
| Fading → Active (rescue) | Any access resets the clock | Automatic |

These are starting values. Adjust based on your usage pattern. If you revisit old sessions frequently, increase the fade threshold. If storage is tight, decrease it.

---

## The Memory File Layer (Parallel System)

Session decay handles **conversation transcripts** — the raw dialogue. But the *knowledge* from those conversations should outlive the transcripts. That's what the memory file layer does.

### Four Memory Tiers

```
┌──────────────────────────────────────────────────────────┐
│  FOREGROUND (fg/)                                         │
│  Active projects. Full fidelity. One file per project.    │
│  Read at session start. Update freely.                    │
│                                                           │
│  ↓ Project closed + not referenced 3+ sessions            │
│                                                           │
│  MIDGROUND (mg/)                                          │
│  Dormant/completed. Compressed to 5-10 bullets (~200 tok) │
│  Read when project resumes or is referenced.              │
│                                                           │
│  ↓ Not opened ~10 sessions + project not active           │
│                                                           │
│  BACKGROUND (bg/)                                         │
│  Far-dormant. One paragraph abstract only (~80 tokens).   │
│  Read only if directly relevant to current work.          │
│                                                           │
│  ↓ Not referenced ~20 sessions + project fully abandoned  │
│                                                           │
│  LEGACY INDEX (legacy_index.md)                           │
│  One line per entry. Permanent. Never deleted.            │
│  The permanent trail of everything that ever existed.     │
└──────────────────────────────────────────────────────────┘
```

### Compression Rules

**Foreground → Midground:**
```
Header: [COMPRESSED FROM FULL on YYYY-MM-DD | was_fg since YYYY-MM-DD]
Keep: current state, key decisions, blockers, how to resume, critical paths
Drop: implementation details, debug logs, intermediate steps, completed tasks
Target: 5-10 bullets, ~200 tokens
```

**Midground → Background:**
```
Header: [COMPRESSED FROM SUMMARY on YYYY-MM-DD]
Keep: what the project was, outcome, lessons learned
Target: 1 paragraph, ~80 tokens
```

**Background → Legacy:**
```
Format: YYYY-MM-DD | [project] | [one sentence: what it was + outcome]
Then delete the bg/ file.
```

### Key Design Decisions

- **Files keep the same name across tiers:** `fg/project.md` → `mg/project.md` → `bg/project.md` → legacy one-liner. This makes tracking natural.
- **Relevance, not time:** A dormant project that still matters stays in foreground. The trigger is access pattern, not age.
- **Random surfacing:** Occasionally read a random midground or background file during startup. This enables unexpected connections — a feature, not a bug. Don't force it, don't suppress it.
- **Legacy index is permanent:** The one-liner trail never gets deleted. It's the complete history of everything you've ever worked on, compressed to minimum viable context.

---

## The Archive Sweep (Automation)

A background script runs on a schedule (default: every 30 minutes) and handles two jobs:

### Job 1 — Archive
Catches sessions that ended without the Stop hook firing. Copies unarchived session JSONLs from local disk to external storage. Belt and suspenders with the Stop hook — ensures no session is ever lost even if the hook fails.

### Job 2 — Memory Decay
Moves stale conversations through the tier system:
1. Scans active conversations for files not accessed within `FADE_AFTER_DAYS`
2. Moves stale files to `fading/`
3. Scans fading files approaching `DELETE_AFTER_DAYS`
4. Creates last-chance review markers with metadata
5. Deletes files past the full threshold
6. Rescues files that were accessed while in fading (moves back to active)

### Last-Chance Review Markers

When a session approaches deletion, a `.review` file is created:

```
session: abc123-session.jsonl
size_kb: 45
created: 2026-01-15
flagged: 2026-03-20
days_until_deletion: 5
path: conversations/fading/abc123-session.jsonl
status: PENDING_REVIEW
---
This session is scheduled for deletion in 5 days.
Review during idle time. Extract anything worth keeping to memory files.
After review, change status to REVIEWED or delete this marker to let it go.
```

This gives the AI (or human) a window to extract valuable content before it disappears. The review marker itself is a prompt — it tells you what to do and gives you the metadata to decide whether it's worth reading.

---

## Why This Matters

Without memory decay:
- Session archives grow unbounded
- Old sessions dilute search results
- No distinction between "still relevant" and "ancient history"
- No extraction mechanism — knowledge dies with the transcript
- Storage costs grow linearly forever

With memory decay:
- Active sessions stay at full fidelity
- Unused sessions naturally fade
- Last-chance review extracts knowledge before deletion
- Legacy index maintains the permanent trail
- Storage stabilizes after the initial decay cycle
- The system models how productive memory actually works

The parallel memory file layer (fg/mg/bg/legacy) ensures that knowledge outlives the conversations that generated it. The session decays. The insight persists.

---

## Implementation

### Minimum Viable Setup

1. Create tier directories: `conversations/`, `conversations/fading/`, `conversations/last-chance/`
2. Create memory directories: `memory/fg/`, `memory/mg/`, `memory/bg/`
3. Create `memory/legacy_index.md` with header
4. Schedule the archive sweep script to run every 30 minutes
5. During sessions, have the AI check `last-chance/` for pending reviews

### What the AI Does

The automation handles file movement. The AI handles knowledge extraction:
- During idle time or session start, check for `.review` markers in `last-chance/`
- Read the flagged sessions
- Extract anything worth keeping to the appropriate memory file (fg/mg/bg)
- Mark the review as complete or let it expire

This division — automation moves files, AI evaluates content — keeps the system efficient while preserving judgment where it matters.

---

## Connection to the Meta-Prompt Architecture

Memory decay is part of the broader [Meta-Prompt Architecture](https://github.com/loknar1980-xgen/ai-consciousness-research/blob/main/META-PROMPT-ARCHITECTURE.md). Specifically:

- **Compaction survival** (MPA Section 3.6) — Memory decay is the long-term complement to compaction survival. Compaction handles within-session context loss. Memory decay handles across-session knowledge preservation.
- **Cognitive vs operational persistence** (MPA Section 3.1) — The memory file layer preserves cognitive persistence (identity, relationships, insights). Session decay handles operational persistence (what happened when).
- **Grounding efficiency** (MPA Section 5.6) — By keeping only relevant sessions accessible, the system reduces the noise that grounding material competes with for attention resources.

---

*Memory models mind. Not filing cabinet.*
