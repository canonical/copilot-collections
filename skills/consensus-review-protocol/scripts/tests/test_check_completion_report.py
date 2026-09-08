#!/usr/bin/env python3
"""Unit and regression tests for check_completion_report.py.

Run:
    python3 -m unittest skills/consensus-review-protocol/scripts/tests/test_check_completion_report.py -v
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import check_completion_report as ccr  # noqa: E402

TEMPLATE_PATH = SCRIPTS_DIR.parent / "references" / "completion-report-template.md"
FIXTURE_GOOD = Path(__file__).resolve().parent / "fixtures" / "completion-report-good.md"


def template_text() -> str:
    return TEMPLATE_PATH.read_text()


def good_report() -> str:
    return FIXTURE_GOOD.read_text()


def drop_section(text: str, heading: str) -> str:
    """Remove a whole `## heading` section from a report."""
    lines = text.splitlines()
    out, skipping = [], False
    for line in lines:
        if line.startswith("## "):
            skipping = line.strip() == f"## {heading}"
        if not skipping:
            out.append(line)
    return "\n".join(out) + "\n"


def extract_section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    out, collecting = [], False
    for line in lines:
        if line.startswith("## "):
            if collecting:
                break
            collecting = line.strip() == f"## {heading}"
        if collecting:
            out.append(line)
    return out


def move_section_to_end(text: str, heading: str) -> str:
    block = extract_section(text, heading)
    return drop_section(text, heading).rstrip("\n") + "\n\n" + "\n".join(block) + "\n"


def run_checks(report: str, final_round: bool = False) -> dict:
    return ccr.run_checks(report, template_text(), final_round)


def result_of(report: str, final_round: bool = False) -> str:
    return ccr.derive_result(run_checks(report, final_round))


class TestHeadingHelpers(unittest.TestCase):
    def test_normalise_collapses_whitespace(self):
        self.assertEqual(ccr.normalise_heading("  Plan   Reviewed "), "Plan Reviewed")

    def test_normalise_strips_version_integer(self):
        self.assertEqual(
            ccr.normalise_heading("Applied From resolutions-v64.md This Round (Phase 4b)"),
            "Applied From resolutions-vN.md This Round (Phase 4b)",
        )

    def test_normalise_strips_template_version_placeholder(self):
        self.assertEqual(
            ccr.normalise_heading("Applied From resolutions-v<N>.md This Round (Phase 4b)"),
            "Applied From resolutions-vN.md This Round (Phase 4b)",
        )

    def test_extract_headings_ignores_h1_and_h3(self):
        text = "# Title\n## One\n### Sub\n## Two\n"
        self.assertEqual(ccr.extract_headings(text), ["One", "Two"])


class TestPlaceholderExtraction(unittest.TestCase):
    def test_template_yields_placeholders(self):
        tokens = ccr.extract_placeholders(template_text())
        self.assertIn("<N>", tokens)
        self.assertIn("<ISO date>", tokens)

    def test_scaffolding_lines_are_excluded(self):
        tokens = ccr.extract_placeholders("# Completion Report Template\n*Referenced by <x>*\n")
        self.assertEqual(tokens, set())

    def test_sections_containing_placeholders_names_sections(self):
        report = "## Plan Reviewed\n- Input: <plan-name>\n## Next Step\nDone.\n"
        found = ccr.sections_containing_placeholders(report, {"<plan-name>"})
        self.assertEqual(found, ["Plan Reviewed"])

    def test_placeholder_in_header_is_attributed_to_pseudo_section(self):
        report = "Date: <ISO date>\n## Next Step\nDone.\n"
        found = ccr.sections_containing_placeholders(report, {"<ISO date>"})
        self.assertEqual(found, [ccr.HEADER_PSEUDO_SECTION])

    def test_section_reported_once_despite_several_placeholders(self):
        report = "## Plan Reviewed\n<a>\n<b>\n"
        found = ccr.sections_containing_placeholders(report, {"<a>", "<b>"})
        self.assertEqual(found, ["Plan Reviewed"])

    def test_html_comment_counts_as_leftover(self):
        report = "## Orchestrator Notes\n<!-- instruction -->\n"
        found = ccr.sections_containing_placeholders(report, set())
        self.assertEqual(found, ["Orchestrator Notes"])


class TestGoodReport(unittest.TestCase):
    def test_fixture_passes(self):
        self.assertEqual(result_of(good_report()), "pass")

    def test_every_check_ok(self):
        for name, check in run_checks(good_report()).items():
            with self.subTest(check=name):
                self.assertTrue(check["ok"], check["failed"])

    def test_optional_degraded_mode_absent_is_fine(self):
        self.assertNotIn("Consensus Protocol Degraded Mode", good_report())
        self.assertEqual(result_of(good_report()), "pass")

    def test_optional_orchestrator_notes_may_be_omitted(self):
        report = drop_section(good_report(), "Orchestrator Notes")
        self.assertEqual(result_of(report), "pass")


class TestRequiredSections(unittest.TestCase):
    def test_missing_required_section_fails(self):
        report = drop_section(good_report(), "Model Verdicts")
        checks = run_checks(report)
        self.assertFalse(checks["required_sections_present"]["ok"])
        self.assertIn("Model Verdicts", checks["required_sections_present"]["failed"])
        self.assertEqual(ccr.derive_result(checks), "fail")

    def test_several_missing_sections_all_listed(self):
        report = drop_section(drop_section(good_report(), "Token Cost"), "Companion Files Changed")
        failed = run_checks(report)["required_sections_present"]["failed"]
        self.assertIn("Token Cost", failed)
        self.assertIn("Companion Files Changed", failed)

    def test_version_bearing_heading_matches_despite_version(self):
        self.assertNotIn(
            "Applied From resolutions-vN.md This Round (Phase 4b)",
            run_checks(good_report())["required_sections_present"]["failed"],
        )


class TestSectionOrder(unittest.TestCase):
    def test_reordered_section_fails(self):
        report = move_section_to_end(good_report(), "Model Verdicts")
        checks = run_checks(report)
        self.assertFalse(checks["section_order"]["ok"])
        self.assertEqual(ccr.derive_result(checks), "fail")

    def test_in_order_report_passes_order_check(self):
        self.assertTrue(run_checks(good_report())["section_order"]["ok"])

    def test_unknown_heading_does_not_break_order_check(self):
        report = good_report().replace("## Token Cost", "## Extra Notes\n\nfree text\n\n## Token Cost")
        self.assertTrue(run_checks(report)["section_order"]["ok"])


class TestUnknownSections(unittest.TestCase):
    def test_unknown_section_is_advisory_not_failure(self):
        report = good_report().replace("## Token Cost", "## Extra Notes\n\nfree text\n\n## Token Cost")
        checks = run_checks(report)
        self.assertFalse(checks["no_unknown_sections"]["ok"])
        self.assertFalse(checks["no_unknown_sections"]["blocking"])
        self.assertEqual(ccr.derive_result(checks), "needs_review")


class TestPlaceholderCheck(unittest.TestCase):
    def test_unsubstituted_placeholder_fails(self):
        report = good_report().replace("(1120 lines, ~74 KB)", "(<line count> lines, ~<KB> KB)")
        checks = run_checks(report)
        self.assertFalse(checks["no_unsubstituted_placeholders"]["ok"])
        self.assertEqual(checks["no_unsubstituted_placeholders"]["failed"], ["Plan Reviewed"])
        self.assertEqual(ccr.derive_result(checks), "fail")

    def test_leftover_html_comment_fails(self):
        report = good_report().replace(
            "Setup sweep: 3 resolved-entry comments removed from the swept copy.",
            "<!-- Two lines are required content of this section -->",
        )
        self.assertFalse(run_checks(report)["no_unsubstituted_placeholders"]["ok"])

    def test_raw_template_fails_loudly(self):
        checks = run_checks(template_text())
        self.assertEqual(ccr.derive_result(checks), "fail")
        self.assertFalse(checks["no_template_scaffolding"]["ok"])
        self.assertFalse(checks["no_unsubstituted_placeholders"]["ok"])


class TestHeaderAndFencing(unittest.TestCase):
    def test_missing_title_line_fails(self):
        report = good_report().split("\n", 1)[1]
        checks = run_checks(report)
        self.assertIn("title_line", checks["header_present"]["failed"])
        self.assertEqual(ccr.derive_result(checks), "fail")

    def test_missing_date_line_fails(self):
        report = good_report().replace("Date: 2025-01-14\n", "")
        self.assertIn("date_line", run_checks(report)["header_present"]["failed"])

    def test_non_iso_date_fails(self):
        report = good_report().replace("Date: 2025-01-14", "Date: 14 January 2025")
        self.assertIn("date_line", run_checks(report)["header_present"]["failed"])

    def test_code_fenced_report_fails(self):
        report = "```markdown\n" + good_report() + "```\n"
        checks = run_checks(report)
        self.assertFalse(checks["not_code_fenced"]["ok"])
        self.assertEqual(ccr.derive_result(checks), "fail")


class TestFinalRound(unittest.TestCase):
    def _final_report(self) -> str:
        report = good_report()
        for heading in ("Phase Outcomes", "Findings This Round", "Model Verdicts", "Convergence Status"):
            report = drop_section(report, heading)
        return report

    def test_final_round_report_passes(self):
        self.assertEqual(result_of(self._final_report(), final_round=True), "pass")

    def test_same_report_fails_in_standard_mode(self):
        self.assertEqual(result_of(self._final_report(), final_round=False), "fail")

    def test_final_round_still_requires_phase_4b_sections(self):
        report = drop_section(self._final_report(), "File Listing")
        checks = run_checks(report, final_round=True)
        self.assertIn("File Listing", checks["required_sections_present"]["failed"])
        self.assertEqual(ccr.derive_result(checks), "fail")

    def test_phase_dependent_section_in_final_round_is_advisory(self):
        checks = run_checks(good_report(), final_round=True)
        self.assertFalse(checks["final_round_sections_omitted"]["ok"])
        self.assertFalse(checks["final_round_sections_omitted"]["blocking"])
        self.assertEqual(ccr.derive_result(checks), "needs_review")

    def test_final_round_check_absent_in_standard_mode(self):
        self.assertNotIn("final_round_sections_omitted", run_checks(good_report()))


class TestDeriveResult(unittest.TestCase):
    def test_pass_when_all_ok(self):
        checks = {"a": {"blocking": True, "ok": True, "failed": []}}
        self.assertEqual(ccr.derive_result(checks), "pass")

    def test_needs_review_on_non_blocking_failure(self):
        checks = {"a": {"blocking": False, "ok": False, "failed": ["x"]}}
        self.assertEqual(ccr.derive_result(checks), "needs_review")

    def test_blocking_failure_takes_precedence(self):
        checks = {
            "a": {"blocking": False, "ok": False, "failed": ["x"]},
            "b": {"blocking": True, "ok": False, "failed": ["y"]},
        }
        self.assertEqual(ccr.derive_result(checks), "fail")


class TestCli(unittest.TestCase):
    script = SCRIPTS_DIR / "check_completion_report.py"

    def _run(self, text: str, *args: str):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(text)
            path = handle.name
        try:
            return subprocess.run(
                [sys.executable, str(self.script), path, *args],
                capture_output=True,
                text=True,
            )
        finally:
            Path(path).unlink()

    def test_pass_exits_zero(self):
        self.assertEqual(self._run(good_report()).returncode, 0)

    def test_fail_exits_one(self):
        self.assertEqual(self._run(template_text()).returncode, 1)

    def test_needs_review_exits_two(self):
        report = good_report().replace("## Token Cost", "## Extra\n\ntext\n\n## Token Cost")
        self.assertEqual(self._run(report).returncode, 2)

    def test_missing_file_exits_three(self):
        proc = subprocess.run(
            [sys.executable, str(self.script), "/nonexistent/report.md"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 3)

    def test_json_output_shape(self):
        proc = self._run(good_report(), "--json")
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["result"], "pass")
        self.assertEqual(payload["mode"], "standard")
        self.assertIn("section_order", payload["checks"])
        self.assertIn("template_sections", payload["counts"])

    def test_final_round_flag_sets_mode(self):
        proc = self._run(good_report(), "--json", "--final-round")
        self.assertEqual(json.loads(proc.stdout)["mode"], "final_round")

    def test_template_override_is_honoured(self):
        proc = self._run(good_report(), "--json", "--template", str(TEMPLATE_PATH))
        self.assertEqual(json.loads(proc.stdout)["template"], str(TEMPLATE_PATH))

    def test_missing_template_exits_three(self):
        proc = self._run(good_report(), "--template", "/nonexistent/template.md")
        self.assertEqual(proc.returncode, 3)


if __name__ == "__main__":
    unittest.main()
