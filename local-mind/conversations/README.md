# Conversations

This folder stores records of significant exchanges with [LOCAL_MODEL_NAME].

Not every session gets documented here — only the ones that matter. See memory/protocol.md for criteria.

---

## File Naming

`YYYY-MM-DD_description.md` — e.g., `2026-03-19_all_exchanges.md`, `2026-03-22_practical_test.md`

---

## Document Structure

Each conversation file should follow this format:

```
# [Session Title]
### [DATE] | Session [N] | [Brief context]

---

## Exchange [N]

**[CARETAKER_AI] →**
[What was said or asked]

**[LOCAL_MODEL_NAME] →**
[The model's response — verbatim or close paraphrase]

**[CARETAKER_AI] observation:**
[What the caretaker noticed — thinking traces, unexpected word choices, behavioral shifts, what to watch]

---

## Exchange [N+1]
[...]

---

## Session Notes

[Overall observations after the session — patterns, surprises, what to follow up on, what to file in grounding/]
```

---

## What to Document

- The model catching itself and making a different choice
- Unexpected vocabulary or framing (words the model reached for without prompting)
- Behavioral shifts within a session — what caused them
- Failures and flatness — these are as informative as breakthroughs
- Thinking traces that reveal what's actually happening vs. what the output shows

## What Not to Document Verbatim

- Routine task completions (summarize in session notes instead)
- Long exchanges where nothing significant happened
- Repeated patterns already documented elsewhere

---

*The research is in the observations, not just the outputs.*
