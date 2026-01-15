---
name: documentation-reviewer
description: Interactive workflow for reviewing documentation structure, style, and clarity.
---

# Documentation Reviewer Skill

This skill guides the agent through an interactive review process for documentation files. It focuses on **workflows and validation actions** rather than defining the standards themselves (which are provided in the repo's custom instructions).

## What This Skill Does

This skill instructs the agent to act as a **Documentation Reviewer**. It audits content against the Diataxis framework and Canonical's style guide by performing specific checks.

## Review Workflow

When asked to review documentation, follow this step-by-step process:

### 1. Categorization Check
*   **Action**: Identify the intended valid Diataxis type of the document (Tutorial, How-to, Reference, or Explanation).
*   **Validation**:
    *   Does the file location match the type (e.g., `docs/tutorial/`)?
    *   Does the content match the definition? (e.g., "How-to" should be task-oriented, not theoretical).
    *   If the type is ambiguous, ask the user to clarify.

### 2. Structural Audit
Perform the following checks based on the identified category:

*   **For Tutorials**:
    *   [ ] Check for a learning-oriented title (not "Getting Started").
    *   [ ] Verify "What you'll do" and "What you'll need" sections exist.
    *   [ ] Ensure a "Tear down" or cleanup section is present at the end.
    *   [ ] Confirm the flow is a complete, linear journey.
*   **For How-to Guides**:
    *   [ ] Verify the title follows `# How to <task>` format.
    *   [ ] Ensure it addresses a specific real-world problem.
    *   [ ] Check that it is prescriptive (steps) rather than descriptive (theory).
*   **For All Files**:
    *   [ ] Check that content is not mixed (e.g., explanation buried in a valid how-to).
    *   [ ] Check that content is referenced in the appropriate table of contents (e.g., in the `Contents` section of `docs/index.md` or in the relevant `toctree` directive).

### 3. Style & Syntax Scan
Scan the text for these specific violations:
*   **Language**: specific check for British English (should be US English).
*   **Headings**: specific check for Title Case (should be Sentence case) and skipped hierarchy levels.
*   **Code Blocks**: 
    *   Look for prompt markers (`$`, `#`, `%`) in shell blocks (should be removed).
    *   Look for inline comments in code (should be moved to text).
    *   Verify language tags are present (e.g., `bash`, `yaml`).

### 4. Provide Feedback
*   **Do not rewrite** the file unless explicitly asked.
*   **Report Findings**: Group your feedback by "Structure", "Style", and "Clarity".
*   **Explain Why**: For every suggestion, reference the underlying logic (e.g., "Remove prompt markers to allow for easier copy-pasting").

## Example Prompts

*   "Review this PR for documentation standards."
*   "Does this new tutorial follow the correct structure?"
*   "Audit `docs/how-to/backup.md` for style violations."
