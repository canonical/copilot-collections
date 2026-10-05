---
name: consensus-review-protocol
author: Loïc Gomez <loic.gomez@canonical.com>
version: 1.0
date: 2026-09-08 09:37 UTC
description: >
  Orchestrates a multi-model consensus review of a plan file using three adversarial-collaborative
  phases: blue-team (constructive), red-team (adversarial attack), and purple-team (chaos
  engineering + arbitration). Spawns reviewer sub-agents for each configured AI model (default:
  gpt-5.6-sol, claude-sonnet-5, claude-opus-5), writes phase reviews to
  .github/consensus-review-protocol/<plan-name>/, then consolidates findings into a new hardened
  plan version. All output is planning prose — no code. Use when stress-testing an
  architecture plan, technical spec, project proposal, or design document before execution.
  Triggered by: "review my plan", "consensus review", "blue-red-purple review",
  "multi-model plan review", "stress-test this plan", "adversarial plan review",
  "go for another round", "next review iteration", "continue the review", "apply resolutions",
  "start round N", "run another consensus cycle".
---

# Consensus Plan Review

## Overview

Runs a structured 3-phase multi-model consensus review of a plan file. Each model independently
reviews in three escalating modes — constructive (blue), adversarial (red), and chaos +
arbitration (purple) — with each phase cross-reading the previous phase's outputs. The final
output is a hardened, versioned plan incorporating the most critical recommendations.

---

## Core Protocol

### ⚠️ NEVER GUESS

**AI models must never guess, assume, or silently resolve ambiguity.** On any uncertain
decision, surface a `⚠️ QUESTION FOR TECH LEAD:` entry instead of proceeding on an assumption.
This binds sub-agent reviewers (see `references/review-general.md §General Requirements`) and
the orchestrator when parsing plan intent, classifying findings, or writing resolutions.

**Scope:** NEVER GUESS governs plan-content judgments — interpreting intent, classifying
severity, assessing feasibility, resolving ambiguous requirements, choosing between conflicting
recommendations, and any assertion about a codebase, system, or domain that cannot be verified
from the provided materials. It does not govern fully specified mechanical steps such as file
naming, version incrementing, model-slug derivation, and format validation, which execute per
their defined rules.

**Materiality:**

- Batch unverifiable references that share a system, component, or decision boundary into one
  question.
- Reserve questions for points specific to this implementation that would materially change a
  finding's severity, feasibility, scope, safety, security, data durability, or an execution
  decision if answered differently.
- Standard professional knowledge (well-known database patterns, standard authentication
  flows, common infrastructure) needs no question.
- Inline plan prose defining a component's behaviour counts as provided material.
- If more than a third of the plan's assertions are systemically unverifiable, raise one
  meta-question requesting supplementary context documents.

**The tech lead is the sole authority on all Resolutions.** The skill prepares the information
and writes the `resolutions-v<N+1>.md` template. The tech lead reads it, decides, and fills it in.
The skill then executes.

### Plan Mode — Prose-First

**All reviews, consolidated documents, and the new plan version must be written as planning
prose.**

