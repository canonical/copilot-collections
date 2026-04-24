---
name: diataxis-landing-page-helper
description: Analyzes documentation pages within a Diataxis quadrant to extract themes, cluster functional domains, and structure landing pages. Generates Quadrant Introductions and inserts structured HTML comment metadata (themes, justifications, user journey context) under each section header for human narrative writers. Use when creating or reorganizing Diataxis-aligned landing pages for how-to guides, tutorials, reference, or explanation categories.
---

# SKILL: Information Architecture for Diataxis-Aligned Landing Pages

## Purpose

To analyze all documentation pages within a Diataxis quadrant, identify cross-cutting themes and functional domains, and structure landing pages accordingly. The skill generates only the Quadrant Introduction as visible prose. All section narratives are written by humans; the skill provides structured HTML comment metadata under each section header to inform the human writer with analysis context (themes, justifications, user journey positioning, and ecosystem scope where applicable).

## Core Principles

1.  **Domain-First Organization:** Organize files by their technical domain or functional theme (e.g., Networking, Security, Data Schema). 
2.  **Avoid Silos:** Do not organize by user persona (e.g., "For Beginners") or user journey (e.g., "Getting Started").
3.  **The Rule of Two:** A section header must contain at least two documents. If a theme only has one document, it must be merged into a broader related theme.
4.  **Aesthetic Pragmatism:**
    * If a Diataxis category contains **5 or more files**, use a **Structured** layout with section headers and HTML comment metadata blocks under each header. Section narratives are not generated — they are written by humans using the metadata as guidance.
    * If a Diataxis category contains **fewer than 5 files**, use a **Flat** layout (simple directory with a Quadrant Introduction only). Flat layouts do not receive HTML comment metadata blocks.
5.  **Avoid Meta-Documentation:** The Quadrant Introduction must not describe the documentation itself (e.g., "This section contains guides on..."). Instead, provide context about the technology, the product lifecycle, or the specific use cases the guides address. This principle applies to visible prose only — HTML comment metadata blocks are intentionally meta-guidance for human writers and are exempt.
6.  **US English Standard:** Use American English spelling conventions throughout all generated text (e.g., "behavior," "lifecycle," "organize," "modeling").

---

## Technical Instructions

### Step 1: Content Analysis

Perform a multi-part analysis of all documentation pages under the target Diataxis quadrant. Each landing page should focus on one quadrant:
* **Tutorials:** Learning-oriented.
* **How-to Guides:** Task-oriented.
* **Reference:** Information-oriented.
* **Explanation:** Understanding-oriented.

#### 1a: Page Reading

Read every page that belongs to (or is proposed for) this quadrant. For each page, extract:
* **Topic:** Primary subject matter (e.g., TLS configuration, backup procedures).
* **Scope:** Breadth of the page — single feature, cross-component workflow, architectural overview.
* **Key concepts:** Domain-specific terms, technologies, and product features referenced.
* **Technologies mentioned:** External tools, protocols, platforms, or standards the page depends on or interacts with.

#### 1b: Theme Extraction

Across all pages, identify cross-cutting themes and functional domains:
* Look for clusters of pages that share subject matter, technology stack, or operational context.
* Note which themes appear in multiple pages versus themes unique to a single page.
* Flag any pages that resist clean categorization — these are candidates for fallback groupings (see Step 3).

#### 1c: Juju Ecosystem Assessment (Conditional)

Perform this sub-step **only** when page reading (1a) detects Juju or charm-related content (e.g., references to charms, Juju relations, models, controllers, or the Juju CLI).

For each relevant page, classify its ecosystem scope on a spectrum:
* **Charm-specific:** Concerns internal charm behavior, configuration, or implementation.
* **Cross-charm:** Involves relations or integrations between this charm and other charms.
* **Model-level:** Addresses deployment topology, model configuration, or multi-application orchestration.
* **Controller-level:** Touches on controller management, cloud credentials, or multi-model concerns.
* **Cloud-level:** References substrate-specific concerns (e.g., Kubernetes vs. machine deployments).

Record which pages reference broader Juju ecosystem concepts and at what scope level.

#### 1d: User Journey Mapping

Assess where each page falls in a typical deployment lifecycle:
* Initial setup → Configuration → Integration → Scaling → Maintenance → Troubleshooting

This mapping informs the HTML comment metadata (see Step 4) but does **NOT** drive the landing page organization. Page grouping is always by functional domain (Principle 1), never by user journey stage (Principle 2).

#### 1e: Domain Clustering

Using the themes from 1b, group pages into functional domains:
* Apply the **Rule of Two** (Principle 3) — every domain must contain at least two pages.
* Merge single-page themes into broader related domains where possible.
* Resort to fallback categories (Step 3) only when logical merging fails.

### Step 2: Workflow Selection (Audit vs. Creation)

Determine if a landing page (e.g., `index.md`) already exists for this category.

#### If the page exists (Audit Workflow):

