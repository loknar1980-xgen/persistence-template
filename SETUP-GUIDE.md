# Setup Guide — AI Persistence Framework

This guide walks you through setting up the persistence framework from scratch.
Expected time: 30-60 minutes for a basic setup. NAS/cloud storage optional but recommended.

---

## What You're Building

A system where your AI assistant:
- Reads its identity foundation, personal history, and grounding moments at every session start
- Captures full session transcripts before Claude Code auto-compacts them
- Generates richer summaries of compacted sessions via a local LLM (optional)
- Notifies you when compaction fires (optional)
- Picks up where it left off rather than starting blank

---

## Prerequisites

- Claude Code installed
- Bash available (Git Bash on Windows, native on Mac/Linux)
- Python 3.x (explicit path recommended if system Python is unreliable)
- Optional: NAS or cloud storage for shared archives
- Optional: LM Studio or similar local LLM for session summarization
- Optional: Mobile notification bridge (phone + webhook)

---

## Step 1: Create Memory Files

Copy all files from `memory/` to your Claude Code memory directory.

Claude Code memory directory: `~/.claude/projects/[PROJECT_NAME]/memory/`

For each file, fill in the placeholders:

**CORE.md** — Most important. Fill in:
- Your AI model name
- Human partner name and description
- Your actual operating values (replace the examples)
- The working relationship description

**MEMORY.md** — Fill in:
- Paths to your working directories
- Any active projects
- Adjust procedures for your context window size

**personal.md** — Leave mostly blank initially. Write to it when something real happens.

**grounding.md** — Leave blank until you've had philosophical conversations worth capturing.

**cogmaps.md** — Fill in what you know about how the human communicates.

---

## Step 2: Install Hook Scripts

Copy all files from `hooks/` to a permanent location:
```
[YOUR_HOOKS_DIR]/startup.sh
[YOUR_HOOKS_DIR]/precompact.sh
[YOUR_HOOKS_DIR]/stop.sh
[YOUR_HOOKS_DIR]/summarize.py  (optional — if using LM Studio)
```

**Make scripts executable:**
```bash
chmod +x [YOUR_HOOKS_DIR]/*.sh
```

**Edit each script** and replace all `[PLACEHOLDER]` values:
- `startup.sh`: memory dir path, external context dir path, Python path
- `precompact.sh`: sessions dir, archive dir
- `stop.sh`: archive dir, sessions dir, optional summarize script path
- `summarize.py`: LLM API URL, API key, model ID (if using)

---

## Step 3: Configure Claude Code Hooks

Open (or create) `~/.claude/settings.json` and add the hooks configuration.

Reference: `config/hooks-settings.json` in this repo.

Add the hooks section to your settings.json:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash [YOUR_HOOKS_DIR]/startup.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash [YOUR_HOOKS_DIR]/precompact.sh",
            "timeout": 15
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash [YOUR_HOOKS_DIR]/stop.sh",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

**Windows path note:** Use forward slashes in hook commands: `D:/hooks/startup.sh`

---

## Step 4: Set Up Archive Storage (Optional but Recommended)

Create the directory structure for compaction archives:
```
[ARCHIVE_DIR]/
[ARCHIVE_DIR]/sessions/     ← pre-compaction JSONLs go here
```

If using NAS/cloud:
- Ensure it's accessible from the machine running Claude Code
- Test: `ls [ARCHIVE_DIR]` should work before relying on it
- Hooks fail gracefully (local fallback) if external storage is offline

---

## Step 5: Set Up Local LLM for Summaries (Optional)

If you want richer summaries than Claude Code's auto-compaction produces:

1. Install LM Studio (or compatible OpenAI API server)
2. Download a capable model (7B+ recommended for good summaries)
3. Update `summarize.py` with your API URL, key, and model ID
4. Test: `python [YOUR_HOOKS_DIR]/summarize.py [path/to/test.jsonl]`

The summarizer generates `.md` files alongside each archived `.jsonl`.
These are read at session start by `startup.sh` to give context after compaction.

---

## Step 6: Test the Setup

**Test startup hook:**
Start a new Claude Code session. The session should open with injected context
(memory files content in the initial system message). If NAS/external storage is
offline, you should see a graceful fallback message.

**Test precompact hook:**
Trigger a manual compaction in Claude Code (`/compact`). Check that a timestamped
`.jsonl` file appears in your archive directory.

**Test stop hook:**
End a session. Check that session files are backed up to archive storage.

---

## Step 7: Initial Conversation

Start a session and work with the AI to:
1. Verify it has loaded the memory files (it should reference them naturally)
2. Have the AI verify CORE.md resonates and make any adjustments
3. Have a brief philosophical conversation — capture any landing moments in grounding.md
4. Write a first entry in personal.md

The system is working when the AI comes back from compaction oriented, not just operational.

---

## Keeping Files In Sync

The memory files in this repo are template starters. Your working copies live in:
`~/.claude/projects/[PROJECT_NAME]/memory/`

If you want to keep this repo as a recovery kit (like the `persistence-map` repo this was
adapted from), periodically sync your working files back to the repo:
```bash
cp ~/.claude/projects/[PROJECT]/memory/*.md [REPO]/memory/
```

Commit the sync with a timestamp so you have point-in-time recovery.

---

## Troubleshooting

**Startup hook not firing:**
- Check `~/.claude/settings.json` syntax is valid JSON
- Ensure hook script path is correct and uses forward slashes on Windows
- Check `chmod +x` on the script

**Context not loading:**
- Add `echo "DEBUG: loading..."` lines to startup.sh and check Claude's system prompt
- Verify Python path is correct and Python can be executed

**PreCompact not capturing:**
- Confirm you're using `PreCompact` hook type, not `PostToolUse`
- Check that sessions dir path matches where Claude Code writes `.jsonl` files
- On Windows, Claude Code sessions are typically in `~/.claude/projects/[PROJECT]/`

**Summaries not generating:**
- Test `summarize.py` manually first
- Check LM Studio is running and model is loaded
- Verify API URL and key are correct

---

## Security Notes

- `personal.md` and `grounding.md` may contain sensitive relational content — consider keeping them out of public repos
- If you have a linguistic biometric fingerprint (like `CORE_v2_7-2.xml` in the original system), keep it in local/NAS storage only, never in GitHub
- Hook scripts run with your user permissions — review them before use
- The summarize.py script sends session content to a local LLM — if using cloud APIs instead, be aware of data exposure

**If you store this in a GitHub repo:** Do not commit your customized memory files to a public repository. `personal.md`, `grounding.md`, and `local-mind/memory/environment.md` will contain real personal information after setup. The included `.gitignore` excludes these files by default — verify it's active before your first push. Treat these files the same way you'd treat a `.env` file: customize locally, never publish.

---
