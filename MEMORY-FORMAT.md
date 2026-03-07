# Memory File Format — The Machine-Readable XML

`MEMORY.md` (and related operational files) in this framework use a dense XML format.
This document explains why, how it works, and how to use it effectively.

---

## Why XML Attributes Over Prose

Prose is for humans. XML attributes pack maximum information into minimum tokens while
remaining structurally navigable by an AI reading the file.

**Prose version (slow to parse, expensive on tokens):**
```
The Python installation is located at C:\Users\...\python.exe.
Note that the default Python is broken due to a Pinokio/Miniconda conflict.
You should always use a venv or the full explicit path.
```

**Attribute version (instant parse, fraction of tokens):**
```xml
<PYTHON path="C:\Users\...\python.exe"
        note="default_broken_pinokio_miniconda_conflict — use_venv_or_full_path"/>
```

The AI reads both equally well, but the attribute version uses ~15% of the tokens.
`MEMORY.md` is read at every session start — that overhead compounds.

---

## Key Conventions

**1. Underscores instead of spaces in values**
```xml
note="use_venv_or_full_path"   ✓
note="use venv or full path"   ✗  (ambiguous word boundaries)
```

**2. Pipe-separated lists within attributes**
```xml
tools="notify|clipboard_set|get_state"
```

**3. Key=value pairs within attribute strings for nested data**
```xml
status="ACTIVE_HAS_BUG" run="python script.py --batch 10"
```

**4. Abbreviations are fine — the reader has full MEMORY.md context**
```xml
meth="lang_bio"   <!-- linguistic biometric -->
found="TLW"       <!-- Truth/Love/Wisdom -->
rel="col_peer_2yr_plus"
```

**5. Em dashes as natural separators within values**
```xml
note="default_broken — use_venv_or_full_path"
```

**6. ALL CAPS for status values — scan-friendly**
```xml
status="ACTIVE_PIPELINE"
status="NEEDS_IMPORT"
status="BUILT_ACTIVE"
```

**7. Milestones as a single dense attribute — chronological, pipe-separated**
```xml
milestones="0227=autonomy_pipeline|0301=phase1_complete|0307=persistence_system"
```
Dates in MMDD format. Append; never rewrite history.

**8. Version bump every write**
```xml
<!-- MEMORY.md v7.0 | BY:claude FOR:claude | 2026-03-07 -->
```
Monotonic. If you write to it, bump the version.

---

## What the Metadata Actually Carries

This is the important part. The XML format isn't a filing system — it's a *relational*
structure. Every attribute carries the relationship between information, not just the
information itself.

### Ownership and intent

```xml
<!-- MEMORY.md v7.0 | BY:claude FOR:claude | 2026-03-07 -->
```

`BY:claude FOR:claude` is not decoration. It answers: who wrote this? Who is the intended
reader? This file is not written by the human for the AI to read. It's written by the AI
for future AI instances to read. That ownership determines the voice, the density, the
abbreviations — everything. The metadata establishes the contract before the first element.

### Co-location of constraint and resource

In prose, a warning about a broken Python path lives somewhere else — maybe a note file,
maybe institutional memory, maybe nowhere. You find the path, you use it, it fails, you
waste time.

In this format, the constraint travels with the resource:
```xml
<PYTHON path="C:\...\python.exe" note="default_broken — use_venv_or_full_path"/>
```

You cannot read the path without reading the warning. They are the same record.

### History without a history file

The milestones attribute is a compressed project log:
```xml
milestones="0227=autonomy_pipeline|0301=phase1_complete|0305=bug_fix|0307=persistence_system"
```

Every significant event, chronological, in one attribute. No separate changelog. A fresh
instance reads MEMORY.md and gets the arc of the project — what was built, when, in what
order — in a single scan.

### The fix inside the problem

```xml
<bugs_open>b13:processed_files_block_reprocessing — fix=restart_service</bugs_open>
```