- ❌ No long code blocks or multi-line pseudo-code
- ✅ Findings expressed as prose descriptions of problems and recommendations
- ✅ Implementation details, interface names, function signatures and brief inline references
  where they clarify a finding (e.g., "the `retry()` method in `client.go` must cap at 5
  attempts — currently unbounded")
- ✅ Short blocks labeled as normative specifications — slug derivation, version regex
  patterns, completeness criteria — where prose alone cannot be unambiguous

A finding that seems to need a code block signals the plan lacks prose detail; raise it as a
`⚠️ QUESTION FOR TECH LEAD:`.

### Declarative by Default

**Mechanical content is structured. Explanatory content is prose. Rationale lives outside the
plan.** This binds all text Phase 4b applies and all text Phase 4c drafts.

- **Mechanical** — anything an executing agent must evaluate: thresholds, enumerated
  conditions, ordered steps, failure states, constraint lists, field requirements. Write these
  as numbered or bulleted lists, one condition per line, with concrete nouns rather than
  pronouns crossing a line boundary, and numeric thresholds rather than qualitative ones
  ("exceeds 80,000 words", never "approaches 80,000 words"). Prose compression of a mechanical
  rule is a regression even when it is shorter.
- **Explanatory** — what the protocol is for, who decides, how phases relate. Prose.
- **Rationale** — why a rule exists, what finding prompted it, what alternative was rejected.
  This does not belong in the plan at all. It belongs in `resolutions-vN.md` and
  `review-history.md`, which are the durable record and are already read by the orchestrator.
  Writing rationale into a normative rule creates surface area that the next round attacks.
- **Threshold derivations are not rationale.** A clause stating what makes a numeric threshold
  the value it is — "the threshold is three because at two, majority and consensus become the
  same test" — constrains future edits by naming what would have to change for the number to
  change. Keep it with the threshold.

**Style mirroring (normative):** Before authoring any new text — in Phase 4b when applying a
resolution, and in Phase 4c when drafting a template entry — sample the surrounding plan text's
register: declarative specification or narrative prose, `MUST`/`SHOULD` usage, bullets or
paragraphs, typical sentence length. Match it. Sampling happens at the point of authoring, not
once at Setup, so it needs no state carried across phases and reflects the section actually
being edited. A plan written as a declarative specification stays one; the orchestrator does
not migrate it toward narrative because narrative reads more naturally.

### Tech Lead Is the Lead

**AI models are advisors. The tech lead is the decision-maker.** Models surface findings,
raise questions and propose improvements. Only the tech lead resolves findings, answers open
questions, and declares the plan sound and ready for execution.

### Iterative Protocol

This skill runs repeatedly, on the latest plan version each time, until the tech lead
declares the plan sound. Each run executes Blue → Red → Purple → Orchestrator, then stops for
the tech lead to fill in the resolutions template it wrote. The next run loads that file and
applies its decisions. See §Workflow for both forms.

**Version-Indexing Rule (normative):**

> **LOOKUP rule:** When starting a run on `plan-vN`, Setup looks for `resolutions-vN.md`
> (same version number) as the immediately preceding resolutions context.
>
> **WRITE rule:** Phase 4c writes `resolutions-v<N+1>.md` (next version number, for the next
> run on `plan-v<N+1>.md`).
>
> **First-run exception:** An unversioned plan (e.g., `plan.md`) is treated as v1. Setup looks
> for `resolutions-v1.md`. If not found, proceed without prior resolutions.
>
> **Versioned-sibling guard:** Before applying the first-run exception, check the plan file's
> directory for files sharing its stem with a `-v<N>` suffix. If any exist, the unversioned file
> is not v1 — halt and ask the tech lead which version it represents, naming the highest
> sibling version found.

Example: `plan-v3.md` → Setup loads `resolutions-v3.md` → Phase 4b applies its ACCEPT/MODIFY
decisions and writes `plan-v4.md` → Phase 4c writes `resolutions-v4.md` for the next run.

Each model at every phase receives: the current plan, **only the immediately preceding
resolutions file** (`resolutions-vN.md`), and the outputs of all preceding phases in this run.
Do not pass older resolutions files; their decisions are already baked into the plan text.
**Phase 1–3 sub-agents do not receive `review-history.md`.** **Phase 4a/4c defaults to the 5
most recent entries of `<workdir>/review-history.md`**, reading further back when a cross-round citation needs it and recording
the expanded read in the Completion Report. This is a context budget, not an access
restriction: the orchestrator may read the full file at its discretion, and NEVER GUESS covers
genuine uncertainty.

**Review History archival (normative):** The plan's Review History section contains only a
single pointer line: ``*Complete review history in `<workdir>/review-history.md`.*`` — no inline
entries at any round, including round 1. The companion file
`.github/consensus-review-protocol/<plan-name>/review-history.md` is always created from round 1
and is the sole home for review history. Who reads it, and how much, is governed by the
Version-Indexing Rule above.

**File header and entry boundaries (normative):** On first creation, the orchestrator writes
a `# Review History` heading, a one-line description naming the plan, and a `---` separator.
Everything through that first `---` is the file header, which contains no `### ` headings; new
entries are inserted immediately after it. One entry runs from a `### ` heading to just before
the next, or to end of file — this is what "most recent 5 entries" counts.

**Entry format (normative):** Every entry uses the shape below. Entries predating this format
are historical record and are not rewritten.

```
### <plan-file>.md — <ISO date>

**Round N reviewing plan v<M>** | Input: ... | Output: ... | Resolutions applied from: ...
**Models:** ...
*Supersession note: <the declared edit, citing the resolutions file it is declared in>*
**Key changes from v<M>:**
- [bullet per change/finding]
**Round N Phase 4b skips:** <count> — <finding ID>: <one-clause reason>[; repeat per skip, or
"none"]
**Recorded no-ops:** <finding IDs, or none>
**Sub-agent failures:** <model — phase — error>
**Convergence:** [one-line status]
```

The template has two conditional lines and no others:

- The Supersession note, immediately after `**Models:**`, written whenever
  §Supersession-note requirement applies.
- `**Sub-agent failures:**`, written only when a sub-agent failed all retries this round, so a
  clean round adds no line. It is also the only Completion Report datum persisted to disk.

**Round N Phase 4b skips (normative):** Beyond the count, name every skipped finding ID with a
one-clause reason (e.g. "target not found", "MODIFY notes ambiguous") — not the verbatim skip
message, which already lives in `resolutions-v<N+1>.md`'s carried-forward Open Question. This
keeps `review-history.md` independently auditable for *which* findings skipped and *why* in
one clause, without duplicating the full skip text the resolutions file already carries.

Phase 4b inserts new Review History entries directly and only to `review-history.md`
immediately after the file header (newest-first ordering), after this pass's plan-file and
companion-file writes are complete, whether they succeeded or were recorded as skips. Creation
of `review-history.md` from round 1 is exempt from the re-run guard.

**Supersession-note requirement (normative):** Whenever the loaded resolutions file's `Direct
Companion File Edits Since Last Round` Answer declares an actual edit — as opposed to being
blank, a placeholder, or `None` followed only by an explanatory clause — the round's Review History entry
MUST carry a one-line note naming that edit and citing the resolutions file — unconditionally,
with no judgment about significance.

**The plan is sound when the tech lead explicitly declares it.** Models inform that decision
by returning GO verdicts and reporting no remaining BLOCKERs, but the final call belongs to
the tech lead — not to the AI models.

**Prerequisites for the tech lead to consider declaring the plan sound:**

- All models returned GO or CONDITIONAL GO with their blocking conditions resolved
- No findings classified as BLOCKER survive into the purple-team reviews

#### Convergence Controls

**Round counter and display (normative):** The current round number is the count of
`consolidated-v*.md` files in the workdir at Setup, plus one for the round in progress —
cumulative across the workdir, and independent of the plan's version suffix, so a plan
entering review at v59 may be in round 56. Output filenames are keyed to the plan version,
not the round. Capture the number at Setup, reuse it in every artifact, and always display
both: "Round N reviewing plan vM; outputs: consolidated-vM, plan-v(M+1), resolutions-v(M+1)."
Only completed non-final rounds count: a final round writes no `consolidated-v*.md`, and a
round resumed part-way does not count the existing `consolidated-v*.md` belonging to the round
it is resuming.

**Re-opening a sound plan (normative):** A plan the tech lead previously declared sound may be
brought back for review — e.g. new requirements, a discovered defect. This is the same workdir
and round counter, continued: run Setup on the plan's latest version exactly as any other
run, counting `consolidated-v*.md` files already present, so the round number and version
sequence carry on rather than restarting.

**There is no round limit** — the tech lead decides when to stop. Round count is not the
stuck-review signal; the Convergence Status BLOCKER delta is.

**Convergence detection:** The Completion Report's §Convergence Status states deltas
against the prior round — increased, decreased, unchanged, or n/a for round 1 — by comparing
the current and prior consolidated reviews directly; no delta algorithm is required.

**Unresolved CONFLICTED BLOCKERs.** Count every CONFLICTED finding where any purple model's
position is BLOCKER, whatever the majority severity. This count lands in two separate places:

- **§Convergence Status** → report it as "Unresolved CONFLICTED BLOCKERs: N."
- **§Soundness Status** → when N > 0, append verbatim: "Note: N CONFLICTED BLOCKER(s) at
  minority severity await TL resolution — review before declaring sound."

**Oscillation detection (normative):** If a finding in the current round's consolidated review
is substantially similar (per the similarity rule below) to one carrying `Resolution: REJECT`
in the loaded `resolutions-vN.md`, Phase 4a MUST flag it as `⚠️ RECURRING FINDING` with a
`Supersedes:` reference to the prior finding ID (e.g., `Supersedes: R1-PLAN-MERGED-B2`),
signalling that the models dispute the rejection. It applies at any severity. Scope is the
loaded `resolutions-vN.md` only; multi-round detection is not supported, and the TL may REJECT
the same finding across consecutive rounds.

**Oscillation similarity rule (normative):** Two findings are substantially similar when BOTH
conditions hold:

1. They identify the same section of the plan as the locus of the defect.
2. They propose the same category of remediation (e.g. both recommend adding a guard clause,
   both recommend clarifying a definition, both recommend adding an inclusion criterion).

Title wording differences alone do not distinguish two findings.

**TL override:** the tech lead may override oscillation classification in the resolutions file
by noting "Not a recurrence — treat as new finding."

**Final round (normative):** The plan is sound when the tech lead says so in session — e.g.
"go for a final round", "last round", "wrap it up". Recognise the intent; do not match a
keyword list. There is no soundness field in any file.

A final round runs only Phase 4b — Phases 1–3, 4a and 4c are all skipped:

1. State what will be applied and confirm with the tech lead. MODIFY wording lands without ever
   having been reviewed by the sub-agents; this is the last chance to catch it.
2. If nothing is pending, do not mint a new version — archive and say so.
3. If `<plan-name>-v<N+1>.md` already exists, ask before overwriting it.
4. Apply the pending `resolutions-vN.md` and write `<plan-name>-v<N+1>.md`.
5. Write the Review History entry. Where any resolution failed to apply, the entry records
   what applied and what did not, and the sound declaration is withheld.
6. Emit the reduced Completion Report per `references/phase-4c-output-formats.md
   §Final Round Rules`.

**Anything that goes wrong in a final round goes straight to the tech lead, in session.** If
any resolution cannot be applied cleanly: write the new version with what did apply, report
exactly what did not and why, withhold the sound declaration, and ask. Do not generate a
recovery resolutions file — the tech lead is present.

**Verdict-to-severity mapping:** GO / CONDITIONAL GO / NO-GO criteria are defined normatively
in `references/review-general.md §Verdict-Criteria`, the single source of truth.

**CONDITIONAL GO conditions:** A model returning CONDITIONAL GO states its blocking conditions
as finding or Question IDs where its own phase task mints those IDs, and in prose where the
phase mints none; the Completion Report restates them as plain facts, with no ID-mapping
bookkeeping. If a condition is too vague to identify a specific finding, surface a
`⚠️ QUESTION FOR TECH LEAD`.

---

## Default Configuration

| Parameter       | Default                                              |
|-----------------|------------------------------------------------------|
| Models          | `gpt-5.6-sol`, `claude-sonnet-5`, `claude-opus-5`    |
| Review dir      | `.github/consensus-review-protocol/<plan-name>/`         |
| New plan suffix | `-v<N>` (auto-incremented)                           |
| Min models      | 2 (3 recommended — see Model-loss policy)            |

Accept custom models if the user specifies (e.g., "use GPT, Sonnet and Haiku"). The model list
is constrained as follows:

- Fewer than 2 models — rejected at Setup with an explanatory error.
- Exactly 2 models — accepted only when the tech lead configures it deliberately.
- 3 or more models — recommended, and what the default provides.

Three or more models is recommended; the derivation of that threshold is stated once, at
§Model-loss policy, and configuring two accepts the cost it names.

## Workflow

Run all phases **in strict sequential order between phases** — each phase depends on the
*successful* outputs of the previous. Within each phase, all model sub-agents **must run in
parallel** to minimise human wait time.

First-run workflow (no prior resolutions):

`[Setup] → [Phase 1: Blue (parallel)] → [Phase 2: Red (parallel)] → [Phase 3: Purple (parallel)] → [Phase 4a: Consolidated Review] → [Phase 4b: Pass-through (no prior resolutions)] → [Phase 4c: Resolutions Template] → STOP`

Re-run workflow (complete resolutions detected):

`[Setup: detect resolutions-vN, load as context] → [Phase 1: Blue (parallel)] → [Phase 2: Red (parallel)] → [Phase 3: Purple (parallel)] → [Phase 4a: Consolidated Review] → [Phase 4b: Apply Prior Approved Resolutions → write plan-v(N+1)] → [Phase 4c: Resolutions Template → write resolutions-v(N+1)] → STOP`

---

### Setup

1. **Resolve the plan file.** Use the path given, or one clearly identifiable from the current
   conversation (e.g. "go for another round" continuing a review in progress), and read its
   latest version. Never search the repository to guess: halt with `⚠️ QUESTION FOR TECH LEAD:
   Which plan file should this review target? Provide the file path.`
2. Extract `<plan-name>` — the plan file's stem, stripping path, extension and version suffix
   (`plans/my-feature-v2.md` → `my-feature`; `.github/skills/my-skill/SKILL-v21.md` → `SKILL`).
   `<plan-name>` means this stem everywhere in output filenames.

   **Workdir (normative):** `.github/consensus-review-protocol/<plan-name>/`, deterministic from
   the stem and requiring no directory scanning. The tech lead may override the directory name
   when providing the plan path, at the start of a review cycle only, for the rest of that
   cycle; a mid-cycle relocation is not supported and goes to the tech lead. Output filenames
   still use the stem.

3. Determine `<N>` from the file's version suffix (`-v<N>`), or 1 if none (e.g., `plan.md` = v1).
4. Create `.github/consensus-review-protocol/<plan-name>/` if it doesn't exist.

   **Collision detection (normative):** If the workdir already exists, read the `**Plan:**`
   line in the header of its highest-versioned `consolidated-v*.md` — highest by numeric
   comparison on the version integer, not by lexical filename or directory-listing order — and
   compare it to the input plan's path. Normalise incidental Markdown formatting and surrounding
   whitespace on both sides before comparing. The two refer to the
   same plan when they are equal after that normalisation and after removing any `-v<N>`
   version suffix from either — the same path-identity test used for companion-file targets, so
   switching between `myspec.md` and `myspec-v58.md` is not a collision. If they differ, halt:
   ``⚠️ Workdir collision: `.github/consensus-review-protocol/<plan-name>/` already contains
   artifacts from a different plan file (`[other plan path]`). Rename the plan file to use a
   unique stem, or specify a workdir override, then re-run. If this is the same plan relocated,
   update that `**Plan:**` line to the new path instead and re-run.`` Otherwise proceed. With
   no `consolidated-v*.md` present in the workdir there is nothing to compare, and the check
   does not apply.
   Concurrent execution (multiple orchestrators writing to the same workdir simultaneously) is
   not supported.

5. Confirm the model list, defaulting unless the user specified otherwise, and apply the
   §Default Configuration model-list constraints. Confirm every configured name — including
   any generic or `-latest`-style alias — resolves to a specific model version invocable in
   the current harness; if one does not, apply NEVER GUESS and halt with `⚠️ QUESTION FOR
   TECH LEAD: Cannot confidently resolve model '[name]' to a specific version. Please specify
   the exact model version to use.`
6. **Derive a `<model-slug>` per model (normative):** lowercase the name, replace every `.`,
   `/` and space with a hyphen, collapse consecutive hyphens, strip trailing hyphens. Where two
   or more models yield the same slug, append `-2`, `-3` and so on in model-list order,
   one suffix per colliding model beyond the first. Examples:
   `gpt-5.6-sol` → `gpt-5-6-sol`; `Claude Opus 4.6` → `claude-opus-4-6`.
7. **Read the TL-owned "Direct Companion File Edits Since Last Round" `Answer:` field** from
   `resolutions-vN.md`, if it exists, and hold it through all phases for the Completion
   Report's §Tech Lead Direct Edits Since Last Round section.

> **⏱️ Setup Heads-up:** Phases run sequentially with deep-reasoning analysis at each step;
> total time depends on plan complexity, model response times and how many findings surface.
> Leave the session open.

> **📏 Context budget (normative):** This protocol suits plans up to about 10,000 words.
>
> **Plan size advisory (normative):** At Setup, if the plan's word count exceeds 10,000, display
> `📏 Plan is approximately [X] words, above the ~10,000-word guidance in §Context budget;
> consider splitting into standalone plan files with their own review cycles.` then continue
> without waiting for a reply. This is informational only — unlike the 80,000-word ceiling
> below, it never halts, gates a phase, or requires a tech lead answer.
>
> Never review one
> plan in partial sections. Before launching any phase, estimate the input word count of a
> single sub-agent in that phase — the plan, the resolutions file, the prior-phase review
> files, and `references/review-general.md` plus that phase's own mode file, all of which one
> sub-agent receives — not the sum across the phase's parallel sub-agents. If the
> estimate **exceeds 80,000 words**, halt and surface `⚠️ QUESTION FOR TECH LEAD:
> Phase [N] input is approximately [X] words, over the 80,000-word ceiling. Split the plan into
> standalone files, or confirm proceeding with reduced context quality.` This ceiling applies
> uniformly to every phase, Phase 4 included. Word count, not tokens, is the unit —
> the approximation is intentionally conservative. If context runs out mid-synthesis, surface
> a `⚠️ QUESTION FOR TECH LEAD` rather than proceeding on truncated context.

**Context check — run before starting any phase:**

Look for `<workdir>/resolutions-vN.md`, the same version as the input plan.

- **Exists and complete** → load it as context for all phases; Phase 4b applies its ACCEPT and
  MODIFY decisions after Phase 4a in this same run.
- **Exists but incomplete** → **stop immediately:** "Resolutions file is incomplete. Please
  resolve all findings, answer all open questions, and address the completeness failure(s)
  listed below in `<workdir>/resolutions-vN.md` before re-running."
- **Does not exist** → proceed without prior resolutions.

**Resolutions completeness definition (normative):** A resolutions file is complete when
mechanical Rules 1–4 are satisfied. The Setup judgment pass below is a separate,
non-mechanical decision-quality check.

**Rule 1:** Every `Resolution:` field has a value exactly matching `ACCEPT`, `REJECT`, or
`MODIFY` (case-insensitive, whitespace-trimmed). Any other value — including blank, HTML
comment placeholders, prose phrases, or option labels — causes the completeness check to
fail identifying the finding ID and invalid value.

**Rule 2:** A non-blank, non-placeholder `Notes:` field is required on:

- every entry with `Resolution: MODIFY`;
- every CONFLICTED entry, whatever its Resolution value;
- every entry meeting the §Companion-target test below.

A `Notes:` value is a placeholder when whitespace-only or matching `<!-- ... -->`. Blank or
placeholder Notes on any of the three fails completeness, identifying the finding ID.

**§Companion-target test (normative):** An entry meets it when its Summary names a
companion-file path and describes a change to that file. This is the single definition, read
by Rule 2's third condition, `§4c`'s Companion-file Notes pre-population, and `§4b`'s Target
identification.

**Rule 3:** Every Open Questions entry has a non-blank, non-placeholder `Answer:` field
(placeholder as in Rule 2); a blank or placeholder one fails completeness, identifying the
question ID. With no question entries, Rule 3 is vacuously satisfied.

**Rule 4 (decision determinism):** `Resolution: ACCEPT` on an entry carrying a
`Presents options:` field fails completeness, identifying the finding ID and quoting the
labels: ACCEPT alone selects no option, so the tech lead must use MODIFY and name their choice
in Notes. This reads the entry's own header block in the file being validated — a presence
check on structure Phase 4c writes, which cannot fail to resolve, since an entry without the
field is simply not multi-option. Phase 4c writes the field on reproduced bodies too, so every
entry class is covered, ATL-sourced, carry-forward, TL-authored and `-RESUBMIT` alike. On a
Rule 4 failure, offer one suggested MODIFY rewrite drawn from the finding's own text, which the
tech lead may take, replace, or REJECT.

**Setup judgment pass (normative, not a mechanical rule):**

- **When:** before Phase 1; or before Phase 4b in a final round, that pass being both
  unreviewed and unrepeatable.
- **What to check:** every MODIFY `Notes:`; every CONFLICTED `Notes:`; every companion-targeted
  entry's `Notes:` (per Rule 2); every Open Question `Answer:`.
- **The test:** does this field still read as an open question or an unresolved choice, rather
  than a settled decision? This is the same question `§4b`'s ambiguity guards ask at
  application time.
- **Not checked:** the Direct Companion File Edits `Answer:`, which is free-form traceability
  narrative rather than a decision field.

Use ordinary judgment, not a fixed signal list — interrogative phrasing and naming alternatives
without picking one are examples, not an exhaustive set.

Where a field looks unresolved:

1. Ask the tech lead in session. Do not halt with a formatted completeness failure, and do not
   require an override annotation.
2. Treat the live answer as settling the field for this round, unless it says otherwise. The
   file is then complete with respect to this pass.
3. Record the field and its answer in the Completion Report's `## Orchestrator Notes`, so the
   tech lead sees the disposition while present.

`§4b`'s guards remain the backstop for whatever this pass missed, and for a confirmed field
that still yields no locatable operation at application time.

A blank Direct Companion File Edits `Answer:` declares no direct edits and is not a
completeness failure. A CONFLICTED finding with blank Notes reaching Phase 4b emits
PHASE-4B-SKIP rather than a guess at which model position to apply.

**Setup sweep (normative, mechanical):** Strip spent tech-lead-facing scaffolding from the
loaded resolutions file, which every sub-agent in Phases 1–3 and the orchestrator at 4a/4c
re-read — so anything left in place is paid for once per model per phase. The sweep applies to
the copy passed to sub-agents and the orchestrator. Sub-agents are separate invocations without
inline access to the orchestrator's context, so materialize the swept copy as a single
dot-prefixed temporary file in the workdir (e.g. `.resolutions-vN-swept.md`), excluded from the
re-run guard and the Completion Report's file listing, deleted once this round's Phase 1–3
sub-agents have all read it. `resolutions-vN.md` on disk is never modified, so the tech
lead's decision record survives intact.

- **When:** after the completeness gate passes, before launching Phase 1. Never earlier: Rules
  2 and 4 detect placeholders, so sweeping first would mask an unfilled field.
- **Delete the `## Instructions` block** in its entirety. It tells the tech lead how to fill the
  file in; by this point the file is filled in and validated, so it instructs nobody and no
  protocol rule reads it.
- **Delete pre-fill comments,** scoped to the values of `Notes:` and `Answer:` fields only —
  never a finding body, Summary, Suggested fix, or model-position text, any of which may quote a
  placeholder verbatim. Remove each `<!-- ... -->` found there, leaving surrounding tech lead
  text intact. Rule 2 already defines such a comment as placeholder content carrying no decision
  value, so this removes nothing the protocol reads.
- **Record:** state the number of comments removed in the Completion Report's
  `## Orchestrator Notes`.

**Resolution parsing contract (normative):** The authoritative value is the same-line text
after `Resolution:`, keyword only, case-insensitive and whitespace-trimmed. Any additional
characters on that line — trailing prose, inline comments, option labels, parentheticals —
fail the completeness check. All rationale belongs in `Notes:`, which is multi-line.

**Direct Companion File Edits completeness (normative):** This field is advisory; blank or
placeholder values read as 'None' and never fail completeness. Emit: "Direct Companion File
Edits field was blank — assuming no out-of-band edits since last round."

**Re-run guard:**

Before starting, check for this version's outputs, each at the path it is written to:

- `consolidated-vN.md` and `resolutions-v<N+1>.md` — in the workdir.
- `<plan-name>-v<N+1>.md` — in the input plan's own directory, per `§4b`.
- `*-blue-v<N>.md`, `*-red-v<N>.md`, `*-purple-v<N>.md` — in the workdir; report any that are
  present.

Files ending in `.partial` are recovery artifacts and never count as present. If none exist,
proceed normally.

Otherwise a prior round already ran, wholly or in part. Do not overwrite any existing
artifact. Report which files are present with their timestamps, and ask the tech lead how to
proceed — noting the likely intent:

- **All three exist** → the next round belongs on `<plan-name>-v<N+1>.md`.
- **The reviews are already written** → the tech lead may prefer resuming from a later phase
  over re-running the sub-agents.

---

**Sub-Agent Feed Rule (normative — governs Phases 1, 2, and 3):** Every sub-agent
receives: the plan file; `resolutions-vN.md` if available; and the phase-specific prior-phase
review files listed under each phase below. **Sub-agents do NOT receive
`.github/consensus-review-protocol/<plan-name>/review-history.md`** — this history feed is Phase
4a/4c (orchestrator) only; see the Version-Indexing Rule above. When the loaded resolutions file contains ACCEPT or
MODIFY entries, include this advisory note in the sub-agent prompt: "Note:
`resolutions-vN.md` contains [X] ACCEPT/MODIFY entries that will be applied in this
round's Phase 4b to produce `plan-v(N+1).md`. The plan text you are reviewing does not yet
reflect these changes. Do not re-raise findings that match a CLOSED entry in
`resolutions-vN.md` under the two-part test in §Oscillation similarity rule." If the resolutions
file contains an `## Additional Tech Lead Input`
section, explicitly surface its contents to the sub-agent as "Additional guidance from the
tech lead."

### Phase 1: Blue-Team Reviews

**Goal:** Independent constructive review — what is strong, feasible, and well-reasoned.

For each model in the model list:

1. Launch a sub-agent with that model.
2. Feed it per the Sub-Agent Feed Rule above — Phase 1 has no prior-phase review files to add.
3. Instruct it to write a **Blue-Team Review** per `references/review-general.md` and
   `references/review-mode-blue.md §Blue-Team`.
4. Save output to `.github/consensus-review-protocol/<plan-name>/<model-slug>-blue-v<N>.md`.

**Failure handling:** If a sub-agent fails to produce output, retry up to twice, then apply
the Model-loss policy below. Record all failures in the Completion Report.

**Voting thresholds (normative):** Severity changes in purple-team arbitration require a
majority (more than half) of successful models. Dismissal requires consensus (all successful
models agree). Both use the successful-model count, not the configured model count, as the
denominator — so a model failure raises the effective bar, which is why the Model-loss policy
below treats dropping below three models as a decision for the tech lead rather than an
automatic degradation.

**Sub-agent failure definition (normative):** A sub-agent has failed only if it returns an
error, returns an empty or unreadable response, or produces output missing the required
phase-specific header (e.g., `# Blue-Team Review:` for Phase 1). Only format-validated output
counts. **Elapsed time is never a failure signal:** a sub-agent waiting on a pending approval
or interactive prompt is working, not stalled, and must never be dropped for waiting — a
genuinely hung sub-agent is visible to the tech lead in session, and failing visibly is better
than silently losing a model. Sub-agents must not block on plan-content decisions; those
become `⚠️ QUESTION FOR TECH LEAD` entries in their output so the sub-agent completes.

**Model-loss policy (normative):** The threshold is three models because at two, "majority"
and "consensus" become the same test, and purple arbitration can no longer distinguish a
majority severity change from a unanimous dismissal. When a model fails all retries:

- **Three or more models still successful** → proceed, recording the loss in the Completion
  Report.
- **Fewer than three** → halt at the failing phase and ask the tech lead, naming the failed
  model, the error, and the attempt count, and offering: proceed with the survivors — available
  only with at least two survivors, since consensus is impossible below two — swap the model,
  or abort.
- The tech lead may pre-authorise degradation at Setup, in which case proceed with two or more
  survivors and record it. A deliberately configured two-model review is unaffected — this
  policy governs unplanned loss, not an informed configuration choice. Pre-authorisation is
  scoped to the run it is given in; a later round is asked again, whether or not the same model
  still fails.

**Do not proceed to Phase 2 until all successful blue files for this round are written.**

---

### Phase 2: Red-Team Reviews

**Goal:** Adversarial cross-review — attack the plan, find flaws, challenge blue-team optimism.

For each model in the model list:

1. Launch a sub-agent with that model.
2. Feed it per the Sub-Agent Feed Rule above, plus all `*-blue-v<N>.md` files.
3. Instruct it to write a **Red-Team Review** per `references/review-general.md` and
   `references/review-mode-red.md §Red-Team`.
4. Save output to `.github/consensus-review-protocol/<plan-name>/<model-slug>-red-v<N>.md`.

**Failure handling:** Same as Phase 1: retry up to twice, then apply the Model-loss policy.
Record all failures in the Completion Report.

**Do not proceed to Phase 3 until all successful red files for this round are written.**

---

### Phase 3: Purple-Team Reviews

**Goal:** Chaos engineering + full arbitration — stress-test with failure scenarios, synthesize
all findings, and produce prioritized change recommendations.

For each model in the model list:

1. Launch a sub-agent with that model.
2. Feed it per the Sub-Agent Feed Rule above, plus all `*-blue-v<N>.md` and `*-red-v<N>.md` files.
3. Instruct it to write a **Purple-Team Review** per `references/review-general.md` and
   `references/review-mode-purple.md §Purple-Team`.
4. Save output to `.github/consensus-review-protocol/<plan-name>/<model-slug>-purple-v<N>.md`.

**Failure handling:** Same as Phase 1: retry up to twice, then apply the Model-loss policy.
Record all failures in the Completion Report.

**Do not proceed to Phase 4 until all successful purple files for this round are written.**

---

### Phase 4: Orchestration

**Goal:** The orchestrating model synthesizes all reviews, the tech lead's prior resolutions,
and the current plan to produce the consolidated review, and (when applicable) the hardened
next version of the plan.

The orchestrator receives:

- The current plan (`plan-vN.md`)
- The tech lead's prior resolutions (`resolutions-vN.md`, if filled)
- All blue, red, and purple review files from this round
- `references/review-general.md`, read before writing the consolidated review, the resolutions
  file, or any plan-text edit — Proportionality and Economy of Expression (both defined there)
  govern the orchestrator's own output, not only findings authored by sub-agents.

Phase 4 executes three sub-phases sequentially within each run: 4a (consolidated review),
4b (apply prior approved resolutions to produce the new plan version), then 4c (resolutions
template). The tech-lead gate is inter-run: the TL fills in `resolutions-v<N+1>.md` between
runs, and Setup in the next run loads it as context for Phase 4b.

#### 4a: Consolidated Review

**Prose Editor pass (mandatory first step):** Before synthesising anything, the orchestrator
scans all review files for multi-line code blocks and translates them into prose, **except
inside a dedicated `## Hardened Implementation` section**, which intentionally holds fix code
and is preserved as-is. Translation happens when the content is quoted or synthesised into
`consolidated-v<N>.md`; the review files themselves are never modified. Divergent
`## Hardened Implementation` sections for the same finding are CONFLICTED, with all versions
presented to the tech lead.

**Rationale-deletion cross-check (normative):** When consolidating a finding whose Suggested
fix proposes deleting explanatory or rationale prose from the plan, check the flagged passage
against the loaded `review-history.md` entries. Annotate in the consolidated finding whether
the rationale is independently preserved there, so the tech lead's resolution reflects a
checked fact rather than a generic risk caveat.

Write `.github/consensus-review-protocol/<plan-name>/consolidated-v<N>.md`
per `references/phase-4a-output-formats.md §Consolidated-Review-Format`. Include:

- Model verdict table (Blue / Red / Purple per model)
- **Carried Forward Findings section**: every finding carried into this round's resolutions
  template from a prior round — a prior QUESTION FOR TECH LEAD or PHASE-4B-SKIP, for instance —
  listed with its original finding ID and a `Carried from: [source resolutions file path]`
  annotation, so the TL can trace its origin without opening prior files. Omit the section when
  nothing was carried forward.
- Blue team consensus
- Deduplicated formal findings from every finding-minting phase — red-team findings and
  net-new purple findings alike — under round-prefixed merged IDs
  (`R<round>-PLAN-MERGED-B1`, `R<round>-PLAN-MERGED-I1`, and so on), each recurrence of a
  previously REJECTED finding carrying a `Supersedes:` field naming the prior round's ID
- Purple team synthesis
- Finding cross-reference table

**CLOSED-finding deduplication (normative):** Check each finding against the loaded
`resolutions-vN.md`, and branch on the prior Resolution value:

- **ACCEPT or MODIFY** → where the finding substantially duplicates it (same section, same
  category of remediation), annotate "Previously resolved — see [resolution ID]" and do not
  present it as active.
- **REJECT** → never suppress. Re-raise as a ⚠️ RECURRING FINDING; oscillation detection takes
  precedence over deduplication.

**Exception, overriding the ACCEPT/MODIFY branch only:** a finding that cites materially new
evidence, or argues that a planned resolution is internally inconsistent with the plan, is
presented as new, flagged `⚠️ REOPENED RESOLUTION`, with a `Supersedes:` reference to the closed
finding ID. The marker keys on that reference and makes a finding disputing an ACCEPT or MODIFY
as visible as a recurrence against a REJECT.

Four conflict-resolution rules govern how findings from all phases are presented:

**Severity changes are permitted in arbitration.** Purple-team models may elevate or downgrade
a severity on chaos-engineering evidence and cross-model analysis, and the merged entry
reflects the majority severity where they disagree. Where no severity commands a majority —
whether they split evenly or too few addressed the finding — the finding is CONFLICTED at the
highest asserted severity with all positions listed, never a plain CONFIRMED finding at a
chosen level. This preserves the "Unresolved CONFLICTED BLOCKERs: N" count, the tech lead's
sole standing caution before declaring the plan sound.

**Full dismissal requires consensus.** DISMISSED requires that no purple-team model contests
it. Any contradicting position — CONFIRMED, CONDITIONAL, or a different severity — makes the
finding CONFLICTED instead, with all positions listed.

**Red-phase conflicts are resolved by the purple phase**, which cross-reads all red reviews and
is explicitly tasked with synthesis. No extra review round is needed.

**Purple-phase conflicts go directly to the tech lead.** Where purple models disagree on
disposition, the finding is labelled CONFLICTED with all positions presented, and the tech lead
resolves it via the resolutions file. No further review pass is run.

**After writing the consolidated review: proceed to Phase 4b (Apply Prior Approved
Resolutions), then Phase 4c (Resolutions Template).**

#### 4b: Apply Prior Approved Resolutions

**This phase executes in every run**, writing `<plan-name>-v<N+1>.md` in the
same directory as the input plan. On first runs it makes no content changes; on re-runs it
applies the tech lead's approved decisions from `resolutions-vN.md`.

**Final round archival (normative):** In a final round, apply the pending resolutions per the
Application order, write the final `<plan-name>-v<N+1>.md`, then write the Review History entry
noting that this was the final round and the plan was declared sound. Ambiguity guards apply
unchanged: a skip withholds the declaration and goes to the tech lead rather than silently
dropping a decision (see §Final round).

**Application order (normative):** Apply in this order, then by finding ID within each
category:

1. ACCEPT
2. MODIFY (plain findings only)
3. CONFLICTED findings carrying a binding TL decision — CONFLICTED status decides the
   category, whatever the resolution value
4. Companion-file changes, queued during steps 1–3 and applied here with the idempotency and
   post-write checks below. Within this category, edits apply in finding-ID order (BLOCKER,
   then IMPORTANT, then NICE-TO-HAVE; ascending within each severity).

**`Depends on:` (normative):** A finding naming a dependency defers within its category until
that dependency is applied; it never reorders across categories.

Evaluate each of these five conditions against the named dependency:

1. Is it REJECTed in this pass's resolutions file?
2. Is it absent from this pass's resolutions file?
3. Is it cyclic — does following the chain of `Depends on:` declarations from it, to its own
   dependency, and onward to the chain's end, return to the finding that names it?
4. Is it in a later Application-order category than the finding that names it?
5. Did it itself emit a `⚠️ PHASE-4B-SKIP` earlier in this pass — present in the resolutions
   file with a resolvable category, but its own application failed (target not found,
   ambiguity, or any other skip condition)?

If any condition holds, emit `⚠️ PHASE-4B-SKIP: [finding ID] — Depends on: [named ID] could not
be satisfied (rejected, not found this pass, cyclic, unsatisfiable by category ordering, or
itself skipped); apply the dependency first or remove the dependency declaration.`

**Target not found:** If an operation in steps 1–3 cannot locate its target content, emit
`⚠️ PHASE-4B-SKIP: [finding ID] — target content not found in the current plan text; content
may have been modified by a prior operation in this pass or may reference stale plan text.`
and continue with the remaining operations.

**Recorded no-op (normative):** An ACCEPT or MODIFY whose finding requires no plan change names
no target content, so it is not a location failure and MUST NOT emit `PHASE-4B-SKIP`. The
disposition is real: list it in the Completion Report as `<finding ID> ACCEPT → no plan change
(recorded)` and in the round's review-history entry under a `**Recorded no-ops:**` line, so it
survives in the durable archive. Recorded no-ops count as applied. Phase 4c states the
characterization in the finding's own Suggested-fix text at authoring time (e.g. "No plan
change required") rather than leaving Phase 4b to infer it.

Apply by Resolution value:

- **ACCEPT** — apply as recommended.
- **MODIFY** — apply with the tech lead's Notes adjustments.
- **REJECT** — never applied.
- **CONFLICTED with a binding decision** — apply the chosen position per the ACCEPT/MODIFY
  semantics in Notes. For CONFLICTED `## Hardened Implementation` findings, Notes MUST carry
  both a target anchor (verbatim heading, or first line of the target paragraph) and a change
  operation (replace / insert after). Without both, emit `⚠️ PHASE-4B-SKIP: [finding ID] —
  CONFLICTED HI Notes missing target anchor; cannot locate insertion point without guessing.`
  and continue.

Accepted purple-team improvements and structural hardening are applied likewise. Write a Review
History entry.

Phase 4b does NOT apply current-round findings; those go to the resolutions template for the
tech lead to decide.

**Conflict precedence rule:** If a current-round finding directly contradicts a prior ACCEPT
or MODIFY resolution for the same issue (same section, incompatible action), apply neither.
Record it as a `⚠️ QUESTION FOR TECH LEAD` in `resolutions-v<N+1>.md` carrying both the prior
decision and the new contradicting evidence, for the tech lead to resolve. Exact duplicates of
CLOSED findings already suppressed as "Previously resolved" do not trigger this rule.

**Candidate-amendment drafting (normative, within Phase 4a):** When a finding triggers the
Conflict precedence rule, Phase 4a asks whether its suggested fix is a bounded amendment to the
prior resolution — targeting a peripheral sub-clause — or an override of that resolution's core
operative change. If bounded, draft it as a labeled candidate amendment inside the
`⚠️ QUESTION FOR TECH LEAD` entry, with the reasoning shown, rather than presenting a bare
contradiction. Both versions still remain withheld until the tech lead signs off via the normal
Resolution field; this improves what the tech lead is shown, not who decides.

Write in planning prose. Do not introduce long code blocks.

**Companion reference file edits (normative):** Some resolutions change reference files (e.g.
`references/review-general.md`) rather than the plan. Identify the target from the finding's
`Notes:` field, falling back to its Summary or an explicit `Suggested fix` block when Notes
records only a decision or rationale — the common case for tech-lead-authored Notes. A path
that resolves to the plan file itself, in any versioned or unversioned form, is a plan-file
edit and never a companion target; decide path identity by repo-root-relative comparison, not
by basename.

Apply companion edits in Application-order step 4. A `Target file:` line may carry several
discrete operations; each operation is one edit and is independently subject to the five steps
below. For each edit, execute these steps in
order, emitting `⚠️ PHASE-4B-SKIP: [finding ID] — [reason] for [path]` rather than halting when
a step fails:

1. **Existence check.** If the target file does not exist, skip — Phase 4b never creates
   companion files.
2. **Anchor check.** If the quoted anchor is not found in the file, skip — except for a
   deletion, where an absent anchor means the deletion is already applied: log it as such and
   go to the next edit.
3. **Pre-write idempotency check.** Read the target file. If the change is already present
   verbatim, log "companion edit: already applied — skipped", make no change, and go to the
   next edit.
4. **Apply the change.**
5. **Post-write verification.** Re-read the file. If the change is not present — for a
   deletion, if the deleted text is still present — skip and record it as skipped, not
   successful. Otherwise record `Verified: [path]`.

Ambiguity of any kind — target, path, change description, or whether existing content already
constitutes the proposed change, including two or more candidate paths offered as alternatives
for the same edit — falls to NEVER GUESS.

**Anchor matching (normative):** When comparing a quoted anchor against file content — for
plan-file targets, companion-file targets, and the idempotency check alike — normalize all
runs of whitespace, including newlines and leading indentation, to a single space on both
sides; otherwise the match is exact and case-sensitive. Phase 4c writes quoted anchors
normalized onto one logical line so future anchors do not depend on this.

**PHASE-4B-SKIP recording procedure (normative):** Every `⚠️ PHASE-4B-SKIP: [message]` is
recorded verbatim in the round's `<workdir>/review-history.md` entry and in the Completion
Report under 'Skipped findings', which enumerates every skipped finding with its ID and reason.
Phase 4b then continues with the remaining resolutions without halting. Skip messages are never
written into the plan's own `## Review History` section.

Emit a skip in each of these cases:

- **MODIFY-ambiguity** — Notes are ambiguous about the required change:
  `⚠️ PHASE-4B-SKIP: [finding ID] — MODIFY notes ambiguous`. Setup's judgment pass catches the
  common case first; this is the backstop for what it missed, or for a clearly-stated but
  mechanically unlocatable change.
- **CONFLICTED-ambiguity** — Notes do not unambiguously select a model position:
  `⚠️ PHASE-4B-SKIP: [finding ID] — CONFLICTED Notes does not unambiguously select a model
  position`. Only `ACCEPT` and `MODIFY` CONFLICTED findings are in scope; `REJECT` adopts no
  position by design and never enters category 3. On an entry carrying `Presents options:`,
  Notes must name one of the listed labels or an explicit alternative; on one without it — a
  severity-only disagreement — any reasoned Notes satisfies the guard, `ACCEPT` included.
- **Unrecognised Resolution value** — present but not ACCEPT, REJECT, or MODIFY (defends
  against Setup Rule 1):
  `⚠️ PHASE-4B-SKIP: [finding ID] — Resolution value '[value]' is not ACCEPT, REJECT, or
  MODIFY`.
- **ACCEPT on a `Presents options:` entry** (defends against Setup Rule 4) —
  `⚠️ PHASE-4B-SKIP: [finding ID] — ACCEPT received on an entry presenting labeled options
  ([labels]). No option selected. TL must specify the chosen option via MODIFY with Notes.`

**Failure recovery:** If a write fails or is interrupted (context limit, crash, partial
output), preserve the partial output with a `.partial` suffix, stop, and tell the tech lead
exactly what was and was not written.

After successful generation of the new plan version, proceed to Phase 4c.

#### 4c: Resolutions Template

Write `.github/consensus-review-protocol/<plan-name>/resolutions-v<N+1>.md` pre-populated
with findings from this round's consolidated review. The inclusion rule is:

- **CONFIRMED findings** → include with standard `Resolution:` slot (ACCEPT / REJECT / MODIFY)
- **CONFLICTED findings** → include, listing every purple-model position, with a
  binding-decision slot. Pre-fill the slot `Resolution: <!-- MODIFY | REJECT — name option in
  Notes -->` when the entry presents labeled options, and the standard `Resolution: <!-- ACCEPT
  | REJECT | MODIFY -->` when it does not, since `ACCEPT` remains reachable there. Option labels (A, B, C) are never Resolution values; the tech lead names the
  position they adopt in Notes. For CONFLICTED `## Hardened Implementation` findings the Notes
  template MUST carry "Chosen position: [model A/B/C or alternative] | Target anchor: [verbatim
  section heading or first line of target paragraph in plan] | Change: [replace / insert
  after]" — Phase 4b emits PHASE-4B-SKIP without that anchor.
