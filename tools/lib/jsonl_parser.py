"""Parse Claude Code JSONL session files into structured data.

Handles the real format: content blocks (text, thinking, tool_use),
progress entries, queue operations. Extracts clean conversation data.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str  # extracted text content
    timestamp: str = ""
    has_thinking: bool = False
    thinking_text: str = ""
    tool_calls: int = 0
    token_estimate: int = 0

    def __post_init__(self):
        self.token_estimate = len(self.content) // 4


@dataclass
class Session:
    session_id: str
    messages: list = field(default_factory=list)
    start_time: str = ""
    hook_fired: bool = False
    compactions: int = 0
    file_size: int = 0

    @property
    def user_messages(self):
        return [m for m in self.messages if m.role == "user"]

    @property
    def assistant_messages(self):
        return [m for m in self.messages if m.role == "assistant"]

    @property
    def total_tokens_estimate(self):
        return sum(m.token_estimate for m in self.messages)


def _extract_text(content):
    """Extract plain text from message content (string or list of blocks)."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        texts = []
        thinking = []
        tool_count = 0
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                texts.append(block.get("text", ""))
            elif block.get("type") == "thinking":
                thinking.append(block.get("thinking", ""))
            elif block.get("type") == "tool_use":
                tool_count += 1
        return " ".join(texts).strip(), " ".join(thinking).strip(), tool_count

    return str(content).strip()


def parse_session(path):
    """Parse a JSONL session file into a Session object."""
    path = Path(path)
    session = Session(
        session_id=path.stem,
        file_size=path.stat().st_size,
    )

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type", "")

            # Detect hook firing
            if entry_type == "progress":
                detail = entry.get("detail", "")
                if isinstance(detail, str) and "SessionStart" in detail:
                    session.hook_fired = True
                # Detect start time from first progress
                if not session.start_time:
                    ts = entry.get("timestamp", "")
                    if ts:
                        session.start_time = ts

            # Extract messages
            if entry_type in ("user", "assistant"):
                msg_data = entry.get("message", {})
                raw_content = msg_data.get("content", "")

                extracted = _extract_text(raw_content)
                if isinstance(extracted, tuple):
                    text, thinking, tool_count = extracted
                else:
                    text, thinking, tool_count = extracted, "", 0

                # Skip empty messages and task notifications
                if not text or text.startswith("<task-notification>"):
                    continue

                msg = Message(
                    role=entry_type,
                    content=text,
                    timestamp=entry.get("timestamp", ""),
                    has_thinking=bool(thinking),
                    thinking_text=thinking,
                    tool_calls=tool_count,
                )
                session.messages.append(msg)

    return session


def iter_sessions(directory, since=None):
    """Yield Session objects for all .jsonl files in a directory.

    Args:
        directory: Path to directory containing .jsonl files
        since: Optional date string (YYYY-MM-DD) to filter by modification time
    """
    directory = Path(directory)
    files = sorted(directory.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)

    for f in files:
        # Skip agent session files
        if f.name.startswith("agent-"):
            continue
        if since:
            from datetime import datetime
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            cutoff = datetime.fromisoformat(since)
            if mtime < cutoff:
                continue
        yield parse_session(f)
