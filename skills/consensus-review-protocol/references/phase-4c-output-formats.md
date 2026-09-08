# Phase 4c Output Formats

*Read this file only when Phase 4c is reached (writing the resolutions template and the Completion Report). It is not needed for Setup or Phases 1–3.*

---

## Resolutions Template Format

The `resolutions-v<N+1>.md` file must be generated with the exact structure below.

### 1. Document Header & Instructions

*   **Header:** Identify the plan name, version, date (ISO format), and round number. The H1 names the plan version the template is written *for*, matching the `Plan:` field — which is the authoritative field if the two ever disagree.
*   **Instructions:** This block is the tech lead's operating manual for the file — read once, then applied across every finding in the round. Write it as a short declarative list, one topic per bullet, never as continuous prose. Cover exactly these topics, each stated once here and never repeated per entry, since all of them apply identically to every entry:
    - **The three resolutions.** What `ACCEPT`, `REJECT` and `MODIFY` each mean.
    - **CONFLICTED findings.** These require a binding decision naming the adopted position, written in `Notes:`.
    - **Multi-option findings (Rule 4).** `ACCEPT` never selects among options — use `MODIFY` and name the chosen option in `Notes:`.
    - **Write settled decisions.** `Notes:` and `Answer:` should read as decisions, not as open questions. A field that still reads as unresolved is raised directly with the tech lead at Setup rather than silently proceeding or hard-failing; no special phrasing or override annotation is needed to mark a field as a deliberate directive.
    - **`Notes:` on ACCEPT or REJECT is informational.** Phase 4b does not read it. Two exceptions, both read by `§4b` whatever the resolution value: orchestrator-populated companion-file target text, and any CONFLICTED entry, whose `Notes:` name the adopted position. Reservations or conditions belong in a `MODIFY` instead.
    - **Answer outside the comments.** Setup's sweep deletes `<!-- ... -->` contents wholesale. Two fields accept a blank value at the completeness gate — `Notes:` on an ACCEPT or REJECT entry, and the Direct Companion File Edits `Answer:` — so text typed inside a comment there would pass validation and then be swept.
    - **`Depends on: [finding ID]`** (optional, see §2). Where one finding's correct application requires another to be applied first, naming the dependency makes Phase 4b order them correctly regardless of finding-ID order.

    **Scope constraint (normative):** describe only operations `SKILL.md §4b` actually defines; any operation named must be traceable to a rule there.

### 2. Findings for Tech Lead Resolution

List each `CONFIRMED` and `CONFLICTED` finding in priority order (`BLOCKER`s first — with CONFLICTED BLOCKERs at the very top of that tier — then `IMPORTANT`, then `NICE-TO-HAVE`).

*   **Entry skeleton (normative):** Every finding entry uses this field order, each field on its own line:
    - `**Severity:**` — BLOCKER / IMPORTANT / NICE-TO-HAVE, plus the CONFLICTED split when models disagree.
    - `**Source:**` — originating model and finding ID, or `Tech lead` for TL-authored entries.
    - `**Depends on:**` — optional.
    - `**Presents options:**` — optional; written whenever Phase 4c wrote labeled options into the entry (see the `Presents options:` bullet below).
    - `**Summary:**` — must state the defect, the evidence that establishes it, and the consequence if unfixed. A restatement of the finding title does not satisfy this.
    - `**Model positions:**` — required on every finding, not only CONFLICTED ones. Scaled to the disagreement: a single line when models agree (e.g. "All three models — CONFIRMED IMPORTANT, no dissent"); one line per model, stating its position and reasoning, when they differ.
    - `**Suggested fix:**` — required on every finding; where the fix is "no plan change", say so explicitly and give the reason. MUST end with a stated risk of adopting it (`Risk: none identified` is a complete and acceptable answer, so this never becomes invented boilerplate). Each labeled option in decision guidance MUST state its own risk in the same way.
    - `Resolution:` and `Notes:` slots — these two (and `Answer:`, in the Open Questions section) are written plain, not bolded, because they are the tech lead's input fields. Every other field above is orchestrator-written output and carries the `**` bold markers shown, exactly as quoted, matching the convention already used for `` `**Plan:**` `` elsewhere in this skill's spec.

    `**Summary:**` is placed immediately after the header block and before
    `**Model positions:**`, so the tech lead reads a statement of the defect before descending
    into per-model detail.

    Decision guidance remains governed by the CONFLICTED bullet below and is not part of this skeleton.
