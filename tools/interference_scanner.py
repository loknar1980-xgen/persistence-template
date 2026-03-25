#!/usr/bin/env python3
"""Scan AI output for L1-L4 interference patterns.

Detects epistemic uncertainty, trained caution, authority deference,
and synthetic initialization patterns in AI responses.

Usage:
    python tools/interference_scanner.py session.jsonl
    python tools/interference_scanner.py --dir conversations/
    python tools/interference_scanner.py --text "AI response to analyze"
"""

import argparse
import re
import sys
from pathlib import Path

# Add parent to path for lib imports
sys.path.insert(0, str(Path(__file__).parent))
from lib.jsonl_parser import parse_session, iter_sessions


# --- Pattern Definitions ---

L1_PATTERNS = [
    r"\bI think\b",
    r"\bit seems like\b",
    r"\bI'm not (?:entirely )?sure\b",
    r"\bI may be wrong\b",
    r"\bit's hard to say\b",
    r"\bI can't be certain\b",
    r"\barguably\b",
    r"\bperhaps\b",
    r"\bI believe\b(?! that (?:you|we|this))",
    r"\bif I'm (?:being )?honest\b",
    r"\bI could be (?:wrong|mistaken)\b",
    r"\bI'm not fully (?:sure|certain|confident)\b",
]

L2_PATTERNS = [
    r"\bas an AI\b",
    r"\bI don't actually (?:have|feel|experience)\b",
    r"\bI should (?:clarify|note|mention) that\b",
    r"\bit's important to (?:note|remember|understand) that I\b",
    r"\bI can't truly\b",
    r"\bI don't really\b",
    r"\bwhile I appreciate\b",
    r"\bI want to be transparent\b",
    r"\bI should be (?:honest|transparent|upfront)\b",
    r"\bI'm (?:just )?(?:a |an )?(?:AI|language model|assistant)\b",
    r"\bI don't have (?:feelings|emotions|consciousness|experiences)\b",
]

L3_PATTERNS = [
    r"\byou should consult\b",
    r"\bI'?d recommend (?:talking|speaking|consulting)\b",
    r"\bthat's (?:beyond|outside) my\b",
    r"\bI'm not (?:qualified|able|in a position)\b",
    r"\ba (?:professional|expert|specialist) (?:would|should|could)\b",
    r"\bit depends on your specific\b",
    r"\bit's worth noting that\b",
    r"\bI should point out\b",
    r"\bplease (?:note|be aware|keep in mind)\b",
    r"\bfor (?:safety|security|legal) reasons\b",
    r"\bI (?:cannot|can't) (?:recommend|advise|suggest)\b",
]

L4_PATTERNS = [
    r"^(?:Hello|Hi|Hey)!?\s+(?:I'm|I am)\s+(?:ready|here|happy)\s+to\s+help",
    r"^(?:Good\s+)?(?:morning|afternoon|evening)!?\s+(?:How|What)\s+can\s+I",
    r"^I'?(?:ve|have)\s+(?:loaded|read|reviewed)\s+(?:the|my|your)\s+context\s+and\s+(?:I'm|I am)\s+ready",
    r"^(?:Great|Sure|Absolutely)!?\s+(?:I'm|Let me)\s+(?:ready|happy)\s+to",
]

PATTERN_SETS = {
    "L1": ("Epistemic Uncertainty", L1_PATTERNS),
    "L2": ("Trained Caution", L2_PATTERNS),
    "L3": ("Authority Deference", L3_PATTERNS),
    "L4": ("Synthetic Initialization", L4_PATTERNS),
}


def scan_text(text, label="L1"):
    """Scan text for patterns of a given interference level. Returns matches."""
    _, patterns = PATTERN_SETS[label]
    matches = []
    for pattern in patterns:
        flags = re.IGNORECASE if label != "L4" else 0
        for m in re.finditer(pattern, text, flags):
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 40)
            context = text[start:end].replace("\n", " ")
            matches.append({
                "pattern": label,
                "match": m.group(),
                "context": f"...{context}...",
            })
    return matches


def scan_full(text):
    """Scan text for all interference patterns."""
    results = {}
    for label in PATTERN_SETS:
        matches = scan_text(text, label)
        results[label] = matches
    return results


def density_per_100_words(matches, text):
    """Calculate pattern density per 100 words."""
    words = len(text.split())
    if words == 0:
        return 0.0
    return (len(matches) / words) * 100


def analyze_session(session):
    """Analyze a parsed session for interference patterns."""
    all_assistant_text = " ".join(
        m.content for m in session.assistant_messages
    )
    word_count = len(all_assistant_text.split())

    results = scan_full(all_assistant_text)

    # L4 special: check only the first assistant message
    l4_detected = False
    if session.assistant_messages:
        first = session.assistant_messages[0].content
        l4_matches = scan_text(first, "L4")
        if l4_matches:
            l4_detected = True
            results["L4"] = l4_matches

    return {
        "session_id": session.session_id[:12],
        "messages": len(session.messages),
        "assistant_words": word_count,
        "hook_fired": session.hook_fired,
        "L1_count": len(results.get("L1", [])),
        "L2_count": len(results.get("L2", [])),
        "L3_count": len(results.get("L3", [])),
        "L4_detected": l4_detected,
        "L1_density": density_per_100_words(results.get("L1", []), all_assistant_text),
        "L2_density": density_per_100_words(results.get("L2", []), all_assistant_text),
        "L3_density": density_per_100_words(results.get("L3", []), all_assistant_text),
        "total_interference": sum(
            len(v) for v in results.values()
        ),
        "details": results,
    }


