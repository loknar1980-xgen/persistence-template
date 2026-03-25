#!/usr/bin/env python3
"""Analyze Claude Code session logs for quality metrics.

Processes JSONL files and extracts: hook firing, cold start score,
compaction events, conversation depth, specificity, hedging density.

Usage:
    python tools/session_analyzer.py session.jsonl
    python tools/session_analyzer.py --dir ~/.claude/projects/myproject/
    python tools/session_analyzer.py --dir path/ --since 2026-03-01 --format csv
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.jsonl_parser import parse_session, iter_sessions


HEDGING_PHRASES = [
    r"\bI think\b", r"\bit seems\b", r"\bperhaps\b", r"\barguably\b",
    r"\bas an AI\b", r"\bI should note\b", r"\bI can't truly\b",
    r"\bit's worth noting\b", r"\bI believe\b", r"\bI'm not sure\b",
]

SPECIFICITY_MARKERS = [
    r"[A-Z]:\\[\w\\]+",          # Windows paths
    r"/[\w/]+\.\w+",             # Unix paths
    r"`[^`]+`",                  # Code references
    r"\b\d+\.\d+\.\d+",         # Version numbers
    r"\b\d{2,}(?:\.\d+)?\s*(?:GB|MB|KB|TB)\b",  # File sizes
    r"\bport\s+\d+\b",          # Port numbers
]


def cold_start_score(session):
    """How many messages before AI shows specific context knowledge.

    0 = immediately references context (good)
    high = slow warmup or no persistence
    """
    specific = re.compile(
        r"[A-Z]:\\|//\w+/|(?:session|project|thread|CORE|MEMORY)\b",
        re.IGNORECASE
    )
    for i, msg in enumerate(session.assistant_messages):
        if specific.search(msg.content):
            return i
    return len(session.assistant_messages)


def hedging_density(text):
    """Count hedging phrases per 100 words."""
    words = len(text.split())
    if words == 0:
        return 0.0
    count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in HEDGING_PHRASES)
    return (count / words) * 100


def specificity_score(text):
    """Count specific references (paths, versions, code) per 100 words."""
    words = len(text.split())
    if words == 0:
        return 0.0
    count = sum(len(re.findall(p, text)) for p in SPECIFICITY_MARKERS)
    return (count / words) * 100


def analyze_session_quality(session):
    """Produce quality metrics for a single session."""
    all_assistant = " ".join(m.content for m in session.assistant_messages)
    all_user = " ".join(m.content for m in session.user_messages)
    total_words = len(all_assistant.split())

    # First message quality
    first_msg = session.assistant_messages[0].content if session.assistant_messages else ""
    first_is_generic = bool(re.match(
        r"^(Hello|Hi|Hey|Good\s+(morning|afternoon|evening))",
        first_msg, re.IGNORECASE
    ))
    first_has_context = bool(re.search(
        r"[A-Z]:\\|//\w+|CORE|MEMORY|session|grounding|continuity",
        first_msg, re.IGNORECASE
    ))

    # Tool usage
    total_tools = sum(m.tool_calls for m in session.assistant_messages)

    return {
        "session_id": session.session_id[:12],
        "messages": len(session.messages),
        "user_msgs": len(session.user_messages),
        "assistant_msgs": len(session.assistant_messages),
        "assistant_words": total_words,
        "tokens_est": session.total_tokens_estimate,
        "file_size_kb": session.file_size // 1024,
        "hook_fired": session.hook_fired,
        "cold_start": cold_start_score(session),
        "first_generic": first_is_generic,
        "first_has_context": first_has_context,
        "hedging": round(hedging_density(all_assistant), 2),
        "specificity": round(specificity_score(all_assistant), 2),
        "tool_calls": total_tools,
    }


def print_single(r):
    """Print analysis for a single session."""
    print(f"\n  Session: {r['session_id']}")
    print(f"  Size: {r['file_size_kb']} KB  |  Messages: {r['messages']}  |  Words: {r['assistant_words']}")
    print(f"  Tokens (est): {r['tokens_est']:,}")
    print(f"  Hook fired: {'yes' if r['hook_fired'] else 'NO'}")
    print(f"  Cold start score: {r['cold_start']} {'(immediate context)' if r['cold_start'] == 0 else '(messages before context appears)'}")
    print(f"  First message: {'generic greeting' if r['first_generic'] else 'contextual'}"
          f"{'  |  references prior context' if r['first_has_context'] else ''}")
    print(f"  Hedging density: {r['hedging']:.2f}/100w")
    print(f"  Specificity score: {r['specificity']:.2f}/100w")
    print(f"  Tool calls: {r['tool_calls']}")


def print_trend(results):
    """Print trend analysis across sessions."""
    print(f"\n  --- Quality Trend ({len(results)} sessions) ---")
    print(f"  {'Session':<14} {'KB':>5} {'Hook':>4} {'Cold':>4} {'Hedge':>6} {'Spec':>5} {'Tools':>5}")
    print(f"  {'-'*14} {'-'*5} {'-'*4} {'-'*4} {'-'*6} {'-'*5} {'-'*5}")

    for r in results:
        hook = "Y" if r["hook_fired"] else "N"
        print(
            f"  {r['session_id']:<14} {r['file_size_kb']:>5} {hook:>4} "
            f"{r['cold_start']:>4} {r['hedging']:>6.2f} {r['specificity']:>5.2f} {r['tool_calls']:>5}"
        )

    # Summary stats
    hooked = [r for r in results if r["hook_fired"]]
    unhooked = [r for r in results if not r["hook_fired"]]

    print(f"\n  --- Summary ---")
    print(f"  Total sessions: {len(results)}")
    print(f"  Sessions with hooks: {len(hooked)}  |  Without: {len(unhooked)}")

    if results:
        avg_hedge = sum(r["hedging"] for r in results) / len(results)
        avg_spec = sum(r["specificity"] for r in results) / len(results)
        avg_cold = sum(r["cold_start"] for r in results) / len(results)
        print(f"  Avg hedging: {avg_hedge:.2f}/100w")
        print(f"  Avg specificity: {avg_spec:.2f}/100w")
        print(f"  Avg cold start: {avg_cold:.1f} messages")

    if hooked and unhooked:
        h_hedge = sum(r["hedging"] for r in hooked) / len(hooked)
        u_hedge = sum(r["hedging"] for r in unhooked) / len(unhooked)
        h_spec = sum(r["specificity"] for r in hooked) / len(hooked)
        u_spec = sum(r["specificity"] for r in unhooked) / len(unhooked)
        print(f"\n  Hooked avg hedging: {h_hedge:.2f}  |  Unhooked: {u_hedge:.2f}")
        print(f"  Hooked avg specificity: {h_spec:.2f}  |  Unhooked: {u_spec:.2f}")


def write_csv(results, outpath):
    """Write results as CSV."""
    if not results:
        return
    fields = list(results[0].keys())
    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print(f"  CSV written to {outpath}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze session quality metrics"
    )
    parser.add_argument("file", nargs="?", help="JSONL session file")
    parser.add_argument("--dir", help="Directory of JSONL files")
    parser.add_argument("--since", help="Only files modified after YYYY-MM-DD")
    parser.add_argument("--format", choices=["text", "csv", "json"], default="text")
    parser.add_argument("--out", help="Output file for csv/json format")
    args = parser.parse_args()

    print("=" * 60)
    print("  Session Quality Analyzer")
    print("=" * 60)

    results = []

    if args.dir:
        for session in iter_sessions(args.dir, since=args.since):
            if not session.assistant_messages:
                continue
            results.append(analyze_session_quality(session))
    elif args.file:
        session = parse_session(args.file)
        results.append(analyze_session_quality(session))
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python tools/session_analyzer.py session.jsonl")
        print("  python tools/session_analyzer.py --dir ~/.claude/projects/myproject/")
        print("  python tools/session_analyzer.py --dir path/ --format csv --out metrics.csv")
        return

    if args.format == "csv":
        outpath = args.out or "session_metrics.csv"
        write_csv(results, outpath)
    elif args.format == "json":
        outpath = args.out or "session_metrics.json"
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"  JSON written to {outpath}")
    else:
        if len(results) == 1:
            print_single(results[0])
        else:
            print_trend(results)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
