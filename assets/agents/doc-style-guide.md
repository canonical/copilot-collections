```{eval-rst}
:orphan:

.. meta::
   :description: Documentation style guide covering file naming,
                 structure, semantic line breaks, reStructuredText and Markdown
                 conventions, terminology, and project-specific patterns.
```

<!--
  ~ Copyright 2026 Canonical Ltd.
  ~ See LICENSE file for licensing details.
-->

# Documentation style guide

This style guide documents the established conventions used in the project documentation. It captures actual patterns observed across the documentation set and serves as a reference for maintaining consistency in new contributions.

This guide is subordinate to your organization's documentation standards but records project-specific decisions and patterns that extend or clarify those standards.

---

## File naming and organization

**Directory structure**

The documentation follows the [Diátaxis](https://diataxis.fr/) framework with four main sections:

```
docs/
├── tutorial/          # Step-by-step learning paths
├── how-to/            # Task-oriented guides
├── explanation/       # Conceptual information
└── reference/         # Technical specifications
```

**File naming convention**

All filenames use lowercase letters and dashes for word separation.

Examples:

- Good: `part-1-get-started.rst`
- Good: `connect-editor.rst`
- Good: `network-interface.rst`
- Good: `container-vs-dockerfile.rst`
- Avoid: `ConnectEditor.rst` (uppercase)
- Avoid: `network_interface.rst` (underscore)

Tutorial files use a sequential numbering pattern:

```
part-1-get-started.rst
part-2-work-with-features.rst
part-3-advanced-concepts.rst
part-4-production-deployment.rst
```

How-to files: Use verb-first naming pattern:

```
add-configuration.rst
connect-editor.rst
forward-ports.rst
debug-issues.rst
resolve-conflicts.rst
```

Explanation files use noun-based naming:

```
concepts.rst
interface-concepts.rst
best-practices.rst
runtime-behavior.rst
```

Reference files match command structure:

```
command-launch.rst
command-connect.rst
build-tool.md
```

Filenames and directory names in the documentation repo should be in lowercase,
with dashes instead of spaces; the directory tree must be built in a way that
provides for readable, meaningful URLs: `/docs/howto/change-tyres`.

---

## Page structure and metadata

**Standard page structure**

Every reStructuredText documentation page follows this structure:

```restructuredtext
.. _anchor_label:

.. meta::
   :description: Brief description for search engines and social media

Page Title
==========

Opening paragraph providing context and purpose.

Section Heading
---------------

Content...

Subsection Heading
~~~~~~~~~~~~~~~~~~

Content...
```

**Metadata block**

Every page must have a `.. meta::` block immediately after the anchor label.

Format:

```restructuredtext
.. meta::
   :description: A brief, clear description of the page content for SEO and
                 social media. Typically 1-2 lines, wrapping at natural phrase
                 boundaries.
```

Examples from the documentation:

```restructuredtext
.. meta::
   :description: Practical introduction to key features, guiding users through
                 defining, launching, and managing environments, and executing commands.
```

```restructuredtext
.. meta::
   :description: A comprehensive explanation of the interface system,
                 detailing how components connect to host system resources through
                 interfaces, and the mechanism of connection points for resource
                 sharing between components.
```

**Anchor labels**

Use lowercase with underscores, prefixed by section type.

Prefixes:

- `tut_` - Tutorial sections
- `how_` - How-to guides
- `exp_` - Explanation articles
- `ref_` - Reference documentation

Examples:

```restructuredtext
.. _tut_get_started:
.. _how_add_actions:
.. _exp_interface_concepts:
.. _ref_command_launch:
```

---

## Writing style and tone

**Voice and audience**

Target audience is developers and technical professionals seeking to:

* Achieve specific goals without much overhead and roundabout musings
* Perform and conceive complex ad-hoc tasks and workflows that require precision and depth
* Attain understanding of the project's key capabilities beneficial for their scenarios

Content follows the Diátaxis framework, providing:

* Concise tutorials for common, starter-level actions and scenarios, eliminating the need to invent custom steps and allowing novice users to journey along the hot path effortlessly
* Elaborate explanations of the thinking behind the project's design, including design decisions, related concepts, and how it should be used
* Detailed how-to guides that address specific needs of advanced users and cover topics beyond basic entry-level operations
* Comprehensive reference of all options, settings, and details available to customize the project's operation in any desirable manner

The tone is authoritative but relaxed, confident but approachable. Think water cooler conversation, not classroom session.

Example from the documentation:

```text
<PROJECT_NAME> is a tool for defining and handling development environments.

List your dependencies and components in YAML to define an environment. The key pieces of a definition are components, independent but connectable units of functionality. The project simplifies experiments with your environment layout.
```

**Direct instructions**

Use imperative mood for instructions. Avoid "you can" or "you may" for required actions.

Preferred:

```
Install the application using the --classic option:
```

Avoid:

```
You can install the application with:
```

**Paragraph length**

Keep paragraphs focused and relatively short (2-5 sentences typically). Complex topics should be broken into multiple paragraphs.

Example from tutorial:

```restructuredtext
Install the project,
upgrading the prerequisites if needed,
then ensure it runs.

Authenticate to the package manager and install
using the required options:
```

**Clarity over cleverness**

- State prerequisites explicitly
- Define terms at first use
- Avoid assumptions about reader knowledge
- Use precise, unambiguous language

**Language and spelling**

Convention: Use US English spelling, grammar, and formatting conventions throughout the documentation.

Examples:
- Good: `color`, `center`, `analyze`, `behavior`
- Avoid: `colour`, `centre`, `analyse`, `behaviour`
- Good: Use serial comma: "components, interfaces, and environments"
- Good: Double quotes for quotations: "The project is a tool"

---

## Semantic line breaks

**Pattern**

The documentation consistently uses semantic line breaks (one line per clause or significant phrase) in reStructuredText files. This improves version control diffs and editing precision.

Rationale: Semantic breaks make git diffs more readable and help reviewers identify exactly what changed in a sentence or paragraph.

**Implementation**

Break lines at natural semantic boundaries:
- After each complete clause
- Before coordinating conjunctions (and, but, or)
- Before relative clauses (which, that, who)
- After introductory phrases

Example from the documentation:

```restructuredtext
This is the first section of the :ref:`four-part series <tut_index>`;
a practical introduction
that takes you on a tour
of the essential |project_markup| activities.
```

```restructuredtext
To make use of these interfaces,
components and :ref:`environments <exp_environment_definition_connections>` define *connection points*.
For example, a :ref:`mount interface <exp_mount_interface>`
creates a source directory to be mounted inside the environment via a connection.
```

```restructuredtext
When building components for |project_markup|,
developers face design decisions
that affect how their components install, integrate, and work inside environments.
Understanding the best practices outlined below
helps developers create more maintainable, reliable, and user-friendly components
that better align with |project_markup|'s architecture and ideology.
```

**When to break**

Break after:
- Complete independent clauses
- Introductory prepositional phrases
- Transitional phrases
- Items in a complex series

Keep together:
- Short phrases that form a single unit
- Inline markup and its target word
- Cross-reference markup

Example:

```restructuredtext
Interfaces are a mechanism for communication and resource sharing.
It is an integral part of environment isolation,
ensuring that each environment operates in its own isolated context,
while still allowing controlled interactions among the components and with the host.
```

---

## Headings and titles

**Capitalization**

Pattern: Sentence case for all headings (capitalize only first word and proper nouns).

Examples:

```restructuredtext
Get started with the project
=============================

Install |project_markup|
------------------------

Prerequisites
~~~~~~~~~~~~~
```

Exception: Product names and proper nouns maintain their capitalization:

```restructuredtext
How to use JetBrains Gateway with the project
==============================================
```

**Heading hierarchy**

reStructuredText heading levels (consistent across documentation):

```restructuredtext
Page Title (H1)
===============

Section (H2)
------------

Subsection (H3)
~~~~~~~~~~~~~~~

Sub-subsection (H4)
^^^^^^^^^^^^^^^^^^^
```

**How-to title pattern**

How-to guides follow the pattern: "How to [action] [object]":
- How to forward ports with tunneling
- How to fix connection conflicts
- How to debug issues in environments

Linking exception: In navigation and links, drop "How to" prefix and use infinitive:

```restructuredtext
How-to guides:

* Debug issues in environments
* Connect IDE to an environment
```

---

## reStructuredText conventions

**Code blocks**

Standard format:

```restructuredtext
.. code-block:: console

   $ command launch dev
```

```restructuredtext
.. code-block:: yaml
   :caption: config.yaml

   name: dev
   base: ubuntu@22.04
```

With emphasis:

```restructuredtext
.. code-block:: yaml
   :caption: config.yaml
   :emphasize-lines: 7-11

   name: dev
   base: ubuntu@22.04
   components:
     - name: runtime
       channel: stable
   
   actions:
     lint: |
       lint-command run
```

Supported languages: `console`, `yaml`, `python`, `go`, `shell`, `ini`, `json`

**Admonitions**

Note:

```restructuredtext
.. note::

   For other installation options,
   see the available installation methods in
   the project documentation.
```

Warning:

```restructuredtext
.. warning::

   This will permanently delete all environment data.
```

**Placement:** Place admonitions at the end of the subsection they relate to, rather than interrupting the flow of text in the middle of a section.

**Inline markup**

Semantic markup preference: Use semantic markup roles (`:samp:`, `:envvar:`, `:file:`, etc.) instead of generic ones (\`, \*, etc.). Choose the most specific role that suits the purpose and use it consistently.

Emphasis (italics):

```restructuredtext
A *component* is a development environment element running in a container.
```

Use italics sparingly to introduce new terms (a link is even better) and for emphasis. Leave bold for product names and commands.

Strong (bold): Rarely used; prefer other markup when possible.

Program/command names:

```restructuredtext
:program:`project-tool`
:command:`project-tool launch`
```

Commands in `:command:` roles should be presented in their complete form (e.g. `project-tool launch`, not just `launch`) and should not be used as verbs or nouns in the text. Use non-breaking spaces to prevent longer compound commands from wrapping.

File paths:

```restructuredtext
:file:`config.yaml`
:file:`/home/user/.config/models/`
```

End directory path names with a slash where possible and conventional to disambiguate directories from files.

Sample values:

```restructuredtext
:samp:`service-name`
:samp:`agent-process`
```

Environment variables:

```restructuredtext
:envvar:`PATH`
:envvar:`HOME`
```

Placeholders:
Format placeholders in uppercase within angle brackets, without underscores:

```restructuredtext
:samp:`project-tool launch {ENVIRONMENT}`
:samp:`{COMPONENT-NAME}@{CHANNEL}`
```

Or in documentation text:

```
project-tool launch <ENVIRONMENT>
```

Substitutions are reusable text replacements defined in `docs/reuse/substitutions.txt` and automatically included in all reStructuredText files:

```restructuredtext
|project_markup|       # Renders as :program:`ProjectName`
|build_tool_markup|    # Renders as :program:`BuildTool`
```

These ensure consistent formatting of product names throughout the documentation. Use them instead of typing product names manually.

Common external links are defined in `docs/reuse/links.txt` for consistent reference across documentation:

```restructuredtext
.. _Project website: https://example.com/
.. _GitHub: https://github.com/org/project/
.. _Container runtime: https://documentation.example.com/container-runtime/
.. _Build tool: https://github.com/org/build-tool/
.. _Releases: https://github.com/org/project/releases/
```

Reference these with trailing underscores:

```restructuredtext
See the `GitHub`_ repository for source code.
Refer to the `Container runtime`_ documentation for setup details.
```

**Non-breaking spaces:** Use non-breaking spaces (U+00A0 or `~` in LaTeX contexts) for important proper names and compound commands where line breaks would be awkward, though this is rarely needed in reStructuredText.

**Lists**

Bulleted lists:

```restructuredtext
- Network interface (manually connected)
- Display interface (manually connected)
- GPU interface (auto-connected)
```

Numbered lists: Use pound signs for auto-numbering:

```restructuredtext
#. First step
#. Second step
#. Third step
```

Multi-line list items: Separate items with a blank line for visibility if at least one item is multi-line:

```restructuredtext
- First item with a longer description
  that spans multiple lines

- Second item that is also long
  and needs proper spacing

- Third item
```

**Table of contents**

Follow this pattern, avoiding hidden ToCs where possible:

```restructuredtext
Heading
=======

Some summary of what's to follow.

These articles say this and this:

.. toctree::
   :glob:
   :maxdepth: 1

   *

These articles say this and this:

.. toctree::
   :glob:
   :maxdepth: 1

   *
```

**"See also" sections**

"See also" sections can appear on pages under any pillar and link to related content not immediately essential but potentially useful. Break link lists down by pillar, listing pillars and individual subsections in alphabetical order:

```restructuredtext
See also
--------

Explanation:

* :ref:`changes, tasks (concepts) <exp_changes_tasks>`
* :ref:`project (concept) <exp_project>`
* :ref:`environment (concept) <exp_environment>`, :ref:`environment definition (file) <exp_environment_definition>`

Reference:

* :ref:`environment changes (command) <ref_environment_changes>`
```

Or using more informal link style:

```restructuredtext
See also
--------

How-to guides:

* Debug :ref:`issues in environments <how_debug_issues_environments>`

Reference:

* :ref:`environment changes (command) <ref_environment_changes>`

Tutorial:

* :ref:`Wait on error <tut_refresh_wait_on_error>`
```

Special case: If "See also" is the only subsection on the page, hide the sidebar ToC on the right using the `:hide-toc:` directive at the top of the file.

**Tab headings**

Pattern: Keep tab headings noun-based and consistent across related content. Avoid "sticky toggling" (where tab state persists inappropriately across different contexts).

Example:

```restructuredtext
.. tabs::

   .. tab:: Ubuntu

      Installation instructions for Ubuntu...

   .. tab:: macOS

      Installation instructions for macOS...
```

**Rubric directive**

Used in CLI reference for section headers:

```restructuredtext
.. rubric:: Usage

.. code-block:: console

   $ project-tool launch <ENVIRONMENT>... [flags]

.. rubric:: Description

This command constructs the environments...

.. rubric:: Examples

Launch the 'dev' and 'test' environments:
```

**Sphinx extensions and roles**

Preference: Use Sphinx-specific [roles](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html) and [directives](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html) over `docutils` generic equivalents. Use all their options and capabilities, listing options in alphabetical order.

Example with options:

```restructuredtext
.. code-block:: yaml
   :caption: config.yaml
   :emphasize-lines: 3-5
   :linenos:

   name: dev
   base: ubuntu@22.04
   components:
     - name: runtime
       channel: stable
```

**Spacing and formatting**

Section gaps: Include a non-cumulative two-line gap (two blank lines) after code samples, lists, tables, and before headings for visual clarity.

Examples from the documentation:

After code blocks:

```restructuredtext
.. code-block:: console

   $ sudo package-manager login
   $ sudo package-manager install --classic project-tool


Prerequisites
~~~~~~~~~~~~~
```

After lists:

```restructuredtext
- :command:`project-tool stop` doesn't destroy the environment,
  unlike :ref:`remove <tut_remove>`

- :command:`project-tool start` doesn't build it from scratch,
  unlike :ref:`launch <tut_launch>` or :ref:`refresh <tut_refresh>`


In the next step, you'll refresh an existing environment.
```

After tables:

```restructuredtext
.. list-table::
  :header-rows: 1
  :widths: 25 75

  * - Component Type
    - Description

  * - Runtime components
    - Core binaries and libraries that change infrequently


However, parts are not mandatory:
```

Before headings:

```restructuredtext
The actions you're about to perform
cover most of your daily needs with |project_markup|.


.. _tut_install:

Install |project_markup|
------------------------
```

---

## Markdown conventions

**Usage pattern**

Markdown is used for:
- Release notes (`release-notes/v*.md`)
- Auto-generated CLI reference (`reference/cli/*/`)
- Special files (`security.md`, project-specific documentation)

**Release notes**

Release notes are written in Markdown and stored in the `docs/release-notes/` directory.

**File naming**

Use the version number as the filename: `vX.Y.Z.md`.

**Template**

Use the following template for new release notes, ensuring all links and version numbers are updated:

````markdown
```{eval-rst}
.. meta::
   :description: Release notes for ProjectName vX.Y.Z, highlighting [key features].
```

# ProjectName vX.Y.Z release notes

## [Day] [Month] [Year]

These release notes cover new features and changes in ProjectName vX.Y.Z.

## Requirements and compatibility

ProjectName requires [list dependencies]:

- See the [Tutorial](https://docs.example.com/stable/tutorial/) for setup instructions.
- Refer to the [Contribution Guide](https://docs.example.com/stable/contributing/) for development prerequisites.

## What's new in ProjectName vX.Y.Z

[Brief summary of the release].

### [Feature Name]

[Description of the feature and its benefit].

----

**Full Changelog**:
https://github.com/org/project/compare/vX.Y.Z-1...vX.Y.Z
````

**Metadata in Markdown files**

Pattern: Markdown files should include metadata using the `{eval-rst}` directive at the top of the file.

Required for:
- Release notes (`release-notes/v0.*.md`)
- Any Markdown documentation files that will be rendered in Sphinx

Format:

````markdown
```{eval-rst}
.. meta::
   :description: Brief description for search engines and social media.
```

# Page Title
````

Exception: Currently, auto-generated CLI reference files (`reference/cli/*/`) do not require metadata blocks, as they are automatically generated from command definitions.

Example from release notes:

````markdown
```{eval-rst}
.. meta::
   :description: Release notes for ProjectName v1.2.3, highlighting key changes,
                 new features, and bug fixes in this version.
```

# ProjectName v1.2.3 release notes
````

**Simplified markup for GitHub**

Use simplified markup for files that have special meaning on GitHub and need to be rendered there (such as `README.rst`, `CONTRIBUTING.rst`, `SECURITY.rst`). For example, don't use `$` prompts in command samples for these files because GitHub doesn't prevent their selection during copying, which can confuse users.

---

## Code examples

**Console examples**

Pattern: Show command with prompt, followed by output (if relevant):

```restructuredtext
.. code-block:: console

   $ project-tool launch dev

     Launching dev...
     Launched dev
```

Command prompts: Use the non-selectable `$` prompt. The `console` lexer in `.. code-block::` automatically handles this, making the prompt non-selectable during copy operations.

Root access: When root access is required, include `sudo` explicitly:

```restructuredtext
.. code-block:: console

   $ sudo package-manager install project-tool --classic
```

Command output: Indent output with two spaces and separate it from the command with a blank line:

```restructuredtext
.. code-block:: console

   $ project-tool list

   Name    Status   Base           Components
   dev     Running  ubuntu@22.04   runtime, tools
   test    Stopped  ubuntu@24.04   runtime
```

Comments in commands: Use two forms for comments:

```restructuredtext
.. code-block:: console

   # Full line comment explaining the command
   $ project-tool launch dev

   $ project-tool exec dev -- echo "test"  # Inline comment with two spaces before #
```

**Configuration examples**

Always include caption:

```restructuredtext
.. code-block:: yaml
   :caption: config.yaml

   name: dev
   base: ubuntu@22.04
   components:
     - name: runtime
       channel: stable
```

Indentation: Use commonly recognized formatting:
- YAML files: 2-space indentation
- JSON files: 4-space indentation

**Multi-line shell commands**

Use backslash continuation or explicit line breaks:

```restructuredtext
.. code-block:: console

   $ project-tool connect dev/service:host 127.0.0.1:11434 \
       --host-port 11434
```

---

## Cross-references and links

**Internal cross-references**

Preferred method: Use `:ref:` links with semantic labels, not paths:

```restructuredtext
:ref:`tut_get_started`
:ref:`how_add_actions`
:ref:`exp_interface_concepts`
```

With custom text:

```restructuredtext
:ref:`four-part series <tut_index>`
:ref:`environment definition <exp_environment_definition_connections>`
```

Avoid `:doc:` links: Use `:doc:` links sparingly and only in specific contexts where finer manual control over table of contents lists is needed. Currently acceptable uses:

- Home page (`index.rst`) for primary navigation structure
- Release notes (`release-notes/index.rst`) for version listings

For all other internal documentation links, prefer `:ref:` with semantic anchor labels, as they are more robust to file reorganization and provide better error checking.

**External links**

Inline:

```restructuredtext
`Container runtime documentation <https://example.com/container-runtime/latest/>`_
```

Anonymous:

```restructuredtext
See the `Build tool guide <https://example.com/build-tool/docs/>`__ for details.
```

**Link text guidelines**

Avoid: Generic "click here" or "see this" text

Prefer: Descriptive phrases integrated into the sentence

Example:

Good:

```
See the available installation options in project documentation.
```

Avoid:

```
See here for more details.
```

**First mention pattern**

Link important terms only at first mention on a page. Avoid excessive linking.

**Reference label convention**

Use the following underline convention for `:ref:` anchor labels:

```restructuredtext
.. _ref_command_launch:
.. _how_add_actions:
.. _exp_interface_concepts:
.. _tut_get_started:
```

Pattern: `.. _{prefix}_{descriptive_name}:` where prefix indicates the section type (ref/how/exp/tut).

---

## Terminology, product names

**Product names**

Use markup substitutions for product names to ensure consistent formatting:
- Use `|project_markup|` for the project name (renders as `:program:`ProjectName``)
- Use `|build_tool_markup|` for the build tool name (renders as `:program:`BuildTool``)
- For external products, use their official capitalization (e.g., JetBrains Gateway, Ubuntu)

**Technical terms**

component (lowercase) - A modular unit of functionality:

```
A component is a development environment element running in a container.
```

interface - Lowercase when referring to the general concept; specific interfaces follow same pattern:
- network interface
- GPU interface  
- mount interface

**Command names**

Always use exact command syntax:

```
project-tool launch
project-tool connect
build-tool build
```

**Substitutions and reusable content**

**Text substitutions**

Use defined substitutions from `docs/reuse/substitutions.txt`:
- `|project_markup|` renders as ProjectName (with `:program:` markup)
- `|build_tool_markup|` renders as BuildTool (with `:program:` markup)

**Reusable link references**

Common external URLs are defined in `docs/reuse/links.txt`:
- `` `GitHub`_ `` links to the project repository
- `` `Container runtime`_ `` links to container runtime documentation
- `` `Build tool`_ `` links to build tool repository
- `` `Releases`_ `` links to project releases page

These files are automatically included via the `docs/conf.py` configuration and are available in all reStructuredText documentation files. Using them ensures consistency and makes it easy to update URLs in a single location.

**Punctuation**

En dash (–): Use to represent a range or connection between two related items:

```
pages 10–15
East–West traffic
Ubuntu 22.04–24.04
```

Em dash (—): Avoid using em dashes. If possible, rephrase the sentence using other punctuation or sentence structure.

**Command line terminology**

Convention: Use [POSIX utility conventions](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html) when discussing command-line syntax, options, arguments, and other CLI elements.

---

## Documentation quality principles

**Clarity**

- State assumptions explicitly
- Define prerequisites clearly
- Avoid jargon without explanation
- Use consistent terminology

**Usability**

- Focus on actionable information
- Use direct imperatives for instructions
- Break complex tasks into clear steps
- Provide working examples

**Precision**

- Avoid ambiguous language
- Use exact commands and syntax
- Specify versions when relevant
- Maintain consistent structure

---

## Contributing

When contributing documentation:

1. Follow established patterns for file naming and structure
2. Use semantic line breaks in reStructuredText files
3. Include required metadata blocks
4. Test examples before including them
5. Run documentation builds locally to verify

For detailed contribution guidelines, see the contributing documentation in the project.
