#!/usr/bin/env python3
"""Unit/regression tests for check_dependencies.py.

Run with:
    python3 -m unittest skills/consensus-review-protocol/scripts/tests/test_check_dependencies.py -v
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_dependencies.py"
REPO_ROOT = Path(__file__).resolve().parents[4]  # .../copilot-collections
REAL_RESOLUTIONS_FILE = (
    REPO_ROOT
    / ".github"
    / "consensus-review-protocol"
    / "consensus-review-protocol-skill"
    / "resolutions-v64.md"
)

_spec = importlib.util.spec_from_file_location("check_dependencies", SCRIPT_PATH)
cd = importlib.util.module_from_spec(_spec)
sys.modules["check_dependencies"] = cd
_spec.loader.exec_module(cd)


HEADER = "# Tech Lead Resolutions: TEST\n\n**Plan:** `plan.md`\n\n---\n\n## Instructions\n\nIgnored.\n\n"


def findings_doc(*entries: str) -> str:
    body = HEADER
    body += "## Findings for Tech Lead Resolution\n\n"
    body += "\n\n---\n\n".join(entries)
    body += "\n\n---\n\n## Open Questions\n\n"
    body += "\n\n## Direct Companion File Edits Since Last Round\n\nAnswer: None\n"
    return body


def entry(
    id_: str,
    resolution: str,
    depends_on: str | None = None,
    severity: str = "IMPORTANT",
    bold_depends: bool = True,
) -> str:
    lines = [f"### {id_}", "", f"**Severity:** {severity}", "**Source:** `MODEL-X`"]
    if depends_on is not None and bold_depends:
        lines.append(f"**Depends on:** {depends_on}")
    lines.extend(
        [
            "**Summary:** A plain finding.",
            "**Model positions:** All models agree.",
            "**Suggested fix:** Do the thing. Risk: none identified.",
            "",
        ]
    )
    if depends_on is not None and not bold_depends:
        lines.append(f"Depends on: {depends_on}")
    lines.append(f"Resolution: {resolution}")
    lines.append("Notes: Apply as written.")
    return "\n".join(lines)


def run_checks(*entries: str) -> dict:
    findings, _questions = cd.check_resolutions.load_entries(findings_doc(*entries))
    return cd.run_checks(findings)


def result_of(*entries: str) -> str:
    return cd.derive_result(run_checks(*entries))


class TestDependencyParsing(unittest.TestCase):
    def test_bold_depends_field_is_read(self):
        checks = run_checks(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "ACCEPT"))
        self.assertEqual(checks["depends_on_present"]["failed"], [])
        self.assertEqual(result_of(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "ACCEPT")), "pass")

    def test_plain_depends_field_is_read(self):
        checks = run_checks(
            entry("R1-A", "ACCEPT", depends_on="R1-B", bold_depends=False),
            entry("R1-B", "ACCEPT"),
        )
        self.assertTrue(checks["depends_on_present"]["ok"])

    def test_backticked_depends_value_is_normalised(self):
        checks = run_checks(entry("R1-A", "ACCEPT", depends_on="`R1-B`"), entry("R1-B", "ACCEPT"))
        self.assertTrue(checks["depends_on_present"]["ok"])


class TestSkipConditions(unittest.TestCase):
    def test_absent_dependency_fails(self):
        checks = run_checks(entry("R1-A", "ACCEPT", depends_on="R1-MISSING"))
        self.assertFalse(checks["depends_on_present"]["ok"])
        self.assertEqual(checks["depends_on_present"]["failed"], [{"id": "R1-A", "value": "R1-MISSING"}])
        self.assertEqual(cd.derive_result(checks), "fail")

    def test_rejected_dependency_fails(self):
        checks = run_checks(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "REJECT"))
        self.assertFalse(checks["depends_on_not_rejected"]["ok"])
        self.assertEqual(checks["depends_on_not_rejected"]["failed"], [{"id": "R1-A", "value": "R1-B"}])
        self.assertEqual(cd.derive_result(checks), "fail")

    def test_self_dependency_is_cycle(self):
        checks = run_checks(entry("R1-A", "ACCEPT", depends_on="R1-A"))
        self.assertFalse(checks["depends_on_acyclic"]["ok"])
        self.assertEqual(checks["depends_on_acyclic"]["failed"], ["R1-A"])
        self.assertEqual(cd.derive_result(checks), "fail")

    def test_multi_hop_cycle_fails_all_participants(self):
        checks = run_checks(
            entry("R1-A", "ACCEPT", depends_on="R1-B"),
            entry("R1-B", "ACCEPT", depends_on="R1-C"),
            entry("R1-C", "ACCEPT", depends_on="R1-A"),
        )
        self.assertEqual(checks["depends_on_acyclic"]["failed"], ["R1-A", "R1-B", "R1-C"])
        self.assertEqual(cd.derive_result(checks), "fail")

    def test_later_category_dependency_fails(self):
        checks = run_checks(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "MODIFY"))
        self.assertFalse(checks["depends_on_category_order"]["ok"])
        self.assertEqual(checks["depends_on_category_order"]["failed"], [{"id": "R1-A", "value": "R1-B"}])
        self.assertEqual(cd.derive_result(checks), "fail")

    def test_dependency_satisfied_within_same_category_passes(self):
        checks = run_checks(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "ACCEPT"))
        self.assertEqual(cd.derive_result(checks), "pass")

    def test_dependency_skipped_by_own_missing_dependency_cascades(self):
        checks = run_checks(
            entry("R1-A", "ACCEPT", depends_on="R1-B"),
            entry("R1-B", "ACCEPT", depends_on="R1-C"),
        )
        self.assertEqual(
            checks["depends_on_dependency_not_skipped"]["failed"],
            [{"id": "R1-A", "value": "R1-B"}],
        )
        self.assertEqual(cd.derive_result(checks), "fail")


class TestCategoryMapping(unittest.TestCase):
    def test_conflicted_resolution_maps_to_category_three(self):
        checks = run_checks(
            entry("R1-A", "MODIFY", depends_on="R1-B"),
            entry("R1-B", "ACCEPT", severity="IMPORTANT -- **CONFLICTED**"),
        )
        self.assertFalse(checks["depends_on_category_order"]["ok"])
        self.assertEqual(checks["depends_on_category_order"]["failed"], [{"id": "R1-A", "value": "R1-B"}])

    def test_conflicted_reject_dependency_is_rejected_not_ambiguous(self):
        checks = run_checks(
            entry("R1-A", "ACCEPT", depends_on="R1-B"),
            entry("R1-B", "REJECT", severity="IMPORTANT -- **CONFLICTED**"),
        )
        self.assertFalse(checks["depends_on_not_rejected"]["ok"])

    def test_invalid_resolution_category_is_advisory(self):
        checks = run_checks(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "MAYBE"))
        self.assertTrue(checks["depends_on_present"]["ok"])
        self.assertTrue(checks["depends_on_not_rejected"]["ok"])
        self.assertFalse(checks["depends_on_category_mapping_advisory"]["ok"])
        self.assertFalse(checks["depends_on_category_mapping_advisory"]["blocking"])
        self.assertEqual(cd.derive_result(checks), "needs_review")


class TestCountsAndResults(unittest.TestCase):
    def test_counts_include_findings_and_dependencies(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(findings_doc(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "ACCEPT")))
            path = Path(handle.name)
        try:
            report = cd.check_file(path)
        finally:
            path.unlink()
        self.assertEqual(report["counts"], {"findings": 2, "with_dependencies": 1})

    def test_derive_result_pass_when_all_ok(self):
        checks = {"a": {"blocking": True, "ok": True, "failed": []}}
        self.assertEqual(cd.derive_result(checks), "pass")

    def test_derive_result_needs_review_on_nonblocking_failure(self):
        checks = {"a": {"blocking": False, "ok": False, "failed": ["R1-A"]}}
        self.assertEqual(cd.derive_result(checks), "needs_review")

    def test_derive_result_blocking_failure_takes_precedence(self):
        checks = {
            "a": {"blocking": False, "ok": False, "failed": ["R1-A"]},
            "b": {"blocking": True, "ok": False, "failed": ["R1-B"]},
        }
        self.assertEqual(cd.derive_result(checks), "fail")


class TestCli(unittest.TestCase):
    def _run(self, text: str, *args: str):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(text)
            path = handle.name
        try:
            return subprocess.run(
                [sys.executable, str(SCRIPT_PATH), path, *args],
                capture_output=True,
                text=True,
            )
        finally:
            Path(path).unlink()

    def test_pass_exits_zero(self):
        proc = self._run(findings_doc(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "ACCEPT")))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_fail_exits_one(self):
        proc = self._run(findings_doc(entry("R1-A", "ACCEPT", depends_on="R1-MISSING")))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)

    def test_needs_review_exits_two(self):
        proc = self._run(findings_doc(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "MAYBE")))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)

    def test_missing_file_exits_three(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "/nonexistent/resolutions.md"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 3)

    def test_json_output_shape(self):
        proc = self._run(
            findings_doc(entry("R1-A", "ACCEPT", depends_on="R1-B"), entry("R1-B", "ACCEPT")),
            "--json",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["result"], "pass")
        self.assertEqual(payload["counts"]["with_dependencies"], 1)
        self.assertIn("depends_on_present", payload["checks"])
        self.assertIn("blocking", payload["checks"]["depends_on_present"])


class TestRealFileRegression(unittest.TestCase):
    @unittest.skipUnless(REAL_RESOLUTIONS_FILE.exists(), "real resolutions-v64.md fixture not present")
    def test_real_resolutions_v64_passes(self):
        report = cd.check_file(REAL_RESOLUTIONS_FILE)
        self.assertEqual(report["result"], "pass")
        self.assertEqual(report["counts"], {"findings": 16, "with_dependencies": 0})


if __name__ == "__main__":
    unittest.main()
