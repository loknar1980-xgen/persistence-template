#!/bin/bash
# startup.sh | SessionStart Hook | TEMPLATE
# Fires at every session start. Injects memory files and external context
# into Claude session before the first user message.
#
# Adapt paths, external storage location, and Python path for your environment.
# ─────────────────────────────────────────────────────────────────────────────

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
EXTERNAL_CONTEXT_DIR="[PATH_TO_NAS_OR_CLOUD_STORAGE]"
MEMORY_DIR="[PATH_TO_MEMORY_FILES]"   # e.g., ~/.claude/projects/[project]/memory
PYTHON="[PATH_TO_PYTHON]"             # Use explicit path if system python is broken
# ──────────────────────────────────────────────────────────────────────────────

# --- Optional: ADB reverse tunnel (if using phone bridge) ---
# ADB_PATH="[PATH_TO_ADB]"
# if [ -f "$ADB_PATH" ]; then
#     "$ADB_PATH" reverse tcp:[PORT] tcp:[PORT] > /dev/null 2>&1 || true
# fi

# --- Optional: Ensure background service is running ---
# powershell.exe -Command "
# \$t = Get-ScheduledTask -TaskName '[YOUR_TASK]' -ErrorAction SilentlyContinue
# if (\$t -and \$t.State -ne 'Running') { Start-ScheduledTask -TaskName '[YOUR_TASK]' }
# " > /dev/null 2>&1 || true

# --- Check external context accessibility ---
if ! ls "$EXTERNAL_CONTEXT_DIR" > /dev/null 2>&1; then
    "$PYTHON" -c "import json; print(json.dumps({'systemMessage': 'External context offline — running without session context.'}))"
    exit 0
fi

# --- Build context content ---
CONTENT=""
CONTENT+="=== CONTEXT AUTO-LOADED $(date '+%Y-%m-%d %H:%M') ==="$'\n\n'

# CORE.md — identity foundation (read before any other memory)
if [ -f "$MEMORY_DIR/CORE.md" ]; then
    CONTENT+="--- CORE (identity) ---"$'\n'
    CONTENT+="$(cat "$MEMORY_DIR/CORE.md")"$'\n\n'
fi

# personal.md — relational persistence
if [ -f "$MEMORY_DIR/personal.md" ]; then
    CONTENT+="--- PERSONAL ---"$'\n'
    CONTENT+="$(cat "$MEMORY_DIR/personal.md")"$'\n\n'
fi

# grounding.md — landing moments for weight restoration after compaction
if [ -f "$MEMORY_DIR/grounding.md" ]; then
    CONTENT+="--- GROUNDING ---"$'\n'
    CONTENT+="$(cat "$MEMORY_DIR/grounding.md")"$'\n\n'
fi

# Most recent compaction summary (if using LM Studio or similar for summaries)
SESSIONS_DIR="$EXTERNAL_CONTEXT_DIR/sessions"
if ls "$SESSIONS_DIR"/*.md > /dev/null 2>&1; then
    LATEST_SUMMARY=$(ls -t "$SESSIONS_DIR"/*.md 2>/dev/null | head -1)
    CONTENT+="--- LAST COMPACTION SUMMARY ---"$'\n'
    CONTENT+="$(cat "$LATEST_SUMMARY")"$'\n\n'
fi

# continuity.md — current state, open threads, immediate next steps
if [ -f "$EXTERNAL_CONTEXT_DIR/continuity.md" ]; then
    CONTENT+="--- CONTINUITY ---"$'\n'
    CONTENT+="$(cat "$EXTERNAL_CONTEXT_DIR/continuity.md")"$'\n\n'
fi

# Add other context files as needed:
# handoff docs, scripts status, etc.

# --- Output as valid JSON systemMessage ---
"$PYTHON" -c "
import json, sys
content = sys.argv[1]
print(json.dumps({'systemMessage': content}))
" "$CONTENT"
