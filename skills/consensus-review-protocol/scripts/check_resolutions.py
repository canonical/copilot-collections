#!/usr/bin/env python3
"""Deterministic completeness checker for a consensus-review-protocol resolutions file.

Implements SKILL.md's Setup Rules 1-4 (resolutions completeness definition):

  Rule 1 - Every `Resolution:` field is exactly ACCEPT, REJECT, or MODIFY
           (case-insensitive, whitespace-trimmed; no trailing text on that line).
  Rule 2 - A non-blank, non-placeholder `Notes:` field is required on every
           MODIFY entry, every CONFLICTED entry (any Resolution value), and every
           entry meeting the Companion-target test (see below).
  Rule 3 - Every Open Questions entry has a non-blank, non-placeholder `Answer:` field.
  Rule 4 - `Resolution: ACCEPT` on an entry carrying `Presents options:` fails.

This script does NOT perform the Setup judgment pass (SKILL.md, non-mechanical:
"does this field still read as an open question?") - that requires reading
comprehension and stays with the orchestrator/tech lead.

Rule 2's third condition (the Companion-target test) is semantic in the plan's own
words ("Summary names a companion-file path and describes a change to it"), so a
`.md` path mention cannot be distinguished from a genuine edit target by text
matching alone. This is implemented as its own non-blocking check
(`rule_2_companion_target_advisory`): a match with blank/placeholder Notes is
reported but never forces a `fail` result on its own - see §Output format below.

Output format (--json):
  {
    "path": "...",
    "counts": {"findings": N, "open_questions": M},
    "result": "pass" | "needs_review" | "fail",
    "checks": {
      "<check_name>": {"blocking": bool, "ok": bool, "failed": [...]}
    }
  }

  Each `checks` entry's `failed` list holds finding/question IDs (Rule 1 and Rule 4
  additionally carry the offending value/labels alongside the ID, since that detail
  isn't otherwise visible from the ID alone).

`result` is derived from `checks`, not stored independently:
  - "fail"         - any blocking check has ok == false.
  - "needs_review" - no blocking failures, but a non-blocking check has ok == false.
  - "pass"         - every check ok == true.

Exit status mirrors `result`: pass -> 0, fail -> 1, needs_review -> 2.
File-not-found or other usage errors -> 3.

Usage:
    python3 check_resolutions.py <path-to-resolutions-vN.md>
    python3 check_resolutions.py <path> --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"^\s*(<!--.*-->\s*)*\s*$", re.DOTALL)
HEADING_RE = re.compile(r"^##\s+(.*?)\s*$")
ENTRY_HEADING_RE = re.compile(r"^###\s+(.*?)\s*$")
FIELD_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z /-]*?):\*\*\s*(.*)$")
PLAIN_FIELD_RE = re.compile(r"^([A-Za-z][A-Za-z ]*?):\s?(.*)$")

VALID_RESOLUTIONS = {"ACCEPT", "REJECT", "MODIFY"}

# Companion-target test heuristic: an entry whose Summary/body names a backticked
# `.md` path is treated as a candidate match for "names a companion-file path".
COMPANION_PATH_RE = re.compile(r"`([\w./-]+\.md)`")


class Entry:
    __slots__ = ("id", "heading", "fields", "resolution", "notes", "answer", "body")

    def __init__(self, id_, heading, fields, resolution, notes, answer, body):
        self.id = id_
        self.heading = heading
        self.fields = fields  # bolded header fields, e.g. "Severity" -> text
        self.resolution = resolution
        self.notes = notes
        self.answer = answer
        self.body = body  # full raw entry text (for heuristics: Summary content)


def is_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    return bool(PLACEHOLDER_RE.match(value))


def split_sections(text: str) -> dict:
    """Split the file into top-level (## ) sections, keyed by heading text."""
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def parse_entries(section_text: str) -> list[Entry]:
    """Split a section's body into ### -headed entries and extract fields."""
    entries: list[Entry] = []
    current_heading = None
    current_lines: list[str] = []

    def flush():
        if current_heading is not None:
            entries.append(_build_entry(current_heading, current_lines))

    for line in section_text.splitlines():
        m = ENTRY_HEADING_RE.match(line)
        if m:
            flush()
            current_heading = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    flush()
    return entries


def _first_token(heading: str) -> str:
    # Entry IDs are the first backtick-quoted or bare token of the heading,
    # e.g. "R60-PLAN-MERGED-I1" or "Q1 -- `R59-PLAN-MERGED-I4` was skipped: ..."
    heading = heading.strip("`")
    return heading.split()[0].strip("`:") if heading.split() else heading


def _build_entry(heading: str, lines: list[str]) -> Entry:
    fields: dict[str, str] = {}
    resolution = None
    notes_lines: list[str] = []
    answer_lines: list[str] = []
    collecting = None  # "notes" | "answer" | None

    for line in lines:
        bold_m = FIELD_RE.match(line)
        if bold_m:
            collecting = None
            fields[bold_m.group(1).strip()] = bold_m.group(2).strip()
            continue
        plain_m = PLAIN_FIELD_RE.match(line)
        if plain_m and plain_m.group(1).strip() in ("Resolution", "Notes", "Answer"):
            field_name = plain_m.group(1).strip()
            value = plain_m.group(2).strip()
            if field_name == "Resolution":
                resolution = value
                collecting = None
            elif field_name == "Notes":
                notes_lines = [value] if value else []
                collecting = "notes"
            elif field_name == "Answer":
                answer_lines = [value] if value else []
                collecting = "answer"
            continue
        if line.strip() == "---":
            # Horizontal-rule entry separator: never part of Notes:/Answer: content.
            collecting = None
            continue
        # Continuation line for a multi-line Notes:/Answer: value, or blank/prose.
        if collecting == "notes":
            notes_lines.append(line)
        elif collecting == "answer":
            answer_lines.append(line)

    notes = "\n".join(notes_lines).strip() if notes_lines else None
    answer = "\n".join(answer_lines).strip() if answer_lines else None

    return Entry(
        id_=_first_token(heading),
        heading=heading,
        fields=fields,
        resolution=resolution,
        notes=notes,
        answer=answer,
        body="\n".join(lines),
    )


def is_conflicted(entry: Entry) -> bool:
    severity = entry.fields.get("Severity", "")
    return "CONFLICTED" in severity.upper()


def meets_companion_target_test(entry: Entry) -> bool:
    """Heuristic stand-in for the plan's semantic Companion-target test."""
    summary = entry.fields.get("Summary", "") + " " + entry.body
    return bool(COMPANION_PATH_RE.search(summary))


def new_check(blocking: bool) -> dict:
    return {"blocking": blocking, "ok": True, "failed": []}


def run_checks(findings: list[Entry], questions: list[Entry]) -> dict:
    checks = {
        "rule_1_resolution_valid": new_check(True),
        "rule_2_notes_required": new_check(True),
        "rule_2_companion_target_advisory": new_check(False),
        "rule_3_answer_required": new_check(True),
        "rule_4_accept_vs_options": new_check(True),
    }

    for e in findings:
        # Rule 1
        if e.resolution is None:
            checks["rule_1_resolution_valid"]["failed"].append({"id": e.id, "value": None})
            continue
        raw = e.resolution.strip()
        first_token = raw.split()[0] if raw else ""
        remainder = raw[len(first_token):].strip()
        if first_token.upper() not in VALID_RESOLUTIONS or remainder:
            checks["rule_1_resolution_valid"]["failed"].append({"id": e.id, "value": raw})
            continue

        resolution = first_token.upper()
        conflicted = is_conflicted(e)
        companion_targeted = meets_companion_target_test(e)
        notes_blank = is_placeholder(e.notes)

        # Rule 2, unambiguous part: MODIFY and CONFLICTED are stated outright in
        # SKILL.md with no reading-comprehension step required.
        if (resolution == "MODIFY" or conflicted) and notes_blank:
            checks["rule_2_notes_required"]["failed"].append(e.id)

        # Rule 2, third condition (companion-target test): semantic, so kept as
        # its own non-blocking check rather than folded into the rule above.
        if companion_targeted and notes_blank:
            checks["rule_2_companion_target_advisory"]["failed"].append(e.id)

        # Rule 4
        if resolution == "ACCEPT" and "Presents options" in e.fields:
            checks["rule_4_accept_vs_options"]["failed"].append(
                {"id": e.id, "options": e.fields.get("Presents options", "")}
            )

    for e in questions:
        if is_placeholder(e.answer):
            checks["rule_3_answer_required"]["failed"].append(e.id)

    for check in checks.values():
        check["ok"] = len(check["failed"]) == 0

    return checks


def derive_result(checks: dict) -> str:
    if any(c["blocking"] and not c["ok"] for c in checks.values()):
        return "fail"
    if any(not c["blocking"] and not c["ok"] for c in checks.values()):
        return "needs_review"
    return "pass"


def load_entries(text: str) -> tuple[list[Entry], list[Entry]]:
    sections = split_sections(text)
    findings_section = None
    open_questions_section = None
    for key, body in sections.items():
        if key.strip() == "Findings for Tech Lead Resolution":
            findings_section = body
        elif key.strip() == "Open Questions":
            open_questions_section = body
    findings = parse_entries(findings_section) if findings_section else []
    questions = parse_entries(open_questions_section) if open_questions_section else []
    return findings, questions


def check_file(path: Path) -> dict:
    text = path.read_text()
    findings, questions = load_entries(text)
    checks = run_checks(findings, questions)
    return {
        "path": str(path),
        "counts": {"findings": len(findings), "open_questions": len(questions)},
        "result": derive_result(checks),
        "checks": checks,
    }


def format_failed_item(item) -> str:
    if isinstance(item, dict):
        extra = {k: v for k, v in item.items() if k != "id"}
        extra_str = ", ".join(f"{k}={v!r}" for k, v in extra.items())
        return f"{item['id']} ({extra_str})" if extra_str else str(item["id"])
    return str(item)


def print_report(report: dict) -> None:
    print(f"Checked: {report['path']}")
    print(f"Findings: {report['counts']['findings']}   Open Questions: {report['counts']['open_questions']}")
    print(f"Result: {report['result'].upper()}")
    for name, check in report["checks"].items():
        if check["ok"]:
            continue
        kind = "blocking" if check["blocking"] else "advisory"
        ids = ", ".join(format_failed_item(i) for i in check["failed"])
        print(f"  [{kind}] {name}: {ids}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path, help="Path to resolutions-vN.md")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 3

    report = check_file(args.path)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return {"pass": 0, "needs_review": 2, "fail": 1}[report["result"]]


if __name__ == "__main__":
    raise SystemExit(main())
