# Documentation Assets Architecture Analysis

## Current State Inventory

### Assets by Type

| Asset | Type | Lines | Scope | Context Loading |
|-------|------|-------|-------|-----------------|
| **doc-reviewer.agent.md** | Agent | 441 | Persona-based | Always-on (if used) |
| **doc-style-guide.md** | Reference | 643 | Agent dependency | Always-on (if agent used) |
| **documentation-reviewer** | Skill | 59 | Task-specific | JIT on intent |
| **documentation.instructions.md** | Path Instruction | 116 | `docs/**/*.md` | JIT on file match |
| **documentation-rtd.instructions.md** | Path Instruction | 94 | `docs/**/*.{md,rst}` | JIT on file match |
| **documentation-not-rtd.instructions.md** | Path Instruction | 25 | `docs/**/*.md` | JIT on file match |
| **documentation-release-notes.instructions.md** | Path Instruction | 76 | `docs/release-notes/artifacts/**` | JIT on file match |
| **TOTAL** | | **1,454 lines** | | |

### Current Distribution Pattern

```
common-documentation collection ships:
├── documentation.instructions.md (116 lines) - JIT loaded
└── documentation-reviewer skill (59 lines) - On-demand

PR #24 proposes adding:
├── doc-reviewer.agent.md (441 lines) - Always-on if used
└── doc-style-guide.md (643 lines) - Always-on dependency
```

---

## Architectural Issues

### 1. **Duplication & Overlap**

**Problem:** Multiple assets define similar content with unclear boundaries.

| Concern | Where It Appears |
|---------|------------------|
| **Diátaxis framework** | `documentation.instructions.md`, `doc-reviewer.agent.md`, `documentation-reviewer` skill |
| **Style rules** (headings, code blocks, lists) | `documentation.instructions.md`, `doc-style-guide.md` |
| **How-to guide format** | `documentation.instructions.md` (90 lines on tutorials/how-tos), `doc-reviewer.agent.md` (Stage 2) |
| **File structure rules** | `documentation-rtd.instructions.md`, `documentation-not-rtd.instructions.md` |

**Example overlap:**

```markdown
# documentation.instructions.md (lines 98-99)
- **Code examples**: Do not use prompt marks (for example, `$` or `#`) in code examples.

