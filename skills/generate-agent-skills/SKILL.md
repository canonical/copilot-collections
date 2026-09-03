---
name: generate-agent-skills
description: "Creates and updates SKILL.md files with YAML frontmatter, workflow steps, and bundle resources. Scaffolds directories via scaffold_skill.py and validates via validate_skill.py. Use when creating a new agent skill, writing a skill.md, updating skill definitions, or generating skill templates."
compatibility: python3
allowed-tools: python3 ls grep cat mkdir
metadata:
  author: canonical/platform-engineering
  version: "1.0.0"
---

# Agent Skill Architect Workflow

Create high-quality Agent Skills following a 6-step process: understand → plan → scaffold → write → validate → test.

**Mandatory constraints:**
1. Run `scripts/scaffold_skill.py` in Step 3 — manual file creation is prohibited.
2. Use the generated templates from `references/` as your foundation.
3. Run `scripts/validate_skill.py` in Step 5 before finalizing.
4. Follow all 6 steps in order.

---

## Step 1: Understanding the Skill

**Before scaffolding**, clearly understand how the skill will be used through concrete examples.

### For New Skills:
Ask the user clarifying questions to understand:
- What functionality should the skill support?
- What are example queries that should trigger this skill?
- What outputs or actions should result?
- Are there existing workflows or tools to integrate?

**Example questions:**
- "Can you give some examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"
- "What existing scripts or documentation should be included?"

### For Existing Skills:
If working with an existing skill, analyze:
- Current SKILL.md structure and content
- Existing scripts, references, and assets
- What's working well vs. what needs improvement

**Conclude this step when:** You have a clear sense of the skill's functionality and triggering scenarios.

---

## Step 2: Planning Reusable Contents

Analyze examples from Step 1 to identify reusable resources. For each, decide: analysis tasks → `references/` (checklists, patterns, domain knowledge); computation tasks → `scripts/` (math, APIs, validation); output artifacts → `assets/` (templates, images, seed data).

**Real example:** A repository-analysis task was initially planned as an `analyze_repo.py` script, then corrected to an `analysis_checklist.md` reference — repository analysis is an LLM strength (reading, pattern detection, synthesis), not deterministic computation. When in doubt, prefer a checklist over a script for analysis work. See `references/BEST_PRACTICES.md` §6 for the full decision flowchart.

**Output:** A list of specific files to create with correct categorization.

---

## Step 3: Skill Scaffolding

Run the scaffolding script (use `--simple` for SKILL.md only):

```bash
python3 scripts/scaffold_skill.py --name <skill-name>
```

Validates naming (`^[a-z0-9][a-z0-9-]*[a-z0-9]$`), creates the directory under `.github/skills/`, and generates SKILL.md with placeholders. Verify with `ls -la .github/skills/<skill-name>/` before proceeding.

**Stop conditions:**
- If `SKILL.md` does NOT exist after running the script → do NOT proceed; the scaffolding failed.
- If you created files manually instead of running the script → delete them and re-run the script.
- If the script reported errors → fix them before continuing to Step 4.

---

## Step 4: Content Generation

### 4.1: Implement Reusable Resources

Replace placeholder files from scaffolding with actual implementations:
- **scripts/**: Replace `example.py` with real scripts. Test each: `python3 scripts/<name>.py`
- **references/**: Replace `example_reference.md` with actual docs. Keep SKILL.md lean — move details here.
- **assets/**: Add template files, images, seed data. Delete unused placeholders.

### 4.2: Write SKILL.md Content

**Frontmatter (YAML):**
- `name`: Must match directory name exactly.
- `description`: High-entropy, keyword-rich, 3rd person. Include a "Use when..." clause with trigger scenarios and concrete capabilities.
  - Example: `"Processes PDF documents for form filling, text extraction, and merging. Use when working with PDF files or when user requests document manipulation tasks."`

**Body (Markdown):**
- Use imperative form ("Run the script", not "You should run").
- Reference scripts/references explicitly by path.
- Choose a structure pattern: workflow-based, task-based, reference/guidelines, or capabilities-based (see `references/workflows.md`).
- Consult `references/BEST_PRACTICES.md` for the Freedom Scale, `references/output-patterns.md` for output formatting.

Delete the "Structuring This Skill" guidance section when done.

### 4.3: Design Patterns

**For multi-step processes:** See `references/workflows.md`
- Sequential workflows (step 1 → step 2 → step 3)
- Conditional workflows (if/then branching)
- Iterative workflows (refinement loops)

**For consistent outputs:** See `references/output-patterns.md`
- Strict templates (non-negotiable formats)
- Flexible guidance (adaptable structure)
- Examples-based (show don't tell)
- Validation checklists (quality requirements)

---

## Step 5: Validation

Run the validation script to ensure specification compliance:

```bash
python3 scripts/validate_skill.py --path .github/skills/<skill-name>
```

Checks: directory naming, SKILL.md exists, required frontmatter fields (`name`, `description`), name matches directory. Warnings about missing `references/` or `scripts/` are advisory.

Fix critical errors before proceeding. Then confirm:
- [ ] Ran `scripts/scaffold_skill.py` (did not create files manually)
- [ ] Ran `scripts/validate_skill.py` with no critical errors
- [ ] Frontmatter `description` includes a "Use when..." clause
- [ ] No placeholder files (`example.py`, `example_reference.md`) remain

If you did not run the scaffolding script or manually created files, STOP and re-do from Step 3.

---

## Step 6: Testing and Iteration

Test the skill with real examples from Step 1, then iterate:

1. **Trigger testing**: Does the skill activate on expected queries? If not, add keywords to the description.
2. **Execution testing**: Do scripts run without errors? Is output quality acceptable?
3. **Context efficiency**: If SKILL.md feels bloated, move content to `references/`.
4. **Re-validate** after each round of changes with `scripts/validate_skill.py`.

## Reference Index

- **Specification** (naming, structure): `references/SPECIFICATION.md`
- **Best practices** (context economy, freedom scale): `references/BEST_PRACTICES.md`
- **Templates** (frontmatter, structure patterns): `references/TEMPLATES.md`
- **Workflows** (sequential, conditional, iterative): `references/workflows.md`
- **Output patterns** (templates, validation checklists): `references/output-patterns.md`

**Do not hallucinate answers.** Always consult the authoritative sources.
