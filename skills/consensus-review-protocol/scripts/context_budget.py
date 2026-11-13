#!/usr/bin/env python3
"""Deterministic context-budget estimator for consensus-review-protocol rounds.

Implements SKILL.md's Setup §Context budget rule by computing the input word
count of one recipient in each phase, not the sum across parallel sub-agents.
That distinction is intentional: Phase 2 and Phase 3 each send one sub-agent all
sibling-model outputs from earlier phases, so those review files are all counted;
the plan itself is still counted once, because each sub-agent receives only one
copy of it.

Phase inputs are derived from the Sub-Agent Feed Rule and Phase 4 orchestration:

  - Phase 1: plan, resolutions, review-general, blue mode reference.
  - Phase 2: Phase 1 inputs with all `*-blue-v<N>.md` review files, using red mode.
  - Phase 3: Phase 2 review files plus all `*-red-v<N>.md` files, using purple mode.
  - Phase 4: plan, resolutions, all blue/red/purple files, orchestrator reference
    files, and an estimate for `review-history.md`.

This script does NOT decide whether a plan should be split or whether reduced
context quality is acceptable. The 10,000-word plan guidance is advisory and
non-blocking; the 80,000-word per-phase ceiling is blocking because SKILL.md says
to halt and ask the tech lead.

Word count is `len(text.split())`, matching the toolkit's conservative
whitespace-split convention. Dot-prefixed and `.partial` files are excluded from
review-file discovery. The one exception is `.resolutions-vN-swept.md`: when
present it is preferred over `resolutions-vN.md`, because Setup sweep says that
copy is what sub-agents and the orchestrator actually read.

Phase 4's review-history estimate defaults to the five most recent `## ` sections
of `<workdir>/review-history.md`, matching SKILL.md's Phase 4a/4c default. Override
with `--review-history-entries`; if the file has no `## ` headings, the full file
is counted so the estimate fails conservative rather than silently guessing.

Output format (--json):
  {
    "plan": "...",
    "workdir": "...",
    "version": N,
    "plan_words": N,
    "review_history_entries": N,
    "phases": {
      "1": {"words": N, "inputs": ["<filename>", ...]},
      "2": {"words": N, "inputs": [...]},
      "3": {"words": N, "inputs": [...]},
      "4": {"words": N, "inputs": [...]}
    },
    "heaviest_phase": "3",
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
    python3 context_budget.py <plan-vN.md> <workdir>
    python3 context_budget.py --json <plan> <workdir>
    python3 context_budget.py --review-history-entries 10 <plan> <workdir>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLAN_VERSION_RE = re.compile(r"(?:^|-)v(\d+)\.md$")
HISTORY_HEADING_RE = re.compile(r"^##\s+")
PHASE_CEILING_WORDS = 80_000
PLAN_ADVISORY_WORDS = 10_000

PHASE_REFERENCES = {
    "1": ("review-general.md", "review-mode-blue.md"),
    "2": ("review-general.md", "review-mode-red.md"),
    "3": ("review-general.md", "review-mode-purple.md"),
    "4": (
        "review-general.md",
        "phase-4a-output-formats.md",
        "phase-4c-output-formats.md",
        "completion-report-template.md",
    ),
}


class UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(3, f"{self.prog}: error: {message}\n")


def word_count(text: str) -> int:
    return len(text.split())


def file_word_count(path: Path) -> int:
    return word_count(path.read_text())


def plan_version(plan_path: Path) -> int:
    match = PLAN_VERSION_RE.search(plan_path.name)
    return int(match.group(1)) if match else 1


def new_check(blocking: bool) -> dict:
    return {"blocking": blocking, "ok": True, "failed": []}


def derive_result(checks: dict) -> str:
    if any(c["blocking"] and not c["ok"] for c in checks.values()):
        return "fail"
    if any(not c["blocking"] and not c["ok"] for c in checks.values()):
        return "needs_review"
    return "pass"


def is_discoverable_input(path: Path) -> bool:
    return path.is_file() and not path.name.startswith(".") and not path.name.endswith(".partial")


def matching_review_files(workdir: Path, version: int, phase: str) -> list[Path]:
    return sorted(
        (
            path
            for path in workdir.glob(f"*-{phase}-v{version}.md")
            if is_discoverable_input(path)
        ),
        key=lambda p: p.name,
    )


def resolution_input(workdir: Path, version: int) -> Path | None:
    swept = workdir / f".resolutions-v{version}-swept.md"
    if swept.is_file():
        return swept
    path = workdir / f"resolutions-v{version}.md"
    return path if path.is_file() else None


def reference_inputs(reference_dir: Path, phase: str) -> list[Path]:
    return [reference_dir / name for name in PHASE_REFERENCES[phase]]


def recent_review_history(text: str, entries: int) -> tuple[str, int]:
    if entries <= 0:
        return "", 0

    sections: list[list[str]] = []
    current: list[str] | None = None
    preamble: list[str] = []

    for line in text.splitlines():
        if HISTORY_HEADING_RE.match(line):
            if current is not None:
                sections.append(current)
            current = [line]
        elif current is None:
            preamble.append(line)
        else:
            current.append(line)

    if current is not None:
        sections.append(current)
    if not sections:
        return text, 1 if text.strip() else 0

    selected = sections[-entries:]
    return "\n".join("\n".join(section) for section in selected), len(selected)


def named_words(paths: list[Path]) -> list[dict]:
    return [{"name": path.name, "words": file_word_count(path)} for path in paths if path.is_file()]


def phase_report(inputs: list[dict]) -> dict:
    return {
        "words": sum(item["words"] for item in inputs),
        "inputs": [item["name"] for item in inputs],
    }


def collect_phase_inputs(
    plan_path: Path,
    workdir: Path,
    version: int,
    reference_dir: Path,
    review_history_entries: int,
) -> tuple[dict, int]:
    base_paths = [plan_path]
    res_path = resolution_input(workdir, version)
    if res_path is not None:
        base_paths.append(res_path)

    blue = matching_review_files(workdir, version, "blue")
    red = matching_review_files(workdir, version, "red")
    purple = matching_review_files(workdir, version, "purple")

    phase_paths = {
        "1": base_paths + reference_inputs(reference_dir, "1"),
        "2": base_paths + blue + reference_inputs(reference_dir, "2"),
        "3": base_paths + blue + red + reference_inputs(reference_dir, "3"),
        "4": base_paths + blue + red + purple + reference_inputs(reference_dir, "4"),
    }

    inputs = {phase: named_words(paths) for phase, paths in phase_paths.items()}
    counted_history_entries = 0
    history_path = workdir / "review-history.md"
    if history_path.is_file():
        history_text, counted_history_entries = recent_review_history(
            history_path.read_text(), review_history_entries
        )
        inputs["4"].append({"name": history_path.name, "words": word_count(history_text)})

    return {phase: phase_report(items) for phase, items in inputs.items()}, counted_history_entries


def run_checks(plan_words: int, phases: dict) -> dict:
    checks = {
        "phase_ceiling_80k": new_check(True),
        "plan_size_advisory_10k": new_check(False),
    }

    checks["phase_ceiling_80k"]["failed"] = [
        phase for phase, data in phases.items() if data["words"] > PHASE_CEILING_WORDS
    ]
    checks["plan_size_advisory_10k"]["failed"] = ["plan"] if plan_words > PLAN_ADVISORY_WORDS else []

    for check in checks.values():
        check["ok"] = len(check["failed"]) == 0

    return checks


def check_budget(
    plan_path: Path,
    workdir: Path,
    reference_dir: Path | None = None,
    review_history_entries: int = 5,
) -> dict:
    reference_dir = reference_dir or default_reference_dir()
    version = plan_version(plan_path)
    plan_words = file_word_count(plan_path)
    phases, counted_history_entries = collect_phase_inputs(
        plan_path, workdir, version, reference_dir, review_history_entries
    )
    checks = run_checks(plan_words, phases)
    heaviest_phase = max(phases, key=lambda phase: phases[phase]["words"])

    return {
        "plan": str(plan_path),
        "workdir": str(workdir),
        "version": version,
        "plan_words": plan_words,
        "review_history_entries": counted_history_entries,
        "phases": phases,
        "heaviest_phase": heaviest_phase,
        "result": derive_result(checks),
        "checks": checks,
    }


def default_reference_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "references"


def print_report(report: dict) -> None:
    print(f"Plan: {report['plan']} ({report['plan_words']} words)")
    print(f"Workdir: {report['workdir']}   Version: {report['version']}")
    print(
        f"Heaviest phase: {report['heaviest_phase']} "
        f"({report['phases'][report['heaviest_phase']]['words']} words)"
    )
    print(f"Result: {report['result'].upper()}")
    for phase, data in report["phases"].items():
        print(f"  Phase {phase}: {data['words']} words ({', '.join(data['inputs'])})")
    for name, check in report["checks"].items():
        if check["ok"]:
            continue
        kind = "blocking" if check["blocking"] else "advisory"
        print(f"  [{kind}] {name}: {', '.join(str(i) for i in check['failed'])}")
    if not report["checks"]["plan_size_advisory_10k"]["ok"]:
        print(
            f"📏 Plan is approximately {report['plan_words']} words, above the "
            "~10,000-word guidance in §Context budget; consider splitting into "
            "standalone plan files with their own review cycles."
        )


def main() -> int:
    parser = UsageParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path, help="Path to the plan file being reviewed")
    parser.add_argument("workdir", type=Path, help="Consensus review workdir for this plan")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    parser.add_argument(
        "--review-history-entries",
        type=int,
        default=5,
        help="Number of most recent review-history entries to count for Phase 4 (default: 5)",
    )
    parser.add_argument(
        "--references",
        type=Path,
        default=None,
        help="Override the references directory (defaults to ../references)",
    )
    args = parser.parse_args()

    if not args.plan.is_file():
        print(f"error: file not found: {args.plan}", file=sys.stderr)
        return 3
    if not args.workdir.is_dir():
        print(f"error: directory not found: {args.workdir}", file=sys.stderr)
        return 3
    reference_dir = args.references or default_reference_dir()
    if not reference_dir.is_dir():
        print(f"error: references directory not found: {reference_dir}", file=sys.stderr)
        return 3
    if args.review_history_entries < 0:
        print("error: --review-history-entries must be >= 0", file=sys.stderr)
        return 3

    report = check_budget(args.plan, args.workdir, reference_dir, args.review_history_entries)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return {"pass": 0, "needs_review": 2, "fail": 1}[report["result"]]


if __name__ == "__main__":
    raise SystemExit(main())
