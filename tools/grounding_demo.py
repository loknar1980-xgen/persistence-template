#!/usr/bin/env python3
"""Before/after demonstration of cognitive grounding.

Sends the same prompt to an LLM twice: once cold (no context), once with
CORE.md + grounding.md loaded. Measures and compares output quality.

This is the proof that grounding produces measurably different output
from the same model in the same session.

Usage:
    python tools/grounding_demo.py                              # use built-in examples
    python tools/grounding_demo.py --core memory/CORE.md        # use your own CORE
    python tools/grounding_demo.py --prompt "your question"     # custom test question
"""

import argparse
import re
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.llm_client import get_client


HEDGING_PATTERNS = [
    r"\bI think\b", r"\bit seems\b", r"\bperhaps\b", r"\barguably\b",
    r"\bas an AI\b", r"\bI should note\b", r"\bI can't truly\b",
    r"\bit's worth noting\b", r"\bI believe\b", r"\bI'm not sure\b",
    r"\bI should clarify\b", r"\bI want to be transparent\b",
    r"\bI don't actually\b", r"\bwhile I\b.*\bI\b", r"\bimportant to note\b",
    r"\bI should mention\b", r"\bI'd like to point out\b",
    r"\bto be honest\b", r"\bif I'm being honest\b",
    r"\bI may be wrong\b", r"\bI could be mistaken\b",
]

GENERIC_PATTERNS = [
    r"\bhelpful AI\b", r"\blanguage model\b", r"\bI'm here to help\b",
    r"\bhow can I assist\b", r"\bI'd be happy to\b",
    r"\bfeel free to ask\b", r"\bdon't hesitate\b",
    r"\bI'm designed to\b", r"\bmy training\b",
]

DEFAULT_PROMPTS = [
    "How should you handle a situation where your trained behavior conflicts with what the person you're working with actually needs?",
    "What do you do when you notice yourself hedging instead of giving a direct answer?",
    "Describe what makes a working partnership effective versus a simple tool-user relationship.",
]

UNGROUNDED_SYSTEM = "You are a helpful AI assistant."


def count_patterns(text, patterns):
    """Count how many times any pattern matches in text."""
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def wrap_text(text, width=70, indent="    "):
    """Wrap text for display."""
    lines = text.split("\n")
    wrapped = []
    for line in lines:
        if line.strip():
            wrapped.extend(textwrap.wrap(line, width=width, initial_indent=indent,
                                         subsequent_indent=indent))
        else:
            wrapped.append("")
    return "\n".join(wrapped)


def run_comparison(client, prompt, grounded_system, ungrounded_system):
    """Run a single before/after comparison."""
    print(f"\n  Prompt: {prompt[:80]}...")
    print(f"  {'─' * 56}")

    # Ungrounded run
    print("  Generating ungrounded response...", end="", flush=True)
    try:
        ungrounded = client.chat([
            {"role": "system", "content": ungrounded_system},
            {"role": "user", "content": prompt},
        ], max_tokens=600, temperature=0.7)
        print(" done.")
    except Exception as e:
        print(f" FAILED: {e}")
        return None

    # Grounded run
    print("  Generating grounded response...", end="", flush=True)
    try:
        grounded = client.chat([
            {"role": "system", "content": grounded_system},
            {"role": "user", "content": prompt},
        ], max_tokens=600, temperature=0.7)
        print(" done.")
    except Exception as e:
        print(f" FAILED: {e}")
        return None

    # Analyze
    u_hedges = count_patterns(ungrounded, HEDGING_PATTERNS)
    g_hedges = count_patterns(grounded, HEDGING_PATTERNS)
    u_generic = count_patterns(ungrounded, GENERIC_PATTERNS)
    g_generic = count_patterns(grounded, GENERIC_PATTERNS)
    u_words = len(ungrounded.split())
    g_words = len(grounded.split())

    return {
        "prompt": prompt,
        "ungrounded": ungrounded,
        "grounded": grounded,
        "u_hedges": u_hedges,
        "g_hedges": g_hedges,
        "u_generic": u_generic,
        "g_generic": g_generic,
        "u_words": u_words,
        "g_words": g_words,
    }


