#!/bin/bash
# stop.sh | Stop Hook | TEMPLATE
# Fires at session end.
# 1. Backs up all session JSONLs to archive storage
# 2. Generates summaries for recent unsummarized archives (if using LM Studio or similar)
# 3. Cleans up old archives beyond retention limit
#
# Adapt paths and summarization method for your environment.
# ─────────────────────────────────────────────────────────────────────────────

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
ARCHIVE_DIR="[PATH_TO_ARCHIVE_STORAGE]"        # NAS, cloud, or local backup
SESSIONS_DIR="[PATH_TO_LOCAL_SESSIONS_DIR]"    # Where your .jsonl files live
SUMMARIZE_SCRIPT="[PATH_TO_SUMMARIZE_SCRIPT]"  # Optional: summarization script
ARCHIVE_RETENTION=20                            # Keep this many archives
# ──────────────────────────────────────────────────────────────────────────────

# --- 1. Backup all session JSONLs ---
if ! ls "$ARCHIVE_DIR" > /dev/null 2>&1; then
    echo "Archive storage offline — session NOT backed up" >&2
    exit 0
fi

SAVED=0
for f in "$SESSIONS_DIR"/*.jsonl; do
    [ -f "$f" ] || continue
    FNAME=$(basename "$f")
    cp "$f" "$ARCHIVE_DIR/$FNAME" 2>/dev/null && SAVED=$((SAVED+1))
done
echo "Session backup: $SAVED files saved"

# --- 2. Summarize unsummarized archives (optional) ---
# Skip this section if you're not using an LM Studio or similar local summarizer.
# The summarizer generates .md files from .jsonl archives for easier review.

SESSIONS_ARCHIVE="$ARCHIVE_DIR/sessions"
if ls "$SESSIONS_ARCHIVE" > /dev/null 2>&1 && [ -f "$SUMMARIZE_SCRIPT" ]; then
    SUMMARIZED=0
    SKIPPED=0
    for archive in "$SESSIONS_ARCHIVE"/*.jsonl; do
        [ -f "$archive" ] || continue
        md_path="${archive%.jsonl}.md"
        if [ -f "$md_path" ]; then
            SKIPPED=$((SKIPPED+1))
            continue
        fi
        # Only summarize archives from the last 24 hours
        ARCHIVE_AGE=$(( $(date +%s) - $(date -r "$archive" +%s 2>/dev/null || echo 0) ))
        [ "$ARCHIVE_AGE" -gt 86400 ] && continue

        echo "Summarizing: $(basename "$archive")"
        python "$SUMMARIZE_SCRIPT" "$archive" 2>&1
        SUMMARIZED=$((SUMMARIZED+1))
    done
    echo "Summarization: $SUMMARIZED generated, $SKIPPED already had summaries"
fi

# --- 3. Cleanup old archives beyond retention limit ---
if ls "$SESSIONS_ARCHIVE"/*.jsonl > /dev/null 2>&1; then
    ARCHIVE_COUNT=$(ls "$SESSIONS_ARCHIVE"/*.jsonl 2>/dev/null | wc -l)
    if [ "$ARCHIVE_COUNT" -gt "$ARCHIVE_RETENTION" ]; then
        ls -t "$SESSIONS_ARCHIVE"/*.jsonl 2>/dev/null | tail -n +$((ARCHIVE_RETENTION+1)) | while read old; do
            rm -f "$old" "${old%.jsonl}.md" 2>/dev/null
        done
        echo "Cleaned up archives beyond retention limit ($ARCHIVE_RETENTION)"
    fi
fi

exit 0
