#!/usr/bin/env python3
"""Deterministic conformance checker for a consensus-review-protocol Completion Report.

SKILL.md's Phase 4c writes `<workdir>/completion-report-v<N>.md` by filling in
`references/completion-report-template.md`, then displays it verbatim. This script
verifies the filled file still matches the template before it is shown to the tech
lead, catching the drift that free-form authoring introduces (dropped sections,
reordered sections, summarised-away sections, unsubstituted placeholders).

The template is not duplicated here. The script reads
`references/completion-report-template.md` and derives from it:

  - the canonical `## ` section list and its order;
  - the exact placeholder tokens (`<...>` and `[...]`) that must not survive.

So the checker stays correct when the template is edited, and a template change
needs no corresponding change here. Only OPTIONAL_SECTIONS and
FINAL_ROUND_REQUIRED below encode judgments the template states in prose.

Failure lists name sections, not tokens or line numbers: the list stays bounded by
the section count, matches the IDs-only convention of the sibling checkers, and
names the unit the orchestrator rewrites to fix the problem.

This script does NOT check the report's factual accuracy - whether a count is
right, whether a verdict matches the review files. That stays with the
orchestrator. It checks structural conformance only.

Output format (--json):
  {
    "path": "...",
    "template": "...",
    "mode": "standard" | "final_round",
    "counts": {"template_sections": N, "report_sections": M},
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
File-not-found or other usage errors -> 3.

Usage:
    python3 check_completion_report.py --json <workdir>/completion-report-vN.md
    python3 check_completion_report.py --json --final-round <path>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^##\s+(.*?)\s*$")
TITLE_RE = re.compile(r"^\s*✅\s+Consensus Review\s+.+\s+Round\s+\d+\s+Complete\s*$")
DATE_RE = re.compile(r"^\s*Date:\s*\d{4}-\d{2}-\d{2}\s*$")
FENCE_RE = re.compile(r"^\s*```")
HTML_COMMENT_RE = re.compile(r"<!--")

ANGLE_TOKEN_RE = re.compile(r"<[^<>\n]+>")
BRACKET_TOKEN_RE = re.compile(r"\[[^\[\]\n]+\]")

# A version-bearing heading is compared with its version integer normalised away,
# so `## Applied From resolutions-v12.md This Round (Phase 4b)` matches the
# template's `## Applied From resolutions-v<N>.md This Round (Phase 4b)`.
VERSION_SUFFIX_RE = re.compile(r"-v(?:<N(?:\+1)?>|\d+)")

# Sections the template itself marks as conditional, in its own prose:
#   - "Orchestrator Notes": "omit this section or write 'None'".
#   - "Consensus Protocol Degraded Mode": "[Only if this round ran under a
#     pre-authorised or ad hoc 2-model setup]".
OPTIONAL_SECTIONS = frozenset(
    {
        "Orchestrator Notes",
        "Consensus Protocol Degraded Mode",
    }
)

# Final round (phase-4c-output-formats.md §Final Round Rules): "omit every section
# that depends on Phase 1-3 or 4a output, list only Phase 4b's output files". These
# four cannot depend on Phase 1-3 or 4a, so they stay required; every other section
# becomes optional rather than forbidden, because the boundary of "depends on Phase
# 1-3 or 4a output" is a judgment the orchestrator makes, not a mechanical test.
FINAL_ROUND_REQUIRED = (
    "Plan Reviewed",
    "Applied From resolutions-v<N>.md This Round (Phase 4b)",
    "File Listing",
    "Next Step",
)

# Sections that unambiguously depend on Phase 1-3 or 4a output. Present in a final
# round, they are reported as a non-blocking advisory rather than a failure.
FINAL_ROUND_PHASE_DEPENDENT = frozenset(
    {
        "Phase Outcomes",
        "Findings This Round",
        "Model Verdicts",
        "Convergence Status",
    }
)

# Literal template scaffolding that must never survive into a filled report.
TEMPLATE_SCAFFOLDING = (
    "# Completion Report Template",
    "Referenced by `references/phase-4c-output-formats.md",
)


def normalise_heading(heading: str) -> str:
    """Collapse whitespace and version integers so headings compare stably."""
    return VERSION_SUFFIX_RE.sub("-vN", " ".join(heading.split()))


def extract_headings(text: str) -> list[str]:
    """Return the `## ` headings of a document, in document order."""
    return [m.group(1).strip() for m in map(HEADING_RE.match, text.splitlines()) if m]


def extract_placeholders(template_text: str) -> set[str]:
    """Return every `<...>` and `[...]` placeholder token used by the template.

    Tokens are matched verbatim against the report, so a substituted value can
    never be mistaken for an unsubstituted placeholder.
    """
    tokens: set[str] = set()
    for line in template_text.splitlines():
        if line.startswith("#") or line.lstrip().startswith("*Referenced by"):
            continue
        tokens.update(ANGLE_TOKEN_RE.findall(line))
        tokens.update(BRACKET_TOKEN_RE.findall(line))
    return tokens


def new_check(blocking: bool) -> dict:
    return {"blocking": blocking, "ok": True, "failed": []}


HEADER_PSEUDO_SECTION = "(header)"


def sections_containing_placeholders(report_text: str, placeholders: set[str]) -> list[str]:
    """Return the report sections still holding unsubstituted template content.

    Section names rather than tokens: the list is then bounded by the section
    count, matches the IDs-only convention the sibling checkers use, and names
    the unit the orchestrator actually rewrites to fix the problem.
    """
    found: list[str] = []
    current = HEADER_PSEUDO_SECTION
    for line in report_text.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            current = normalise_heading(heading.group(1))
            continue
        if current in found:
            continue
        if HTML_COMMENT_RE.search(line) or any(token in line for token in placeholders):
            found.append(current)
    return found


def check_heading_order(report_headings: list[str], template_headings: list[str]) -> list[str]:
    """Return report headings that break the template's ordering.

    Walks the report's headings against the template order; a heading that cannot
    be found at or after the current template position is out of order. Unknown
    headings are ignored here - `no_unknown_sections` reports those separately.
    """
    out_of_order: list[str] = []
    position = 0
    for heading in report_headings:
        if heading not in template_headings:
            continue
        index = template_headings.index(heading)
        if index < position:
            out_of_order.append(heading)
        else:
            position = index
    return out_of_order


def run_checks(report_text: str, template_text: str, final_round: bool) -> dict:
    template_headings = [normalise_heading(h) for h in extract_headings(template_text)]
    report_headings = [normalise_heading(h) for h in extract_headings(report_text)]
    report_seen = set(report_headings)

    if final_round:
        required = [normalise_heading(h) for h in FINAL_ROUND_REQUIRED]
    else:
        required = [h for h in template_headings if h not in OPTIONAL_SECTIONS]

    checks = {
        "header_present": new_check(True),
        "required_sections_present": new_check(True),
        "section_order": new_check(True),
        "no_unsubstituted_placeholders": new_check(True),
        "no_template_scaffolding": new_check(True),
        "not_code_fenced": new_check(True),
        "no_unknown_sections": new_check(False),
    }
    if final_round:
        checks["final_round_sections_omitted"] = new_check(False)

    lines = report_text.splitlines()
    if not any(TITLE_RE.match(line) for line in lines):
        checks["header_present"]["failed"].append("title_line")
    if not any(DATE_RE.match(line) for line in lines):
        checks["header_present"]["failed"].append("date_line")

    checks["required_sections_present"]["failed"] = [h for h in required if h not in report_seen]
    checks["section_order"]["failed"] = check_heading_order(report_headings, template_headings)

    placeholders = extract_placeholders(template_text)
    checks["no_unsubstituted_placeholders"]["failed"] = sections_containing_placeholders(
        report_text, placeholders
    )

    checks["no_template_scaffolding"]["failed"] = [s for s in TEMPLATE_SCAFFOLDING if s in report_text]

    if any(FENCE_RE.match(line) for line in lines):
        checks["not_code_fenced"]["failed"].append("code_fence_present")

    checks["no_unknown_sections"]["failed"] = [
        h for h in report_headings if h not in template_headings
    ]

    if final_round:
        checks["final_round_sections_omitted"]["failed"] = [
            h for h in report_headings if h in FINAL_ROUND_PHASE_DEPENDENT
        ]

    for check in checks.values():
        check["ok"] = len(check["failed"]) == 0

    return checks


def derive_result(checks: dict) -> str:
    if any(c["blocking"] and not c["ok"] for c in checks.values()):
        return "fail"
    if any(not c["blocking"] and not c["ok"] for c in checks.values()):
        return "needs_review"
    return "pass"


def default_template_path() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "completion-report-template.md"


def check_file(path: Path, template_path: Path, final_round: bool = False) -> dict:
    report_text = path.read_text()
    template_text = template_path.read_text()
    checks = run_checks(report_text, template_text, final_round)
    return {
        "path": str(path),
        "template": str(template_path),
        "mode": "final_round" if final_round else "standard",
        "counts": {
            "template_sections": len(extract_headings(template_text)),
            "report_sections": len(extract_headings(report_text)),
        },
        "result": derive_result(checks),
        "checks": checks,
    }


def print_report(report: dict) -> None:
    print(f"Checked: {report['path']}")
    print(f"Template: {report['template']}   Mode: {report['mode']}")
    print(
        f"Sections: {report['counts']['report_sections']} in report, "
        f"{report['counts']['template_sections']} in template"
    )
    print(f"Result: {report['result'].upper()}")
    for name, check in report["checks"].items():
        if check["ok"]:
            continue
        kind = "blocking" if check["blocking"] else "advisory"
        print(f"  [{kind}] {name}: {', '.join(str(i) for i in check['failed'])}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("path", type=Path, help="Path to completion-report-vN.md")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    parser.add_argument(
        "--final-round",
        action="store_true",
        help="Apply §Final Round Rules: only Phase 4b-independent sections are required",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Override the template path (defaults to ../references/completion-report-template.md)",
    )
    args = parser.parse_args()

    template_path = args.template or default_template_path()

    if not args.path.is_file():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 3
    if not template_path.is_file():
        print(f"error: template not found: {template_path}", file=sys.stderr)
        return 3

    report = check_file(args.path, template_path, args.final_round)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return {"pass": 0, "needs_review": 2, "fail": 1}[report["result"]]


if __name__ == "__main__":
    raise SystemExit(main())
