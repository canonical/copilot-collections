---
name: diataxis-landing-page-helper
description: To create or update documentation landing pages that organize content by functional domains, ensuring a professional, balanced aesthetic while adhering to the Diataxis framework.
---

# SKILL: Information Architecture for Diataxis-Aligned Landing Pages

## Purpose

To create or update documentation landing pages that organize content by functional domains, ensuring a professional, balanced aesthetic while adhering to the Diataxis framework.

## Core Principles

1.  **Domain-First Organization:** Organize files by their technical domain or functional theme (e.g., Networking, Security, Data Schema). 
2.  **Avoid Silos:** Do not organize by user persona (e.g., "For Beginners") or user journey (e.g., "Getting Started").
3.  **The Rule of Two:** A section header must contain at least two documents. If a theme only has one document, it must be merged into a broader related theme.
4.  **Aesthetic Pragmatism:** * If a Diataxis category contains **5 or more files**, use a **Structured** layout with section headers and descriptive text.
    * If a Diataxis category contains **fewer than 5 files**, use a **Flat** layout (simple directory).
5.  **Avoid Meta-Documentation:** Do not describe the documentation itself (e.g., "This section contains guides on..."). Instead, provide context about the technology, the product lifecycle, or the specific use cases the guides address.
6.  **US English Standard:** Use American English spelling conventions throughout all generated text (e.g., "behavior," "lifecycle," "organize," "modeling").

---

## Technical Instructions

### Step 1: Diataxis Categorization

Identify which of the four Diataxis quadrants the documents belong to. Each landing page should focus on one quadrant:
* **Tutorials:** Learning-oriented.
* **How-to Guides:** Task-oriented.
* **Reference:** Information-oriented.
* **Explanation:** Understanding-oriented.

### Step 2: Workflow Selection (Audit vs. Creation)

Determine if a landing page (e.g., `index.md`) already exists for this category.

#### If the page exists (Audit Workflow):

1.  **Respect Existing Taxonomy:** If the current domains are functional and thematic, do not rename them unless they violate the "Rule of Two."
2.  **Identify Content Gaps:** Compare the local file list against the existing links. Integrate any "orphan" files into existing domains or create new ones if the Rule of Two is met.
3.  **The "Naked List" Fix:** If a section header is followed immediately by a list of links with no context, you **must** write a **Section Narrative** (see Step 4).

#### If the page does not exist (Creation Workflow):

1.  **Check Count:** If there are < 5 files, create a Flat layout. If ≥ 5, create a Structured layout.
2.  **Cluster Domains:** Group files into functional domains.
3.  **Apply Fallbacks:** Use the designated fallback category only as a last resort for files that cannot be grouped.

### Step 3: Fallback Categories

When the Rule of Two cannot be met through logical merging, use these specific fallback headers:
* **How-to Guides:** "Advanced operations"
* **Tutorials:** "Advanced tutorials"
* **Reference:** "Advanced topics"
* **Explanation:** "Conceptual deep-dives"

### Step 4: Content Generation (Split Responsibility Model)

To ensure the page is both informative and future-proof, follow this distribution of detail:

1.  **Quadrant Introduction (1-2 sentences):** Establish the quadrant's purpose by connecting its Domain Style (see Content Mapping Reference Table) to the product's functional domain. Ground the description with a few representative examples drawn from the section themes, rather than exhaustively summarizing every section.
    * **Constraint:** Describe the category as if it were already fully populated. Do not refer to the specific number of current files or use their titles. Do not use meta-phrases like "These guides cover..."
    * **Flat Layout note:** In a Flat layout without section narratives, the journey summary may be slightly more specific about individual outcomes since the introduction is the only descriptive text on the page.
    * *Example (Reference):* "Technical specifications and descriptions for the Discourse charm's configuration surfaces, integration interfaces, and runtime behavior within a Juju-managed Kubernetes environment."

2.  **Section Narratives (Structured Layout Only - Use-Case Focused):** Write 1-2 sentences of technical context for every domain header.
    * **Focus:** Describe the architectural importance or the specific use case (e.g., "Maintaining system health requires a proactive diagnostic strategy to identify resource bottlenecks before they impact performance").
    * **Optionality:** When a section groups pages that address independent or situational needs (e.g., configuring different optional integrations), the narrative must frame them as available options rather than a mandatory sequence. Use language that acknowledges the user may only need a subset (e.g., "depending on your infrastructure requirements" or "as your deployment requires").
    * **Contextual coherence:** Section narratives should stay grounded in the product context established by the Quadrant Introduction. If the introduction frames the product as a component within a specific platform or ecosystem, narratives should reference that platform where the section's content naturally relates to it, rather than substituting generic technical abstractions (e.g., prefer "Juju relation interfaces" over "service mesh" when documenting a Juju charm).
    * **Prohibited phrases:** "This section includes," "Learn how to," or "Links to."

3.  **Strategic Guidance:** If a section contains multiple competing options (e.g., two different deployment methods), add a sentence advising the user on how to choose between them based on their requirements.

---

## Content Mapping Reference Table

| Diataxis Type | Domain Style | Fallback Category (Last Resort) |
| :--- | :--- | :--- |
| **Tutorials** | Educational/Module-based | Advanced tutorials |
| **How-to Guides** | Functional/Task-based | Advanced operations |
| **Reference** | Technical/Machinery-based | Advanced topics |
| **Explanation** | Conceptual/Architectural | Conceptual deep-dives |
