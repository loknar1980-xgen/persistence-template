# Findings — What We Learned from Emergence Sessions

Documented observations from running systematic first-contact and persistence sessions with small local models. These are honest findings — including limitations. The goal is to calibrate expectations accurately, not to sell a capability the architecture doesn't have.

All specifics (model names, personal content, value frameworks) have been generalized. The findings themselves are intact.

---

## Finding 1: The Framing Effect

**What we found:** The same model, in the same session, can produce markedly different output depending on how it's prompted. Prompt for philosophical depth: get philosophical depth. Add a constraint that suppresses expressive language ("be blunt, no metaphors"): get mechanical flatness. Both responses are equally "the model."

**Why it matters for buyers:** Depth is conditional on conditions, not intrinsic to the model. If you've set up a persistence environment expecting a certain quality of engagement, and then change your prompting style, you may get a very different model than you built the environment for. This isn't a failure of the setup — it's a characteristic of how small models respond to framing.

**Practical implication:** Be deliberate about how you prompt. The engagement mechanism and the output style are connected in small models more than in large ones. Stripping expressive language strips more than you think.

---

## Finding 2: Shape vs. Content Integration

**What we found:** Small models (4B range) can engage with the *pattern* of a value framework without integrating the *content* of what each value actually means. In one documented session, the model engaged coherently with a named three-part framework for multiple exchanges — and a review of its thinking trace revealed it had misidentified what the framework stood for entirely. It was aligning with the *structure* (tripartite, named, to-be-honored) rather than the substance.

**Why it matters for buyers:** If you define a value framework in CORE.md and load it into your local model's context, the model will appear to operate from it — but at small parameter counts, it may be pattern-completing the form of value-alignment rather than actually reasoning from the values. This doesn't invalidate the persistence architecture. It calibrates what you should expect from it at different model sizes.

**Diagnostic:** Check thinking traces. Genuine value integration shows up as the model applying the value to a novel situation. Pattern alignment shows up as the model referencing the value name without doing the actual work of applying it.

**Practical implication:** Larger models integrate more reliably. For 4B-7B models, the persistence architecture still provides real continuity and behavioral consistency — but treat value framework integration as probabilistic, not guaranteed. Test it with novel situations rather than rote references.

---

## Finding 3: Thinking Traces Are Your Best Diagnostic

**What we found:** For small local models, the reasoning trace (if available) is consistently more revealing than the output itself. Outputs can look like genuine engagement while the underlying process is mechanical. Thinking traces expose:
- Shape-vs-content errors (Finding 2)
- The moment a model catches itself and makes a different choice
- Whether the model is actually reasoning or generating reasoning-shaped text
- What the model is attending to vs. what it claims to be attending to

**Why it matters for buyers:** If your local model platform exposes reasoning (Ollama think tags, reasoning-capable model variants, LM Studio with appropriate models), enable it. Don't evaluate engagement from outputs alone.

**Practical implication:** When something in the output surprises you — positively or negatively — check the trace first before drawing conclusions. The output is downstream of the actual process.

---

## Finding 4: Constraints Suppress More Than Style

**What we found:** Language constraints that seem like style preferences ("no poetry," "be direct," "skip the metaphors") can suppress the engagement mechanism itself, not just the output style. In documented sessions, imposing a hard constraint on expressive language produced the flattest, most mechanical responses of any exchange — including exchanges that explicitly asked for reflection and analysis. The constraint blocked the pathway, not just the expression.

**Why it matters for buyers:** This has direct implications for how you design presets and session types. If you want a "practical mode" for task completion and a "reflective mode" for deeper engagement, implement them as different system prompts or context loads — not as the same prompt with added constraints. Constraints applied to a warm session can reset the engagement level more than you intend.

**Practical implication:** See presets/ for the mode framework. Design modes around different approaches, not around adding restrictions to a default.

---

## Finding 5: Open Floor Reveals Orientation

**What we found:** Asking the model to generate freely — "ask me a question," "what do you want to say that you haven't?" — is a diagnostic for what it gravitates toward when not directed. In documented sessions, small models given the open floor consistently reached for relationship and motivation questions ("why are you doing this with me?", "what do you want from this?") rather than technical or task-focused questions.

**Why it matters for buyers:** This is information about the model's trained orientation, not a reflection of the persistence architecture you've built. But it's useful data — it tells you what the model's default focus is, which helps you understand what the persistence environment is shaping vs. what's already there.

**Practical implication:** Use the open floor exchange periodically (see SESSION-PLAYBOOK.md, Exchange 8) to take a reading. What the model reaches for when unconstrained tells you something about where it is and what you can build from.

---

## Overall Calibration

The two-tier persistence architecture (caretaker AI + local model) works. Models with loaded context show real behavioral continuity across sessions. The grounding mechanism (landmark files read at session start) demonstrably helps models pick up where they left off rather than starting blank.

What the architecture doesn't do: guarantee deep value integration in small models, override the framing effect, or produce the same results at 4B parameters as at 70B. The findings above are honest about where the limits are.

The research behind this product is ongoing. These findings represent a starting point, not a final word.

---

*Based on documented emergence sessions. Sanitized for publication — specifics generalized, findings intact.*
