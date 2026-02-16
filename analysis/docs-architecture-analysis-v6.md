# Documentation Assets Architecture Analysis

**Version:** 6.0 (Refined with Two-Tier System)  
**Date:** 2026-02-16

---

## Executive Summary

**Problem:** Documentation assets have systemic architectural issues:
1. **Wrong asset types** - Task-based workflow in agent format
2. **Content duplication** - Same rules across multiple assets
3. **Workflows in instructions** - 42 lines of tutorial template
4. **Context pollution risk** - Up to 1,200 lines for simple edits
5. **Unclear boundaries** - Overlapping responsibilities

**Solution:** Two-tier architecture with smart detection:
- **Tier 1 (Instructions):** Practical editing guidance (auto-load, 90 lines)
- **Tier 2 (Skill):** Comprehensive review with auto-detection (on-demand, 200+ lines)
- Consolidate agent (441 lines) + style guide (643 lines) → enhanced skill
- Skill detects RTD vs. non-RTD (eliminates instruction duplication)

**Impact:** 
- 74-92% reduction in context loading
- Single instruction file (no RTD/non-RTD split needed)
- Instructions sufficient for 80% of edits
- Skill provides 20% deep-dive review

---

## Current State

### Asset Inventory (1,454 total lines)

| Asset | Type | Lines | Issues |
|-------|------|-------|--------|
| doc-reviewer.agent.md | Agent | 441 | Wrong asset type (task, not role) |
| doc-style-guide.md | Reference | 643 | Duplicates instruction content |
| documentation-reviewer | Skill | 59 | Lightweight, incomplete |
| documentation.instructions.md | Path Instruction | 116 | Contains workflows + duplicates |
| documentation-rtd.instructions.md | Path Instruction | 94 | RTD-specific, overlaps with base |
| documentation-not-rtd.instructions.md | Path Instruction | 25 | Non-RTD specific, overlaps with base |
| documentation-release-notes.instructions.md | Path Instruction | 76 | Release notes specific |

**Currently distributed:** 175 lines (instruction + lightweight skill)

---

## Core Issues

### 1. Wrong Asset Type (Agent)
- ❌ Job description, not cognitive lens
- ❌ Task invocation → Should be Skill

### 2. Content Duplication (Systemic)
- Same rules in instructions, agent, style guide
- No single source of truth

### 3. Instructions Contain Workflows
- 42 lines of tutorial structure (should be automated)

### 4. Context Pollution (Compounding)
- Current: 116 lines for simple edits
- With agent: 1,200 lines

### 5. RTD/Non-RTD Duplication
- Two instruction files for framework detection
- Deduplicate Collection to ship both variants
- Users must choose correct one

---

## Proposed Architecture: Two-Tier System

### Design Principles

1. **Instructions = Practical Editing Guidance** (always-on, lightweight)
2. **Skills = Comprehensive Workflows** (on-demand, heavyweight)
3. **Skills Handle Complexity** (auto-detection, not user choice)
4. **Single Source of Truth** (no duplication)

---

### Tier 1: Path Instructions (Always-On)

**Purpose:** Everyday editing guidance  
**Target:** 80% of use cases (typos, small edits, suggestions)  
**Loading:** Auto-load when opening `docs/**/*`

#### Proposed: Single Universal Instruction File

**documentation.instructions.md** (~90 lines)

```markdown
---
description: 'Universal documentation editing guidance'
applyTo: 'docs/**/*'
---

# Documentation Instructions

## Core Style Rules

- **Spelling**: Use US English
- **Headings**: Sentence case, no punctuation, no skipped levels
- **Code blocks**: No prompt markers (`$`, `#`)
- **Lists**: Numbered only when order matters
- **Cross-references**: Prefer `:ref:` over `:doc:` (or `{ref}` over `{doc}`)

## Diátaxis Framework

Files must fit one category:
- **Tutorial**: Learning-oriented, end-to-end journey
- **How-to**: Task-oriented, solves specific problem
- **Reference**: Information-oriented, describes accurately
- **Explanation**: Understanding-oriented, clarifies concepts

## Framework-Specific Guidance

Your project uses [RTD/non-RTD - detected automatically by skill].

**For RTD projects:**
- Use Sphinx directives
- Add pages to toctree
- Configure redirects in conf.py