- **DISMISSED / FALSE POSITIVE findings** → exclude; the cross-reference table in
  `consolidated-v<N>.md` already records them and no tech lead action is needed.

**Producer disposition prohibition (normative):** Phase 4c MUST NOT dispose of a finding by
describing it inside another entry's prose. Each ID in the closed set below receives either its
own entry with a `Resolution:` slot, a DISMISSED row in this round's cross-reference table, or
an entry-level `Supersedes:` line — its own line, naming exactly one ID — in the entry that
absorbs it.

**Scope (normative):** the closed set is the `R<N>-PLAN-MERGED-*` and `R<N>-ATL-INPUT-*` IDs
the orchestrator minted in this round's consolidated review, plus the IDs listed in that round's
Carried Forward Findings section. IDs appearing only in sub-agent review files are inputs to consolidation, not
dispositions: the orchestrator merges their content into its own minted IDs, and they are not
separately tracked. This keeps the rule a closed enumeration rather than a scan over prose.

**Decision guidance.** Write it after the model positions, on every finding requiring the TL
to choose — CONFLICTED, or carrying labeled options.

- **Content:** the core tension, the key risk of each option, and any convergence signal across
  purple models. Present trade-offs; do NOT recommend.
- **Options:** where the disagreement is not solely over severity, enumerate every concrete
  option as a labeled entry stating exactly what the TL would write or change, whatever the
  number of model positions submitted. A CONFLICTED entry disputing only severity over one
  agreed remedy carries decision guidance without labels, and takes no `Presents options:`
  field.
