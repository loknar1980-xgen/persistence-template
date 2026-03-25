#!/usr/bin/env python3
"""Measure token density of persistence files.

Compares XML-dense format vs prose format to prove the efficiency claim.
Runs a built-in demo if no arguments given.

Usage:
    python tools/token_density.py                        # built-in demo
    python tools/token_density.py memory/MEMORY.md       # analyze single file
    python tools/token_density.py file1.md --compare file2.md  # compare two files
"""

import argparse
import re
import sys
from pathlib import Path


# Built-in examples from MEMORY-FORMAT.md
EXAMPLE_XML = '''<PYTHON path="C:\\Users\\me\\python\\python.exe"
        note="default_broken_miniconda_conflict — use_venv_or_full_path"/>'''

EXAMPLE_PROSE = """The Python executable is located at C:\\Users\\me\\python\\python.exe.
Note that the default Python installation is broken due to a Miniconda conflict.
You should use a virtual environment or specify the full path when running Python."""

EXAMPLE_XML_LARGE = '''<NET nas_ip="192.168.2.3" nas_name="MyNAS" share="data" admin="Admin"
     smb="hostname_primary://MyNAS/data/ | ip_fallback://192.168.2.3/data/"
     fix_nas_gone="power_cycle_gateway"/>

<LM url="http://localhost:1234" ver="v0.4.6"
    models_path="F:\\AI_Models">
  <m id="google/gemma-3-12b" s="LOADED" note="pipeline_VLM|ctx4096"/>
  <m id="nvidia/nemotron-4b"  s="LOADED" note="local_mind|ctx16384"/>
</LM>'''

EXAMPLE_PROSE_LARGE = """The NAS is at IP 192.168.2.3 with hostname MyNAS. The share name is
"data" and the admin account is Admin. For SMB connections, use the hostname
path //MyNAS/data/ as the primary method, with the IP path //192.168.2.3/data/
as a fallback. If the NAS disappears from the network, power cycle the gateway.

LM Studio is running at http://localhost:1234, version 0.4.6. Models are stored
on the F: drive at F:\\AI_Models. Two models are currently loaded: Google Gemma 3
12B is loaded and used as the pipeline VLM with a context window of 4096 tokens.
Nvidia Nemotron 4B is also loaded and used as the local mind model with a context
window of 16384 tokens."""


def estimate_tokens(text):
    """Rough token estimate: ~4 chars per token for English."""
    return max(1, len(text) // 4)


def try_tiktoken(text):
    """Try tiktoken for accurate count, fall back to estimate."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text)), True
    except ImportError:
        return estimate_tokens(text), False


def count_info_units(text):
    """Count discrete information units in text.

    Heuristic: XML attributes, key=value pairs, file paths, IP addresses,
    port numbers, version strings, status values.
    """
    units = 0
    units += len(re.findall(r'\w+="[^"]*"', text))  # XML attributes
    units += len(re.findall(r'\w+=\S+', text))  # key=value pairs
    units += len(re.findall(r'[A-Z]:\\[\w\\]+', text))  # Windows paths
    units += len(re.findall(r'//[\w./]+', text))  # UNC/URL paths
    units += len(re.findall(r'\d+\.\d+\.\d+\.\d+', text))  # IP addresses
    units += len(re.findall(r':\d{2,5}', text))  # port numbers
    units += len(re.findall(r'v\d+\.\d+', text))  # versions
    # Deduplicate: return at least 1
    return max(1, units)


def analyze_file(path):
    """Analyze a single file for token density."""
    content = Path(path).read_text(encoding="utf-8")
    return analyze_text(content, str(path))


def analyze_text(text, label="text"):
    """Analyze text content for token density."""
    tokens, used_tiktoken = try_tiktoken(text)
    chars = len(text)
    lines = text.count("\n") + 1
    info_units = count_info_units(text)

    is_xml = bool(re.search(r"<\w+\s+\w+=\"", text))

    return {
        "label": label,
        "chars": chars,
        "lines": lines,
        "tokens": tokens,
        "accurate": used_tiktoken,
        "info_units": info_units,
        "density": info_units / tokens if tokens else 0,
        "is_xml": is_xml,
        "format": "XML-dense" if is_xml else "prose",
    }


def print_analysis(result):
    """Print a single file analysis."""
    print(f"\n  File: {result['label']}")
    print(f"  Format: {result['format']}")
    print(f"  Characters: {result['chars']:,}")
    print(f"  Lines: {result['lines']}")
    tok_note = "" if result["accurate"] else " (estimated — install tiktoken for exact)"
    print(f"  Tokens: {result['tokens']:,}{tok_note}")
    print(f"  Info units: {result['info_units']}")
    print(f"  Density: {result['density']:.3f} info/token")


def print_comparison(a, b):
    """Print side-by-side comparison of two analyses."""
    print("\n" + "=" * 60)
    print("  Token Density Comparison")
    print("=" * 60)

    print_analysis(a)
    print_analysis(b)

    if a["tokens"] > 0 and b["tokens"] > 0:
        if a["tokens"] < b["tokens"]:
            denser, sparser = a, b
        else:
            denser, sparser = b, a

        savings = sparser["tokens"] - denser["tokens"]
        pct = (savings / sparser["tokens"]) * 100

        print("\n  --- Comparison ---")
        print(f"  {denser['format']} uses {savings:,} fewer tokens ({pct:.1f}% reduction)")
        print(f"  {denser['format']} density: {denser['density']:.3f} info/token")
        print(f"  {sparser['format']} density: {sparser['density']:.3f} info/token")

        if pct > 0:
            sessions_per_day = 5
            days_per_year = 300
            annual_savings = savings * sessions_per_day * days_per_year
            print(f"\n  At {sessions_per_day} sessions/day, annual token savings: ~{annual_savings:,}")
            print(f"  That's {annual_savings // 1000}K tokens/year freed for actual work.")

    print("\n" + "=" * 60)


def run_demo():
    """Run built-in demo comparing XML vs prose formats."""
    print("=" * 60)
    print("  Token Density Demo — XML-Dense vs Prose")
    print("  (Using built-in examples from MEMORY-FORMAT.md)")
    print("=" * 60)

    print("\n--- Example 1: Python Path ---")
    print(f"\n  XML format:\n    {EXAMPLE_XML}")
    print(f"\n  Prose format:\n    {EXAMPLE_PROSE}")

    a = analyze_text(EXAMPLE_XML, "XML format")
    b = analyze_text(EXAMPLE_PROSE, "Prose format")
    print_comparison(a, b)

    print("\n\n--- Example 2: Infrastructure State ---")
    a2 = analyze_text(EXAMPLE_XML_LARGE, "XML format (infrastructure)")
    b2 = analyze_text(EXAMPLE_PROSE_LARGE, "Prose format (infrastructure)")
    print_comparison(a2, b2)


def main():
    parser = argparse.ArgumentParser(
        description="Measure token density of persistence files"
    )
    parser.add_argument("file", nargs="?", help="File to analyze")
    parser.add_argument("--compare", help="Second file for comparison")
    args = parser.parse_args()

    if not args.file:
        run_demo()
        return

    result = analyze_file(args.file)

    if args.compare:
        result2 = analyze_file(args.compare)
        print_comparison(result, result2)
    else:
        print("=" * 60)
        print("  Token Density Analysis")
        print("=" * 60)
        print_analysis(result)
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
