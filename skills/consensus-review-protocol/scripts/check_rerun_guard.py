#!/usr/bin/env python3
"""Deterministic Setup helper for consensus-review-protocol re-run guards.

Computes the mechanical Setup facts for a plan path:

  - plan stem (`<plan-name>`) and version `<N>`;
  - default or overridden workdir;
  - current round number from existing `consolidated-v*.md` files;
  - model slugs, including deterministic collision suffixes;
  - already-present outputs for this plan version;
  - versioned siblings of an unversioned input plan.

This script deliberately does NOT decide how to recover from prior artifacts or
versioned siblings. SKILL.md sends those cases to the tech lead, so they are
non-blocking checks that produce `needs_review`. The only blocking check here is
the mechanical model-list minimum from §Default Configuration: fewer than two
models is rejected at Setup. No semantic or judgment-based condition is a hard
failure.

Output format (--json):
  {
    "plan": "...",
    "derived": {
      "stem": "...",
      "version": N,
      "workdir": "...",
      "round": N,
      "model_slugs": {"<model name>": "<slug>"}
    },
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
    python3 check_rerun_guard.py --json path/to/plan-v3.md
    python3 check_rerun_guard.py --workdir .github/consensus-review-protocol/custom path/to/plan.md
    python3 check_rerun_guard.py --model gpt-5.6-sol --model "Claude Opus 4.6" path/to/plan.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_MODELS = ("gpt-5.6-sol", "claude-sonnet-5", "claude-opus-5")
DEFAULT_WORKDIR_ROOT = Path(".github") / "consensus-review-protocol"

VERSION_SUFFIX_RE = re.compile(r"^(?P<stem>.+)-v(?P<version>\d+)$")
CONSOLIDATED_RE = re.compile(r"^consolidated-v\d+\.md$")
PHASE_RE_TEMPLATE = r"^.+-{phase}-v{version}\.md$"

EXIT_CODES = {"pass": 0, "fail": 1, "needs_review": 2}


def extract_stem_version(plan_path: Path) -> tuple[str, int]:
    """Return (`<plan-name>`, `<N>`) from a plan filename."""
    stem = plan_path.stem
    match = VERSION_SUFFIX_RE.match(stem)
    if not match:
        return stem, 1
    return match.group("stem"), int(match.group("version"))


def default_workdir(stem: str) -> Path:
    return DEFAULT_WORKDIR_ROOT / stem


def visible_non_partial(path: Path) -> bool:
    return not path.name.startswith(".") and not path.name.endswith(".partial")


def count_round(workdir: Path) -> int:
    if not workdir.is_dir():
        return 1
    count = sum(
        1
        for path in workdir.iterdir()
        if path.is_file() and visible_non_partial(path) and CONSOLIDATED_RE.match(path.name)
    )
    return count + 1


def slug_base(model: str) -> str:
    slug = re.sub(r"[./ ]", "-", model.lower())
    slug = re.sub(r"-+", "-", slug)
    return slug.rstrip("-")


def derive_model_slugs(models: list[str] | tuple[str, ...]) -> dict[str, str]:
    slugs: dict[str, str] = {}
    seen: dict[str, int] = {}
    for model in models:
        base = slug_base(model)
        seen[base] = seen.get(base, 0) + 1
        slugs[model] = base if seen[base] == 1 else f"{base}-{seen[base]}"
    return slugs


def new_check(blocking: bool) -> dict:
    return {"blocking": blocking, "ok": True, "failed": []}


def existing_file(path: Path) -> bool:
    return path.is_file() and visible_non_partial(path)


def find_rerun_artifacts(plan_path: Path, stem: str, version: int, workdir: Path) -> list[str]:
    found: list[str] = []
    candidates = (
        workdir / f"consolidated-v{version}.md",
        workdir / f"resolutions-v{version + 1}.md",
        plan_path.parent / f"{stem}-v{version + 1}{plan_path.suffix}",
    )
    found.extend(str(path) for path in candidates if existing_file(path))

    if workdir.is_dir():
        for phase in ("blue", "red", "purple"):
            phase_re = re.compile(PHASE_RE_TEMPLATE.format(phase=phase, version=version))
            found.extend(
                str(path)
                for path in sorted(workdir.iterdir())
                if path.is_file() and visible_non_partial(path) and phase_re.match(path.name)
            )

    return found


def highest_versioned_sibling(plan_path: Path, stem: str, version: int) -> str | None:
    if version != 1 or VERSION_SUFFIX_RE.match(plan_path.stem):
        return None
    sibling_re = re.compile(rf"^{re.escape(stem)}-v(?P<version>\d+){re.escape(plan_path.suffix)}$")
    highest: tuple[int, Path] | None = None
    for path in plan_path.parent.iterdir():
        if not path.is_file() or not visible_non_partial(path):
            continue
        match = sibling_re.match(path.name)
        if not match:
            continue
        sibling_version = int(match.group("version"))
        if highest is None or sibling_version > highest[0]:
            highest = (sibling_version, path)
    return str(highest[1]) if highest else None


def run_checks(
    plan_path: Path,
    stem: str,
    version: int,
    workdir: Path,
    models: list[str] | tuple[str, ...],
) -> dict:
    checks = {
        "model_list_minimum": new_check(True),
        "rerun_guard": new_check(False),
        "versioned_sibling_guard": new_check(False),
    }

    if len(models) < 2:
        checks["model_list_minimum"]["failed"].append("fewer_than_2_models")

    checks["rerun_guard"]["failed"] = find_rerun_artifacts(plan_path, stem, version, workdir)

    sibling = highest_versioned_sibling(plan_path, stem, version)
    if sibling:
        checks["versioned_sibling_guard"]["failed"].append(sibling)

    for check in checks.values():
        check["ok"] = len(check["failed"]) == 0

    return checks


def derive_result(checks: dict) -> str:
    if any(c["blocking"] and not c["ok"] for c in checks.values()):
        return "fail"
    if any(not c["blocking"] and not c["ok"] for c in checks.values()):
        return "needs_review"
    return "pass"


def check_plan(plan_path: Path, workdir: Path | None = None, models: list[str] | None = None) -> dict:
    model_list = models if models is not None else list(DEFAULT_MODELS)
    stem, version = extract_stem_version(plan_path)
    resolved_workdir = workdir if workdir is not None else default_workdir(stem)
    checks = run_checks(plan_path, stem, version, resolved_workdir, model_list)
    return {
        "plan": str(plan_path),
        "derived": {
            "stem": stem,
            "version": version,
            "workdir": str(resolved_workdir),
            "round": count_round(resolved_workdir),
            "model_slugs": derive_model_slugs(model_list),
        },
        "result": derive_result(checks),
        "checks": checks,
    }


def print_report(report: dict) -> None:
    derived = report["derived"]
    print(f"Plan: {report['plan']}")
    print(
        f"Derived: stem={derived['stem']} version={derived['version']} "
        f"round={derived['round']} workdir={derived['workdir']}"
    )
    print("Model slugs: " + ", ".join(f"{model}={slug}" for model, slug in derived["model_slugs"].items()))
    print(f"Result: {report['result'].upper()}")
    for name, check in report["checks"].items():
        if check["ok"]:
            continue
        kind = "blocking" if check["blocking"] else "advisory"
        print(f"  [{kind}] {name}: {', '.join(str(i) for i in check['failed'])}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path, help="Path to the input plan file")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    parser.add_argument(
        "--workdir",
        type=Path,
        default=None,
        help="Override the review workdir (defaults to .github/consensus-review-protocol/<plan-name>)",
    )
    parser.add_argument(
        "--model",
        action="append",
        default=None,
        help="Model name; repeat for each configured model (defaults to SKILL.md defaults)",
    )
    args = parser.parse_args()

    if not args.plan.is_file():
        print(f"error: file not found: {args.plan}", file=sys.stderr)
        return 3

    report = check_plan(args.plan, args.workdir, args.model)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return EXIT_CODES[report["result"]]


if __name__ == "__main__":
    raise SystemExit(main())