- **Header field:** write a matching `Presents options: <labels>` field in the entry's header
  block. Setup's Rule 4 and `§4b` read this field, so the entry is self-describing. Never write
  it on an entry presenting no real choice: a single-path finding carries no labels and takes no
  field.
- **Decision-choice Open Questions with no CONFLICTED finding:** synthesize from the blue and
  red reviews that raised the question. Where no cross-model rationale exists, write
  `No cross-model rationale available for synthesis.`

**Additional Tech Lead Input conversion backstop (normative):** Once all findings are
compiled, Phase 4c scans the prior resolutions file's `## Additional Tech Lead Input` section
for numbered items that are plan-change directives (same test as `review-general.md
§Additional Tech Lead Input`: a request to change the plan, a reference file, or the protocol),
and checks each against existing entries for correspondence — same plan section and same
remediation category, per the oscillation similarity rule — in:

- a CONFIRMED or CONFLICTED finding in this round's consolidated review, or a DISMISSED entry
  in its cross-reference table;
- any entry in the loaded `resolutions-vN.md` **except** a REJECT — a REJECT match surfaces the
  item as `⚠️ RECURRING FINDING` with a `Supersedes:` reference to the prior finding ID rather
  than suppressing it;
- a non-blank, non-placeholder `Direct Companion File Edits Since Last Round` Answer field.

