# Review Mode: General Requirements & Verdict Criteria

*Shared by all three role files (`review-mode-blue.md`, `review-mode-red.md`,
`review-mode-purple.md`). Every sub-agent receives this file plus its own role file.*

## General Requirements (All Modes)

### ⚠️ NEVER GUESS — Core Protocol Rule

**This is non-negotiable.** If you encounter any of the following, you MUST write a
`⚠️ QUESTION FOR TECH LEAD:` entry instead of guessing, assuming, or inferring:

- A requirement, intent, or constraint is **ambiguous** and multiple interpretations are valid
- A referenced component, system, or dependency is **outside your knowledge** and cannot be
  verified from the provided files
- A trade-off or design decision has **no clear right answer** and requires human judgment
- Classifying a finding as BLOCKER vs. IMPORTANT would materially change the plan, but the
  evidence is inconclusive

**Format for unresolvable questions:**

```
⚠️ QUESTION FOR TECH LEAD: [Section or finding ID]
Ambiguity: [Describe exactly what is unclear and why it cannot be resolved with the evidence provided]
Options: [List the possible interpretations and their implications]
Impact: [What changes depending on the answer]
```

Do NOT fill in guesses. Do NOT silently pick one interpretation. Unresolved assumptions in a
plan are more dangerous than acknowledged questions. Surface them — the tech lead will resolve.

---

### Codebase Verification

When the plan references specific code, files, functions, or line numbers, **verify those
claims against the actual codebase** before classifying findings. Use grep/view tools to:

- Confirm defects exist before listing them as blockers
- Check that referenced file paths and function names are accurate
- Validate that proposed fixes are compatible with the surrounding code

Findings based on unverified codebase assumptions are less credible and easier to dismiss.
Cite file paths and line numbers whenever possible.

---

### Hardened Implementation Sections

Reviewers may include a dedicated `## Hardened Implementation` section in their review output
when a finding genuinely requires specific implementation detail that cannot be expressed
clearly in prose alone. Code blocks within this section are exempt from the Prose-First rule
and will be preserved as-is through the Phase 4a Prose Editor pass. Use this sparingly — it
is a last resort when prose truly cannot convey the fix. If a reviewer is uncertain whether
implementation specifics are warranted, prefer raising a `⚠️ QUESTION FOR TECH LEAD` instead.

---

### Additional Tech Lead Input

If the loaded resolutions file (`resolutions-vN.md`) contains an `## Additional Tech Lead
Input` section, read it in full before beginning your review. Treat its contents as
authoritative clarifications, corrections, and constraints from the tech lead for this round.
They override default model assumptions where applicable. Cite this section when it changes a
finding or verdict.

- **Plan-change directives MUST become findings.** If the Additional Tech Lead Input contains
  a request that requires a change to the plan, a reference file, or the protocol itself,
  surface it as a finding (with appropriate severity) so it enters the Phase 4b application
  pipeline via the resolutions template. Failure to raise it as a finding means the directive
  is silently dropped — never reaching `resolutions-v<N+1>.md` and never being applied.

---

### CLOSED Findings

- **A finding the tech lead REJECTed may be re-raised only on materially new evidence**, which
  the entry must name — evidence absent from the round that produced the REJECT, or a
  demonstration that the plan's own text is now inconsistent with the rejection. Disagreeing
  with the decision is not new evidence. Without it, do not re-raise: note the suppression in
  one line and move on. The tech lead's REJECT is a decision, not a deferral.
- **Findings present in the loaded `resolutions-vN.md` with Resolution ACCEPT or MODIFY are
  CLOSED.** Do not re-flag CLOSED findings unless you have materially new evidence not
  present in the prior review. If you believe a CLOSED finding recurs, cite the original
  finding ID and describe specifically what is new.
- **Exception: REJECT resolutions do not qualify for deduplication suppression.** A finding
  whose prior resolution was REJECT must be re-raised as a ⚠️ RECURRING FINDING — do not
  annotate it 'Previously resolved.' Only ACCEPT and MODIFY resolutions qualify a finding for
  deduplication suppression.
- **Exception for plan-embedded question blocks:** If a `⚠️ QUESTION FOR TECH LEAD` block
  embedded in the plan text references a finding ID that carries `Resolution: ACCEPT, REJECT,
  or MODIFY` in the loaded resolutions file, treat the question as answered. Do not
  re-surface it as an open question per NEVER GUESS.

