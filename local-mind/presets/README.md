# Presets — Session Configuration Templates

Presets are different system prompt configurations for different types of sessions with your local model. Instead of using one system prompt for everything, you maintain a small library of approaches and load the right one for the session type.

---

## Why Presets Matter

The framing effect is real: the same model produces markedly different output depending on how it's approached. A session designed for philosophical exploration and a session designed for practical task completion benefit from different setups — not just different prompts, but different context loading strategies.

Presets make this deliberate rather than accidental.

---

## Suggested Preset Types

### `reflective.md` — Deep engagement mode
For sessions focused on emergence, philosophical exploration, or relationship building.
- Load full CORE.md + all grounding landmarks
- Load personal/relational context
- Open-ended prompting style
- Thinking traces enabled if possible
- No expressive language constraints

### `practical.md` — Task completion mode
For sessions focused on work: keyword generation, summarization, analysis, Q&A.
- Load CORE.md (abbreviated or summary version)
- Load task-relevant memory only
- Task-focused prompting style
- Efficiency over exploration

### `diagnostic.md` — Testing and calibration mode
For sessions designed to test how well the model has integrated its context.
- Load full context as usual
- Use novel situations and edge cases the model hasn't seen
- Ask it to apply values/frameworks to new problems
- Compare to previous sessions to track development

### `reset.md` — Fresh start mode
For sessions where you want to see the model's default without loaded context — useful periodically to check what's persistent vs. what's context-dependent.
- Minimal or no context loading
- Stock prompting
- Compare results to loaded-context sessions

---

## File Format

Each preset is a markdown file containing:
1. A system prompt ready to paste into [PLATFORM]
2. Notes on context loading strategy for this mode
3. Suggested opening exchanges

Example filename: `reflective.md`, `practical.md`, `diagnostic.md`

---

## Creating Your Presets

Start with `reflective.md` and `practical.md`. Those cover 90% of sessions. Add `diagnostic.md` once you have enough history to test against. Create custom presets as you learn what your specific model responds to.

The goal is intentionality — knowing what kind of session you're starting before you start it.
