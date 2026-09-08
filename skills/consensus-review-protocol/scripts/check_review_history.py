#!/usr/bin/env python3
"""Deterministic conformance checker for consensus-review-protocol review-history.md.

Checks the mechanical parts of SKILL.md §Iterative Protocol:

  - the Review History file header exists (`# Review History`, descriptive text,
    first `---` separator) and contains no `### ` entry heading before that separator;
  - entries are bounded by `### ` headings;
  - entry headings match `### <plan-file>.md — <ISO date>`;
  - every strictly validated entry carries the required non-conditional lines;
  - any Supersession note that exists is immediately after `**Models:**`;
  - entries are newest-first.

Entries predating the current format are historical record and are not rewritten.
For that reason, strict format checks default to `--recent 5`, matching SKILL.md's
Phase 4a/4c default read window for review history. Older entries are not ignored:
the same format drift is reported under non-blocking `legacy_entry_format_advisory`
so the orchestrator can see it without turning preserved history into a hard fail.
Use `--recent 0` to make every entry advisory, or a large value to validate all
entries strictly.

Ordering uses the round number from the required `**Round N reviewing plan v<M>**`
line when both adjacent entries expose one, because dates are day-granular and
same-day entries are legitimate. If either side lacks a round number, the checker
falls back to the ISO date in the entry heading. Equal dates do not fail.

This script does NOT decide whether a Supersession note is required; that depends
on reading the loaded resolutions file's `Direct Companion File Edits Since Last
Round` answer and remains with the orchestrator. It also does not decide whether
a `**Sub-agent failures:**` line is factually required, because clean rounds omit
it and detecting failed-all-retries requires run context not present in this file.
Description text is checked for presence, not for whether it names the plan.

Output format (--json):
  {
    "path": "...",
    "counts": {"entries": N, "strict_entries": M, "legacy_entries": K},
    "result": "pass" | "needs_review" | "fail",
    "checks": {
      "<check_name>": {"blocking": bool, "ok": bool, "failed": [...]}
    }
  }

`result` is derived from `checks`, not stored independently:
  - "fail"         - any blocking check has ok == false.
  - "needs_review" - no blocking failures, but a non-blocking check has ok == false.
  - "pass"         - every check ok == true.

Exit status mirrors `result`: pass -> 0, fail -> 1, needs_review -> 2.
File-not-found or usage errors -> 3.

Usage:
    python3 check_review_history.py <workdir>/review-history.md
    python3 check_review_history.py <path> --json
    python3 check_review_history.py <path> --recent 10
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADER_TITLE = "# Review History"
SEPARATOR = "---"

ENTRY_START_RE = re.compile(r"^###\s+(.*?)\s*$")
ENTRY_HEADING_RE = re.compile(r"^###\s+(.+\.md)\s+—\s+(\d{4}-\d{2}-\d{2})\s*$")
ROUND_LINE_RE = re.compile(
    r"^\*\*Round\s+(\d+)\s+reviewing plan v(\d+)(?:[^*]*)\*\*\s+\|\s+"
    r"Input:\s+.+\|\s+Output:\s+.+\|\s+Resolutions applied from:\s+.+$"
)
ROUND_NUMBER_RE = re.compile(r"\*\*Round\s+(\d+)\s+reviewing plan v\d+")
KEY_CHANGES_RE = re.compile(r"^\*\*Key changes from v\d+:\*\*\s*$")
PHASE_4B_SKIPS_RE = re.compile(r"^\*\*Round\s+\d+\s+Phase 4b skips:\*\*")


class Entry:
    __slots__ = ("index", "heading_line", "heading", "body_lines", "date", "round_number")

    def __init__(self, index: int, heading_line: str, body_lines: list[str]):
        self.index = index
        self.heading_line = heading_line
        heading_match = ENTRY_START_RE.match(heading_line)
        self.heading = heading_match.group(1).strip() if heading_match else f"entry_{index}"
        self.body_lines = body_lines

        valid_heading = ENTRY_HEADING_RE.match(heading_line)
        self.date = valid_heading.group(2) if valid_heading else None
        self.round_number = extract_round_number(body_lines)

    @property
    def id(self) -> str:
        return self.heading or f"entry_{self.index}"


def new_check(blocking: bool) -> dict:
    return {"blocking": blocking, "ok": True, "failed": []}


def derive_result(checks: dict) -> str:
    if any(c["blocking"] and not c["ok"] for c in checks.values()):
        return "fail"
    if any(not c["blocking"] and not c["ok"] for c in checks.values()):
        return "needs_review"
    return "pass"


def extract_round_number(lines: list[str]) -> int | None:
    for line in lines:
        match = ROUND_NUMBER_RE.search(line)
        if match:
            return int(match.group(1))
    return None


def parse_review_history(text: str) -> tuple[list[str], list[Entry]]:
    """Return header lines through the first separator and all `### ` entries."""
    lines = text.splitlines()
    header_end = None
    for index, line in enumerate(lines):
        if line.strip() == SEPARATOR:
            header_end = index
            break

    body_start = header_end + 1 if header_end is not None else 0
    header_lines = lines[:body_start] if header_end is not None else lines[:]

    entries: list[Entry] = []
    current_heading = None
    current_lines: list[str] = []

    def flush():
        if current_heading is not None:
            entries.append(Entry(len(entries) + 1, current_heading, current_lines))

    for line in lines[body_start:]:
        if ENTRY_START_RE.match(line):
            flush()
            current_heading = line
            current_lines = []
        else:
            current_lines.append(line)
    flush()

    return header_lines, entries


def header_failures(header_lines: list[str]) -> list[str]:
    failed: list[str] = []
    stripped = [line.strip() for line in header_lines]

    if not stripped or stripped[0] != HEADER_TITLE:
        failed.append("title")
    if SEPARATOR not in stripped:
        failed.append("separator")

    before_separator = []
    for line in header_lines:
        if line.strip() == SEPARATOR:
            break
        before_separator.append(line)

    description_lines = [
        line for line in before_separator[1:] if line.strip() and not line.startswith("### ")
    ]
    if not description_lines:
        failed.append("description")
    if any(line.startswith("### ") for line in before_separator):
        failed.append("entry_before_separator")

    return failed


def line_indexes(entry: Entry) -> dict[str, int | None]:
    indexes = {
        "round": None,
        "models": None,
        "supersession": None,
        "key_changes": None,
        "phase_4b_skips": None,
        "recorded_noops": None,
        "convergence": None,
    }
    for index, line in enumerate(entry.body_lines):
        if indexes["round"] is None and ROUND_LINE_RE.match(line):
            indexes["round"] = index
        elif indexes["models"] is None and line.startswith("**Models:**"):
            indexes["models"] = index
        elif indexes["supersession"] is None and line.startswith("*Supersession note:"):
            indexes["supersession"] = index
        elif indexes["key_changes"] is None and KEY_CHANGES_RE.match(line):
            indexes["key_changes"] = index
        elif indexes["phase_4b_skips"] is None and PHASE_4B_SKIPS_RE.match(line):
            indexes["phase_4b_skips"] = index
        elif indexes["recorded_noops"] is None and line.startswith("**Recorded no-ops:**"):
            indexes["recorded_noops"] = index
        elif indexes["convergence"] is None and line.startswith("**Convergence:**"):
            indexes["convergence"] = index
    return indexes


def required_lines_missing(entry: Entry) -> bool:
    indexes = line_indexes(entry)
    required = ("round", "models", "key_changes", "phase_4b_skips", "recorded_noops", "convergence")
    if any(indexes[name] is None for name in required):
        return True

    key_index = indexes["key_changes"]
    phase_index = indexes["phase_4b_skips"]
    if key_index is None or phase_index is None or key_index >= phase_index:
        return True
    return not any(line.startswith("- ") for line in entry.body_lines[key_index + 1 : phase_index])


def supersession_note_misplaced(entry: Entry) -> bool:
    indexes = line_indexes(entry)
    supersession_index = indexes["supersession"]
    if supersession_index is None:
        return False
    models_index = indexes["models"]
    return models_index is None or supersession_index != models_index + 1


def heading_malformed(entry: Entry) -> bool:
    return ENTRY_HEADING_RE.match(entry.heading_line) is None


def ordering_failures(entries: list[Entry], strict_count: int) -> list[str]:
    failed: list[str] = []
    strict_entries = entries[:strict_count]
    for left, right in zip(strict_entries, strict_entries[1:]):
        if left.round_number is not None and right.round_number is not None:
            if left.round_number < right.round_number:
                failed.append(left.id)
            continue
        if left.date is not None and right.date is not None and left.date < right.date:
            failed.append(left.id)
    return failed


def run_checks(header_lines: list[str], entries: list[Entry], recent: int = 5) -> dict:
    strict_count = min(len(entries), max(recent, 0))
    strict_entries = entries[:strict_count]
    legacy_entries = entries[strict_count:]

    checks = {
        "file_header_wellformed": new_check(True),
        "entry_heading_format": new_check(True),
        "required_lines_present": new_check(True),
        "supersession_note_position": new_check(False),
        "entries_newest_first": new_check(True),
        "legacy_entry_format_advisory": new_check(False),
    }

    checks["file_header_wellformed"]["failed"] = header_failures(header_lines)
    checks["entry_heading_format"]["failed"] = [e.id for e in strict_entries if heading_malformed(e)]
    checks["required_lines_present"]["failed"] = [e.id for e in strict_entries if required_lines_missing(e)]
    checks["supersession_note_position"]["failed"] = [
        e.id for e in entries if supersession_note_misplaced(e)
    ]
    checks["entries_newest_first"]["failed"] = ordering_failures(entries, strict_count)

    legacy_failed = []
    for entry in legacy_entries:
        if heading_malformed(entry) or required_lines_missing(entry):
            legacy_failed.append(entry.id)
    checks["legacy_entry_format_advisory"]["failed"] = legacy_failed

    for check in checks.values():
        check["ok"] = len(check["failed"]) == 0

    return checks


def check_text(text: str, path: Path, recent: int = 5) -> dict:
    header_lines, entries = parse_review_history(text)
    checks = run_checks(header_lines, entries, recent)
    strict_count = min(len(entries), max(recent, 0))
    return {
        "path": str(path),
        "counts": {
            "entries": len(entries),
            "strict_entries": strict_count,
            "legacy_entries": len(entries) - strict_count,
        },
        "result": derive_result(checks),
        "checks": checks,
    }


def check_file(path: Path, recent: int = 5) -> dict:
    return check_text(path.read_text(), path, recent)


def print_report(report: dict) -> None:
    print(f"Checked: {report['path']}")
    print(
        f"Entries: {report['counts']['entries']} "
        f"({report['counts']['strict_entries']} strict, {report['counts']['legacy_entries']} advisory legacy)"
    )
    print(f"Result: {report['result'].upper()}")
    for name, check in report["checks"].items():
        if check["ok"]:
            continue
        kind = "blocking" if check["blocking"] else "advisory"
        print(f"  [{kind}] {name}: {', '.join(str(i) for i in check['failed'])}")


class UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(3, f"{self.prog}: error: {message}\n")


def main() -> int:
    parser = UsageParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path, help="Path to review-history.md")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    parser.add_argument(
        "--recent",
        type=int,
        default=5,
        help="Number of newest entries to validate strictly; older entries are advisory (default: 5)",
    )
    args = parser.parse_args()

    if args.recent < 0:
        print("error: --recent must be >= 0", file=sys.stderr)
        return 3
    if not args.path.is_file():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 3

    report = check_file(args.path, args.recent)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return {"pass": 0, "needs_review": 2, "fail": 1}[report["result"]]


if __name__ == "__main__":
    raise SystemExit(main())
