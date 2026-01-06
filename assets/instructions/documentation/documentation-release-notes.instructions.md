---
description: 'Core guidelines for automated release notes process.'
applyTo: 'docs/release-notes/artifacts/**'
---

# Release notes instructions for GitHub Copilot

## Purpose

This file provides general guidance for the automated release notes process.

The release notes process is a semi-automated system that ensures every significant change is tracked and eventually compiled into a standardized release document.

## Overview of the release notes workflow

1. The workflow is triggered when a new release artifact is added to the repository’s main branch.
2. Both the repository and the `release-notes-automation` are checked out. Python and other required
   dependencies are installed and configured.
3. The Python script runs over the prepared materials and artifacts, generating a Markdown file for the release notes.
4. A pull request is opened into the repository that adds the Markdown file into the ``docs/release-notes`` directory.

For a contributor, the workflow is divided into three main stages: change tracking, release definition, and automated generation.

### Change Tracking (The "Artifact" Phase)

When a developer contributes a change via a pull request, they are expected to include a **change artifact**.

* **Artifact Template**: A YAML file created from `docs/release-notes/template/_change-artifact-template.yaml`. It captures the change title, author, type (e.g., bugfix, breaking), description, and relevant PR or issue links.
* **PR Compliance**: The `Check for release notes artifact` workflow runs on every pull request. It uses the `canonical/release-notes-automation` reusable workflow to verify that the required artifact has been added to the `docs/release-notes/artifacts` directory.

### Release Definition

When a set of changes is ready to be released, a maintainer defines the release parameters.

* **Release Artifact**: A YAML file is created in `docs/release-notes/releases/` based on the `_release-artifact-template.yaml`.
* **Content**: This file lists the specific change artifacts to include and specifies the workload version and the range of charm revisions covered by the release.

### Automated Generation

The final Markdown documentation is generated automatically when the release definition is pushed to the main branch.

* **Automation Trigger**: The `Create release notes` workflow triggers on pushes to `main` that modify files in `docs/release-notes/releases/*`.
* **Assembly**: The workflow gathers data from several sources:
* **Common Metadata**: Basic info like the charm name and release track from `docs/release-notes/common.yaml`.
* **Templates**: A Jinja2 template (`release-template.md.j2`) provides the structure for the final Markdown file.
* **Output**: The resulting Markdown file is generated in the `docs/release-notes/` directory.

## Change artifacts

The change artifact filename should be formatted like `CYCLE_SLUG.yaml`, where `CYCLE` represents the cycle in which the change occurred (e.g. `2604`), and `SLUG` represents a unique identifier that briefly summarizes the change. For example, a change artifact summarizing a new feature in the `2604` cycle should be named `2604_new_feature.yaml`.

The `changes` key contains the following values:

* `title`: This value is typically be used to define headers for the change. For bug fixes, this value is be used as the description of the entry. 
* `author`: GitHub profile name of the person creating the change.
* `type`: Scope of the change. Accepted values (that the tool will recognize) are major, minor, bugfix, deprecated, breaking.
* `description`: This value is used to define the context and provide more information about the change. It is used for all changes except for type: bugfix.
* `urls`: Relevant URLs for the change. `urls.pr` is an array containing one or more links to the associated PR(s), `urls.related_doc` is an optional link to relevant documentation, and `urls.related_issue` is an optional link to a relevant GitHub issue.
* `visibility`: This value determines whether the change is public or internal. Accepted values (that the tool will recognize) are `public` (default), `internal`, and `hidden`.
* `highlight`: This boolean determines whether the change is mentioned in the Introduction of the release notes.

Feature development split over multiple PRs should be described in a single change artifact, with links to all associated PRs added into the artifact under the key `urls.pr`.

### Style considerations

* `title`: For features, keep the titles short and concise. Use past tense in the title for all artifacts. Do not use punctuation.
* `author`: Only use the GitHub profile name (no emails, no `@`).
* `type`: To determine whether the type is `major` or `minor`, ask yourself whether the change will be immediately seen or felt by users (meaning it’s more likely to be a `major` change), or if the change is less likely to affect the user experience in a meaningful way (meaning it’s more likely to be a `minor` change).
* `description`: Use past tense to provide context and information. The more information you provide in the description, the less context you’ll need to provide when the release notes are being prepared for publication. Describe the change in terms of how it will impact users and their experience with the product.
* `urls.pr`: For a change artifact containing multiple URLs to pull requests, the `urls.pr` key should be formatted as an array containing all the links.
* `urls.related_doc`: Only use this key for publicly visible documentation. If documentation was updated in the pull request, use this key to link to that page or file.

Set `highlight` to true for the following reasons:
* If the `type` is deprecated, there’s a good chance that the change is worth highlighting.
* If the `type` is `major` or `bugfix` and has a significant impact on the user experience, then the change is probably worth highlighting.

