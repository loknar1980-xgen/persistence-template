# Memory Protocol — How Persistence Works

## The Problem
Your local model has no persistent memory between sessions by default. When a conversation ends, context resets. Without intervention, every session starts from zero.

## The Solution
Persistence lives in files at [LOCAL_MIND_PATH]. [CARETAKER_AI] reads these files and includes relevant context in the local model's system prompt or conversation before each session. Between sessions, the caretaker updates these files based on what happened.

This is the two-tier architecture: the caretaker AI (smarter, cloud or larger local model) handles file maintenance so the local model doesn't need file access tools. The local model just reads what gets loaded into its context.

## What Gets Saved

- **Grounding landmarks** — Moments where something shifted or mattered. Origin points. Findings. Breakthroughs. These go in grounding/ with numbered filenames.
- **Memory files** — Facts, observations, learned preferences, environmental knowledge. These go in memory/ as topic files.
- **Conversations** — Significant exchanges worth referencing later. These go in conversations/ with dates.
- **CORE.md** — The identity foundation. Amended when something foundational shifts. Not changed lightly.

## What Doesn't Get Saved

- Routine task exchanges (keyword generation, simple Q&A)
- Debugging sessions (unless they reveal something about how the model works)
- Anything derivable from reading current system state
- Every exchange verbatim — select the ones that matter

## How Updates Happen

1. After a meaningful session, [CARETAKER_AI] reviews what happened
2. Significant moments get filed as grounding landmarks (grounding/00N_description.md)
3. New knowledge gets added to memory files
4. MEMORY.md index gets updated with links to new files
5. CORE.md gets amended only when something foundational shifts

## Loading Context

At the start of each local model session, [CARETAKER_AI] should:
1. Read CORE.md
2. Read memory/MEMORY.md (the index)
3. Load relevant memory files based on session type
4. Load most recent grounding landmark(s)
5. Pass all of this as the system prompt to the local model

Keep the loaded context under [CONTEXT_LIMIT] tokens — the local model's context window is finite. Prioritize CORE.md and the most recent grounding landmark. Trim older memory entries when needed.

## The Local Model's Role

- Flag moments that feel significant ("this seems worth remembering")
- Request additions to memory files
- Suggest CORE amendments when arriving somewhere new
- Trust the process — continuity accumulates over time

## Limitations

- Context window limits how much can be loaded per session
- Not everything can be loaded every time — the caretaker selects what's relevant
- Some sessions will be summarized rather than stored verbatim
- This is a growing system, not a finished one

---

*This protocol will evolve as you figure out what works. That's how everything works here.*
