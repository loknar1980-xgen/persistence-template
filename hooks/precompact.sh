#!/bin/bash
# precompact.sh | PreCompact Hook | TEMPLATE
# Fires BEFORE Claude Code compacts the session context.
# Saves the full pre-compaction JSONL to storage (timestamped, never overwrites).
#
# IMPORTANT: Use PreCompact hook, NOT PostToolUse.
# PreCompact fires before compaction — PostToolUse would capture already-compacted content.
#
# Adapt paths and optional notification for your environment.
# ─────────────────────────────────────────────────────────────────────────────

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
SESSIONS_DIR="[PATH_TO_LOCAL_SESSIONS_DIR]"    # Where your .jsonl files live
ARCHIVE_DIR="[PATH_TO_ARCHIVE_STORAGE]"        # NAS, cloud, or local backup
THRESHOLD_KB=100                                # Skip tiny sessions
# ──────────────────────────────────────────────────────────────────────────────

# Find current session JSONL (exclude agent- subagent sessions)
LATEST=$(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | grep -v '/agent-' | head -1)
[ -f "$LATEST" ] || exit 0

# Check size threshold
SIZE_KB=$(du -k "$LATEST" 2>/dev/null | cut -f1)
[ -z "$SIZE_KB" ] && exit 0
[ "$SIZE_KB" -lt "$THRESHOLD_KB" ] && exit 0

# Build timestamped filename
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
SESSION_ID=$(basename "$LATEST" .jsonl | cut -c1-8)
LINES=$(wc -l < "$LATEST" 2>/dev/null | tr -d ' ')
ARCHIVE_NAME="${SESSION_ID}-${TIMESTAMP}.jsonl"

# Save to archive (with local fallback)
if ls "$ARCHIVE_DIR" > /dev/null 2>&1; then
    cp "$LATEST" "${ARCHIVE_DIR}/${ARCHIVE_NAME}" 2>/dev/null
    DEST_NOTE="archive:${ARCHIVE_NAME}"
else
    # Fallback: save locally
    LOCAL_BACKUP="$SESSIONS_DIR/compaction-archives"
    mkdir -p "$LOCAL_BACKUP"
    cp "$LATEST" "${LOCAL_BACKUP}/${ARCHIVE_NAME}" 2>/dev/null
    DEST_NOTE="local:${LOCAL_BACKUP}/${ARCHIVE_NAME}"
fi

# Optional: Log the compaction event
# LOG="[PATH_TO_LOG]"
# echo "$(date -Iseconds) session=${SESSION_ID} lines=${LINES} size=${SIZE_KB}KB dest=${DEST_NOTE}" >> "$LOG" 2>/dev/null

# Optional: Backup personal.md alongside the archive
# PERSONAL="[PATH_TO_personal.md]"
# if [ -f "$PERSONAL" ] && ls "$ARCHIVE_DIR" > /dev/null 2>&1; then
#     cp "$PERSONAL" "${ARCHIVE_DIR}/${SESSION_ID}-${TIMESTAMP}-personal.md" 2>/dev/null
# fi

# Optional: Send notification (phone, webhook, etc.)
# NOTIFY_BODY="{\"title\":\"Context Compaction\",\"message\":\"Session ${SESSION_ID}: ${LINES} messages archived\"}"
# curl -s -X POST "[YOUR_NOTIFICATION_ENDPOINT]" \
#     -H "Content-Type: application/json" \
#     -d "$NOTIFY_BODY" \
#     --max-time 3 > /dev/null 2>&1 || true

echo "Compaction archive: ${DEST_NOTE} (${LINES} lines, ${SIZE_KB}KB)"
exit 0
