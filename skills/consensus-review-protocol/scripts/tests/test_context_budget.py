#!/usr/bin/env python3
"""Unit and regression tests for context_budget.py.

Run:
    python3 -m unittest skills/consensus-review-protocol/scripts/tests/test_context_budget.py -v
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
sys.path.insert(0, str(SCRIPTS_DIR))

import context_budget as cb  # noqa: E402

REAL_PLAN = REPO_ROOT / "skills" / "consensus-review-protocol" / "SKILL.md"
REAL_WORKDIR = (
    REPO_ROOT
    / ".github"
    / "consensus-review-protocol"
    / "consensus-review-protocol-skill"
)


def words(count: int, prefix: str = "w") -> str:
    return " ".join(f"{prefix}{i}" for i in range(count))


def write(path: Path, count: int, prefix: str | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(words(count, prefix or path.stem))
    return path


def write_refs(root: Path, counts: dict[str, int] | None = None) -> Path:
    counts = counts or {}
    for name in {
        "review-general.md",
        "review-mode-blue.md",
        "review-mode-red.md",
        "review-mode-purple.md",
        "phase-4a-output-formats.md",
        "phase-4c-output-formats.md",
        "completion-report-template.md",
    }:
        write(root / name, counts.get(name, 0), name)
    return root


class BudgetFixture:
    def __init__(self, root: Path, version: int = 7):
        self.root = root
        self.plan = root / f"plan-v{version}.md"
        self.workdir = root / "work"
        self.refs = root / "refs"
        self.version = version
        self.workdir.mkdir()
        self.refs.mkdir()

    def report(self, review_history_entries: int = 5) -> dict:
        return cb.check_budget(self.plan, self.workdir, self.refs, review_history_entries)


class TestCounting(unittest.TestCase):
    def test_per_phase_accumulation_is_exact_for_all_four_phases(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp))
            write(fx.plan, 10)
            write(fx.workdir / "resolutions-v7.md", 4)
            write(fx.workdir / "alpha-blue-v7.md", 2)
            write(fx.workdir / "beta-blue-v7.md", 3)
            write(fx.workdir / "alpha-red-v7.md", 5)
            write(fx.workdir / "beta-red-v7.md", 7)
            write(fx.workdir / "alpha-purple-v7.md", 11)
            fx.workdir.joinpath("review-history.md").write_text("## H1\nold\n\n## H2\nnew\n")
            write_refs(
                fx.refs,
                {
                    "review-general.md": 2,
                    "review-mode-blue.md": 3,
                    "review-mode-red.md": 5,
                    "review-mode-purple.md": 7,
                    "phase-4a-output-formats.md": 11,
                    "phase-4c-output-formats.md": 13,
                    "completion-report-template.md": 17,
                },
            )

            report = fx.report(review_history_entries=2)

            self.assertEqual(report["version"], 7)
            self.assertEqual(report["plan_words"], 10)
            self.assertEqual(report["phases"]["1"]["words"], 10 + 4 + 2 + 3)
            self.assertEqual(report["phases"]["2"]["words"], 10 + 4 + 2 + 3 + 2 + 5)
            self.assertEqual(report["phases"]["3"]["words"], 10 + 4 + 2 + 3 + 5 + 7 + 2 + 7)
            self.assertEqual(
                report["phases"]["4"]["words"],
                10 + 4 + 2 + 3 + 5 + 7 + 11 + 2 + 11 + 13 + 17 + 6,
            )
            self.assertEqual(report["heaviest_phase"], "4")

    def test_plan_is_counted_once_per_subagent_not_multiplied_by_model_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp), version=1)
            write(fx.plan, 100)
            write(fx.workdir / "a-blue-v1.md", 1)
            write(fx.workdir / "b-blue-v1.md", 1)
            write(fx.workdir / "c-blue-v1.md", 1)
            write_refs(fx.refs)

            report = fx.report()

            self.assertEqual(report["phases"]["2"]["words"], 103)
            self.assertNotEqual(report["phases"]["2"]["words"], 303)

    def test_missing_resolutions_file_is_handled(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp), version=3)
            write(fx.plan, 5)
            write_refs(fx.refs)

            report = fx.report()

            self.assertNotIn("resolutions-v3.md", report["phases"]["1"]["inputs"])
            self.assertEqual(report["phases"]["1"]["words"], 5)

    def test_review_history_excluded_from_phases_1_to_3_and_included_in_phase_4(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp), version=2)
            write(fx.plan, 5)
            write_refs(fx.refs)
            fx.workdir.joinpath("review-history.md").write_text("## Old\none two\n\n## New\nthree four\n")

            report = fx.report(review_history_entries=1)

            for phase in ("1", "2", "3"):
                self.assertNotIn("review-history.md", report["phases"][phase]["inputs"])
                self.assertEqual(report["phases"][phase]["words"], 5)
            self.assertIn("review-history.md", report["phases"]["4"]["inputs"])
            self.assertEqual(report["review_history_entries"], 1)
            self.assertEqual(report["phases"]["4"]["words"], 9)

    def test_dot_files_and_partial_files_are_excluded_but_swept_resolution_is_preferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp), version=4)
            write(fx.plan, 10)
            write(fx.workdir / "resolutions-v4.md", 100)
            write(fx.workdir / ".resolutions-v4-swept.md", 1)
            write(fx.workdir / ".hidden-blue-v4.md", 50)
            write(fx.workdir / "partial-blue-v4.md.partial", 50)
            write(fx.workdir / "visible-blue-v4.md", 2)
            write_refs(fx.refs)

            report = fx.report()

            self.assertIn(".resolutions-v4-swept.md", report["phases"]["1"]["inputs"])
            self.assertNotIn("resolutions-v4.md", report["phases"]["1"]["inputs"])
            self.assertEqual(report["phases"]["2"]["words"], 13)
            self.assertEqual(report["phases"]["2"]["inputs"].count("visible-blue-v4.md"), 1)
            self.assertNotIn(".hidden-blue-v4.md", report["phases"]["2"]["inputs"])
            self.assertNotIn("partial-blue-v4.md.partial", report["phases"]["2"]["inputs"])

    def test_heaviest_phase_identification(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp), version=5)
            write(fx.plan, 1)
            write(fx.workdir / "heavy-red-v5.md", 20)
            write_refs(fx.refs)

            self.assertEqual(fx.report()["heaviest_phase"], "3")


class TestChecks(unittest.TestCase):
    def test_clean_small_plan_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp))
            write(fx.plan, 1)
            write_refs(fx.refs)
            self.assertEqual(fx.report()["result"], "pass")

    def test_10k_advisory_fires_without_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp))
            write(fx.plan, 10_001)
            write_refs(fx.refs)

            report = fx.report()

            self.assertEqual(report["result"], "needs_review")
            self.assertFalse(report["checks"]["plan_size_advisory_10k"]["blocking"])
            self.assertEqual(report["checks"]["plan_size_advisory_10k"]["failed"], ["plan"])

    def test_80k_ceiling_fires_as_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = BudgetFixture(Path(tmp), version=8)
            write(fx.plan, 1)
            write(fx.workdir / "huge-blue-v8.md", 80_000)
            write_refs(fx.refs)

            report = fx.report()

            self.assertEqual(report["result"], "fail")
            self.assertTrue(report["checks"]["phase_ceiling_80k"]["blocking"])
            self.assertEqual(report["checks"]["phase_ceiling_80k"]["failed"], ["2", "3", "4"])

    def test_derive_result_precedence(self):
        self.assertEqual(cb.derive_result({"a": {"blocking": True, "ok": True, "failed": []}}), "pass")
        self.assertEqual(
            cb.derive_result({"a": {"blocking": False, "ok": False, "failed": ["x"]}}),
            "needs_review",
        )
        self.assertEqual(
            cb.derive_result(
                {
                    "a": {"blocking": False, "ok": False, "failed": ["x"]},
                    "b": {"blocking": True, "ok": False, "failed": ["y"]},
                }
            ),
            "fail",
        )


class TestReviewHistoryEstimate(unittest.TestCase):
    def test_recent_review_history_uses_last_n_h2_sections(self):
        text = "preamble ignored\n## One\nold words\n## Two\nnew words\n## Three\nlatest words\n"
        selected, count = cb.recent_review_history(text, 2)
        self.assertEqual(count, 2)
        self.assertNotIn("old words", selected)
        self.assertIn("new words", selected)
        self.assertIn("latest words", selected)

    def test_review_history_without_h2_counts_full_file_conservatively(self):
        selected, count = cb.recent_review_history("no headings here", 5)
        self.assertEqual(selected, "no headings here")
        self.assertEqual(count, 1)


class TestCli(unittest.TestCase):
    script = SCRIPTS_DIR / "context_budget.py"

    def _fixture(self, plan_words: int = 1, version: int = 1):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        fx = BudgetFixture(root, version)
        write(fx.plan, plan_words)
        write_refs(fx.refs)
        return temp, fx

    def _run(self, fx: BudgetFixture, *args: str):
        return subprocess.run(
            [
                sys.executable,
                str(self.script),
                str(fx.plan),
                str(fx.workdir),
                "--references",
                str(fx.refs),
                *args,
            ],
            capture_output=True,
            text=True,
        )

    def test_pass_exits_zero(self):
        temp, fx = self._fixture()
        with temp:
            self.assertEqual(self._run(fx).returncode, 0)

    def test_fail_exits_one(self):
        temp, fx = self._fixture(version=9)
        with temp:
            write(fx.workdir / "huge-blue-v9.md", 80_000)
            self.assertEqual(self._run(fx).returncode, 1)

    def test_needs_review_exits_two(self):
        temp, fx = self._fixture(plan_words=10_001)
        with temp:
            self.assertEqual(self._run(fx).returncode, 2)

    def test_missing_file_exits_three(self):
        temp, fx = self._fixture()
        with temp:
            proc = subprocess.run(
                [sys.executable, str(self.script), str(fx.plan.with_name("missing.md")), str(fx.workdir)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 3)

    def test_usage_error_exits_three(self):
        proc = subprocess.run([sys.executable, str(self.script)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 3)

    def test_json_output_shape(self):
        temp, fx = self._fixture(version=6)
        with temp:
            proc = self._run(fx, "--json")
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["result"], "pass")
            self.assertEqual(payload["version"], 6)
            self.assertIn("1", payload["phases"])
            self.assertIn("phase_ceiling_80k", payload["checks"])
            self.assertIn("heaviest_phase", payload)


class TestRealSmoke(unittest.TestCase):
    @unittest.skipUnless(REAL_PLAN.exists() and REAL_WORKDIR.exists(), "real plan/workdir not present")
    def test_real_skill_plan_smoke(self):
        report = cb.check_budget(REAL_PLAN, REAL_WORKDIR)
        self.assertGreaterEqual(report["plan_words"], 0)
        self.assertIn(report["heaviest_phase"], {"1", "2", "3", "4"})
        for phase in ("1", "2", "3", "4"):
            self.assertGreaterEqual(report["phases"][phase]["words"], 0)


if __name__ == "__main__":
    unittest.main()
