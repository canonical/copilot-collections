#!/usr/bin/env python3
"""Generate deterministic final-round session statistics for consensus review.

Implements the Session statistics block from
`references/phase-4c-output-formats.md` §Final Round Rules.

The statistics are derived from the workdir file listing, whitespace-split word
counts, and anchored `Resolution:` line counts. The spec says not to reopen files
for content reads; that forbids semantic review of consolidated/resolutions/review
artifacts. Word counting and anchored decision counting are explicitly sanctioned,
so this script implements those operations directly in Python rather than shelling
out to `wc` or `grep`.

Dot-prefixed files are excluded as temporary scaffolding, and files ending
`.partial` are excluded as recovery artifacts. `review-history.md` is a normal
artifact and counts. Word counts use the skill's convention elsewhere:
`text.split()` whitespace tokens.

This script does NOT compute findings by severity, BLOCKER trend, or convergence
history; those require semantic content reads and stay with the orchestrator.

Output format (--json):
  {
    "workdir": "...",
    "counts": {
      "completed_non_final_rounds": N,
      "artifacts_generated": {"total_files": N, "review_files": M},
      "total_workdir_words": N,
      "model_slugs": {
        "distinct_count": N,
        "slugs": [...],
        "caveat": "Alias-style names such as ..."
      },
      "plan_version_span": {"first": N, "final": M} | null,
      "tech_lead_decisions": {"ACCEPT": N, "MODIFY": M, "REJECT": K}
    },
    "final_plan": {"path": "...", "found": true, "words": N, "lines": M}
                  | {"path": "...", "found": false}
                  | null
  }

Usage:
    python3 session_stats.py <workdir>
    python3 session_stats.py <workdir> <final-plan-path>
    python3 session_stats.py <workdir> --plan <final-plan-path> --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REVIEW_FILE_RE = re.compile(r"^(.+)-(blue|red|purple)-v(\d+)\.md$")
CONSOLIDATED_RE = re.compile(r"^consolidated-v(\d+)\.md$")
RESOLUTIONS_RE = re.compile(r"^resolutions-v(\d+)\.md$")
DECISION_RE = re.compile(r"^Resolution:\s*(ACCEPT|MODIFY|REJECT)\s*$")

MODEL_SLUG_CAVEAT = (
    "Alias-style names such as `claude-opus-latest` inflate this distinct-slug "
    "count above the number of distinct real models."
)


def is_counted_file(path: Path) -> bool:
    """Return whether a direct workdir file participates in session stats."""
    return path.is_file() and not path.name.startswith(".") and not path.name.endswith(".partial")


def list_counted_files(workdir: Path) -> list[Path]:
    return sorted((p for p in workdir.iterdir() if is_counted_file(p)), key=lambda p: p.name)


def count_words(text: str) -> int:
    return len(text.split())


def count_lines(text: str) -> int:
    return len(text.splitlines())


def file_word_count(path: Path) -> int:
    return count_words(path.read_text())


def total_word_count(paths: list[Path]) -> int:
    return sum(file_word_count(path) for path in paths)


def review_files(paths: list[Path]) -> list[Path]:
    return [path for path in paths if REVIEW_FILE_RE.match(path.name)]


def model_slugs(paths: list[Path]) -> list[str]:
    slugs = set()
    for path in review_files(paths):
        match = REVIEW_FILE_RE.match(path.name)
        if match:
            slugs.add(match.group(1))
    return sorted(slugs)


def version_numbers(paths: list[Path]) -> list[int]:
    versions: list[int] = []
    for path in paths:
        for regex in (CONSOLIDATED_RE, RESOLUTIONS_RE):
            match = regex.match(path.name)
            if match:
                versions.append(int(match.group(1)))
                break
    return versions


def plan_version_span(paths: list[Path]) -> dict | None:
    versions = version_numbers(paths)
    if not versions:
        return None
    return {"first": min(versions), "final": max(versions)}


def count_completed_non_final_rounds(paths: list[Path]) -> int:
    return sum(1 for path in paths if CONSOLIDATED_RE.match(path.name))


def count_decisions(paths: list[Path]) -> dict:
    counts = {"ACCEPT": 0, "MODIFY": 0, "REJECT": 0}
    for path in paths:
        if not RESOLUTIONS_RE.match(path.name):
            continue
        for line in path.read_text().splitlines():
            match = DECISION_RE.match(line)
            if match:
                counts[match.group(1)] += 1
    return counts


def final_plan_stats(plan_path: Path | None) -> dict | None:
    if plan_path is None:
        return None
    if not plan_path.is_file():
        return {"path": str(plan_path), "found": False}

    text = plan_path.read_text()
    return {
        "path": str(plan_path),
        "found": True,
        "words": count_words(text),
        "lines": count_lines(text),
    }


def collect_stats(workdir: Path, plan_path: Path | None = None) -> dict:
    paths = list_counted_files(workdir)
    reviews = review_files(paths)
    slugs = model_slugs(paths)
    return {
        "workdir": str(workdir),
        "counts": {
            "completed_non_final_rounds": count_completed_non_final_rounds(paths),
            "artifacts_generated": {
                "total_files": len(paths),
                "review_files": len(reviews),
            },
            "total_workdir_words": total_word_count(paths),
            "model_slugs": {
                "distinct_count": len(slugs),
                "slugs": slugs,
                "caveat": MODEL_SLUG_CAVEAT,
            },
            "plan_version_span": plan_version_span(paths),
            "tech_lead_decisions": count_decisions(paths),
        },
        "final_plan": final_plan_stats(plan_path),
    }


def format_span(span: dict | None) -> str:
    if span is None:
        return "none"
    return f"v{span['first']} to v{span['final']}"


def print_report(report: dict) -> None:
    counts = report["counts"]
    artifacts = counts["artifacts_generated"]
    slugs = counts["model_slugs"]
    decisions = counts["tech_lead_decisions"]

    print(f"Workdir: {report['workdir']}")
    print(f"Completed non-final rounds: {counts['completed_non_final_rounds']}")
    print(
        f"Artifacts generated: {artifacts['total_files']} files, "
        f"{artifacts['review_files']} review files"
    )
    print(f"Total workdir size: {counts['total_workdir_words']} words")
    print(f"Model slugs used: {slugs['distinct_count']} distinct")
    print(f"Model-slug caveat: {slugs['caveat']}")
    print(f"Plan version span: {format_span(counts['plan_version_span'])}")

    plan = report["final_plan"]
    if plan and plan.get("found"):
        print(f"Final plan size: {plan['words']} words, {plan['lines']} lines")
    elif plan:
        print(f"Final plan size: unavailable (plan not found: {plan['path']})")

    print(
        "Tech-lead decisions: "
        f"ACCEPT {decisions['ACCEPT']}, MODIFY {decisions['MODIFY']}, REJECT {decisions['REJECT']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("workdir", type=Path, help="Consensus review workdir")
    parser.add_argument("plan_arg", nargs="?", type=Path, help="Optional final plan path")
    parser.add_argument("--plan", type=Path, default=None, help="Optional final plan path")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    args = parser.parse_args()

    if not args.workdir.is_dir():
        print(f"error: workdir not found: {args.workdir}", file=sys.stderr)
        return 3
    if args.plan_arg and args.plan:
        print("error: final plan path supplied twice", file=sys.stderr)
        return 3

    report = collect_stats(args.workdir, args.plan or args.plan_arg)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
