# Completion Report Template

*Referenced by `references/phase-4c-output-formats.md §Completion Report Format`. This file's
content is itself the literal report structure — substitute all bracketed placeholders, then
emit the result exactly as written, as rendered markdown. Do NOT wrap it in a code fence: this
template's headings, tables, and emoji status markers only render correctly unfenced. All
sections below must appear in the order shown.*

---

✅ Consensus Review <workdir-name> Round <N> Complete
Date: <ISO date>

## Plan Reviewed

- Input: <full repo-root-relative path to `<plan-name>-v<N>.md`> (<line count> lines, ~<KB> KB)
- Output: <full repo-root-relative path to `<plan-name>-v<N+1>.md`>

## Phase Outcomes

**🔵 Blue-team:** [Prose summary — what all models agreed on, any divergence, overall feasibility signal]
**🔴 Red-team:** [Prose summary — key attacks found, BLOCKER count, IMPORTANT count, most critical finding titles]
**🟣 Purple-team:** [Prose summary — arbitration results, confirmed BLOCKERs and their merged IDs, convergence assessment]

## Findings This Round

- 🔴 BLOCKERs: <count> (<IDs>)
- 🟠 IMPORTANT: <count> (<IDs>)
- 🔀 CONFLICTED: <count> (<IDs or "None">)
- ✨ NICE-TO-HAVE: <count> (<IDs>)
- ⚠️ Questions for Tech Lead: <count>

## Tech Lead Direct Edits Since Last Round

[From the prior round's TL-owned "Direct Companion File Edits Since Last Round" Answer field in resolutions-vN.md, or "None recorded"]

## Model Verdicts

| Model | Blue | Red | Purple |
|-------|------|-----|--------|
| <Model 1> | <verdict> | <verdict> | <verdict> |
| <Model 2> | <verdict> | <verdict> | <verdict> |
| <Model 3> | <verdict> | <verdict> | <verdict> |

## Convergence Status

[Converging / Not yet converging] — [Brief rationale: BLOCKER delta from prior round, new BLOCKERs introduced]
Unresolved CONFLICTED BLOCKERs: <N>
Skip count: <this round's PHASE-4B-SKIP total> (prior round: <N>; increased/decreased/unchanged/n/a for round 1)
Plan size: <lines> lines / <words> words (prior version: <lines>/<words>; net <+/-N> lines this round)

## Soundness Status

[If prerequisites met (0 BLOCKERs, all models GO/CONDITIONAL GO with conditions resolved, 0 unanswered Open Questions)]:
ℹ️ All review prerequisites are met. Ask for a final round when you want the pending resolutions applied and the plan declared sound.

[If prerequisites not met]:
Prerequisites not yet met — [X] BLOCKERs remain / [Y] CONDITIONAL GO conditions unresolved.

[If Unresolved CONFLICTED BLOCKERs > 0, append to whichever message fired above]:
Note: N CONFLICTED BLOCKER(s) at minority severity await TL resolution — review before declaring sound.

## Applied From resolutions-v<N>.md This Round (Phase 4b)

[List each applied resolution: <finding-ID> <ACCEPT|MODIFY> → <one-line status>, or "None — first run (pass-through)"]

## Context-Window Report

- Plan size: <plan-name>-v<N>.md = ~<X> words [advisory if >10K words ⚠️]
- Plan size after this round's Phase 4b: <plan-name>-v<N+1>.md = ~<X> words (no threshold
  logic — informational only; the advisory itself fires only at the next round's Setup, against
  this figure)
- Review history read for Phase 4a/4c: <N> most recent entries (note if expanded beyond 5)
- Heaviest phase: Phase <N> ≈ ~<X> words [⚠️ if approaching the 80,000-word ceiling]

## Token Cost

- Approximate total: ~<N>K tokens across <M> sub-agents (~<avg>K avg per sub-agent) (approximate at ~1.3 tokens/word, or use provider-reported usage when available)

## Companion Files Changed

[List companion files edited during Phase 4b, or "None"]

## Skipped Findings (PHASE-4B-SKIP)

[List any skipped findings with IDs and reasons, or "None"]

## Sub-Agent Failures

[List any failures with model and phase, or "None"]

## Orchestrator Notes

<!-- Two lines are required content of this section whenever they apply this round:
- **Setup sweep:** "Setup sweep: [N] resolved-entry comments removed from the swept copy." —
  required whenever a sweep ran.
- **Setup judgment pass:** one line per field asked about — "Setup judgment pass: [field] asked
  about — TL answer: [answer]." — required whenever the pass asked the tech lead about any
  field this round.
Write "not applicable this round" for neither; simply omit a line whose condition did not occur. -->

The remainder of the section is optional and discretionary — free-form observations the
orchestrator chooses to surface: verification
work performed and what it found, divergences between a model's stated rationale and underlying
source material, judgment calls made under an operational directive and why, cross-artifact
observations no single reviewer could make, or confidence caveats about its own synthesis. Where
neither required line applies and there is nothing discretionary to add, omit this section or
write "None". This section MUST NOT carry a
decision of record: any item requiring a tech-lead decision must also appear as a finding or an
Open Question elsewhere — this section may summarize or cross-reference such items but never
substitutes for them, and NEVER GUESS is unaffected. It is additive only and never displaces or
abbreviates any other section.]

[Only if this round ran under a pre-authorised or ad hoc 2-model setup]

## Consensus Protocol Degraded Mode

This round ran with a degraded 2-model setup. The next round reverts to the default model list; state explicitly if it should run degraded again.

## File Listing

All <count> output files, in `<workdir path>`:

- **Phase 1:** <blue filenames, comma-separated>
- **Phase 2:** <red filenames, comma-separated>
- **Phase 3:** <purple filenames, comma-separated>
- **Phase 4a:** consolidated-vN.md
- **Phase 4b:** <plan-name>-v<N+1>.md — state its directory here when the plan does not live in the workdir
- **Phase 4c:** resolutions-v<N+1>.md

⚠️ Pending changes: The findings in resolutions-v<N+1>.md have NOT yet been applied to plan-v<N+1>.md. They will be applied in the next run's Phase 4b.

## Next Step

Fill in `resolutions-v<N+1>.md`, then re-run this skill on `plan-v<N+1>.md`.
