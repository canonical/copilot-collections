#!/usr/bin/env python3
"""Unit/regression tests for session_stats.py.

Run with:
    python3 -m unittest skills/consensus-review-protocol/scripts/tests/test_session_stats.py -v
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = Path(__file__).resolve().parents[4]
REAL_WORKDIR = (
    REPO_ROOT / ".github" / "consensus-review-protocol" / "consensus-review-protocol-skill"
)

sys.path.insert(0, str(SCRIPTS_DIR))

import session_stats as ss  # noqa: E402


def write(path: Path, text: str = "one two\nthree\n") -> Path:
    path.write_text(text)
    return path


class WorkdirCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.workdir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def stats(self, plan: Path | None = None) -> dict:
        return ss.collect_stats(self.workdir, plan)


class TestFileClassification(WorkdirCase):
    def test_empty_workdir_behaviour(self):
        report = self.stats()
        self.assertEqual(report["counts"]["completed_non_final_rounds"], 0)
        self.assertEqual(report["counts"]["artifacts_generated"]["total_files"], 0)
        self.assertEqual(report["counts"]["artifacts_generated"]["review_files"], 0)
        self.assertEqual(report["counts"]["total_workdir_words"], 0)
        self.assertEqual(report["counts"]["model_slugs"]["distinct_count"], 0)
        self.assertIsNone(report["counts"]["plan_version_span"])
        self.assertEqual(
            report["counts"]["tech_lead_decisions"],
            {"ACCEPT": 0, "MODIFY": 0, "REJECT": 0},
        )

    def test_round_artifact_and_review_counts(self):
        write(self.workdir / "consolidated-v1.md")
        write(self.workdir / "consolidated-v2.md")
        write(self.workdir / "resolutions-v2.md")
        write(self.workdir / "gpt-5-blue-v1.md")
        write(self.workdir / "gpt-5-red-v1.md")
        write(self.workdir / "gpt-5-purple-v1.md")
        write(self.workdir / "review-history.md")

        counts = self.stats()["counts"]
        self.assertEqual(counts["completed_non_final_rounds"], 2)
        self.assertEqual(counts["artifacts_generated"]["total_files"], 7)
        self.assertEqual(counts["artifacts_generated"]["review_files"], 3)

    def test_dot_files_and_partial_files_are_excluded(self):
        write(self.workdir / "consolidated-v1.md")
        write(self.workdir / ".resolutions-v1-swept.md", "many ignored words")
        write(self.workdir / "claude-blue-v1.md.partial", "many ignored words")

        counts = self.stats()["counts"]
        self.assertEqual(counts["artifacts_generated"]["total_files"], 1)
        self.assertEqual(counts["artifacts_generated"]["review_files"], 0)
        self.assertEqual(counts["total_workdir_words"], 3)


class TestModelSlugsAndVersions(WorkdirCase):
    def test_distinct_slug_parsing_deduplicates_across_phases(self):
        write(self.workdir / "claude-opus-latest-blue-v9.md")
        write(self.workdir / "claude-opus-latest-red-v9.md")
        write(self.workdir / "gpt-5-6-sol-purple-v9.md")

        model_slugs = self.stats()["counts"]["model_slugs"]
        self.assertEqual(model_slugs["distinct_count"], 2)
        self.assertEqual(model_slugs["slugs"], ["claude-opus-latest", "gpt-5-6-sol"])
        self.assertIn("Alias-style names", model_slugs["caveat"])

    def test_version_span_is_numeric_not_lexical(self):
        write(self.workdir / "consolidated-v9.md")
        write(self.workdir / "resolutions-v10.md")
        write(self.workdir / "consolidated-v2.md")

        self.assertEqual(self.stats()["counts"]["plan_version_span"], {"first": 2, "final": 10})


class TestCounts(WorkdirCase):
    def test_workdir_words_and_final_plan_words_lines(self):
        write(self.workdir / "consolidated-v1.md", "one two\nthree\n")
        write(self.workdir / "review-history.md", "four\n\nfive six")
        plan = write(self.workdir / "final-plan.md", "alpha beta\n\ngamma\n")

        report = self.stats(plan)
        self.assertEqual(report["counts"]["total_workdir_words"], 9)
        self.assertEqual(
            report["final_plan"],
            {"path": str(plan), "found": True, "words": 3, "lines": 3},
        )

    def test_missing_plan_file_degrades_gracefully(self):
        missing = self.workdir / "missing-plan.md"
        report = self.stats(missing)
        self.assertEqual(report["final_plan"], {"path": str(missing), "found": False})

    def test_decision_distribution_uses_anchored_exact_values(self):
        write(
            self.workdir / "resolutions-v2.md",
            "\n".join(
                [
                    "Resolution: ACCEPT",
                    "Resolution:   MODIFY   ",
                    "Resolution: REJECT",
                    "Resolution: <!-- ACCEPT | REJECT | MODIFY -->",
                    "Resolution: ACCEPT with caveat",
                ]
            ),
        )
        write(self.workdir / "resolutions-v3.md", "Resolution: ACCEPT\n")

        self.assertEqual(
            self.stats()["counts"]["tech_lead_decisions"],
            {"ACCEPT": 2, "MODIFY": 1, "REJECT": 1},
        )


class TestCli(WorkdirCase):
    script = SCRIPTS_DIR / "session_stats.py"

    def test_json_output_shape(self):
        write(self.workdir / "consolidated-v1.md")
        proc = subprocess.run(
            [sys.executable, str(self.script), str(self.workdir), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["workdir"], str(self.workdir))
        self.assertIn("completed_non_final_rounds", payload["counts"])
        self.assertIn("artifacts_generated", payload["counts"])
        self.assertIsNone(payload["final_plan"])

    def test_positional_plan_argument(self):
        plan = write(self.workdir / "final.md", "a b\n")
        proc = subprocess.run(
            [sys.executable, str(self.script), str(self.workdir), str(plan), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["final_plan"]["words"], 2)

    def test_plan_option(self):
        plan = write(self.workdir / "final.md", "a b c\n")
        proc = subprocess.run(
            [sys.executable, str(self.script), str(self.workdir), "--plan", str(plan), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["final_plan"]["lines"], 1)

    def test_missing_workdir_exits_three(self):
        proc = subprocess.run(
            [sys.executable, str(self.script), str(self.workdir / "missing")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 3)

    def test_plan_supplied_twice_exits_three(self):
        plan = write(self.workdir / "final.md", "a\n")
        proc = subprocess.run(
            [
                sys.executable,
                str(self.script),
                str(self.workdir),
                str(plan),
                "--plan",
                str(plan),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 3)


class TestFormatting(unittest.TestCase):
    def test_format_span(self):
        self.assertEqual(ss.format_span({"first": 9, "final": 10}), "v9 to v10")
        self.assertEqual(ss.format_span(None), "none")


class TestRealWorkdirSmoke(unittest.TestCase):
    @unittest.skipUnless(REAL_WORKDIR.exists(), "real consensus-review-protocol workdir absent")
    def test_real_workdir_runs_with_plausible_non_negative_numbers(self):
        report = ss.collect_stats(REAL_WORKDIR)
        counts = report["counts"]
        self.assertGreaterEqual(counts["completed_non_final_rounds"], 0)
        self.assertGreaterEqual(counts["artifacts_generated"]["total_files"], 0)
        self.assertGreaterEqual(counts["artifacts_generated"]["review_files"], 0)
        self.assertGreaterEqual(counts["total_workdir_words"], 0)
        self.assertGreaterEqual(counts["model_slugs"]["distinct_count"], 0)
        for value in counts["tech_lead_decisions"].values():
            self.assertGreaterEqual(value, 0)


if __name__ == "__main__":
    unittest.main()