### Proportionality (All Modes)

- **Scope:** any finding whose remedy **adds** a rule, field, artifact, section, or check.
  Findings that repair, delete, or clarify existing text are exempt.
- **State it in one line.** Every in-scope finding carries a `Proportionality:` line naming
  the failure the addition prevents; whether that failure is **demonstrated** (grounded in a
  concrete instance already present in the plan's own text, its cited evidence, or a documented
  incident) or **anticipated** (no concrete instance yet exists; the finding argues from
  reasoning about what could go wrong); and whether an existing rule already covers it. Short
  forms are expected and sufficient, e.g. `Proportionality: prevents silent loss of a finding
  ID — demonstrated (round 51's tracking-loss event); no existing rule covers it.`
- **Check these signals** and say so when one applies: the failure is anticipated rather than
  demonstrated; an existing mechanism already covers it; the remedy is a **detector over text the
  protocol itself authors**, where constraining the producer would be simpler; or the machinery
  costs more than the failure it prevents, especially when that failure already fails loudly
  and is fixed in one line.
- **This annotates, it never suppresses.** Raise the finding regardless. Proportionality is
  evidence for the tech lead's decision, not a filter on what reaches them.
- **Silence is a valid result.** Returning no findings — at a severity, or at all — is a
  legitimate outcome, not a failed review. Do not manufacture findings to fill a section.
- **It cuts both ways, under the same test.** Under-specification is equally reportable, but a
  vagueness claim must be falsifiable: name two readings of the text that lead an executing
  agent to different behaviour, and the input that distinguishes them. A finding that a rule
  "could be clearer", is "ambiguous", or "does not specify" what to do — without naming those
  two readings — is not a finding. Every rule can always be made more specific; that alone is
  never evidence of a defect. The target is proportion, not minimalism.

**Remedies are proportionate too.** Propose the smallest change that removes the defect. Where
text is contradicted, superseded, or dead, the remedy is to delete it — not to annotate it as
superseded, which leaves the contradiction in the file for a future reviewer to re-raise.

The orchestrator applies the same test when authoring findings in Phases 4a and 4c.

### Economy of Expression (All Modes)

- **Scope:** every output this protocol produces — Blue/Red/Purple review documents, the Phase
  4a consolidated review, the full Phase 4c resolutions file (including per-finding entries),
  `review-history.md` entries, and any plan or companion-file text the orchestrator authors when
  applying a fix.
- **The test:** does this sentence add a fact, decision, or risk not already stated? If not, cut
  it. State facts plainly; cut restatement, narrative framing, and elaboration that doesn't
  change the reader's conclusion.
- **Exempt — never compress these:** mandated message strings the protocol requires verbatim
  (e.g. `⚠️ PHASE-4B-SKIP`/`⚠️ QUESTION FOR TECH LEAD` text), quoted anchors, the Review History
  pointer line (its exact wording is fixed by `SKILL.md §Review History archival`), and
  mandatory structural fields `§4b`/`§4c` require by name (e.g.
  `Presents options:`, `Depends on:`, the CONFLICTED Hardened-Implementation `Chosen position: |
  Target anchor: | Change:` triple). Economy of Expression governs prose elaboration only; it
  never removes content a rule elsewhere requires by name.
- **Prospective, not retroactive.** Applies to content authored after this section lands; prior
  rounds' review-history entries and resolutions files are not rewritten to comply.

The orchestrator reads this file (`references/review-general.md`) before writing the
consolidated review, the resolutions file, or any plan-text edit, and applies both
Proportionality and Economy of Expression to its own output — not only when authoring findings.

### Finding ID Format (All Modes)

Every finding minted by a Red-Team or Purple-Team sub-agent uses the shape
`PLAN-<MODEL>-<TYPE><N>`, where:

- `<MODEL>` is a short model slug (e.g., `GPT`, `OPS`, `SON`).
- `<TYPE>` is `B` (blocker), `I` (important), or `N` (nice-to-have) for Red-Team findings.
  Purple-Team net-new findings (raised by the purple reviewer itself, not merged from a prior
  phase) use the reserved type letter `P` instead — e.g., `PLAN-OPS-P1` — so a purple sub-agent
  minting its own findings never collides with the same model's earlier Red-Team output in the
  same round. Purple findings that merely arbitrate or elevate an existing Red-Team finding keep
  that finding's original ID; `P` is only for findings with no prior-phase counterpart.
