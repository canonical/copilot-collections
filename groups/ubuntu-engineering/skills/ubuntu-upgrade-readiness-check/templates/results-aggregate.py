#!/usr/bin/env python3
"""Cross-tabulate upgrade-path test results into the report matrix.

Reads the per-phase results files written by the test suite
(results-<container>-<phase>.txt: '### phase: <phase> ... role: <role>'
header plus PASS:/FAIL: lines) and prints one pipe-table row per test, one
column per phase (first-seen order — name files so baseline sorts first),
plus a per-file FAIL list.

Cell values: PASS | FAIL | MIXED(v1/v2) when containers disagree within a
phase (normal for role-split tests, e.g. legacy vs modern flavors) | '-'
when no container ran that test in that phase (annotate as N/A by hand in
the report, with the reason).

Usage:
    results-aggregate.py [results-*.txt ...]     # default: glob in cwd
"""
import glob
import re
import sys


def parse(path):
    """Return (phase, role, {test: PASS|FAIL}) for one results file."""
    phase = role = None
    results = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.match(r"###\s*phase:\s*(\S+).*?role:\s*(\S+)", line)
            if m:
                phase, role = m.groups()
                continue
            m = re.match(r"(PASS|FAIL):\s*(\S+)", line)
            if m:
                results[m.group(2)] = m.group(1)
    return phase, role, results


def cell(values):
    if not values:
        return "-"
    if values == {"PASS"}:
        return "PASS"
    if values == {"FAIL"}:
        return "FAIL"
    return "MIXED(" + "/".join(sorted(values)) + ")"


def main(argv):
    files = argv[1:] or sorted(glob.glob("results-*.txt"))
    if not files:
        sys.exit("no results-*.txt files found (pass files or run in the workdir)")

    phases = []          # phase names, first-seen order
    phase_cells = {}     # phase -> {test: set of values}
    per_file = []
    for f in files:
        phase, role, results = parse(f)
        phase = phase or f  # no header line: fall back to the filename
        if phase not in phases:
            phases.append(phase)
        cells = phase_cells.setdefault(phase, {})
        for test, val in results.items():
            cells.setdefault(test, set()).add(val)
        fails = sorted(t for t, v in results.items() if v == "FAIL")
        per_file.append((f, phase, role, fails))

    tests = []
    for p in phases:
        for t in phase_cells[p]:
            if t not in tests:
                tests.append(t)

    fw = max([len("feature")] + [len(t) for t in tests])
    cw = max([len("MIXED(PASS/FAIL)")] + [len(p) for p in phases])
    sep = "|" + "-" * (fw + 2) + ("|" + "-" * (cw + 2)) * len(phases) + "|"

    def row(label, values):
        cells = "".join(" " + v.ljust(cw) + " |" for v in values)
        return "| " + label.ljust(fw) + " |" + cells

    print(row("feature", phases))
    print(sep)
    for t in tests:
        print(row(t, [cell(phase_cells[p].get(t)) for p in phases]))
    print()
    for f, phase, role, fails in per_file:
        r = f" role={role}" if role else ""
        if fails:
            print(f"{f} [phase={phase}{r}]: {len(fails)} FAIL -> " + ", ".join(fails))
        else:
            print(f"{f} [phase={phase}{r}]: all PASS")


if __name__ == "__main__":
    main(sys.argv)
