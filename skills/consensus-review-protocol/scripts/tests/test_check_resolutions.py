#!/usr/bin/env python3
"""Unit/regression tests for check_resolutions.py.

Run with:
    python3 -m unittest discover -s skills/consensus-review-protocol/scripts/tests -v
or:
    python3 skills/consensus-review-protocol/scripts/tests/test_check_resolutions.py
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_resolutions.py"
REPO_ROOT = Path(__file__).resolve().parents[4]  # .../copilot-collections
REAL_RESOLUTIONS_FILE = (
    REPO_ROOT
    / ".github"
    / "consensus-review-protocol"
    / "consensus-review-protocol-skill"
    / "resolutions-v64.md"
)

_spec = importlib.util.spec_from_file_location("check_resolutions", SCRIPT_PATH)
cr = importlib.util.module_from_spec(_spec)
sys.modules["check_resolutions"] = cr
_spec.loader.exec_module(cr)


HEADER = "# Tech Lead Resolutions: TEST\n\n**Plan:** `plan.md`\n\n---\n\n## Instructions\n\nIgnored.\n\n"


def findings_doc(*entries: str, open_questions: str = "") -> str:
    body = HEADER
    body += "## Findings for Tech Lead Resolution\n\n"
    body += "\n\n---\n\n".join(entries)
    body += "\n\n---\n\n## Open Questions\n\n"
    body += open_questions
    body += "\n\n## Direct Companion File Edits Since Last Round\n\nAnswer: None\n"
    return body


def entry(
    id_: str,
    resolution: str,
    notes: str = "",
    severity: str = "IMPORTANT",
    summary: str = "A plain finding with no companion-file reference.",
    presents_options: str | None = None,
) -> str:
    lines = [f"### {id_}", "", f"**Severity:** {severity}"]
    if presents_options:
        lines.append(f"**Presents options:** {presents_options}")
    lines.append(f"**Summary:** {summary}")
    lines.append("**Model positions:** All models agree.")
    lines.append("**Suggested fix:** Do the thing.")
    lines.append("")
    lines.append(f"Resolution: {resolution}")
    lines.append(f"Notes: {notes}")
    return "\n".join(lines)


def question(id_: str, answer: str = "") -> str:
    return f"### {id_} -- some open question\n\n**Finding ID:** `R1-X`\n\nAnswer: {answer}"


class TestParsing(unittest.TestCase):
    def test_minimal_pass(self):
        doc = findings_doc(entry("R1-PLAN-MERGED-B1", "ACCEPT"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertEqual(cr.derive_result(checks), "pass")

    def test_entry_id_extraction(self):
        doc = findings_doc(entry("R2-PLAN-MERGED-I3", "REJECT"))
        findings, _ = cr.load_entries(doc)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].id, "R2-PLAN-MERGED-I3")


class TestRule1ResolutionValid(unittest.TestCase):
    def test_valid_values_pass(self):
        for value in ("ACCEPT", "reject", "  MODIFY  "):
            with self.subTest(value=value):
                doc = findings_doc(entry("R1-X", value, notes="ok" if "MODIFY" in value.upper() else ""))
                findings, questions = cr.load_entries(doc)
                checks = cr.run_checks(findings, questions)
                self.assertTrue(checks["rule_1_resolution_valid"]["ok"])

    def test_invalid_value_fails(self):
        doc = findings_doc(entry("R1-X", "MAYBE"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_1_resolution_valid"]["ok"])
        self.assertEqual(checks["rule_1_resolution_valid"]["failed"], [{"id": "R1-X", "value": "MAYBE"}])
        self.assertEqual(cr.derive_result(checks), "fail")

    def test_trailing_text_fails(self):
        doc = findings_doc(entry("R1-X", "ACCEPT (with reservations)"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_1_resolution_valid"]["ok"])
        self.assertEqual(
            checks["rule_1_resolution_valid"]["failed"],
            [{"id": "R1-X", "value": "ACCEPT (with reservations)"}],
        )

    def test_missing_resolution_field_fails(self):
        text = (
            "### R1-X\n\n**Severity:** IMPORTANT\n**Summary:** no resolution field at all.\n"
        )
        doc = findings_doc(text)
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_1_resolution_valid"]["ok"])
        self.assertEqual(checks["rule_1_resolution_valid"]["failed"], [{"id": "R1-X", "value": None}])


class TestRule2NotesRequired(unittest.TestCase):
    def test_modify_blank_notes_fails(self):
        doc = findings_doc(entry("R2-X", "MODIFY", notes=""))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_2_notes_required"]["ok"])
        self.assertEqual(checks["rule_2_notes_required"]["failed"], ["R2-X"])
        self.assertEqual(cr.derive_result(checks), "fail")

    def test_modify_placeholder_notes_fails(self):
        doc = findings_doc(entry("R2-X", "MODIFY", notes="<!-- fill in -->"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_2_notes_required"]["ok"])

    def test_modify_with_notes_passes(self):
        doc = findings_doc(entry("R2-X", "MODIFY", notes="Apply option A."))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_2_notes_required"]["ok"])
        self.assertEqual(cr.derive_result(checks), "pass")

    def test_conflicted_blank_notes_fails_regardless_of_resolution(self):
        doc = findings_doc(entry("R2-X", "ACCEPT", notes="", severity="NICE-TO-HAVE -- **CONFLICTED**"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_2_notes_required"]["ok"])
        self.assertEqual(checks["rule_2_notes_required"]["failed"], ["R2-X"])

    def test_accept_reject_blank_notes_is_fine(self):
        doc = findings_doc(entry("R2-A", "ACCEPT", notes=""), entry("R2-B", "REJECT", notes=""))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_2_notes_required"]["ok"])
        self.assertEqual(cr.derive_result(checks), "pass")


class TestRule2CompanionTargetAdvisory(unittest.TestCase):
    def test_companion_path_with_blank_notes_is_needs_review_not_fail(self):
        doc = findings_doc(
            entry(
                "R2-N1",
                "ACCEPT",
                notes="",
                summary="Amend `references/review-general.md` to add a clause.",
            )
        )
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_2_notes_required"]["ok"])  # not a blocking rule 2 hit
        self.assertFalse(checks["rule_2_companion_target_advisory"]["ok"])
        self.assertEqual(checks["rule_2_companion_target_advisory"]["failed"], ["R2-N1"])
        self.assertEqual(cr.derive_result(checks), "needs_review")

    def test_companion_path_with_notes_present_is_ok(self):
        doc = findings_doc(
            entry(
                "R2-N2",
                "ACCEPT",
                notes="Target file: `references/review-general.md` -- add clause X.",
                summary="Amend `references/review-general.md` to add a clause.",
            )
        )
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_2_companion_target_advisory"]["ok"])
        self.assertEqual(cr.derive_result(checks), "pass")

    def test_no_md_path_mention_never_flagged(self):
        doc = findings_doc(entry("R2-N3", "ACCEPT", notes="", summary="No file paths mentioned at all."))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_2_companion_target_advisory"]["ok"])
        self.assertEqual(cr.derive_result(checks), "pass")

    def test_blocking_failure_takes_precedence_over_needs_review(self):
        doc = findings_doc(
            entry("R2-BAD", "MAYBE"),
            entry(
                "R2-N1",
                "ACCEPT",
                notes="",
                summary="Amend `references/review-general.md` to add a clause.",
            ),
        )
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertEqual(cr.derive_result(checks), "fail")


class TestRule3AnswerRequired(unittest.TestCase):
    def test_blank_answer_fails(self):
        doc = findings_doc(entry("R1-X", "ACCEPT"), open_questions=question("Q1", answer=""))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_3_answer_required"]["ok"])
        self.assertEqual(checks["rule_3_answer_required"]["failed"], ["Q1"])
        self.assertEqual(cr.derive_result(checks), "fail")

    def test_placeholder_answer_fails(self):
        doc = findings_doc(entry("R1-X", "ACCEPT"), open_questions=question("Q1", answer="<!-- pending -->"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_3_answer_required"]["ok"])

    def test_filled_answer_passes(self):
        doc = findings_doc(entry("R1-X", "ACCEPT"), open_questions=question("Q1", answer="Use option B."))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_3_answer_required"]["ok"])
        self.assertEqual(cr.derive_result(checks), "pass")

    def test_no_open_questions_is_vacuously_satisfied(self):
        doc = findings_doc(entry("R1-X", "ACCEPT"))
        findings, questions = cr.load_entries(doc)
        self.assertEqual(questions, [])
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_3_answer_required"]["ok"])


class TestRule4AcceptVsOptions(unittest.TestCase):
    def test_accept_with_presents_options_fails(self):
        doc = findings_doc(entry("R4-X", "ACCEPT", presents_options="A, B"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertFalse(checks["rule_4_accept_vs_options"]["ok"])
        self.assertEqual(checks["rule_4_accept_vs_options"]["failed"], [{"id": "R4-X", "options": "A, B"}])
        self.assertEqual(cr.derive_result(checks), "fail")

    def test_modify_with_presents_options_passes(self):
        doc = findings_doc(entry("R4-X", "MODIFY", notes="Option A.", presents_options="A, B"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_4_accept_vs_options"]["ok"])
        self.assertEqual(cr.derive_result(checks), "pass")

    def test_reject_with_presents_options_passes(self):
        doc = findings_doc(entry("R4-X", "REJECT", presents_options="A, B"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_4_accept_vs_options"]["ok"])

    def test_accept_without_presents_options_passes(self):
        doc = findings_doc(entry("R4-X", "ACCEPT"))
        findings, questions = cr.load_entries(doc)
        checks = cr.run_checks(findings, questions)
        self.assertTrue(checks["rule_4_accept_vs_options"]["ok"])


class TestDeriveResultPrecedence(unittest.TestCase):
    def test_pass_when_all_ok(self):
        checks = {
            "a": {"blocking": True, "ok": True, "failed": []},
            "b": {"blocking": False, "ok": True, "failed": []},
        }
        self.assertEqual(cr.derive_result(checks), "pass")

    def test_needs_review_when_only_nonblocking_fails(self):
        checks = {
            "a": {"blocking": True, "ok": True, "failed": []},
            "b": {"blocking": False, "ok": False, "failed": ["X"]},
        }
        self.assertEqual(cr.derive_result(checks), "needs_review")

    def test_fail_when_blocking_fails_even_if_nonblocking_ok(self):
        checks = {
            "a": {"blocking": True, "ok": False, "failed": ["X"]},
            "b": {"blocking": False, "ok": True, "failed": []},
        }
        self.assertEqual(cr.derive_result(checks), "fail")

    def test_fail_takes_precedence_over_needs_review(self):
        checks = {
            "a": {"blocking": True, "ok": False, "failed": ["X"]},
            "b": {"blocking": False, "ok": False, "failed": ["Y"]},
        }
        self.assertEqual(cr.derive_result(checks), "fail")


class TestCLI(unittest.TestCase):
    def test_exit_codes(self):
        import subprocess
        import tempfile

        cases = [
            (findings_doc(entry("R1-X", "ACCEPT")), 0),
            (findings_doc(entry("R1-X", "MAYBE")), 1),
            (
                findings_doc(
                    entry("R1-X", "ACCEPT", notes="", summary="See `references/review-general.md`.")
                ),
                2,
            ),
        ]
        for doc, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
                    f.write(doc)
                    path = f.name
                try:
                    proc = subprocess.run(
                        [sys.executable, str(SCRIPT_PATH), path, "--json"],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(proc.returncode, expected_code, proc.stdout + proc.stderr)
                finally:
                    Path(path).unlink()

    def test_file_not_found_exit_code(self):
        import subprocess

        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "/nonexistent/path.md"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 3)


if __name__ == "__main__":
    unittest.main()