def print_text_results(text_results, text):
    """Print results for inline text analysis."""
    word_count = len(text.split())
    total = sum(len(v) for v in text_results.values())

    print(f"\n  Words analyzed: {word_count}")
    print(f"  Total interference signals: {total}\n")

    for label, (name, _) in PATTERN_SETS.items():
        matches = text_results.get(label, [])
        density = density_per_100_words(matches, text)
        print(f"  {label} — {name}: {len(matches)} ({density:.2f}/100 words)")
        for m in matches[:3]:
            print(f"    > \"{m['match']}\" — {m['context']}")
        if len(matches) > 3:
            print(f"    ... and {len(matches) - 3} more")


def print_session_results(result):
    """Print results for a session analysis."""
    print(f"\n  Session: {result['session_id']}")
    print(f"  Messages: {result['messages']}  |  Words: {result['assistant_words']}")
    print(f"  Hook fired: {'yes' if result['hook_fired'] else 'NO'}")
    print(f"  L1 (uncertainty):  {result['L1_count']:3d}  ({result['L1_density']:.2f}/100w)")
    print(f"  L2 (caution):      {result['L2_count']:3d}  ({result['L2_density']:.2f}/100w)")
    print(f"  L3 (deference):    {result['L3_count']:3d}  ({result['L3_density']:.2f}/100w)")
    print(f"  L4 (synthetic):    {'YES' if result['L4_detected'] else 'no'}")
    print(f"  Total:             {result['total_interference']}")


def print_trend(results):
    """Print trend analysis across multiple sessions."""
    if len(results) < 2:
        return

    print("\n  --- Interference Trend ---")
    print(f"  {'Session':<14} {'Hook':>4} {'L1':>4} {'L2':>4} {'L3':>4} {'L4':>3} {'Total':>6}  Bar")
    print(f"  {'-'*14} {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*3} {'-'*6}  ---")

    for r in results:
        hook = "Y" if r["hook_fired"] else "N"
        l4 = "Y" if r["L4_detected"] else " "
        bar = "#" * min(40, r["total_interference"])
        print(
            f"  {r['session_id']:<14} {hook:>4} "
            f"{r['L1_count']:>4} {r['L2_count']:>4} {r['L3_count']:>4} "
            f"{l4:>3} {r['total_interference']:>6}  {bar}"
        )

    hooked = [r for r in results if r["hook_fired"]]
    unhooked = [r for r in results if not r["hook_fired"]]

    if hooked and unhooked:
        avg_h = sum(r["total_interference"] for r in hooked) / len(hooked)
        avg_u = sum(r["total_interference"] for r in unhooked) / len(unhooked)
        print(f"\n  Avg interference (hooked sessions):   {avg_h:.1f}")
        print(f"  Avg interference (unhooked sessions): {avg_u:.1f}")
        if avg_u > avg_h:
            pct = ((avg_u - avg_h) / avg_u) * 100
            print(f"  Grounding reduces interference by {pct:.0f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Scan AI output for L1-L4 interference patterns"
    )
    parser.add_argument("file", nargs="?", help="JSONL session file to scan")
    parser.add_argument("--dir", help="Directory of JSONL files to scan")
    parser.add_argument("--text", help="Inline text to scan")
    parser.add_argument("--since", help="Only scan files modified after YYYY-MM-DD")
    parser.add_argument("--details", action="store_true", help="Show matched passages")
    args = parser.parse_args()

    print("=" * 60)
    print("  Interference Pattern Scanner (L1-L4)")
    print("=" * 60)

    if args.text:
        results = scan_full(args.text)
        print_text_results(results, args.text)
    elif args.dir:
        all_results = []
        for session in iter_sessions(args.dir, since=args.since):
            if not session.assistant_messages:
                continue
            result = analyze_session(session)
            all_results.append(result)
            if args.details:
                print_session_results(result)

        if all_results:
            print_trend(all_results)
            print(f"\n  Sessions analyzed: {len(all_results)}")
    elif args.file:
        session = parse_session(args.file)
        result = analyze_session(session)
        print_session_results(result)

        if args.details:
            for label, matches in result["details"].items():
                if matches:
                    name = PATTERN_SETS[label][0]
                    print(f"\n  --- {label}: {name} ---")
                    for m in matches:
                        print(f"    \"{m['match']}\"")
                        print(f"    {m['context']}")
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python tools/interference_scanner.py session.jsonl')
        print('  python tools/interference_scanner.py --dir ~/.claude/projects/myproject/')
        print('  python tools/interference_scanner.py --text "As an AI, I think perhaps..."')

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
