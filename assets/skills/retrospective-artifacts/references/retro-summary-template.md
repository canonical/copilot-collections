# Retrospective Summary Template

Use this template for `.retrospectives/*/retro-summary.md`.

```yaml
---
date: "[YYYY-MM-DD]"
session_type: "[troubleshooting | asset_creation | refactor | architecture | incident_review]"
primary_tags: ["[tag1]", "[tag2]", "[tag3]"]
status: "[resolved | parked | escalated]"
initiator: "[User | Developer | Agent]"
downstream_signals:
  okb_worthy: [true | false]
  context_asset_improvement_needed: [true | false]
---
```

# Retrospective: [Short Session Name]

## Scope & Focus
- **Focus Directive:** [What this retro intentionally focuses on]
- **Explicit Exclusions:** [What was intentionally excluded]

## 1. Executive Summary
[2-3 sentences: goal, key discovery, and final outcome.]

## 2. The Catalyst (Problem / Goal)
- **Symptom/Goal:** [Description]
- **Impact:** [Operational/product/team impact]

## 3. Investigation & Context Breakdown
[Summarize investigation flow and evidence. Use relative references to files in `context/` and `logs/` when applicable.]

## 4. Resolution & Implementation
- **Solution:** [What changed and why it solved the issue]
- **Code Changes:** [Relative references in `code-snippets/` if applicable]

## 5. Downstream Agent Signals
### A. Context Asset Recommendations
- **Missing Skill:** [Yes/No + explanation]
- **Instruction Update:** [Yes/No + explanation]

### B. OKB Learnings
- **Core Concept:** [Generalizable technical learning]
- **Gotchas/Pitfalls:** [What to avoid next time]

## 6. Evidence Index
- `./context/[file]` - [what it contains]
- `./logs/[file]` - [what it contains]
- `./code-snippets/[file]` - [what it contains]

## 7. Acquisition Graph (Optional but Recommended)
- Seed Sources:
  - [source-url-1]
- Recursively Gathered:
  - [child-url] (discovered from: [source-url-1])

## Completion Rules
- Keep statements evidence-backed
- Do not cite files that do not exist
- Keep language concise and operational
