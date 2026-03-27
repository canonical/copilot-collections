#!/usr/bin/env python3
"""Detect Harness-based unit tests that still need migration."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Iterable, Sequence

HARNESS_PATTERNS = [
    r"\btesting\.Harness\b",
    r"\bops\.testing\.Harness\b",
    r"\bHarness\(",
    r"\btesting\.Scenario\b",
    r"\bScenario\(",
]


def iter_python_files(paths: Sequence[str], extensions: Sequence[str]) -> Iterable[Path]:
    for raw in paths:
        base = Path(raw)
        if not base.exists():
            continue
        if base.is_file() and base.suffix in extensions:
            yield base
            continue
        if base.is_dir():
            for candidate in base.rglob("*"):
                if candidate.suffix in extensions and candidate.is_file():
                    yield candidate


def scan_file(path: Path, regexes: Sequence[re.Pattern[str]]) -> list[tuple[int, str]]:
    matches: list[tuple[int, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                if any(regex.search(line) for regex in regexes):
                    matches.append((line_no, line.rstrip()))
    except OSError as exc:
        print(f"⚠️  Skipping {path}: {exc}", file=sys.stderr)
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description="Report files that still rely on ops.testing.Harness")
    parser.add_argument(
        "paths",
        nargs="*",
        default=["tests"],
        help="Directories or files to scan (default: tests)",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=[".py"],
        help="File extensions to include (default: .py)",
    )
    args = parser.parse_args()

    regexes = [re.compile(pattern) for pattern in HARNESS_PATTERNS]
    total_matches = 0

    for file_path in sorted(set(iter_python_files(args.paths, args.extensions))):
        hits = scan_file(file_path, regexes)
        if not hits:
            continue
        total_matches += len(hits)
        print(f"\n{file_path}")
        for line_no, line in hits:
            print(f"  {line_no:>5}: {line}")

    if total_matches == 0:
        print("✅ No Harness usages found. Ready to enforce state-transition tests.")
    else:
        print(f"\nFound {total_matches} Harness-style references. Migrate these suites next.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