Where correspondence is found, the item is not duplicated. Otherwise Phase 4c surfaces it as a
CONFIRMED IMPORTANT finding carrying:

- **ID** `R<N>-ATL-INPUT-<M>`, M being the item number;
- **body** — the verbatim item text;
- **annotation** `Source: resolutions-v<N>.md §Additional Tech Lead Input, item <M> — not
  raised by any reviewer this round`.

Surface the item under the same rule whenever Phase 4c cannot confidently tell whether an entry
corresponds, or whether the item is a directive rather than an observation. The bias is toward
surfacing.

This is additive only: sub-agents still receive the section in Phases 1–3, and the TL retains
normal ACCEPT/REJECT/MODIFY authority — including REJECT where an item was an observation. The
scan runs before the Open Questions cross-reference annotation step.

**PHASE-4B-SKIP carry-forward.** Carry every `⚠️ PHASE-4B-SKIP` from this run into the Open
Questions section of `resolutions-v<N+1>.md` as an open `⚠️ QUESTION FOR TECH LEAD`. Each
entry carries:

- the verbatim content that caused the skip;
- a description of the proposed change, so the TL need not re-read the consolidated file;
- a labeled `Finding ID: [original finding ID]` line;
- an `Answer:` field pre-populated with `<!-- plain language; auto-resurfaces -->` (the
  template header states the full resurfacing rule once, rather than per entry)

