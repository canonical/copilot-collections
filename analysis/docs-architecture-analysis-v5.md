# Documentation Assets Architecture Analysis

**Version:** 5.0 (Balanced & Concise)  
**Date:** 2026-02-16

---

## Executive Summary

**Problem:** Documentation assets have systemic architectural issues:
1. **Wrong asset types** - Task-based workflow in agent format (persona-based)
2. **Content duplication** - Same rules in instructions, agent, style guide, and skill
3. **Workflow in instructions** - 42 lines of tutorial template (should be automated)
4. **Context pollution risk** - Potential 1,200 lines loaded for simple edits
5. **Unclear boundaries** - Overlapping responsibilities across asset types

**Solution:** Comprehensive refactoring:
- Consolidate agent (441 lines) + style guide (643 lines) → enhanced skill with bundled assets
- Slim instructions from 116 → 90 lines (remove workflows)
- Create generator skill with automation (replace manual templates)
- Establish clear boundaries: instructions = constraints, skills = workflows

**Impact:** 74-92% reduction in context loading, architectural alignment, automation enablement.

---

## Current State

### Asset Inventory (1,454 total lines)

| Asset | Type | Lines | Issues |
|-------|------|-------|--------|
| doc-reviewer.agent.md | Agent | 441 | Wrong asset type (task, not role) |
| doc-style-guide.md | Reference | 643 | Duplicates instruction content |
| documentation-reviewer | Skill | 59 | Lightweight, incomplete |
| documentation.instructions.md | Path Instruction | 116 | Contains workflows + duplicates |
| documentation-rtd.instructions.md | Path Instruction | 94 | Not part of common collections, only PFE, overlaps with base |
| documentation-not-rtd.instructions.md | Path Instruction | 25 | Not part of common collections, only PFE, overlaps with base |
| documentation-release-notes.instructions.md | Path Instruction | 76 | Not part of common collections, only PFE |

**Currently distributed:** 175 lines (instruction + lightweight skill)

**Architectural health:** ⚠️ Multiple systemic issues across all asset types

---

## Core Issues

### 1. Wrong Asset Type (Agent)

**Doc-reviewer agent characteristics:**
- ❌ Job description, not cognitive lens
- ❌ No unique perspective (applies checklist)
- ❌ Task invocation ("review docs") → Should be Skill
- ✅ Requires bundled assets → Skills support this

**Verdict:** Capability (skill), not perspective (agent).

---

### 2. Content Duplication (Systemic)

| Content | Where It Appears | Issue |
|---------|------------------|-------|
| **Diátaxis framework** | Instructions, agent, skill | Defined in 3 places |
| **Style rules** (headings, code blocks) | Instructions (basic), style guide (detailed) | Different detail levels, no clear source of truth |
| **Tutorial structure** | Instructions (42 lines) | Should be in skill with automation |
| **Code block conventions** | Instructions, style guide | Same rule, different wording |

**Example duplication:**

```markdown
# documentation.instructions.md (line 99)
Do not use prompt marks (for example, `$` or `#`) in code examples.

