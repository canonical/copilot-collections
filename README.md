# **Canonical Copilot Collections**

**Centralized context management for GitHub Copilot across the Canonical ecosystem.**

This repository acts as a "Toolkit" to distribute standardized Copilot Custom Instructions, Prompts, and Agent definitions. It allows individual repositories to "subscribe" to specific sets of instructions (e.g., Python standards, Juju/Ops Framework patterns) and keep them synchronized automatically.

## **What are Collections?**

A **Collection** is a logical group of markdown files (instructions, prompts) defined in `collections.yaml.`

Instead of copying specific instructions into 50 different repositories manually, the consuming repository defines a configuration file listing the collections it needs.

**Available Collections (Examples):**

* common-python: Standard Python coding style.  
* charm-python: Includes common-python + Juju Ops Framework specifics.  
* pfe-charms: Platform Engineering specific collection.

## **Usage: Adding to a Repository**

To add Copilot collections to your repository, follow these three steps.

### **1. Create the Configuration**

Create a file named `.collections-config.yaml` in the root of your repository.

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

**Note:** This will generate files in .github/instructions/ and .github/prompts/. Do not edit these files manually; they will be overwritten.

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
      config_file: ".collections-config.yaml"  
    secrets: inherit
```

## **Inspiration & Credits**

Some prompts and instruction patterns in this collection were inspired by the [Awesome GitHub Copilot](https://github.com/github/awesome-copilot) repository.

We highly encourage you to explore it for further inspiration, including advanced chat modes, persona definitions, and framework-specific prompts that you might want to adapt for your specific projects.

## **Maintaining**

### **Directory Structure**

* assets/: Raw markdown files.  
  * instructions/: .md files for Copilot Custom Instructions.  
  * prompts/: .prompt.md files for specific tasks.  
* collections.yaml: The manifest defining groups and inheritance.  
* scripts/: Logic for syncing files.  
* .github/workflows/: Reusable workflows.

### **How to add a new Instruction**

1. **Add the file:** Create `assets/instructions/my-topic/my-new-instructions.md`.  
2. **Update Manifest:** Edit `collections.yaml`.  
   * Add it to an existing collection items list.  
   * OR create a new collection key if it represents a new logical group.  
3. **Release:**  
   * Open PR.
   * Merge changes to main.  
   * Create a new GitHub Release (e.g., v1.1.0).  
   * *Consumer repos will pick this up automatically on their next scheduled run.*
