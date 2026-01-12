<!--
  ~ Copyright 2026 Canonical Ltd.
  ~ See LICENSE file for licensing details.
-->

# **Canonical Copilot Collections**

**Centralized context management for GitHub Copilot across the Canonical ecosystem.**

This repository acts as a "Toolkit" to distribute standardized Copilot Custom Instructions, Prompts, Agents and Skills. It allows individual repositories to "subscribe" to specific sets of assets (e.g., Python standards, Juju/Ops Framework patterns) and keep them synchronized automatically.

## **What are Collections?**

A **Collection** is a logical group of markdown files (instructions, prompts, agents, and skills) defined in `collections.yaml.`

Instead of copying specific instructions into 50 different repositories manually, the consuming repository defines a configuration file listing the collections it needs.

**Available Collections (Examples):**

* common-python: Standard Python coding style.  
* common-documentation: Documentation standards with review skill.
* charm-python: Includes common-python + Juju Ops Framework specifics.  
* pfe-charms: Platform Engineering specific collection.

## **Usage: Adding to a Repository**

To add Copilot collections to your repository, follow these three steps.

### **1. Create the Configuration**

Create a file named `.copilot-collections.yaml` in the root of your repository.

```yaml
copilot:  
  # The version of the toolkit to use (matches a Release Tag in this repo)  
  version: "v1.0.0"  
    
  # The collections you want to install  
  collections:  
    - charm-python  
    - pfe-charms
```

### **2. Run the Initial Sync (Local)**

You can sync the instructions immediately to your local machine to verify them.

```bash
curl -sL https://raw.githubusercontent.com/canonical/copilot-collections/main/scripts/local_sync.sh | bash
```

**Note:** This will generate files in .github/instructions/, .github/prompts/, and .github/skills/. Do not edit these files manually; they will be overwritten.

### **3. Configure Auto-Updates (CI)**

To ensure your repo stays up to date when the Toolkit releases new versions, add this workflow.

**File:** `.github/workflows/copilot-collections-update.yml`

```yaml
name: Auto-Update Copilot Instructions  
on:  
  schedule:  
    - cron: '0 9 * * 1' # Run every Monday at 09:00 UTC  
  workflow_dispatch:

jobs:  
  check-update:  
    # Always pin to @main to get the latest logic, but the content version is controlled by your .yaml file  
    uses: canonical/copilot-collections/.github/workflows/auto_update_collections.yaml@main  
    with:  
      config_file: ".copilot-collections.yaml"  
    secrets: inherit
```

## **Inspiration & Credits**

Some prompts and instruction patterns in this collection were inspired by the [Awesome GitHub Copilot](https://github.com/github/awesome-copilot) repository.

We highly encourage you to explore it for further inspiration, including advanced chat modes, persona definitions, and framework-specific prompts that you might want to adapt for your specific projects.

## **Maintaining**

### **Directory Structure**

* assets/: Raw markdown files (Core assets).
  * instructions/: Custom instruction files.
  * prompts/: Prompt files.
  * agents/: Agent files.
  * skills/: Agent skill directories (each containing SKILL.md).
* collections.yaml: Core definitions.
* groups/: Team specific collections.
  * <team-name>/: Folder for team assets.
    * collections.yaml: Team specific definitions.
* scripts/: Logic for syncing files.
* .github/workflows/: Reusable workflows.

### **How to add a new Instruction**

1. **Add the file:** Create `assets/instructions/my-topic/my-new-instructions.md` (for core) or `groups/<team>/instructions/...` (for teams).
2. **Update Manifest:** Edit `collections.yaml` (core) or `groups/<team>/collections.yaml`.
   * Add it to an existing collection items list.
   * OR create a new collection key if it represents a new logical group.
3. **Release:**
   * Open PR.
   * Merge changes to main.
   * Create a new GitHub Release (e.g., v1.1.0).
   * *Consumer repos will pick this up automatically on their next scheduled run.*

### **How to add a new Agent Skill**

1. **Create the directory:** Create `assets/skills/<skill-name>/` (for core) or `groups/<team>/skills/<skill-name>/` (for teams).
2. **Add SKILL.md:** Create the skill definition file with required YAML frontmatter:
   ```markdown
   ---
   name: skill-name
   description: What the skill does
   ---
   # Skill content here
   ```
3. **Update Manifest:** Edit `collections.yaml` and add to a collection's items:
   ```yaml
   - src: assets/skills/<skill-name>
     dest: .github/skills/<skill-name>/
   ```
   **Important:** Skills are directories, so `dest` must end with `/`.
4. **Validate:** Run `./scripts/validate_collections.sh .`
5. **Release:** Follow the same release process as instructions.

### **Group Collections**

Teams can manage their own collections in `groups/<team-name>/`.

**Naming Convention:**
Collection names are global. To avoid collisions, **prefix your collection names with your group name**.
*   ✅ `pfe-charms`
*   ❌ `charms` (Too generic)

**Path Resolution:**
*   **Relative Paths**: `src: instructions/guide.md` -> Resolves to `groups/<team>/instructions/guide.md`.
*   **Root Paths**: `src: /assets/common/logo.png` -> Resolves to `assets/common/logo.png` (Repository Root).