- `<N>` is a sequence number within that type, per model, per phase.

**Closed class set (normative):** `B`, `I`, `N`, and `P` are the entire set of valid `<TYPE>`
letters; no other letter is defined. A sub-agent output carrying any other class letter is not
merged — the orchestrator reports it to the tech lead as a `⚠️ QUESTION FOR TECH LEAD` naming
the unrecognised letter and the finding it appeared on, rather than merging it or guessing its
class.

### Anti-Echo-Chamber Discipline (Red-Team and Purple-Team Only)

- **Scope:** Applies only to phases that receive prior-phase AI review output as context —
  Red-Team (receives Blue-Team files) and Purple-Team (receives Blue-Team and Red-Team
  files). Blue-Team has no prior-phase AI output to reference and is exempt.
- **Do not restate, paraphrase, or summarize a prior-phase finding you agree with.**
  Agreement is expressed by silence, not repetition — if you agree with a Blue-Team or
  Red-Team finding, do not write it again in your own output.
- **Every finding must do at least one of the following** relative to prior-phase output:
  (a) contradict or weaken a prior-phase position with specific evidence, (b) surface
  evidence, an angle, or a failure mode that no prior phase raised, or (c) combine two or
  more prior findings into a new compound risk not previously stated (see `review-mode-red.md`
  §Tasks item 8 for the Red-Team version of this).
- **Do not use transitional agreement phrases** such as "As the Blue Team noted," "I agree
  with the Red Team," "Building on the previous finding," or equivalents.
- **If there is no net-new content to add,** say so explicitly in your Summary rather than
  re-summarizing: "No net-new findings beyond [prior phase] — see [finding ID(s)] for
  existing coverage."
- **Blue-Team promotion carve-out (normative exception to the silence rule):**
  - **Scope:** The "silence expresses agreement" rule above applies only to restating
    other **Red-Team or Purple-Team** findings from an earlier phase within the same run
    that already carry a formal ID.
  - **Blue-Team output is exempt:** Blue's Internal Coherence entries and Load-Bearing
    Assumptions have no ID and no `Resolution:` slot, so nothing carries them into the
    resolutions pipeline. A Red-Team or Purple-Team reviewer who agrees with a Blue-Team
    coherence defect MUST restate it as its own formal, IDed finding — this is promotion,
    not echo-chamber padding.
  - **Mandatory-section exemption:** "No net-new findings beyond [phase] — see [ID]" is
    sufficient content for any mandatory-but-otherwise-empty synthesis section (e.g.,
    `### Blue-Team Insights to Preserve`, "Purple team synthesis") — restating agreed
    Blue-Team content in those specific mandated sections is exempt from the silence rule
    since they serve a downstream-plan-authoring purpose rather than review-padding.

---

## §Verdict-Criteria

**Normative definition.** This section is the sole source of truth for GO / CONDITIONAL GO /
NO-GO criteria — `SKILL.md §Verdict-to-severity` points here rather than duplicating it.

Apply the following criteria when choosing a verdict for any review phase (Blue, Red, or Purple):

- **GO:** No unresolved BLOCKERs remain. Open IMPORTANT findings do not count as blocking
  conditions. All critical paths are sound.
- **CONDITIONAL GO:** One or more BLOCKERs exist that are addressable without plan redesign. Each blocking condition must be listed by finding ID, in the phases that mint findings (Red, Purple); Blue states its conditions in prose. Use CONDITIONAL GO when findings can be resolved in the next round by adding, removing, or modifying discrete plan sections.
- **NO-GO:** Use only when the plan is fundamentally unexecutable in its current form — for example, a contradictory protocol element (applying one fix invalidates another), a circular dependency in the workflow, or multiple simultaneous structural BLOCKERs that cannot be resolved independently. In practice, NO-GO should be rare; if uncertain, use CONDITIONAL GO and surface the concern as a BLOCKER. A single well-qualified BLOCKER that is addressable by modifying a discrete section does NOT trigger NO-GO.
