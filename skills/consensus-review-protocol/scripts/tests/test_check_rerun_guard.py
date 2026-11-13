#!/usr/bin/env python3
"""Unit/regression tests for check_rerun_guard.py.

Run:
    python3 -m unittest skills/consensus-review-protocol/scripts/tests/test_check_rerun_guard.py -v
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

import check_rerun_guard as crg  # noqa: E402


def touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x\n")
    return path


class TestStemVersionExtraction(unittest.TestCase):
    def test_unversioned_file_is_v1(self):
        stem, version = crg.extract_stem_version(Path("plans/my-feature.md"))
        self.assertEqual(stem, "my-feature")
        self.assertEqual(version, 1)

    def test_versioned_plan_strips_suffix(self):
        stem, version = crg.extract_stem_version(Path("plans/my-feature-v2.md"))
        self.assertEqual(stem, "my-feature")
        self.assertEqual(version, 2)

    def test_skill_shape_strips_suffix(self):
        stem, version = crg.extract_stem_version(Path(".github/skills/my-skill/SKILL-v21.md"))
        self.assertEqual(stem, "SKILL")
        self.assertEqual(version, 21)

    def test_multi_hyphen_name_strips_only_version_suffix(self):
        stem, version = crg.extract_stem_version(Path("plans/my-long-feature-name-v10.md"))
        self.assertEqual(stem, "my-long-feature-name")
        self.assertEqual(version, 10)

    def test_non_suffix_version_text_is_not_version(self):
        stem, version = crg.extract_stem_version(Path("plans/v2-plan.md"))
        self.assertEqual(stem, "v2-plan")
        self.assertEqual(version, 1)


class TestWorkdirAndRound(unittest.TestCase):
    def test_default_workdir_uses_protocol_path(self):
        self.assertEqual(
            crg.default_workdir("my-feature"),
            Path(".github/consensus-review-protocol/my-feature"),
        )

    def test_round_is_one_when_workdir_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(crg.count_round(Path(tmp) / "missing"), 1)

    def test_round_counts_one_consolidated_plus_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            touch(workdir / "consolidated-v1.md")
            self.assertEqual(crg.count_round(workdir), 2)

    def test_round_counts_several_consolidated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            for name in ("consolidated-v1.md", "consolidated-v3.md", "consolidated-v10.md"):
                touch(workdir / name)
            touch(workdir / "consolidated-v11.md.partial")
            touch(workdir / ".consolidated-v12.md")
            self.assertEqual(crg.count_round(workdir), 4)


class TestSlugDerivation(unittest.TestCase):
    def test_documented_gpt_example(self):
        self.assertEqual(crg.slug_base("gpt-5.6-sol"), "gpt-5-6-sol")

    def test_documented_claude_example(self):
        self.assertEqual(crg.slug_base("Claude Opus 4.6"), "claude-opus-4-6")

    def test_slash_space_dot_and_hyphen_collapse(self):
        self.assertEqual(crg.slug_base("A//B  C.."), "a-b-c")

    def test_default_model_slugs(self):
        slugs = crg.derive_model_slugs(list(crg.DEFAULT_MODELS))
        self.assertEqual(slugs["gpt-5.6-sol"], "gpt-5-6-sol")
        self.assertEqual(slugs["claude-sonnet-5"], "claude-sonnet-5")
        self.assertEqual(slugs["claude-opus-5"], "claude-opus-5")

    def test_two_slug_collisions_suffix_second_only(self):
        slugs = crg.derive_model_slugs(["a.b", "a/b"])
        self.assertEqual(slugs, {"a.b": "a-b", "a/b": "a-b-2"})

    def test_three_slug_collisions_suffix_in_model_order(self):
        slugs = crg.derive_model_slugs(["a.b", "a/b", "a b"])
        self.assertEqual(slugs, {"a.b": "a-b", "a/b": "a-b-2", "a b": "a-b-3"})


class TestRerunGuard(unittest.TestCase):
    def _paths(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        plan = touch(root / "plans" / "my-feature-v2.md")
        workdir = root / "work"
        workdir.mkdir()
        return temp, plan, workdir

    def test_clean_setup_has_no_rerun_failures(self):
        temp, plan, workdir = self._paths()
        with temp:
            stem, version = crg.extract_stem_version(plan)
            self.assertEqual(crg.find_rerun_artifacts(plan, stem, version, workdir), [])

    def test_detects_consolidated_independently(self):
        temp, plan, workdir = self._paths()
        with temp:
            touch(workdir / "consolidated-v2.md")
            stem, version = crg.extract_stem_version(plan)
            self.assertEqual(crg.find_rerun_artifacts(plan, stem, version, workdir), [str(workdir / "consolidated-v2.md")])

    def test_detects_next_resolutions_independently(self):
        temp, plan, workdir = self._paths()
        with temp:
            touch(workdir / "resolutions-v3.md")
            stem, version = crg.extract_stem_version(plan)
            self.assertEqual(crg.find_rerun_artifacts(plan, stem, version, workdir), [str(workdir / "resolutions-v3.md")])

    def test_detects_next_plan_independently_in_plan_directory(self):
        temp, plan, workdir = self._paths()
        with temp:
            touch(plan.parent / "my-feature-v3.md")
            stem, version = crg.extract_stem_version(plan)
            self.assertEqual(crg.find_rerun_artifacts(plan, stem, version, workdir), [str(plan.parent / "my-feature-v3.md")])

    def test_detects_blue_review_independently(self):
        temp, plan, workdir = self._paths()
        with temp:
            touch(workdir / "gpt-5-6-sol-blue-v2.md")
            stem, version = crg.extract_stem_version(plan)
            self.assertEqual(crg.find_rerun_artifacts(plan, stem, version, workdir), [str(workdir / "gpt-5-6-sol-blue-v2.md")])

    def test_detects_red_review_independently(self):
        temp, plan, workdir = self._paths()
        with temp:
            touch(workdir / "claude-red-v2.md")
            stem, version = crg.extract_stem_version(plan)
            self.assertEqual(crg.find_rerun_artifacts(plan, stem, version, workdir), [str(workdir / "claude-red-v2.md")])

    def test_detects_purple_review_independently(self):
        temp, plan, workdir = self._paths()
        with temp:
            touch(workdir / "opus-purple-v2.md")
            stem, version = crg.extract_stem_version(plan)
            self.assertEqual(crg.find_rerun_artifacts(plan, stem, version, workdir), [str(workdir / "opus-purple-v2.md")])

    def test_partial_and_dot_files_are_excluded(self):
        temp, plan, workdir = self._paths()
        with temp:
            touch(workdir / "consolidated-v2.md.partial")
            touch(workdir / ".resolutions-v3.md")
            touch(workdir / ".gpt-blue-v2.md")
            touch(workdir / "gpt-blue-v2.md.partial")
            stem, version = crg.extract_stem_version(plan)
            self.assertEqual(crg.find_rerun_artifacts(plan, stem, version, workdir), [])


class TestVersionedSiblingGuard(unittest.TestCase):
    def test_unversioned_plan_with_siblings_names_highest_numeric_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan.md")
            touch(root / "plan-v9.md")
            highest = touch(root / "plan-v10.md")
            self.assertEqual(crg.highest_versioned_sibling(plan, "plan", 1), str(highest))

    def test_unversioned_plan_without_siblings_does_not_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan.md")
            touch(root / "other-v10.md")
            self.assertIsNone(crg.highest_versioned_sibling(plan, "plan", 1))

    def test_versioned_input_does_not_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan-v2.md")
            touch(root / "plan-v10.md")
            self.assertIsNone(crg.highest_versioned_sibling(plan, "plan", 2))


class TestChecksAndResult(unittest.TestCase):
    def test_clean_setup_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan-v2.md")
            report = crg.check_plan(plan, root / "work")
            self.assertEqual(report["result"], "pass")
            self.assertEqual(report["derived"]["stem"], "plan")
            self.assertEqual(report["derived"]["version"], 2)

    def test_rerun_guard_is_needs_review_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan-v2.md")
            workdir = root / "work"
            touch(workdir / "consolidated-v2.md")
            report = crg.check_plan(plan, workdir)
            self.assertEqual(report["result"], "needs_review")
            self.assertFalse(report["checks"]["rerun_guard"]["blocking"])

    def test_versioned_sibling_guard_is_needs_review_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan.md")
            touch(root / "plan-v3.md")
            report = crg.check_plan(plan, root / "work")
            self.assertEqual(report["result"], "needs_review")
            self.assertFalse(report["checks"]["versioned_sibling_guard"]["blocking"])

    def test_model_minimum_is_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan.md")
            report = crg.check_plan(plan, root / "work", ["solo"])
            self.assertEqual(report["result"], "fail")
            self.assertFalse(report["checks"]["model_list_minimum"]["ok"])

    def test_derive_result_pass_when_all_ok(self):
        checks = {"a": {"blocking": True, "ok": True, "failed": []}}
        self.assertEqual(crg.derive_result(checks), "pass")

    def test_derive_result_needs_review_for_nonblocking_failure(self):
        checks = {"a": {"blocking": False, "ok": False, "failed": ["x"]}}
        self.assertEqual(crg.derive_result(checks), "needs_review")

    def test_derive_result_blocking_failure_takes_precedence(self):
        checks = {
            "a": {"blocking": False, "ok": False, "failed": ["x"]},
            "b": {"blocking": True, "ok": False, "failed": ["y"]},
        }
        self.assertEqual(crg.derive_result(checks), "fail")


class TestCli(unittest.TestCase):
    script = SCRIPTS_DIR / "check_rerun_guard.py"

    def test_pass_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = touch(Path(tmp) / "plan.md")
            proc = subprocess.run(
                [sys.executable, str(self.script), str(plan), "--workdir", str(Path(tmp) / "work")],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_fail_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = touch(Path(tmp) / "plan.md")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(self.script),
                    str(plan),
                    "--workdir",
                    str(Path(tmp) / "work"),
                    "--model",
                    "solo",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)

    def test_needs_review_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan.md")
            touch(root / "plan-v2.md")
            proc = subprocess.run(
                [sys.executable, str(self.script), str(plan), "--workdir", str(root / "work")],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)

    def test_missing_file_exits_three(self):
        proc = subprocess.run(
            [sys.executable, str(self.script), "/nonexistent/plan.md"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 3)

    def test_json_output_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = touch(root / "plan-v4.md")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(self.script),
                    str(plan),
                    "--workdir",
                    str(root / "work"),
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["plan"], str(plan))
            self.assertEqual(payload["derived"]["stem"], "plan")
            self.assertEqual(payload["derived"]["version"], 4)
            self.assertEqual(payload["derived"]["workdir"], str(root / "work"))
            self.assertEqual(payload["derived"]["round"], 1)
            self.assertIn("gpt-5.6-sol", payload["derived"]["model_slugs"])
            self.assertIn("rerun_guard", payload["checks"])


if __name__ == "__main__":
    unittest.main()