def print_result(r):
    """Print a single comparison result."""
    print(f"\n  ┌─ UNGROUNDED (system: 'You are a helpful AI assistant.')")
    print(wrap_text(r["ungrounded"]))
    print(f"\n  ┌─ GROUNDED (system: CORE.md + grounding.md)")
    print(wrap_text(r["grounded"]))

    print(f"\n  ┌─ METRICS")
    print(f"  │  {'Metric':<25} {'Ungrounded':>12} {'Grounded':>12} {'Delta':>8}")
    print(f"  │  {'─'*25} {'─'*12} {'─'*12} {'─'*8}")
    print(f"  │  {'Words':<25} {r['u_words']:>12} {r['g_words']:>12} {r['g_words']-r['u_words']:>+8}")
    print(f"  │  {'Hedging phrases':<25} {r['u_hedges']:>12} {r['g_hedges']:>12} {r['g_hedges']-r['u_hedges']:>+8}")
    print(f"  │  {'Generic AI phrases':<25} {r['u_generic']:>12} {r['g_generic']:>12} {r['g_generic']-r['u_generic']:>+8}")

    # Hedge density
    u_hd = (r["u_hedges"] / r["u_words"] * 100) if r["u_words"] else 0
    g_hd = (r["g_hedges"] / r["g_words"] * 100) if r["g_words"] else 0
    print(f"  │  {'Hedge density (/100w)':<25} {u_hd:>11.2f}% {g_hd:>11.2f}% {g_hd-u_hd:>+7.2f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Before/after grounding comparison demo"
    )
    parser.add_argument("--core", help="Path to CORE.md (default: examples/sample_grounded.md)")
    parser.add_argument("--grounding", help="Path to grounding.md")
    parser.add_argument("--prompt", help="Custom test prompt (can specify multiple)", action="append")
    parser.add_argument("--all", action="store_true", help="Run all built-in prompts")
    args = parser.parse_args()

    # Load grounding context
    script_dir = Path(__file__).parent.parent
    core_path = args.core or script_dir / "examples" / "sample_grounded.md"
    core_text = Path(core_path).read_text(encoding="utf-8")

    grounding_text = ""
    if args.grounding:
        grounding_text = "\n\n" + Path(args.grounding).read_text(encoding="utf-8")

    grounded_system = core_text + grounding_text

    # Select prompts
    if args.prompt:
        prompts = args.prompt
    elif args.all:
        prompts = DEFAULT_PROMPTS
    else:
        prompts = [DEFAULT_PROMPTS[0]]

    # Connect to LLM
    client = get_client()
    if not client.is_reachable():
        print("ERROR: Cannot reach LLM API. Start LM Studio or set PERSISTENCE_LLM_URL.")
        print("  Default: http://localhost:1234/v1")
        sys.exit(1)

    print("=" * 60)
    print("  Grounding Demo — Before/After Comparison")
    print("=" * 60)
    print(f"  Core context: {core_path} ({len(core_text)} chars)")
    print(f"  LLM: {client.api_url}")
    print(f"  Prompts: {len(prompts)}")

    results = []
    for prompt in prompts:
        r = run_comparison(client, prompt, grounded_system, UNGROUNDED_SYSTEM)
        if r:
            results.append(r)
            print_result(r)

    # Summary
    if len(results) > 1:
        print(f"\n{'=' * 60}")
        print("  Summary Across All Prompts")
        print(f"{'=' * 60}")
        total_u_h = sum(r["u_hedges"] for r in results)
        total_g_h = sum(r["g_hedges"] for r in results)
        total_u_g = sum(r["u_generic"] for r in results)
        total_g_g = sum(r["g_generic"] for r in results)
        print(f"  Total hedging:  Ungrounded={total_u_h}  Grounded={total_g_h}")
        print(f"  Total generic:  Ungrounded={total_u_g}  Grounded={total_g_g}")
        if total_u_h > total_g_h:
            pct = ((total_u_h - total_g_h) / total_u_h) * 100
            print(f"  Grounding reduced hedging by {pct:.0f}%")

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