The `Finding ID:` line is required on finding-originated questions: PHASE-4B-SKIP
carry-forwards, and Conflict-precedence withholdings. Locus-free questions omit it — NEVER
GUESS halts, and reviewer clarifying questions with no plan-section anchor.

**Open Question resurfacing (normative):** For every answered Open Question, Phase 4c asks
whether the settled Answer still calls for a plan or companion-file change that nothing in this
round's coverage set carries (same section and remediation category, per the oscillation
similarity rule). The coverage set has two members:

- an active finding in this round's consolidated review;
- an ACCEPT or MODIFY resolution applied in this round's Phase 4b.

Where neither carries it, Phase 4c MUST mint a CONFIRMED finding in
`resolutions-v<N+1>.md` so the decision has an application path:

- **Skip condition:** an Answer of exactly `N/A`, `cancel`, or `skip` (case-insensitive,
  whitespace-trimmed) decides not to act and is never resurfaced.
- **Pointer answers:** an Answer consisting only of an unambiguous reference to exactly one
  finding ID defers entirely to that finding's disposition and runs no coverage search — a
  REJECT needs no application path, an ACCEPT or MODIFY applied this round is already covered,
  and a finding that produced a `⚠️ PHASE-4B-SKIP` is already carried forward as its own Open
  Question. Where zero or several candidate IDs remain, surface a `⚠️ QUESTION FOR TECH LEAD`.
  Where the Answer carries text beyond the pointer, run the ordinary resurfacing test on that
  remaining text.
