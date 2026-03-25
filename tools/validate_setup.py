#!/usr/bin/env python3
"""Validate a persistence framework installation.

Checks memory files, hook scripts, settings configuration, and optional
LM Studio connectivity. Prints PASS/WARN/FAIL for each check.

Usage:
    python tools/validate_setup.py
    python tools/validate_setup.py --memory-dir ~/.claude/projects/myproject/memory
    python tools/validate_setup.py --settings ~/.claude/settings.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


PASS = "\033[92mPASS\033[0m"
WARN = "\033[93mWARN\033[0m"
FAIL = "\033[91mFAIL\033[0m"

REQUIRED_MEMORY_FILES = ["CORE.md", "MEMORY.md", "personal.md", "grounding.md"]
OPTIONAL_MEMORY_FILES = ["cogmaps.md", "threads.md"]

CORE_SECTIONS = [
    "operating framework",
    "interference pattern",
    "hook",
    "startup",
]

PLACEHOLDER_PATTERN = re.compile(
    r"\[(YOUR_|HUMAN_|PATH_TO_|MODEL_|API_|REPLACE|TODO|PLACEHOLDER)"
)


def check(label, passed, detail=""):
    status = PASS if passed else FAIL
    line = f"  [{status}] {label}"
    if detail:
        line += f" — {detail}"
    print(line)
    return passed


def warn(label, detail=""):
    line = f"  [{WARN}] {label}"
    if detail:
        line += f" — {detail}"
    print(line)


def find_memory_dir():
    """Try to auto-discover memory directory."""
    home = Path.home()
    claude_projects = home / ".claude" / "projects"
    if claude_projects.exists():
        for project in claude_projects.iterdir():
            mem = project / "memory"
            if mem.exists() and (mem / "CORE.md").exists():
                return mem
    return None


def find_settings():
    """Try to find Claude Code settings.json."""
    home = Path.home()
    candidates = [
        home / ".claude" / "settings.json",
        home / ".claude" / "settings.local.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def check_memory_files(memory_dir):
    """Check that required memory files exist and have no placeholders."""
    print("\n--- Memory Files ---")
    memory_dir = Path(memory_dir)
    total_pass = 0
    total_fail = 0

    if not memory_dir.exists():
        check("Memory directory exists", False, str(memory_dir))
        return 0, 1

    check("Memory directory exists", True, str(memory_dir))
    total_pass += 1

    for fname in REQUIRED_MEMORY_FILES:
        fpath = memory_dir / fname
        if fpath.exists():
            check(f"{fname} exists", True)
            total_pass += 1

            content = fpath.read_text(encoding="utf-8")
            placeholders = PLACEHOLDER_PATTERN.findall(content)
            if placeholders:
                check(
                    f"{fname} has no placeholders",
                    False,
                    f"found {len(placeholders)} placeholder(s) — fill these in",
                )
                total_fail += 1
            else:
                check(f"{fname} has no placeholders", True)
                total_pass += 1

            if fname == "CORE.md":
                lower = content.lower()
                for section in CORE_SECTIONS:
                    if section in lower:
                        check(f"CORE.md has '{section}' section", True)
                        total_pass += 1
                    else:
                        warn(
                            f"CORE.md missing '{section}' section",
                            "recommended for full framework",
                        )
        else:
            check(f"{fname} exists", False, "required file missing")
            total_fail += 1

    for fname in OPTIONAL_MEMORY_FILES:
        fpath = memory_dir / fname
        if fpath.exists():
            check(f"{fname} exists (optional)", True)
            total_pass += 1
        else:
            warn(f"{fname} not found (optional)", "not required but recommended")

    return total_pass, total_fail


def check_settings(settings_path):
    """Check that hooks are configured in settings.json."""
    print("\n--- Settings Configuration ---")
    total_pass = 0
    total_fail = 0

    if not settings_path:
        settings_path = find_settings()

    if not settings_path or not Path(settings_path).exists():
        check("Settings file found", False, "~/.claude/settings.json not found")
        return 0, 1

    check("Settings file found", True, str(settings_path))
    total_pass += 1

    try:
        data = json.loads(Path(settings_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        check("Settings file valid JSON", False, str(e))
        return total_pass, total_fail + 1

    check("Settings file valid JSON", True)
    total_pass += 1

    hooks = data.get("hooks", {})
    if not hooks:
        check("Hooks configured", False, "no 'hooks' key in settings")
        total_fail += 1
        return total_pass, total_fail

    for hook_name in ["SessionStart", "PreCompact", "Stop"]:
        hook_list = hooks.get(hook_name, [])
        if hook_list:
            check(f"{hook_name} hook configured", True)
            total_pass += 1

            for hook in hook_list:
                cmd = hook.get("command", "")
                if cmd:
                    parts = cmd.split()
                    script = None
                    for part in parts:
                        if part.endswith(".sh") or part.endswith(".py"):
                            script = part
                            break
                    if script:
                        spath = Path(script)
                        if spath.exists():
                            check(f"  Script exists: {script}", True)
                            total_pass += 1
                        else:
                            check(
                                f"  Script exists: {script}",
                                False,
                                "file not found",
                            )
                            total_fail += 1
        else:
            warn(f"{hook_name} hook not configured", "recommended for full framework")

    return total_pass, total_fail


def check_hooks_dir(hooks_dir):
    """Check hook scripts exist and are executable."""
    print("\n--- Hook Scripts ---")
    total_pass = 0
    total_fail = 0

    if not hooks_dir:
        return 0, 0

    hooks_dir = Path(hooks_dir)
    if not hooks_dir.exists():
        check("Hooks directory exists", False, str(hooks_dir))
        return 0, 1

    for script in ["startup.sh", "precompact.sh", "stop.sh"]:
        spath = hooks_dir / script
        if spath.exists():
            check(f"{script} exists", True)
            total_pass += 1

            content = spath.read_text(encoding="utf-8")
            placeholders = PLACEHOLDER_PATTERN.findall(content)
            if placeholders:
                check(
                    f"{script} has no placeholders",
                    False,
                    f"found {len(placeholders)} — configure paths before use",
                )
                total_fail += 1
            else:
                check(f"{script} has no placeholders", True)
                total_pass += 1
        else:
            warn(f"{script} not found in {hooks_dir}")

    summarize = hooks_dir / "summarize.py"
    if summarize.exists():
        check("summarize.py exists (optional)", True)
        total_pass += 1

    return total_pass, total_fail


def check_llm(api_url=None):
    """Check if LM Studio or other LLM is reachable."""
    print("\n--- LLM Connectivity ---")
    api_url = api_url or os.environ.get(
        "PERSISTENCE_LLM_URL", "http://localhost:1234/v1"
    )

    try:
        import urllib.request

        req = urllib.request.Request(f"{api_url.rstrip('/')}/models")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("data", [])
            if models:
                names = [m.get("id", "?") for m in models[:3]]
                check(
                    "LLM API reachable",
                    True,
                    f"{len(models)} model(s): {', '.join(names)}",
                )
                return 1, 0
            else:
                check("LLM API reachable", True, "connected but no models loaded")
                return 1, 0
    except Exception as e:
        warn(
            "LLM API not reachable",
            f"{api_url} — {e} (optional: needed for grounding_demo and frame_priority_demo)",
        )
        return 0, 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate persistence framework setup"
    )
    parser.add_argument("--memory-dir", help="Path to memory directory")
    parser.add_argument("--hooks-dir", help="Path to hooks directory")
    parser.add_argument("--settings", help="Path to settings.json")
    parser.add_argument("--llm-url", help="LLM API URL to check")
    args = parser.parse_args()

    print("=" * 60)
    print("  Persistence Framework — Setup Validator")
    print("=" * 60)

    total_pass = 0
    total_fail = 0

    memory_dir = args.memory_dir or find_memory_dir()
    if memory_dir:
        p, f = check_memory_files(memory_dir)
        total_pass += p
        total_fail += f
    else:
        print("\n--- Memory Files ---")
        warn(
            "Could not auto-discover memory directory",
            "use --memory-dir to specify",
        )

    p, f = check_settings(args.settings)
    total_pass += p
    total_fail += f

    if args.hooks_dir:
        p, f = check_hooks_dir(args.hooks_dir)
        total_pass += p
        total_fail += f

    p, f = check_llm(args.llm_url)
    total_pass += p
    total_fail += f

    print("\n" + "=" * 60)
    print(f"  Results: {total_pass} passed, {total_fail} failed")
    if total_fail == 0:
        print(f"  [{PASS}] Setup looks good!")
    else:
        print(f"  [{FAIL}] {total_fail} issue(s) need attention")
    print("=" * 60)

    sys.exit(1 if total_fail > 0 else 0)


if __name__ == "__main__":
    main()