*   **CONFIRMED Findings:** Pre-fill with `Resolution: <!-- ACCEPT | REJECT | MODIFY -->` and a bare `Notes:` line with no comment (the header states its semantics; a comment here would only be swept at Setup). Where Phase 4c wrote labeled options into a CONFIRMED entry, use the option-bearing pre-fill instead: `Resolution: <!-- MODIFY | REJECT — name option in Notes -->`.
*   **CONFLICTED / Multi-Option Findings:** List all purple-model positions and include brief decision guidance (trade-offs and concrete labeled resolution options). Where the entry presents labeled options, pre-fill with `Resolution: <!-- MODIFY | REJECT — name option in Notes -->`; where a CONFLICTED entry presents no labeled options, keep the standard pre-fill `Resolution: <!-- ACCEPT | REJECT | MODIFY -->`.
*   **`Presents options:` field (normative):** When Phase 4c writes labeled options into an entry — whether the entry is CONFLICTED or a CONFIRMED finding carrying alternatives — it MUST add `Presents options: <labels>` to that entry's header block, listing the labels it used (e.g. `Presents options: A, B, C`). The field is written only when true, so its presence is the test, exactly as for `Depends on:`. It is read by Setup's Rule 4 (which fails `ACCEPT` on an entry carrying it) and by the pre-filled `Resolution:` placeholder choice. Entries with no labeled options omit the field entirely.
*   **`Depends on:` field (optional, normative):** If a finding's own Summary, Suggested fix, or purple synthesis states that it must be applied only after another specific finding lands (e.g., it overrides or builds on that finding's outcome), Phase 4c adds `Depends on: [finding ID]` directly beneath that finding's `Severity:`/`Source:` header block. This is populated by Phase 4c from the review evidence, not left for the tech lead to add — the tech lead may still add or remove it via MODIFY if the dependency is wrong. See `SKILL.md §4b Application order` for how Phase 4b orders dependent findings.
*   **Cross-round reference traceability (normative):** The first time a finding entry references a finding ID from an earlier round, it MUST also give, in the same place: the repo-root-relative path of the artifact that item lives in; a one-to-three sentence summary of what that item proposed or found, quoting its operative text where the current finding turns on exact wording; and its disposition if one exists (the tech lead's Resolution, or that it was withheld, superseded, or carried forward). The test is that a reader must be able to evaluate the current finding without opening the referenced file. Repeat references to the same ID within one entry need not restate the summary.
*   **ATL Reference Traceability (normative):** Findings referencing an ATL item MUST include a repo-root-relative link to the source resolutions file.

### 3. Open Questions

List `⚠️ QUESTION FOR TECH LEAD` entries raised across all phases (context, options, and an `Answer:` line).

*   **`Finding ID:` field (normative):** Every **finding-originated** Open Question entry MUST carry a labeled `Finding ID: [original finding ID]` line as an entry-level field (its own line, naming exactly one finding ID — an incidental prose mention does not count), so the tech lead can trace the question to its origin. Finding-originated means the question arose from a specific finding: PHASE-4B-SKIP carry-forwards, and questions recorded because `SKILL.md §4b`'s Conflict precedence rule withheld a change. Locus-free questions — orchestrator NEVER GUESS halts, and reviewer clarifying questions with no plan-section anchor — omit it.
*   **Exclusions:** Do NOT include questions whose sole purpose is soliciting a soundness declaration or continuation-round selection — soundness is declared in session, not in this file (see `SKILL.md §Final round`).
*   **Cross-References:** If an Open Question is substantially identical to a finding in Section 2, append `*(Related finding: [ID] — this question is also addressed there.)*`. Do NOT suppress the question.

### 4. Additional Tech Lead Input

Include an HTML comment inviting remarks/corrections.

*   **Format:** Instruct the user to use a numbered list with a blank line between items.

### 5. Direct Companion File Edits Since Last Round

TL-owned `Answer:` field for edits made outside the Phase 4b pipeline (Format: file path, what changed, reason, or "None"). Phase 4b's own edits are not listed here — see the Completion Report's §Companion Files Changed.

---

## Completion Report Format

**Completion Report output format (normative):** After Phase 4c, emit the Completion Report
exactly per the template in `references/completion-report-template.md`, substituting every
bracketed placeholder with this round's actual values. The template file's content is itself
valid rendered markdown — emit it exactly as written, in the section order given, never wrapped
in a code fence.

### Final Round Rules (normative)

In a final round, omit every section that depends on Phase 1–3 or 4a output, list only Phase 4b's output files, and replace the "Next step" instructions with either the sound declaration or — if anything failed to apply — a plain statement of what did not apply and why, addressed to the tech lead.

**Session statistics block (normative):** The final round's report carries a session statistics block derived entirely from the workdir file listing, `wc` output, and anchored `grep -c` counts. Read no file's contents: no `consolidated-v*.md`, `resolutions-v*.md` or `*-blue/red/purple-v*.md` is reopened, and no bookkeeping file is created. Report:

*   **Completed non-final rounds** — the `consolidated-v*.md` count.
*   **Artifacts generated** — total workdir file count, and the review-file count.
*   **Total workdir size** in words.
*   **Model slugs used** — parsed from the `<model-slug>-` prefix of the review filenames. Report a distinct-slug count, not a model count, and state that alias-style names such as `claude-opus-latest` inflate it above the number of distinct real models.
*   **Plan version span** — first to final.
*   **Final plan size** in words and lines.
*   **Tech-lead decision distribution** across the cycle — three `grep -c` passes over `resolutions-v*.md` for `^Resolution: ACCEPT`, `^Resolution: MODIFY` and `^Resolution: REJECT`, each anchored to line start and end of value so a `Resolution: <!-- ... -->` placeholder is not miscounted.

Findings by severity, the BLOCKER trend and convergence history each require a content read and are out of scope.