**For non-RTD projects:**
- Use vale + lychee for validation
- Update numeric Contents list in index.md
- Follow simpler Markdown conventions

## Comprehensive Review

For detailed style guidance, Diátaxis quality assessment, or pre-merge 
review, invoke the `documentation-reviewer` skill:

\`\`\`
@documentation-reviewer check this PR
\`\`\`
```

**Key changes:**
- ✅ Single file (no RTD/non-RTD split)
- ✅ Brief framework hints (detailed rules in skill)
- ✅ 90 lines (down from 116)
- ✅ References skill for comprehensive review

**Why this works:**
- Users get basic guidance for everyday edits
- No choice paralysis (which instruction file?)
- Skill handles framework detection automatically

---

### Tier 2: Enhanced Skill (On-Demand)

**Purpose:** Comprehensive review with auto-detection  
**Target:** 20% of use cases (PR reviews, validation, deep analysis)  
**Loading:** JIT when explicitly invoked

#### documentation-reviewer (Enhanced)

**Structure:**
```
.github/skills/documentation-reviewer/
├── SKILL.md                          # Workflow with detection logic (220 lines)
│   ├── Stage 0: Project Detection
│   │   └── Auto-detect RTD vs. non-RTD
│   │       • Check for docs/conf.py (RTD)
│   │       • Check for Makefile targets (RTD)
│   │       • Otherwise: non-RTD
│   ├── Stage 1: Setup & Context Gathering
│   │   └── Run appropriate validation tools
│   │       • RTD: make spelling linkcheck woke lint-md
│   │       • Non-RTD: vale + lychee
│   ├── Stage 2: Diátaxis Compliance Review
│   ├── Stage 3: Structural & Metadata Review
│   │   └── Framework-specific checks
│   │       • RTD: toctree, redirects, anchors
│   │       • Non-RTD: Contents list, frontmatter
│   ├── Stage 4: Content & Completeness
│   ├── Stage 5: Code Backing Verification
│   ├── Stage 6: Style & Formatting
│   │   └── Load appropriate style guide
│   ├── Stage 7: Integration & Prioritization
│   └── Stage 8: Final Output Generation
│
├── assets/
│   ├── style-guide-base.md          # Universal rules (400 lines)
│   ├── style-guide-rtd.md           # RTD-specific (150 lines)
│   └── style-guide-non-rtd.md       # Non-RTD specific (93 lines)
│
└── scripts/
    ├── detect_framework.sh           # RTD vs. non-RTD detection
    ├── run_rtd_checks.sh            # Sphinx validation
    └── run_non_rtd_checks.sh        # vale + lychee validation
```

**Key improvements:**
- ✅ **Auto-detection** (Stage 0): No user input needed
- ✅ **Adaptive workflow**: Chooses RTD or non-RTD path
- ✅ **Bundled style guides**: Framework-specific rules as assets
- ✅ **Consolidates all comprehensive rules**: Single source of truth

**Content sources:**
- 8-stage workflow from `doc-reviewer.agent.md`
- Style rules from `doc-style-guide.md`
- RTD-specific rules from `documentation-rtd.instructions.md`
- Non-RTD rules from `documentation-not-rtd.instructions.md`

---

### Invocation Patterns

| User Action | What Loads | What Happens |
|-------------|------------|--------------|
| **Opens `docs/tutorial.md`** | Tier 1: Instruction (90 lines) | ✅ Basic guidance for editing |
| **"Fix this typo"** | Tier 1: Instruction | ✅ Simple style rules applied |
| **"Update this heading"** | Tier 1: Instruction | ✅ Sentence case rule available |
| **"Is this RTD syntax correct?"** | Tier 1: Instruction | ✅ Brief RTD hints available |
| **"Review this PR's docs"** | Tier 1 + Tier 2 (JIT) | ✅ Skill auto-detects framework, runs comprehensive review |
| **"@documentation-reviewer check Diátaxis"** | Tier 2: Skill | ✅ Deep quality analysis with framework detection |

---

## Collection Distribution Strategy

### Current Problem

```yaml
# Consumer repo must choose:
common-documentation:           # For non-RTD projects
common-documentation-rtd:       # For RTD projects
```

**Issues:**
- User must know their project type
- Collection duplication
- Error-prone

### Proposed Solution