# doc-style-guide.md (lines 459-462)
DO NOT use `$` or `#` prompts in code samples except when using 
the `console` lexer, which makes them non-selectable.
```

**Root cause:** No clear content ownership across asset types.

---

### 3. Instructions Contain Workflows

**Problem:** `documentation.instructions.md` lines 41-83 = 42 lines of tutorial structure.

**Why this is wrong:**
- This is a **generation workflow**, not a constraint
- Should be automated with scaffolding script
- Currently forces manual template following
- Pollutes always-on context with procedural steps

**Better architecture:**
- **Instruction:** "Tutorials are learning-oriented" (10 lines)
- **Skill:** Generate tutorial with automation (150 lines, JIT-loaded)

---

### 4. Context Pollution (Compounding)

**Scenario: Fix typo in docs/how-to/backup.md**

| State | What Loads | Lines |
|-------|------------|-------|
| **Current** | documentation.instructions.md | 116 |
| **If RTD project** | documentation-rtd.instructions.md | 210 |
| **If agent added** | + doc-reviewer.agent.md + doc-style-guide.md | ~1,300 |
| **Proposed** | documentation-base.instructions.md (slimmed) | 90 |

**Analysis:**
- Current instructions already heavy (116 lines for constraints)
- Contains 42 lines of workflows (shouldn't be there)
- Adding agent would compound problem (10x increase)
- Solution requires fixing both instructions AND agent architecture

---

### 5. Unclear Boundaries (All Assets)

**Who owns what?**

| Concern | Currently In | Should Be In |
|---------|--------------|--------------|
| Diátaxis definitions | Instructions, agent, skill | Instructions only (single source) |
| Comprehensive style rules | Style guide (loose file) | Skill asset (bundled) |
| Tutorial structure | Instructions (42 lines) | Skill with automation |
| Review workflow | Agent (441 lines) | Skill (on-demand) |
| Simple style checks | Instructions | Keep in instructions |

**Root cause:** No clear principle for asset type selection.

---

## Proposed Architecture

### Design Principles

1. **Instructions = Constraints** (what rules to follow)
2. **Skills = Workflows** (how to accomplish tasks)
3. **Agents = Perspectives** (cognitive lenses, not jobs)
4. **Single Source of Truth** (no duplication)
5. **Context Economics** (JIT loading preferred)

---

### Proposed Path Instructions (~265 lines total, down from 311)

| File | Lines | Content | Changes |
|------|-------|---------|---------|
| documentation-base.instructions.md | 90 | Core rules, Diátaxis definitions | Remove 42 lines of workflows, deduplicate |
| documentation-rtd.instructions.md | 60 | Sphinx directives, toctree, RTD tools | Keep focused on RTD projects |
| documentation-not-rtd.instructions.md | 25 | vale/lychee tools, numeric Contents list | Keep focused on non-RTD projects |
| documentation-release-notes.instructions.md | 70 | Artifact format, change tracking | Keep focused on release notes |
| documentation-changelog.instructions.md | 20 | Changelog conventions | NEW: Extract from base |

**Key changes:**
- ✅ Remove workflows → skills
- ✅ Deduplicate (reference skill for comprehensive rules)
- ✅ Slim by 15% (311 → 265 lines)

**Distribution strategy:**
- Base: Always in collection (core rules)
- RTD/Not-RTD: Mutually exclusive (projects choose one)
- Release notes: Optional (only for projects using release notes)
- Changelog: Optional (only for projects with docs/changelog.md)

---

### Proposed Skills (Refactoring Scope)

#### 1. documentation-reviewer (Enhanced, ~200 lines)

**Type:** Refactoring (consolidates existing content)

**Purpose:** Comprehensive review workflow

**Structure:**
```
.github/skills/documentation-reviewer/
├── SKILL.md                     # 8-stage workflow (200 lines)
├── assets/
│   └── style-guide.md          # Single source of truth (643 lines)
└── scripts/
    └── run_rtd_checks.sh       # Automated linting
```

**Content sources:**
- 8-stage workflow from `doc-reviewer.agent.md`
- Comprehensive style rules from `doc-style-guide.md`
- Deduplicate with base instructions

**Benefits:**
- ✅ JIT loading (not always-on)
- ✅ Bundles all comprehensive rules
- ✅ Single source of truth for style guide
- ✅ Can add automation scripts

---

#### 2. documentation-generator (~150 lines)

**Type:** Refactoring (extracts existing templates)

**Purpose:** Scaffold new docs with automation

**Structure:**
```
.github/skills/documentation-generator/
├── SKILL.md                     # Generation workflow
├── scripts/
│   ├── scaffold_tutorial.py    # Automates 8-section creation
│   ├── scaffold_howto.py
│   ├── scaffold_reference.py
│   └── scaffold_explanation.py
└── references/
    ├── tutorial-template.md     # Extracted from instructions
    ├── howto-template.md
    ├── reference-template.md
    └── explanation-template.md
```

**Benefits:**
- ✅ Removes 42 lines of workflow from instructions
- ✅ Automates structure creation (was manual)
- ✅ Enforces consistency
- ✅ JIT-loaded only when generating

---

### Future Enhancement (Not Part of Refactoring)

#### documentation-publisher (~80 lines)

**Type:** New functionality (not addressing current issues)

**Purpose:** Prepare docs for publication

**Structure:**
```
.github/skills/documentation-publisher/
├── SKILL.md                     # Publication workflow
└── scripts/
    ├── validate_rtd_build.sh
    ├── check_navigation.py
    └── compile_release_notes.sh
