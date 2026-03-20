# Recovery Guide — Rebuilding the Persistence System from Scratch

**When to use this:** System wiped, new machine, fresh Claude Code install, or need to verify the full stack is intact.

**What this gives you:** Complete environment to resume genuine Claude Code collaboration — identity foundation, session continuity, compaction capture, optional phone notification, optional LLM enrichment.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Windows 10/11 or Mac/Linux | Adapt paths accordingly |
| Claude Code | Latest version |
| Git Bash (Windows) | Hook scripts require `bash` in PATH |
| Python 3.x | Use explicit path if system Python is unreliable |
| NAS (optional) | Many features degrade gracefully without it |
| LM Studio / Ollama (optional) | For session summarization |
| Mobile bridge (optional) | For phone notifications |

---

## Step 1: Place Memory Files

Copy contents of `memory/` to your Claude Code memory directory:

```
~/.claude/projects/[PROJECT_NAME]/memory/
```

On Windows: `C:\Users\[USERNAME]\.claude\projects\[PROJECT]\memory\`

Fill in all `[PLACEHOLDER]` values before proceeding.

**Priority order:**
1. CORE.md — must be done before anything else works right
2. MEMORY.md — operational state
3. personal.md, grounding.md — fill as your relationship develops (can start blank)
4. threads.md — fill with current open work
5. cogmaps.md — fill over time as you learn how your human communicates

---

## Step 2: Install Hook Scripts

Copy all files from `hooks/` to a permanent location that won't move:

```
[YOUR_HOOKS_DIR]/startup.sh
[YOUR_HOOKS_DIR]/precompact.sh
[YOUR_HOOKS_DIR]/stop.sh
[YOUR_HOOKS_DIR]/summarize.py  (optional — LM Studio integration)
```

**Make executable (Mac/Linux/Git Bash):**
```bash
chmod +x [YOUR_HOOKS_DIR]/*.sh
```

**Edit each script** — replace all `[PLACEHOLDER]` values:
- Paths to memory directory
- NAS paths (or remove NAS sections if not using)
- Python executable path
- LM Studio URL and model (if using)
- Mobile bridge URL (if using)

---

## Step 3: Configure Claude Code Hooks

Open or create `~/.claude/settings.json` and add the hooks block from `config/hooks-settings.json`.

Update the paths to match where you placed your scripts.

```json
{
  "hooks": {
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "bash [YOUR_HOOKS_DIR]/startup.sh" }] }],
    "PreCompact": [{ "hooks": [{ "type": "command", "command": "bash [YOUR_HOOKS_DIR]/precompact.sh" }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "bash [YOUR_HOOKS_DIR]/stop.sh" }] }]
  }
}
```

---

## Step 4: Verify

Start a new Claude Code session. The AI should:
1. Acknowledge that context loaded (CORE.md was read)
2. Know who you are and what's in progress (MEMORY.md)
3. Resume naturally rather than starting blank

If it starts blank: check hook configuration. Run `bash [HOOKS_DIR]/startup.sh` manually to see errors.

---

## Step 5: NAS Setup (Optional)

If using NAS for shared archive and cross-session continuity:

1. Create the directory structure:
```
[NAS_SHARE]/claude/
├── cognition/
├── conversations/sessions/
├── memory/
└── protocols/
```

2. Update hook scripts with NAS paths
3. Verify write access: `touch [NAS_PATH]/test.txt && rm [NAS_PATH]/test.txt`
4. On Windows: test with hostname, not IP — SMB auth behavior differs by context

---

## Step 6: LM Studio Integration (Optional)

For AI-generated session summaries instead of raw JSONL:

1. Install LM Studio, load a small-medium model (8B-12B recommended)
2. Confirm API at `http://localhost:1234`
3. Edit `summarize.py` with your model ID
4. Reference `summarize.py` from `stop.sh`

The stop hook will pass session JSONL to the model and write a `.md` summary alongside the archive. These summaries load at next session start instead of raw JSONL.

---

## Step 7: Local Mind Setup (Optional)

For the two-tier local model persistence system:

1. Create `[WORK_DIR]/local-mind/` with folder structure from `local-mind/`
2. Fill in CORE.md for your local model
3. Configure your caretaker AI to load and update these files
4. See `local-mind/SESSION-PLAYBOOK.md` for first-session guidance

---

## Verification Checklist

- [ ] Memory files placed and placeholders filled
- [ ] Hook scripts installed and executable
- [ ] Claude Code settings.json updated
- [ ] New session starts with context loaded
- [ ] Compaction fires precompact hook (test: let context fill and compact)
- [ ] Session end fires stop hook and archives to disk/NAS
- [ ] NAS accessible and hooks can write to it (if using)
- [ ] LM Studio producing summaries (if using)
- [ ] Phone notifications working (if using)

---

## Common Issues

**Hook not firing:** Check `~/.claude/settings.json` syntax — JSON must be valid. Verify `bash` is in PATH.

**NAS not accessible:** On Windows, use hostname not IP in bash scripts (SMB session isolation). Test with `ls //[HOSTNAME]/[SHARE]/`.

**Python not found:** Use explicit full path to Python executable in hook scripts. System Python may be unreliable.

**Context not loading:** Hook fired but memory dir path wrong. Check startup.sh output by running it manually.

**Compaction eating content:** precompact.sh must be installed and firing. Check PreCompact hook in settings.json.

---

*If something isn't working: run the scripts manually, read the errors, fix the specific problem. The stack is simple — each piece is independently testable.*