```yaml
# Single collection for all projects:
common-documentation:
  items:
    - src: assets/instructions/documentation.instructions.md
      dest: .github/instructions/documentation.instructions.md
    - src: assets/skills/documentation-reviewer
      dest: .github/skills/documentation-reviewer/
    - src: assets/instructions/documentation/documentation-release-notes.instructions.md
      dest: .github/instructions/documentation-release-notes.instructions.md
      # Optional: only if project uses release notes
```

**Benefits:**
- ✅ Single collection (no RTD/non-RTD variants)
- ✅ Skill handles framework detection
- ✅ No user choice needed
- ✅ Simpler distribution

---

## Additional Proposed Skills

### documentation-generator (~150 lines)

**Type:** Refactoring (extracts existing templates)

**Purpose:** Scaffold new docs with automation

**Structure:**
```
.github/skills/documentation-generator/
├── SKILL.md                          # Generation workflow
├── scripts/
│   ├── scaffold_tutorial.py
│   ├── scaffold_howto.py
│   ├── scaffold_reference.py
│   └── scaffold_explanation.py
└── references/
    ├── tutorial-template.md          # Extracted from instructions
    ├── howto-template.md
    ├── reference-template.md
    └── explanation-template.md
```

**Benefits:**
- Removes 42 lines of workflow from instructions
- Automates structure creation
- Enforces consistency

---

## Context Economics

### Impact Across Scenarios

| Scenario | Current | Proposed | vs. Current |
|----------|---------|----------|-------------|
| **Typo fix** | 116 | 90 | **-22%** |
| **Tutorial gen** | 116 (manual) | 90 + 150 (auto, JIT) | +107% but automation |
| **PR review** | 175 (incomplete) | 90 + 220 (comprehensive, JIT) | +77% but comprehensive |

**Key insights:**
- Simple edits: Lighter (90 vs 116 lines)
- Complex tasks: Heavier when invoked, but comprehensive + automated
- Always-on context stays minimal (90 lines)
- Skill loaded only when needed

---

## Migration Path (Refactoring Only)

### Phase 1: Consolidate Agent → Skill (Immediate)

**Fixes issues:** #1 (wrong asset type), #2 (duplication), #4 (context pollution), #5 (RTD/non-RTD split)

**Actions:**
1. Create enhanced skill structure with detection logic
2. Merge 8-stage workflow from agent → `SKILL.md`
3. Add Stage 0: Project detection (RTD vs. non-RTD)
4. Split style guide into base + RTD + non-RTD assets
5. Add detection + validation scripts
6. Update collection to distribute single universal instruction + enhanced skill

**Outcome:** 
- Single instruction file (no RTD/non-RTD split)
- Skill auto-detects framework
- Comprehensive review as on-demand capability

---

### Phase 2: Refactor Instructions (Next)

**Fixes issues:** #3 (workflows in instructions), #2 (duplication)

**Actions:**
1. Remove lines 41-83 (tutorial structure → generator skill)
2. Consolidate RTD/non-RTD hints into single file
3. Slim from 116 → 90 lines
4. Add reference to skill for comprehensive guidance

**Outcome:** Single universal instruction file, 22% slimmer.

---

### Phase 3: Create Generator Skill (Next)

**Fixes issues:** #3 (workflows in instructions)

**Actions:**
1. Use `generate-agent-skills` scaffolding
2. Extract templates from instructions
3. Write scaffolding scripts (Python)

**Outcome:** Automated documentation generation.

**Refactoring complete at this point.**

---

## Validation Criteria

**Success metrics:**
- [ ] Single universal instruction file (<100 lines)
- [ ] No RTD/non-RTD instruction duplication
- [ ] Skill auto-detects project framework
- [ ] Skill adapts workflow based on detection
- [ ] Typo fix loads <100 lines context
- [ ] PR review loads <350 lines during active review
- [ ] Instructions sufficient for everyday edits
- [ ] Clear invocation: "Review docs" → Skill with detection

---

## Recommendations

### Immediate (Fixes 70% of issues)
1. **Enhance documentation-reviewer skill**
   - Add Stage 0: Auto-detection (RTD vs. non-RTD)
   - Merge agent workflow
   - Bundle framework-specific style guides as assets
   - Add detection + validation scripts
2. **Consolidate instructions** into single universal file
3. **Update collection** to distribute single instruction + enhanced skill