# doc-style-guide.md (lines 459-462)
**DO NOT** use `$` or `#` prompts in code samples except when using the 
`console` lexer, which makes them non-selectable.
```

### 2. **Instructions Containing Workflows**

**Problem:** Path instructions contain procedural steps, which should be in skills.

**`documentation.instructions.md` (lines 41-83):**
- 8-step tutorial structure (title → introduction → what you'll do → ... → tear down)
- This is a **generation workflow**, not a constraint

**Better split:**
- **Instruction**: "Tutorials follow Diátaxis principles (learning-oriented, end-to-end journey)"
- **Skill**: "Generate a tutorial" (with scaffolding script that creates the 8-section structure)

### 3. **Context Pollution Risk**

**Scenario:** Developer opens `docs/how-to/backup-database.md` to fix a typo.

**What loads:**
1. ✅ `documentation.instructions.md` (116 lines) - Relevant, appropriate
2. ✅ `documentation-rtd.instructions.md` (94 lines) - If RTD project, relevant
3. ❌ All Diátaxis guidance (duplicated across files)
4. ❌ Tutorial structure rules (not relevant for how-to edit)
5. ❌ Release notes guidance (if matching glob pattern)

**If doc-reviewer agent is active:**
- ❌ +441 lines of agent persona
- ❌ +643 lines of style guide
- ❌ **Total: 1,294 lines loaded for a typo fix**

### 4. **Unclear Asset Boundaries**

When should you use what?

| User Intent | Current Answer | Clarity |
|-------------|----------------|---------|
| "Fix this typo in docs" | Instructions auto-load? Agent active? | ❌ Unclear |
| "Review my docs PR" | Use agent? Use skill? Both? | ❌ Unclear |
| "Generate a tutorial" | Instructions have template, but no workflow | ❌ Workflow missing |
| "Ensure RTD compliance" | RTD instructions? Agent stage 1? | ❌ Overlap |

---

## Proposed Architecture

### Design Principles

1. **Instructions = Constraints** (what rules to follow)
2. **Skills = Workflows** (how to accomplish tasks)
3. **Agents = Perspectives** (cognitive lenses, not jobs)
4. **Minimize Overlap** (DRY principle across asset types)

### Proposed Asset Map

#### **Path Instructions (Context-Aware Rules)**

**What they should contain:**
- Hard constraints (US English, sentence case)
- Framework-specific syntax (MyST vs reST)
- Project conventions (file naming, directory structure)
- Tool compliance (vale, lychee, spelling)

**What they should NOT contain:**
- Workflows (how to generate/review docs)
- Long examples (reference external assets)
- Procedural checklists (move to skills)

**Proposed files:**

```
.github/instructions/
├── documentation-base.instructions.md          # Core rules (90 lines)
│   ├── Diátaxis categories (definitions only)
│   ├── Style rules (headings, lists, code blocks)
│   ├── applyTo: docs/**/*
│
├── documentation-rtd.instructions.md           # RTD-specific (60 lines)
│   ├── Sphinx directives, toctree rules
│   ├── Redirect rules for conf.py
│   ├── applyTo: docs/**/*.{md,rst}
│
├── documentation-release-notes.instructions.md # Release notes (70 lines)
│   ├── Artifact format, filename conventions
│   ├── applyTo: docs/release-notes/artifacts/**
│
└── documentation-changelog.instructions.md     # Changelog rules (NEW, 20 lines)
    ├── When to update changelog
    ├── applyTo: docs/changelog.md
```

**Total Instructions Context: ~240 lines** (down from 311, removing workflow content)

---

#### **Agent Skills (On-Demand Workflows)**

**Skill 1: `documentation-reviewer`** (Enhanced, ~200 lines)

**Purpose:** Comprehensive documentation review workflow

**Structure:**
```
.github/skills/documentation-reviewer/
├── SKILL.md                          # Main workflow (200 lines)
│   ├── Stage 1: Categorization (Diátaxis)
│   ├── Stage 2: Structural audit
│   ├── Stage 3: Style & syntax
│   ├── Stage 4: Completeness & navigation
│   ├── Stage 5: Code backing verification
│   ├── Stage 6: Final report generation
│
├── assets/
│   └── style-guide.md                # Comprehensive style guide (643 lines)
│       ├── Complete style rules
│       ├── Canonical patterns
│       ├── Fetched during review, not always-on
│
└── scripts/
    └── run_rtd_checks.sh             # Automated linting (NEW)
        ├── make spelling linkcheck woke lint-md
        ├── Captures output for agent review
```

**Invocation examples:**
- "Review this PR's documentation"
- "Audit docs/how-to/backup.md"
- "@documentation-reviewer check for Diátaxis compliance"

**Key improvements:**
- Consolidates agent workflow + style guide
- Loads JIT (only when review needed)
- Bundles all reference material
- Can be enhanced with automation scripts

---

**Skill 2: `documentation-generator`** (NEW, ~150 lines)

**Purpose:** Scaffold new documentation files following Canonical patterns

**Structure:**
```
.github/skills/documentation-generator/
├── SKILL.md                          # Generation workflow (150 lines)
│   ├── Step 1: Determine category (Tutorial/How-to/Reference/Explanation)
│   ├── Step 2: Run scaffolding script
│   ├── Step 3: Populate with content
│   ├── Step 4: Validate structure
│
├── scripts/
│   ├── scaffold_tutorial.py          # Creates 8-section tutorial
│   ├── scaffold_howto.py             # Creates "How to..." guide
│   ├── scaffold_reference.py         # Creates reference doc
│   └── scaffold_explanation.py       # Creates explanation doc
│
└── references/
    ├── tutorial-template.md          # 8-section structure from instructions
    ├── howto-template.md
    ├── reference-template.md
    └── explanation-template.md
```

**Invocation examples:**
- "Generate a tutorial for deploying the charm"
- "Create a how-to guide for backup procedures"
- "Scaffold reference docs for the CLI commands"

**Key benefits:**
- Removes workflow content from instructions
- Provides automation (DRY for repetitive structure)
- Enforces consistency via templates
- Can be extended with AI content generation

---

**Skill 3: `documentation-publisher`** (NEW, ~80 lines)

**Purpose:** Prepare documentation for publication (RTD build, release notes compilation)

**Structure:**
```
.github/skills/documentation-publisher/
├── SKILL.md                          # Publication workflow (80 lines)
│   ├── Step 1: Run full RTD build
│   ├── Step 2: Check for broken links/spelling
│   ├── Step 3: Validate toctree structure
│   ├── Step 4: Verify redirects configured
│   ├── Step 5: Check release notes artifacts
│
└── scripts/
    ├── validate_rtd_build.sh         # Full docs build
    ├── check_navigation.py           # Toctree validator
    └── compile_release_notes.sh      # Release notes assembly
```

**Invocation examples:**
- "Prepare docs for RTD deployment"
- "Validate all documentation is ready for release"
- "Check for broken links before merging"

---

#### **Custom Agents: Do We Need Any?**

**Question:** Should we keep a `doc-reviewer` agent or eliminate it entirely?

**Analysis:**

| Criterion | Doc-Reviewer Agent | Strong Agent (e.g., Security Auditor) |
|-----------|-------------------|--------------------------------------|
| **Unique perspective?** | ❌ Applies checklist | ✅ "Think like an attacker" |
| **Tool constraints?** | ❌ Uses all tools | ✅ Read-only, no code edits |
| **Cognitive lens?** | ❌ "Follow 8 stages" | ✅ "Assume hostility" |
| **Context persistence?** | ❌ One-time review | ✅ Ongoing security mindset |

**Recommendation: ❌ No custom agent needed.**

**Rationale:**
- Documentation review is a **task** ("review these docs"), not a **role** ("be a reviewer")
- The comprehensive skill provides all necessary workflow
- Path instructions provide context-aware rules
- No unique cognitive value from agent persona

**Alternative for "persistent doc focus":**
- Use path instructions (already JIT loaded when in docs/)
- Invoke skill explicitly when review needed
- If user wants "doc-focused session", they can say "I'm working on docs, help me follow guidelines" (Copilot will naturally weight doc-related context)

---

## Migration Path

### Phase 1: Consolidate Skills (Immediate)

**Action:** Merge agent → enhanced skill

1. **Create enhanced skill:**
   ```bash
   # Use generate-agent-skills workflow
   mkdir -p assets/skills/documentation-reviewer/assets
   mv assets/agents/doc-style-guide.md assets/skills/documentation-reviewer/assets/
   # Merge doc-reviewer.agent.md workflow into SKILL.md
   ```

2. **Update collection:**
   ```yaml
   common-documentation:
     description: "Documentation standards and review skill"
     items:
       - src: assets/instructions/documentation/documentation.instructions.md
         dest: .github/instructions/documentation.instructions.md
       - src: assets/skills/documentation-reviewer
         dest: .github/skills/documentation-reviewer/
       # Remove agent + loose style guide
   ```

3. **Validate:**
   ```bash
   python3 assets/skills/generate-agent-skills/scripts/validate_skill.py \
     --path assets/skills/documentation-reviewer
   ```

**Impact:**
- ✅ Removes 1,084 lines from always-on context (agent + style guide)
- ✅ Makes comprehensive workflow available on-demand
- ✅ Bundles all reference material together
- ✅ No breaking changes (skill already exists in collection)

---

### Phase 2: Refactor Instructions (Next)

**Action:** Extract workflows → create generator skill

1. **Slim down documentation.instructions.md:**
   - Remove lines 41-92 (tutorial/how-to structure details)
   - Keep only Diátaxis **definitions** (what each category means)
   - Keep style rules (but reference skill for details)

2. **Create documentation-generator skill:**
   - Extract structure templates to `references/`
   - Write scaffolding scripts
   - Define generation workflow

3. **Update instructions:**
   ```markdown
   ### Guidance on tutorials
   
   A tutorial is a learning-based, end-to-end experience. For detailed 
   structure and generation workflow, use the `documentation-generator` skill.
   
   Key principles:
   - Learning-oriented (not task-oriented)
   - Complete journey (setup → deploy → verify → teardown)
   - Safe environment (Multipass, test model)
   ```

**Impact:**
- ✅ Instructions become pure constraints (shorter, clearer)
- ✅ Workflows moved to reusable, automatable skills
- ✅ Path instructions load faster (less content)
- ✅ Enables future automation (scaffolding scripts)

---

### Phase 3: Add Publisher Skill (Future)

**Action:** Formalize publication workflows

1. **Create documentation-publisher skill:**
   - RTD build validation
   - Navigation structure checks
   - Release notes compilation

2. **Integrate with CI:**
   - Skill can be invoked from GH Actions
   - Provides consistent pre-merge checks
   - Automates release notes assembly

**Impact:**
- ✅ Codifies tribal knowledge
- ✅ Reduces manual release prep work
- ✅ Consistent quality gates

---

## Context Economics Comparison

### Current State (with PR #24)

| Scenario | Context Loaded | Lines |
|----------|----------------|-------|
| **Typo fix in docs/** | Path instruction + Agent + Style guide | 116 + 441 + 643 = **1,200** |
| **New tutorial generation** | Path instruction + (no workflow) | 116 (missing tools) |
| **PR review** | Path instruction + Agent + Style guide + Skill (?) | **1,259** (duplication) |

### Proposed State

| Scenario | Context Loaded | Lines |
|----------|----------------|-------|
| **Typo fix in docs/** | Path instruction only | **90** (88% reduction) |
| **New tutorial generation** | Path instruction + Generator skill (JIT) | 90 + 150 = **240** |
| **PR review** | Path instruction + Reviewer skill (JIT) | 90 + 200 = **290** (77% reduction) |

**Aggregate Savings:**
- **Typo fix:** 1,200 → 90 lines (**-92%**)
- **PR review:** 1,259 → 290 lines (**-77%**)
- **Tutorial generation:** Now possible with automation (was manual)

---

## Recommendations Summary

### ✅ Do This

1. **Immediate:** Merge doc-reviewer agent → enhanced documentation-reviewer skill
2. **Next sprint:** Refactor instructions to remove workflow content
3. **Future:** Create documentation-generator skill with scaffolding scripts
4. **Future:** Create documentation-publisher skill for release prep

### ❌ Don't Do This

1. ❌ Don't keep both agent and skill (duplication)
2. ❌ Don't put workflows in path instructions (wrong asset type)
3. ❌ Don't create a doc-reviewer agent (no unique perspective)
4. ❌ Don't leave style guide as loose file (bundle in skill)

### 🎯 North Star

**"Instructions define what; Skills define how."**

- **Instructions:** "Use sentence case for headings" (constraint)
- **Skills:** "Review this file's headings for sentence case compliance" (workflow)

---

## Open Questions

1. **Should documentation.instructions.md become documentation-base.instructions.md?**
   - Clearer naming (base = common rules)
   - Aligns with -rtd/-release-notes variants

2. **Should we split style-guide.md into multiple assets?**
   - Current: 643 lines monolithic
   - Alternative: style-guide-base.md + style-guide-rtd.md + style-guide-canonical.md
   - Tradeoff: Modularity vs. simplicity

3. **How should users discover skills?**
   - Current: Must know skill name
   - Future: Intent matching ("I'm writing a tutorial" → suggest generator skill)
   - GitHub Copilot skill discovery UX unclear

4. **Should validation scripts be part of skills or separate tools?**
   - Option A: Bundle in skills (skills/documentation-reviewer/scripts/)
   - Option B: Separate tools repo (canonical/docs-validation-tools)
   - Tradeoff: Convenience vs. reusability

---

## Next Steps

1. **Review this analysis** with team (Samuel + Arthem)
2. **Get consensus** on Phase 1 approach
3. **Prototype enhanced skill** (merge agent workflow)
4. **Validate** with real documentation PR
5. **Document** the new architecture in README
6. **Update** generate-agent-skills templates to reflect learnings