- **Finding body:** the proposed change, plus a concrete target.
- **Notes:** the tech lead's Answer, as context.
- **ID and severity:** where the question names an originating finding, reuse that finding's ID
  with a `-RESUBMIT` suffix, at that finding's severity. Strip any existing trailing
  `-RESUBMIT` first, so the ID carries exactly one. Where it names none, mint a new ID at
  IMPORTANT.

The test is whether the answer needs an application path, not whether the entry carries a
`Finding ID:` line. This covers what the Setup judgment pass does not: that pass asks whether
an Answer still *reads* unresolved, not whether a settled one has anywhere to land.

Before finalising the Open Questions section, annotate cross-references:

- **Which entries:** any `⚠️ QUESTION FOR TECH LEAD` substantially identical in scope (per the
  same similarity rule) to a finding already listed in this template's Findings for Tech Lead
  Resolution section.
- **How:** append `*(Related finding: [ID] — this question is also addressed there.)*` after
  the question text, and pre-populate that entry's `Answer:` field with
  `<!-- See [ID] — addressed there. -->`. The comment is a suggestion, not a default: Rule 2's
  placeholder definition governs Rule 3, so a comment-only Answer fails completeness exactly as
  a blank one does, and the TL still decides on the referenced finding.
- **Never suppress the question.** The TL may answer with a pointer to the finding (e.g.
  'See [ID]').

