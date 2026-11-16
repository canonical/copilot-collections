#!/usr/bin/env python3
"""Unit and regression tests for check_review_history.py.

Run:
    python3 -m unittest skills/consensus-review-protocol/scripts/tests/test_check_review_history.py -v
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

import check_review_history as crh  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[4]  # .../copilot-collections
REAL_REVIEW_HISTORY_FILE = (
    REPO_ROOT
    / ".github"
    / "consensus-review-protocol"
    / "consensus-review-protocol-skill"
    / "review-history.md"
)
OLD_REVIEW_HISTORY_FILE = (
    REPO_ROOT
    / ".github"
    / "consensus-review-plan"
    / "consensus-review-protocol-skill"
    / "review-history.md"
)


def history_doc(*entries: str, header: str | None = None) -> str:
    if header is None:
        header = "# Review History\n\n*Complete review history for `plan.md`.*\n\n---\n\n"
    return header + "\n\n".join(entries)


def entry(
    round_: int = 2,
    version: int = 1,
    date: str = "2025-01-02",
    plan_file: str = "plan-v2.md",
    supersession: str | None = None,
    sub_agent_failures: str | None = None,
    omit: str | None = None,
    malformed_heading: bool = False,
) -> str:
    lines = []
    heading = f"### {plan_file} — {date}"
    lines.append(f"### not-a-valid-heading {date}" if malformed_heading else heading)
    lines.append("")
    if omit != "round":
        lines.append(
            f"**Round {round_} reviewing plan v{version}** | "
            f"Input: `plan-v{version}.md` | Output: `{plan_file}` | "
            f"Resolutions applied from: `resolutions-v{version}.md`"
        )
    if omit != "models":
        lines.append("**Models:** gpt, claude")
    if supersession is not None and omit != "supersession":
        lines.append(f"*Supersession note: {supersession}*")
    if omit != "key_changes":
        lines.append(f"**Key changes from v{version}:**")
        if omit != "bullet":
            lines.append("- R1 — Applied the finding.")
    if omit != "phase_4b_skips":
        lines.append(f"**Round {round_} Phase 4b skips:** 0 — none")
    if omit != "recorded_noops":
        lines.append("**Recorded no-ops:** none")
    if sub_agent_failures is not None:
        lines.append(f"**Sub-agent failures:** {sub_agent_failures}")
    if omit != "convergence":
        lines.append("**Convergence:** GO.")
    return "\n".join(lines)


def result_of(text: str, recent: int = 5) -> str:
    header, entries = crh.parse_review_history(text)
    return crh.derive_result(crh.run_checks(header, entries, recent))


class TestReviewHistoryParsing(unittest.TestCase):
    def test_well_formed_multi_entry_file_passes(self):
        doc = history_doc(
            entry(round_=3, version=2, date="2025-01-03", plan_file="plan-v3.md"),
            entry(round_=2, version=1, date="2025-01-02", plan_file="plan-v2.md"),
        )
        self.assertEqual(result_of(doc), "pass")

    def test_single_entry_file_passes(self):
        self.assertEqual(result_of(history_doc(entry())), "pass")

    def test_zero_entry_file_passes(self):
        self.assertEqual(result_of(history_doc()), "pass")

    def test_counts_entries(self):
        report = crh.check_text(history_doc(entry(), entry(round_=1, date="2025-01-01")), Path("x.md"))
        self.assertEqual(report["counts"]["entries"], 2)
        self.assertEqual(report["counts"]["strict_entries"], 2)


class TestHeader(unittest.TestCase):
    def test_missing_file_header_fails(self):
        doc = "### plan-v1.md — 2025-01-01\n"
        header, entries = crh.parse_review_history(doc)
        checks = crh.run_checks(header, entries)
        self.assertFalse(checks["file_header_wellformed"]["ok"])
        self.assertIn("title", checks["file_header_wellformed"]["failed"])
        self.assertEqual(crh.derive_result(checks), "fail")

    def test_heading_before_separator_fails(self):
        bad_header = "# Review History\n\n### stray\n\n*desc*\n\n---\n\n"
        header, entries = crh.parse_review_history(history_doc(entry(), header=bad_header))
        checks = crh.run_checks(header, entries)
        self.assertFalse(checks["file_header_wellformed"]["ok"])
        self.assertIn("entry_before_separator", checks["file_header_wellformed"]["failed"])


class TestEntryFormat(unittest.TestCase):
    def test_malformed_entry_heading_fails(self):
        checks = crh.run_checks(*crh.parse_review_history(history_doc(entry(malformed_heading=True))))
        self.assertFalse(checks["entry_heading_format"]["ok"])
        self.assertEqual(crh.derive_result(checks), "fail")

    def test_clean_round_does_not_require_sub_agent_failures_line(self):
        checks = crh.run_checks(*crh.parse_review_history(history_doc(entry(sub_agent_failures=None))))
        self.assertTrue(checks["required_lines_present"]["ok"])
        self.assertEqual(crh.derive_result(checks), "pass")

    def test_sub_agent_failures_line_is_allowed_when_present(self):
        checks = crh.run_checks(
            *crh.parse_review_history(history_doc(entry(sub_agent_failures="claude — red — timeout")))
        )
        self.assertTrue(checks["required_lines_present"]["ok"])
        self.assertEqual(crh.derive_result(checks), "pass")

    def test_supersession_note_wrong_position_is_advisory(self):
        lines = entry(supersession="Declared in resolutions-v1.md.").splitlines()
        note = lines.pop(3)
        lines.append(note)
        checks = crh.run_checks(*crh.parse_review_history(history_doc("\n".join(lines))))
        self.assertFalse(checks["supersession_note_position"]["ok"])
        self.assertFalse(checks["supersession_note_position"]["blocking"])
        self.assertEqual(crh.derive_result(checks), "needs_review")

    def test_legacy_entry_format_is_advisory(self):
        entries = [entry(round_=6, version=5, date="2025-01-06", plan_file="plan-v6.md")]
        for number in range(5, 0, -1):
            entries.append(
                entry(
                    round_=number,
                    version=number - 1,
                    date=f"2025-01-0{number}",
                    plan_file=f"plan-v{number}.md",
                    malformed_heading=number == 1,
                )
            )
        checks = crh.run_checks(*crh.parse_review_history(history_doc(*entries)))
        self.assertTrue(checks["entry_heading_format"]["ok"])
        self.assertFalse(checks["legacy_entry_format_advisory"]["ok"])
        self.assertEqual(crh.derive_result(checks), "needs_review")


class TestRequiredLines(unittest.TestCase):
    def test_each_required_line_missing_fails(self):
        omissions = (
            "round",
            "models",
            "key_changes",
            "bullet",
            "phase_4b_skips",
            "recorded_noops",
            "convergence",
        )
        for omission in omissions:
            with self.subTest(omission=omission):
                checks = crh.run_checks(*crh.parse_review_history(history_doc(entry(omit=omission))))
                self.assertFalse(checks["required_lines_present"]["ok"])
                self.assertEqual(checks["required_lines_present"]["failed"], ["plan-v2.md — 2025-01-02"])
                self.assertEqual(crh.derive_result(checks), "fail")


class TestOrdering(unittest.TestCase):
    def test_out_of_order_rounds_fail(self):
        doc = history_doc(
            entry(round_=1, version=1, date="2025-01-03", plan_file="plan-v1.md"),
            entry(round_=2, version=2, date="2025-01-02", plan_file="plan-v2.md"),
        )
        checks = crh.run_checks(*crh.parse_review_history(doc))
        self.assertFalse(checks["entries_newest_first"]["ok"])
        self.assertEqual(checks["entries_newest_first"]["failed"], ["plan-v1.md — 2025-01-03"])
        self.assertEqual(crh.derive_result(checks), "fail")

    def test_out_of_order_dates_fail_when_rounds_unavailable(self):
        doc = history_doc(
            entry(round_=1, date="2025-01-01", plan_file="plan-v1.md", omit="round"),
            entry(round_=2, date="2025-01-02", plan_file="plan-v2.md", omit="round"),
        )
        checks = crh.run_checks(*crh.parse_review_history(doc))
        self.assertFalse(checks["entries_newest_first"]["ok"])

    def test_equal_date_entries_do_not_fail(self):
        doc = history_doc(
            entry(round_=3, version=3, date="2025-01-02", plan_file="plan-v3.md"),
            entry(round_=2, version=2, date="2025-01-02", plan_file="plan-v2.md"),
        )
        self.assertEqual(result_of(doc), "pass")


class TestDeriveResult(unittest.TestCase):
    def test_pass_when_all_ok(self):
        checks = {"a": {"blocking": True, "ok": True, "failed": []}}
        self.assertEqual(crh.derive_result(checks), "pass")

    def test_needs_review_on_non_blocking_failure(self):
        checks = {"a": {"blocking": False, "ok": False, "failed": ["x"]}}
        self.assertEqual(crh.derive_result(checks), "needs_review")

    def test_blocking_failure_takes_precedence(self):
        checks = {
            "a": {"blocking": False, "ok": False, "failed": ["x"]},
            "b": {"blocking": True, "ok": False, "failed": ["y"]},
        }
        self.assertEqual(crh.derive_result(checks), "fail")


class TestCli(unittest.TestCase):
    script = SCRIPTS_DIR / "check_review_history.py"

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
        self.assertEqual(self._run(history_doc(entry())).returncode, 0)

    def test_fail_exits_one(self):
        self.assertEqual(self._run(history_doc(entry(omit="models"))).returncode, 1)

    def test_needs_review_exits_two(self):
        lines = entry(supersession="Declared in resolutions-v1.md.").splitlines()
        note = lines.pop(3)
        lines.append(note)
        self.assertEqual(self._run(history_doc("\n".join(lines))).returncode, 2)

    def test_missing_file_exits_three(self):
        proc = subprocess.run(
            [sys.executable, str(self.script), "/nonexistent/review-history.md"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 3)

    def test_usage_error_exits_three(self):
        proc = subprocess.run([sys.executable, str(self.script)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 3)

    def test_json_output_shape(self):
        proc = self._run(history_doc(entry()), "--json")
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["result"], "pass")
        self.assertEqual(payload["counts"]["entries"], 1)
        self.assertIn("file_header_wellformed", payload["checks"])
        self.assertIn("legacy_entries", payload["counts"])


class TestRealReviewHistory(unittest.TestCase):
    @unittest.skipUnless(
        REAL_REVIEW_HISTORY_FILE.exists() or OLD_REVIEW_HISTORY_FILE.exists(),
        "real review-history.md artifact not present",
    )
    def test_real_review_history_parses_entries(self):
        path = REAL_REVIEW_HISTORY_FILE if REAL_REVIEW_HISTORY_FILE.exists() else OLD_REVIEW_HISTORY_FILE
        report = crh.check_file(path)
        self.assertGreater(report["counts"]["entries"], 0)
        self.assertIn(report["result"], {"pass", "needs_review", "fail"})


if __name__ == "__main__":
    unittest.main()