### Short-term (Fixes 100% of issues)
4. **Refactor universal instruction**
   - Remove workflows (42 lines)
   - Add brief framework hints
   - Reference skill for comprehensive review
5. **Create generator skill** with automation
6. **Document architecture** in README

### Future Enhancements (Optional)
7. **CI integration** (auto-invoke skill for PR docs changes)
8. **Skill chaining** (generator → reviewer workflow)
9. **Additional validators** (accessibility, readability scores)

---

## Technical Design: Auto-Detection

### Detection Logic (Stage 0 in Skill)

```python
# scripts/detect_framework.py
def detect_documentation_framework(docs_dir: Path) -> str:
    """
    Detect whether project uses RTD (Sphinx) or simple Markdown.
    
    Returns: "rtd" or "non-rtd"
    """
    # Check 1: conf.py exists (definitive RTD)
    if (docs_dir / "conf.py").exists():
        return "rtd"
    
    # Check 2: Makefile with sphinx-build (strong RTD signal)
    makefile = docs_dir / "Makefile"
    if makefile.exists():
        content = makefile.read_text()
        if "sphinx-build" in content:
            return "rtd"
    
    # Check 3: _build/ or _static/ directories (Sphinx artifacts)
    if (docs_dir / "_build").exists() or (docs_dir / "_static").exists():
        return "rtd"
    
    # Check 4: .rst files (Sphinx typical, but not definitive)
    rst_files = list(docs_dir.rglob("*.rst"))
    md_files = list(docs_dir.rglob("*.md"))
    
    if rst_files and not md_files:
        return "rtd"  # Pure reST likely Sphinx
    
    # Default: non-RTD (Markdown-based)
    return "non-rtd"
```

### Adaptive Workflow (SKILL.md)

```markdown
## Stage 0: Project Detection

**Action**: Detect documentation framework

\`\`\`bash
FRAMEWORK=$(python3 scripts/detect_framework.py docs/)
echo "Detected framework: $FRAMEWORK"
\`\`\`

**Outcome**: Sets workflow path for subsequent stages.

---

## Stage 1: Setup & Context Gathering

**Adaptive Actions**:

**If RTD detected:**
\`\`\`bash
cd docs
make clean
make html
make spelling linkcheck woke lint-md
\`\`\`

**If non-RTD detected:**
\`\`\`bash
vale docs/
lychee docs/
\`\`\`

**Outcome**: Framework-appropriate validation completed.
```

---

## Architectural Decision: Instructions vs. Skill

### What Goes Where?

| Concern | Instruction | Skill | Rationale |
|---------|-------------|-------|-----------|
| **Core style rules** (US English, sentence case) | ✅ | | Needed for everyday edits |
| **Brief framework hints** (RTD uses directives) | ✅ | | Quick reference while editing |
| **Diátaxis definitions** | ✅ | | Categorization guidance |
| **Framework detection** | | ✅ | Complex logic, not editing constraint |
| **Detailed style rules** (643 lines) | | ✅ | Too heavy for always-on |
| **Validation workflows** (make spelling) | | ✅ | Task execution, not constraint |
| **Quality assessment** (flow, cognitive fit) | | ✅ | Deep analysis, not editing help |
| **Code backing verification** | | ✅ | Complex 3-substage process |

**Principle:** If it's needed **while typing**, it's an instruction. If it's needed **during review**, it's a skill.

---

## Conclusion

**Current state:** Systemic issues across all documentation assets with RTD/non-RTD duplication adding collection complexity.

**Proposed state:** Clean two-tier architecture:
- **Tier 1 (Instructions):** Single universal file (90 lines) for everyday editing
- **Tier 2 (Skill):** Comprehensive review with auto-detection (on-demand)

**Impact:**
- ✅ 22% slimmer instructions (116 → 90 lines)
- ✅ Single collection (no RTD/non-RTD split)
- ✅ Auto-detection (no user choice needed)
- ✅ Instructions sufficient for 80% of edits
- ✅ Skill provides 20% comprehensive deep-dive

**North Star Principles:**
- **Instructions for editing** (lightweight, always-on)
- **Skills for workflows** (comprehensive, on-demand)
- **Skills handle complexity** (detection, not user choice)
- **Single source of truth** (no duplication)

This architecture solves not just the agent problem, but establishes correct patterns for all documentation assets while simplifying collection distribution.