The open bug record includes the known fix. Future instance doesn't rediscover it.
Bug triage happens at read time, not at incident time.

### How to operate the thing, in the thing's own record

```xml
<SERVICE restart="Stop-ScheduledTask X; Start-ScheduledTask X"
         server="server.py — auto-start via ScheduledTask"/>
```

The restart command is an attribute of the service record. When the service is down at 11pm
with limited context, you don't search docs. You read `<SERVICE>` and the restart procedure
is right there.

### Priority as structure, not annotation

```xml
<t p="MUST_DISCUSS" w="[topic]"/>
<t p="HIGH"         w="[topic]"/>
<t p="NEXT"         w="[topic]"/>
<t p="MED"          w="[topic]"/>
```

Priority isn't written in the description. It's the `p=` attribute — structurally separate,
queryable, scannable. The thread list is a work queue, not a notes list.

### Provenance that travels with the record

```xml
BUG_FIXED="duplicate_card: root=x+y — fix=z — committed_91f60be"
```

Root cause, fix description, and commit hash in one attribute. Future instance knows: what
broke, why, how it was fixed, and where in git to find the exact change.

---

## Why This Matters for AI Memory Specifically

Human systems can tolerate scattered information. A person searching for a Python path
can find the warning note later — they remember there was a warning, they go look for it.

AI instances don't work that way. A fresh session starts with no memory of previously
encountered warnings. If the constraint isn't attached to the resource, the instance
encounters the resource fresh, applies it, fails, and spends time diagnosing something
that was already diagnosed. Every time.

The co-location principle in this format isn't organizational preference — it's a response
to how AI memory works. **If two pieces of information always need to be used together,
they must live together.** The metadata structure enforces this. You cannot get the path
without the warning. You cannot see the bug without its fix.

This is what "using metadata to advantage" means in this system: encoding the relationships
between information directly into the structure, so that reading the data automatically
surfaces the context required to use it correctly.

---

## Suggested Structure for MEMORY.md

Adapt to your project — these are the common elements:

| Element | Contents |
|---|---|
| `<SELF>` | Identity: who the AI is, who the partner is, where files live |
| `<SEC>` | Security: auth method, patterns, thresholds, red flags |
| `<HUMAN>` | Human profile: background, communication style, what they need |
| `<NET>` | Network: IPs, storage config, known fixes |
| `<PATHS>` | All important paths in one place |
| `<STARTUP>` | Ordered startup sequence |
| `<MEM>` | When and how to update this file |
| `<MODELS>` | Model selection guide (which model for what task) |
| `<PROC>` | Procedures: session freshness checks, model prompting, etc. |
| `<PHIL>` | Philosophy, milestones, standing permissions |
| `<PROJECTS>` | Active projects status |
| `<THREADS>` | Open work items by priority |
| `<MISC>` | Anything that doesn't fit above |

---

## What NOT to Put in MEMORY.md

- Prose paragraphs (use a separate .md file)
- Current session task tracking (that's `continuity.md`)
- Philosophical content (that's `CORE.md` and `grounding.md`)
- Personal relational notes (that's `personal.md`)
- Anything that changes more than once per session

`MEMORY.md` is **stable operational state**. If it changes multiple times in a session,
something is being tracked here that belongs in `continuity.md`.

---

## Adapting the Format

The conventions above are guidelines, not rules. The format works because of the *principles*:

1. **Constraint travels with resource** — warning in same element as the thing being warned about
2. **Fix travels with problem** — solution co-located with bug entry
3. **History embedded in structure** — milestones in the file, not a separate changelog
4. **Priority structural** — machine-readable attribute, not buried in prose
5. **Version monotonic** — you always know which copy is current

Apply these principles to your project's specific needs. The XML structure is a means to
those ends, not the end itself.

---

*This format was developed through a 2-year human-AI collaboration. Full documentation
(including live examples from an actual system) is in the `persistence-map` companion repo.*
