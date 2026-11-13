#!/usr/bin/env python3
"""Deterministic checker for `Depends on:` declarations in a resolutions file.

Implements SKILL.md §4b's file-derived `Depends on:` skip conditions:

  - the named dependency is absent from this pass's resolutions file;
  - the named dependency is REJECTed in this pass's resolutions file;
  - the dependency chain is cyclic;
  - the named dependency is in a later Application-order category than the finding
    that names it;
  - the named dependency itself deterministically skips because of one of the
    conditions above, allowing same-pass dependency failures to cascade.

The checker deliberately does NOT decide Phase 4b application/runtime failures such
as target-not-found, anchor ambiguity, or post-write validation failures. Those are
known only while applying edits to the plan and companion files, so they stay with
the orchestrator. It also does not infer companion-file category membership for a
finding: category 4 is a property of queued edits, while this file only contains
finding-level decisions. Category-order validation is therefore limited to the
unambiguous finding categories in §4b: ACCEPT, MODIFY plain findings, and
CONFLICTED ACCEPT/MODIFY findings carrying a binding TL decision. Ambiguous category
mapping is a non-blocking advisory, never a hard failure.

Both `**Depends on:** ID` and `Depends on: ID` are accepted. The template writes the
field bolded, but the declaration is TL/orchestrator-authored and older or manual
files may use the plain form.

Output format (--json):
  {
    "path": "...",
    "counts": {"findings": N, "with_dependencies": M},
    "result": "pass" | "needs_review" | "fail",
    "checks": {
      "<check_name>": {"blocking": bool, "ok": bool, "failed": [...]}
    }
  }

`failed` lists hold IDs only, except where the dependency ID is needed to make the
bare finding ID actionable; those entries use `{"id": finding_id, "value": dep_id}`.

`result` is derived from `checks`, not stored independently:
  - "fail"         - any blocking check has ok == false.
  - "needs_review" - no blocking failures, but a non-blocking check has ok == false.
  - "pass"         - every check ok == true.

Exit status mirrors `result`: pass -> 0, fail -> 1, needs_review -> 2.
File-not-found or other usage errors -> 3.

Usage:
    python3 check_dependencies.py <path-to-resolutions-vN.md>
    python3 check_dependencies.py <path> --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import check_resolutions  # noqa: E402

Entry = check_resolutions.Entry

VALID_RESOLUTIONS = {"ACCEPT", "REJECT", "MODIFY"}
PLAIN_DEPENDS_RE = re.compile(r"^Depends on:\s*(.*?)\s*$")
BACKTICKED_RE = re.compile(r"`([^`]+)`")

CATEGORY_ACCEPT = 1
CATEGORY_MODIFY_PLAIN = 2
CATEGORY_CONFLICTED = 3


def normalise_resolution(entry: Entry) -> str | None:
    """Return ACCEPT/REJECT/MODIFY when the Resolution value is mechanically valid."""
    if entry.resolution is None:
        return None
    raw = entry.resolution.strip()
    first_token = raw.split()[0] if raw else ""
    remainder = raw[len(first_token):].strip()
    if first_token.upper() not in VALID_RESOLUTIONS or remainder:
        return None
    return first_token.upper()


def normalise_finding_id(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if check_resolutions.is_placeholder(value):
        return None
    quoted = BACKTICKED_RE.search(value)
    token = quoted.group(1) if quoted else value.split()[0]
    token = token.strip().strip("`.,;:()[]")
    return token or None


def depends_on(entry: Entry) -> str | None:
    """Return the declared dependency ID, accepting bolded and plain field forms."""
    dep = normalise_finding_id(entry.fields.get("Depends on"))
    if dep:
        return dep
    for line in entry.body.splitlines():
        match = PLAIN_DEPENDS_RE.match(line)
        if match:
            return normalise_finding_id(match.group(1))
    return None


def application_category(entry: Entry) -> int | None:
    """Return the unambiguous §4b Application-order category for a finding."""
    resolution = normalise_resolution(entry)
    if resolution is None or resolution == "REJECT":
        return None
    if check_resolutions.is_conflicted(entry):
        return CATEGORY_CONFLICTED
    if resolution == "ACCEPT":
        return CATEGORY_ACCEPT
    if resolution == "MODIFY":
        return CATEGORY_MODIFY_PLAIN
    return None


def new_check(blocking: bool) -> dict:
    return {"blocking": blocking, "ok": True, "failed": []}


def dependency_map(findings: list[Entry]) -> dict[str, str]:
    return {entry.id: dep for entry in findings if (dep := depends_on(entry))}


def cycle_members(start: str, deps: dict[str, str]) -> set[str]:
    """Return the cycle reachable from start, or an empty set if none is reachable."""
    seen_at: dict[str, int] = {}
    chain: list[str] = []
    current = start
    while current in deps:
        if current in seen_at:
            return set(chain[seen_at[current] :])
        seen_at[current] = len(chain)
        chain.append(current)
        current = deps[current]
    return set()


def cyclic_finding_ids(deps: dict[str, str]) -> list[str]:
    found: set[str] = set()
    for finding_id in deps:
        found.update(cycle_members(finding_id, deps))
    return sorted(found)


def failed_dependency_ids(checks: dict) -> set[str]:
    failed: set[str] = set()
    for name, check in checks.items():
        if name == "depends_on_dependency_not_skipped" or not check["blocking"]:
            continue
        for item in check["failed"]:
            if isinstance(item, dict):
                failed.add(item["id"])
            else:
                failed.add(item)
    return failed


def run_checks(findings: list[Entry]) -> dict:
    entries = {entry.id: entry for entry in findings}
    deps = dependency_map(findings)
    checks = {
        "depends_on_present": new_check(True),
        "depends_on_not_rejected": new_check(True),
        "depends_on_acyclic": new_check(True),
        "depends_on_category_order": new_check(True),
        "depends_on_dependency_not_skipped": new_check(True),
        "depends_on_category_mapping_advisory": new_check(False),
    }

    for entry_id, dep_id in deps.items():
        entry = entries[entry_id]
        dep_entry = entries.get(dep_id)
        if dep_entry is None:
            checks["depends_on_present"]["failed"].append({"id": entry_id, "value": dep_id})
            continue
        if normalise_resolution(dep_entry) == "REJECT":
            checks["depends_on_not_rejected"]["failed"].append({"id": entry_id, "value": dep_id})

        entry_category = application_category(entry)
        dep_category = application_category(dep_entry)
        if entry_category is None or dep_category is None:
            checks["depends_on_category_mapping_advisory"]["failed"].append(
                {"id": entry_id, "value": dep_id}
            )
        elif dep_category > entry_category:
            checks["depends_on_category_order"]["failed"].append({"id": entry_id, "value": dep_id})

    checks["depends_on_acyclic"]["failed"] = cyclic_finding_ids(deps)

    for check in checks.values():
        check["ok"] = len(check["failed"]) == 0

    while True:
        skipped = failed_dependency_ids(checks)
        cascade = [
            {"id": entry_id, "value": dep_id}
            for entry_id, dep_id in deps.items()
            if dep_id in skipped and entry_id not in skipped
        ]
        if cascade == checks["depends_on_dependency_not_skipped"]["failed"]:
            break
        checks["depends_on_dependency_not_skipped"]["failed"] = cascade
        checks["depends_on_dependency_not_skipped"]["ok"] = len(cascade) == 0

    return checks


def derive_result(checks: dict) -> str:
    if any(c["blocking"] and not c["ok"] for c in checks.values()):
        return "fail"
    if any(not c["blocking"] and not c["ok"] for c in checks.values()):
        return "needs_review"
    return "pass"


def check_file(path: Path) -> dict:
    text = path.read_text()
    findings, _questions = check_resolutions.load_entries(text)
    checks = run_checks(findings)
    return {
        "path": str(path),
        "counts": {
            "findings": len(findings),
            "with_dependencies": len(dependency_map(findings)),
        },
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
    print(
        f"Findings: {report['counts']['findings']}   "
        f"With dependencies: {report['counts']['with_dependencies']}"
    )
    print(f"Result: {report['result'].upper()}")
    for name, check in report["checks"].items():
        if check["ok"]:
            continue
        kind = "blocking" if check["blocking"] else "advisory"
        ids = ", ".join(format_failed_item(i) for i in check["failed"])
        print(f"  [{kind}] {name}: {ids}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
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