1.  **Respect Existing Taxonomy:** If the current domains are functional and thematic, do not rename them unless they violate the "Rule of Two."
2.  **Identify Content Gaps:** Compare the local file list against the existing links. Integrate any "orphan" files into existing domains or create new ones if the Rule of Two is met.
3.  **The "Naked List" Fix:** If a section header is followed immediately by a list of links with no context, you **must** insert an **HTML comment metadata block** (see Step 4) beneath that header.

#### If the page does not exist (Creation Workflow):

1.  **Check Count:** If there are < 5 files, create a Flat layout. If ≥ 5, create a Structured layout.
2.  **Cluster Domains:** Group files into functional domains based on the analysis from Step 1.
3.  **Apply Fallbacks:** Use the designated fallback category only as a last resort for files that cannot be grouped.
4.  **Insert Metadata:** For Structured layouts, insert an HTML comment metadata block beneath each section header (see Step 4).

### Step 3: Fallback Categories

When the Rule of Two cannot be met through logical merging, use these specific fallback headers:
* **How-to Guides:** "Advanced operations"
* **Tutorials:** "Advanced tutorials"
* **Reference:** "Advanced topics"
* **Explanation:** "Conceptual deep-dives"

HTML comment metadata blocks for fallback sections must include:
* A **Fallback** flag indicating the grouping has a weaker thematic connection than standard domain sections.
* A note that the section narrative **can be framed by the specific guides** in the section, since the weaker thematic connection means the narrative benefits from being grounded in the concrete pages rather than an abstract domain theme.

### Step 4: Output Generation

#### Quadrant Introduction (1-2 sentences)

Establish the quadrant's purpose by connecting its Domain Style (see Content Mapping Reference Table) to the product's functional domain. Ground the description with a few representative examples drawn from the section themes, rather than exhaustively summarizing every section.

* **Constraint:** Describe the category as if it were already fully populated. Do not refer to the specific number of current files or use their titles. Do not use meta-phrases like "These guides cover..."
* **Flat Layout note:** In a Flat layout, the Quadrant Introduction may be slightly more specific about individual outcomes since it is the only descriptive text on the page.
* *Example (Reference):* "Technical specifications and descriptions for the Discourse charm's configuration surfaces, integration interfaces, and runtime behavior within a Juju-managed Kubernetes environment."

#### HTML Comment Metadata Blocks (Structured Layout Only)

For each section header in a Structured layout, insert an HTML comment block immediately below the header. These comments provide analysis context for the human writer who will author the section narrative.

**Format rules:**
* Use structured key-value pairs with short, fragmented prose values (keywords, phrases, comma-separated lists).
* **Do not write complete sentences.** The metadata must remain scannable and must not be directly usable as copy/paste narrative text.
* Use the exact field names shown below.

**Required fields:**
* **Themes:** Comma-separated list of functional themes or domains represented by the pages in this section.
* **Justification:** Short phrase explaining why these pages were grouped — the reasoning behind the structural choice.
* **User journey context:** Deployment lifecycle stage keywords (e.g., "post-deployment, scaling phase," "initial setup, first integration").

**Conditional fields:**
* **Juju ecosystem scope:** Include only when the content analysis (Step 1c) detected Juju/charm-related content. Use scope keywords: "charm-specific," "cross-charm," "model-level," "controller-level," "cloud-level."

**Optional fields:**
* **Strategic notes:** Include when a section contains competing approaches, alternative methods, or mutually exclusive options. Flag the alternatives and their distinguishing criteria so the human writer can craft guidance for the reader.
* **Fallback:** Include only for fallback category sections (see Step 3). Flag that the grouping has a weaker thematic connection. Note that the section narrative can be framed by the specific guides in the section.

**Example (How-to Guides, Structured layout):**

```markdown
## Backup and recovery
<!--
Themes: data persistence, disaster recovery, point-in-time restore
Justification: shared operational concern — protecting stateful data across failure scenarios
User journey context: post-deployment, maintenance phase
Juju ecosystem scope: charm-specific (backup actions), cross-charm (shared database relations)
-->

- [Create a backup](/t/...)
- [Restore from backup](/t/...)
- [Schedule automatic backups](/t/...)
```

**Example (fallback section):**

```markdown
## Advanced operations
<!--
Themes: log rotation, charm debug tooling
Justification: single-page topics without a shared peer — merged into fallback
User journey context: maintenance, troubleshooting
Fallback: weaker thematic connection; narrative can be framed by the specific guides
-->

- [Configure log rotation](/t/...)
- [Debug charm hooks](/t/...)
```

---

## Content Mapping Reference Table

| Diataxis Type | Domain Style | Fallback Category (Last Resort) | Typical Lifecycle Stages |
| :--- | :--- | :--- | :--- |
| **Tutorials** | Educational/Module-based | Advanced tutorials | Initial setup, first deployment |
| **How-to Guides** | Functional/Task-based | Advanced operations | Configuration, integration, maintenance |
| **Reference** | Technical/Machinery-based | Advanced topics | All stages (lookup-driven) |
| **Explanation** | Conceptual/Architectural | Conceptual deep-dives | Pre-deployment planning, scaling decisions |
