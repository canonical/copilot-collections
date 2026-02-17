---
name: documentation-diataxis
description: "Classifies documentation pages by Diataxis content type and flags structural mismatches between intent and form."
---

# Diataxis Classification Review

## Scope

Diataxis classification only: identify whether each page is a tutorial,
how-to guide, explanation, or reference; flag mismatches between
content type and declared category.

## Inputs

- Documentation file(s) under review.
- Diataxis framework principles.

## Actions

1. **Identify intended category**: Determine the declared category
  based on directory location
  (`tutorial/`, `how-to/`, `explanation/`, `reference/`)
  and file metadata (front matter keys such as `category`, `type`,
  `diataxis`, or reST `.. meta::` entries).

2. **Infer actual category**: Analyse the text's structure, tone,
   and progression to determine which quadrant it actually resembles.

3. **Check user need alignment**:

   - **Tutorials**: Is it a learning-oriented lesson?
     Does it build confidence through doing? Is it linear and safe?
   - **How-to guides**: Is it a task-oriented recipe?
     Does it help a competent user solve a specific problem?
     Is it goal-focused?
   - **Reference**: Is it information-oriented?
     Does it describe things accurately and completely?
     Is it structured for lookup?
   - **Explanation**: Is it understanding-oriented?
     Does it clarify concepts, context, and relationships?
     Is it discursive?

4. **Evaluate quality**:

   - **Functional quality**: Is the content accurate, complete,
     consistent, useful, and precise?
   - **Deep quality**: Does the content have good flow?
     Does it anticipate user questions?
     Is the cognitive load appropriate? Is the experience clear?

5. **Document misalignments**: Explicitly identify where the document
   fails to meet the needs of its category
   or where quality breaks down.

## Constraints

- Do not ignore the Diataxis framework.
- Assign each page to exactly one quadrant.

## Output

A Diataxis Compliance Report detailing:

- Declared category.
- Inferred category.
- User need alignment analysis.
- Functional and deep quality findings.
- Misalignments with corrective actions.