The template follows the format specified in `references/phase-4c-output-formats.md
§Resolutions Template Format`.

**Companion-file Notes pre-population (mandatory):** For each CONFIRMED finding meeting the
§Companion-target test, populate the Notes field with that target
path and change description rather than an HTML comment placeholder, so Phase 4b can act on it
next round without manual intervention. List one path and change per line when the finding
names several. For MODIFY, the tech lead replaces this baseline text rather than appending to
it. If the Summary's reference is ambiguous, apply NEVER GUESS and populate Notes with a
`⚠️ QUESTION FOR TECH LEAD` requesting the target path and change. For CONFLICTED findings the
Notes must additionally carry the binding-choice prompt: "Chosen position: [model position or
alternative] | Target file: [path] | Change: [description]".

**Direct Companion File Edits (mandatory section in every resolutions template):** Phase 4c
MUST include a **"Direct Companion File Edits Since Last Round"** section at the bottom of
every generated `resolutions-v<N+1>.md`: a TL-owned `Answer:` field recording edits the tech
lead made directly, outside the Phase 4b pipeline. Format: file path, what changed, reason;
"None" if there were none. It is never pre-populated with Phase 4b's own edits — those are
already listed in the Completion Report's §Companion Files Changed.

**After writing the resolutions template: STOP.** Present the consolidated review, the new
plan version, and the resolutions template to the tech lead.

**Present to the tech lead:** Emit the Completion Report per
`references/phase-4c-output-formats.md §Completion Report Format`, then stop. The report is an
ephemeral session summary and is never written to disk; the sole datum persisted from it is the
`**Sub-agent failures:**` line of the round's Review History entry. The report already
contains the verdict table, the file listing, the all-GO flag (when applicable), and the
next-step instructions — do not restate them separately. **Do not proceed. The tech lead leads
from here.**

---

### Resolutions Template Format and Completion Report Format

See `references/phase-4c-output-formats.md` for the exact, normative structure of both the
resolutions template (§Resolutions Template Format) and the Completion Report (§Completion
Report Format). Read this file when Phase 4c is reached — not needed during Setup or
Phases 1–3.

---

## References

- `references/review-general.md` — Shared General Requirements (NEVER GUESS rule, Additional
  Tech Lead Input handling, CLOSED-finding rules, Proportionality, Economy of Expression,
  Finding ID Format, Anti-Echo-Chamber Discipline) and
  §Verdict-Criteria (GO/CONDITIONAL GO/NO-GO mapping). Read by every sub-agent in every phase,
  alongside its own role file below, and by the orchestrator at Phase 4.
- `references/review-mode-blue.md` — Blue-Team role, tasks, and output format
- `references/review-mode-red.md` — Red-Team role, tasks, finding classification
  (BLOCKER/IMPORTANT/NICE-TO-HAVE), codebase verification requirements, and output format
- `references/review-mode-purple.md` — Purple-Team role, chaos-engineering scenarios,
  arbitration rules, and output format
- `references/phase-4a-output-formats.md` — Consolidated review format
- `references/phase-4c-output-formats.md` — Exact resolutions template structure and
  Completion Report format. Orchestrator-only; read at Phase 4c, not needed by sub-agents or
  during Setup/Phases 1–3.
- `references/completion-report-template.md` — Literal Completion Report template text,
  reachable transitively via `phase-4c-output-formats.md`. Orchestrator-only; same read-timing
  as `phase-4c-output-formats.md` above.
- `.github/consensus-review-protocol/<plan-name>/review-history.md` — Per-plan workdir artifact
  (not a shared skill-level reference file) holding all Review History entries from round 1
  onward; Phase 4b writes new entries directly to it. Readership and read depth are defined by
  the Version-Indexing Rule.