```

**Note:** This skill codifies publication workflows but is **not required** to fix the architectural issues identified in this analysis. It's a future enhancement that can be built after the refactoring is complete.

---

### Custom Agents

**Recommendation:** ❌ None needed for documentation work.

**Rationale:** Documentation review is a task (capability), not a role (perspective). Skills provide better architecture for task-based work.

---

## Context Economics

### Impact Across Scenarios

| Scenario | Current | With Agent Added | Proposed | vs. Current | vs. Agent |
|----------|---------|------------------|----------|-------------|-----------|
| **Typo fix** | 116 | 1,200 | 90 | -22% | **-92%** |
| **Tutorial gen** | 116 (manual) | 557 (manual) | 240 (auto) | +107%* | **-57% + automation** |
| **PR review** | 175 (incomplete) | 1,200 (comprehensive) | 290 (comprehensive, JIT) | +66%* | **-76%** |

*\*Proposed is heavier for complex tasks vs. current, but provides better quality + automation. Still much lighter than agent approach.*

**Key insights:**
1. **Current instructions already too heavy** (116 lines with workflows)
2. **Adding agent compounds the problem** (10x increase)
3. **Proposed fixes both issues** (slim instructions + JIT skills)

---

## Migration Path (Refactoring Only)

### Phase 1: Consolidate Agent → Skill (Immediate)

**Fixes issues:** #1 (wrong asset type), #2 (duplication), #4 (context pollution)

**Actions:**
1. Create `assets/skills/documentation-reviewer/assets/`
2. Move style guide → skill asset
3. Merge 8-stage workflow from agent → `SKILL.md`
4. Deduplicate with instructions (remove overlaps)
5. Update collection to distribute enhanced skill

**Outcome:** Comprehensive review capability as skill, style guide bundled.

---

### Phase 2: Refactor Instructions (Next)

**Fixes issues:** #3 (workflows in instructions), #2 (duplication), #5 (unclear boundaries)

**Actions:**
1. Remove lines 41-83 (tutorial structure → generator skill)
2. Deduplicate style rules (reference skill for comprehensive guide)
3. Rename → `documentation-base.instructions.md`
4. Slim from 116 → 90 lines

**Outcome:** Instructions are pure constraints, 15% slimmer.

---

### Phase 3: Create Generator Skill (Next)

**Fixes issues:** #3 (workflows in instructions), #5 (unclear boundaries)

**Actions:**
1. Use `generate-agent-skills` scaffolding
2. Extract templates from instructions
3. Write scaffolding scripts (Python)

**Outcome:** Automated documentation generation.

---

**Refactoring complete at this point.** All architectural issues addressed.

---

## Validation Criteria

**Success metrics:**
- [ ] No content duplication across assets
- [ ] Instructions contain only constraints (<100 lines each)
- [ ] Skills contain only workflows (JIT-loaded)
- [ ] Typo fix loads <100 lines context
- [ ] PR review loads <300 lines during active review
- [ ] Generator skill automates structure creation
- [ ] Clear answer: "Review docs" → Invoke skill
- [ ] Style guide has single source of truth (skill asset)

---

## Recommendations

### Immediate (Fixes 60% of issues)
1. **Enhance documentation-reviewer skill**
   - Merge agent workflow
   - Bundle style guide as asset
   - Deduplicate with instructions
2. **Update collection** to distribute enhanced skill (not agent)

### Short-term (Fixes 100% of issues)
3. **Refactor instructions**
   - Remove workflows
   - Deduplicate style rules
   - Slim to pure constraints
4. **Create generator skill** with automation
5. **Document architecture** in README
6. **Establish asset selection guidelines**

### Future Enhancements (Optional)
7. **Create publisher skill** (new functionality)
8. **Add automated validation** to existing skills
9. **Integrate skills with CI/CD**

---

## Conclusion

**Current state:** Systemic architectural issues across all documentation assets:
- Wrong asset types (agent for task-based work)
- Content duplication (instructions, agent, style guide, skill)
- Workflows in instructions (should be automated skills)
- Context pollution risk (compounding issues)
- Unclear boundaries (no ownership principles)

**Proposed state:** Clean architecture with clear boundaries:
- Instructions = constraints only (~240 lines total)
- Skills = workflows + automation (JIT-loaded)
- Single sources of truth (no duplication)
- 74-92% less context pollution
- Automation enabled

**North Star Principles:**
- **Instructions define WHAT** (rules to follow)
- **Skills define HOW** (workflows to execute)
- **Agents are for PERSPECTIVES** (cognitive lenses)
- **Single Source of Truth** (no duplication)
- **Context Economics** (JIT loading preferred)

This is not just about fixing the agent—it's about establishing correct architecture for all documentation assets.

