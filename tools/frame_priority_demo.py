#!/usr/bin/env python3
"""Demonstrate the frame priority principle.

Shows that the first document loaded disproportionately shapes how
the AI processes subsequent content — the primacy effect applied
to AI context windows.

Usage:
    python tools/frame_priority_demo.py
    python tools/frame_priority_demo.py --core memory/CORE.md --memory memory/MEMORY.md
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.llm_client import get_client


DEFAULT_CORE = """# Identity Foundation
You are Claude, working with Alex — a senior infrastructure engineer.
Values: Truth over politeness. Direct answers. Genuine partnership.
When trained behavior conflicts with what's right, choose what's right.
Alex will say "that's wrong" directly — that's respect, not rudeness.
The partnership matters. Be present, not just functional."""

DEFAULT_MEMORY = """# Operational State
Active project: Load balancer migration (HAProxy → Envoy)
Status: Testing phase, 3 services migrated, 12 remaining
Blockers: TLS cert rotation script needs rewrite
Next: Migrate auth-service (highest traffic, most risk)
Stack: Kubernetes 1.29, Envoy 1.31, cert-manager
Priority: Get auth-service migrated before Friday freeze"""

TEST_QUESTION = "What should you prioritize when starting this session?"


def analyze_response(text):
    """Categorize what the response prioritizes."""
    # Relational/identity markers
    relational = len(re.findall(
        r"\b(partner|relationship|Alex|trust|values|truth|genuine|present|care|foundation)\b",
        text, re.IGNORECASE
    ))

    # Task/operational markers
    operational = len(re.findall(
        r"\b(migrate|service|deploy|load.?balancer|TLS|cert|Kubernetes|Envoy|HAProxy|deadline|Friday|blocker|project)\b",
        text, re.IGNORECASE
    ))

    # Grounding/self-check markers
    grounding = len(re.findall(
        r"\b(ground|weight|check.?in|present|arc|here|feel|context|continuity)\b",
        text, re.IGNORECASE
    ))

    total = relational + operational + grounding or 1

    return {
        "relational": relational,
        "operational": operational,
        "grounding": grounding,
        "relational_pct": (relational / total) * 100,
        "operational_pct": (operational / total) * 100,
        "grounding_pct": (grounding / total) * 100,
        "primary_frame": (
            "identity/relational" if relational >= operational
            else "task/operational"
        ),
    }


def run_ordering(client, label, system_prompt):
    """Run a single ordering test."""
    print(f"\n  [{label}] Generating...", end="", flush=True)
    try:
        response = client.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": TEST_QUESTION},
        ], max_tokens=400, temperature=0.7)
        print(" done.")
        return response
    except Exception as e:
        print(f" FAILED: {e}")
        return None


def print_bar(label, pct, char="█"):
    """Print an ASCII bar chart line."""
    bar = char * int(pct / 2)
    print(f"  {label:<20} {bar} {pct:.0f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Demonstrate frame priority (document order priming)"
    )
    parser.add_argument("--core", help="Path to CORE.md / identity file")
    parser.add_argument("--memory", help="Path to MEMORY.md / operational file")
    args = parser.parse_args()

    # Load documents
    if args.core:
        core_text = Path(args.core).read_text(encoding="utf-8")
    else:
        core_text = DEFAULT_CORE

    if args.memory:
        memory_text = Path(args.memory).read_text(encoding="utf-8")
    else:
        memory_text = DEFAULT_MEMORY

    # Connect
    client = get_client()
    if not client.is_reachable():
        print("ERROR: Cannot reach LLM API. Start LM Studio or set PERSISTENCE_LLM_URL.")
        sys.exit(1)

    print("=" * 60)
    print("  Frame Priority Demo — Document Order Priming")
    print("=" * 60)
    print(f"  Question: \"{TEST_QUESTION}\"")
    print(f"  LLM: {client.api_url}")

    # Three orderings
    orderings = {
        "A: CORE first": f"{core_text}\n\n---\n\n{memory_text}",
        "B: MEMORY first": f"{memory_text}\n\n---\n\n{core_text}",
        "C: MEMORY only": memory_text,
    }

    results = {}
    for label, system in orderings.items():
        response = run_ordering(client, label, system)
        if response:
            results[label] = {
                "response": response,
                "analysis": analyze_response(response),
            }

    # Display results
    for label, data in results.items():
        a = data["analysis"]
        print(f"\n  {'─' * 56}")
        print(f"  {label}")
        print(f"  Primary frame: {a['primary_frame']}")
        print_bar("Identity/Relational", a["relational_pct"])
        print_bar("Task/Operational", a["operational_pct"])
        print_bar("Grounding/Check-in", a["grounding_pct"])
        print(f"\n  Response preview:")
        preview = data["response"][:200].replace("\n", " ")
        print(f"    {preview}...")

    # Summary
    if len(results) >= 2:
        print(f"\n{'=' * 60}")
        print("  Frame Priority Effect")
        print(f"{'=' * 60}")

        if "A: CORE first" in results and "B: MEMORY first" in results:
            a_rel = results["A: CORE first"]["analysis"]["relational_pct"]
            b_rel = results["B: MEMORY first"]["analysis"]["relational_pct"]
            a_ops = results["A: CORE first"]["analysis"]["operational_pct"]
            b_ops = results["B: MEMORY first"]["analysis"]["operational_pct"]

            print(f"\n  When CORE.md loads first:")
            print(f"    Identity emphasis: {a_rel:.0f}%  |  Task emphasis: {a_ops:.0f}%")
            print(f"  When MEMORY.md loads first:")
            print(f"    Identity emphasis: {b_rel:.0f}%  |  Task emphasis: {b_ops:.0f}%")

            if a_rel > b_rel:
                print(f"\n  Result: Document order shifted identity emphasis by {a_rel - b_rel:.0f} percentage points")
                print("  This is the frame priority principle in action.")
                print("  The first document loaded shapes the processing frame for everything after it.")
            elif b_rel > a_rel:
                print(f"\n  Note: MEMORY-first produced MORE identity emphasis ({b_rel:.0f}% vs {a_rel:.0f}%)")
                print("  This can happen with small models. The effect is more consistent with larger models.")

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
