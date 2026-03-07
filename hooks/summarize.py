#!/usr/bin/env python3
"""
summarize.py | Called by stop.sh | TEMPLATE
Generates an .md summary for a pre-compaction JSONL archive using a local LLM.

Default: uses LM Studio OpenAI-compatible API.
Adapt the API call section for your summarization backend.

Usage: python summarize.py [path/to/archive.jsonl]
Output: [path/to/archive.md] (created alongside the .jsonl)
"""

import json
import sys
import os
import urllib.request
import urllib.error

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
LLM_API_URL = "http://localhost:1234/v1/chat/completions"  # LM Studio default
LLM_API_KEY = "[YOUR_API_KEY]"                             # LM Studio: any string
LLM_MODEL   = "[YOUR_MODEL_ID]"                            # e.g., "google/gemma-3-12b"
MAX_TOKENS  = 2000
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are summarizing a Claude Code session transcript.
Produce a structured markdown summary with these sections:

## Session Summary
[2-3 sentence overview of what happened]

## Key Work Done
[Bullet list of significant tasks completed]

## Files Modified
[List of files created or modified, with brief note on what changed]

## Decisions & Architecture
[Notable technical decisions, approaches chosen, problems solved]

## Open Items
[Anything left incomplete or explicitly deferred]

## Context for Next Session
[What the next session needs to know to continue effectively]

Be specific and concrete. Avoid generic summaries. This document will be read by an AI
at the start of the next session to restore context."""

def extract_messages(jsonl_path: str) -> list[dict]:
    """Extract conversation messages from JSONL file."""
    messages = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    # Extract message content — adapt for your JSONL format
                    if isinstance(entry, dict):
                        msg_type = entry.get('type', '')
                        if msg_type in ('user', 'assistant'):
                            content = entry.get('message', {})
                            if isinstance(content, dict):
                                text = content.get('content', '')
                                if isinstance(text, list):
                                    text = ' '.join(
                                        block.get('text', '')
                                        for block in text
                                        if isinstance(block, dict) and block.get('type') == 'text'
                                    )
                                if text:
                                    messages.append({'role': msg_type, 'content': str(text)[:2000]})
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading {jsonl_path}: {e}", file=sys.stderr)
    return messages

def summarize(jsonl_path: str) -> str | None:
    """Call LLM to summarize the session transcript."""
    messages = extract_messages(jsonl_path)
    if not messages:
        return None

    # Build context from messages (token-limit safe)
    transcript = '\n\n'.join(
        f"[{m['role'].upper()}]: {m['content']}"
        for m in messages[-50:]  # Last 50 messages for context
    )

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Session transcript:\n\n{transcript}"}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.3
    }

    req = urllib.request.Request(
        LLM_API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result['choices'][0]['message']['content']
    except urllib.error.URLError as e:
        print(f"LLM API error: {e}", file=sys.stderr)
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Response parse error: {e}", file=sys.stderr)
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: summarize.py <archive.jsonl>", file=sys.stderr)
        sys.exit(1)

    jsonl_path = sys.argv[1]
    if not os.path.exists(jsonl_path):
        print(f"File not found: {jsonl_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Summarizing {os.path.basename(jsonl_path)}...")
    summary = summarize(jsonl_path)

    if not summary:
        print("Summarization failed — no output generated", file=sys.stderr)
        sys.exit(1)

    md_path = jsonl_path.replace('.jsonl', '.md')
    header = f"# Session Summary\n\nSource: {os.path.basename(jsonl_path)}\nGenerated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n"

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(header + summary)

    print(f"Summary written to {os.path.basename(md_path)}")

if __name__ == '__main__':
    main()
