# Context Intake Checklist

Use this checklist before generating a retrospective artifact.

## Minimum Required Inputs
- [ ] Clear session goal or problem statement
- [ ] Observable impact (user/system/team)
- [ ] Investigation summary (key steps)
- [ ] Resolution state (`resolved`, `parked`, or `escalated`)
- [ ] Focus directive defining what to include/exclude from large context exports

## Focus Directive Examples
- [ ] Include high-friction loops (multiple failed iterations)
- [ ] Include workarounds and dead ends
- [ ] Include only successful resolution path
- [ ] Include agent/tooling friction signals
- [ ] Exclude routine, low-signal steps

## Current Session Signals
- [ ] Final solution or current blocker is explicit
- [ ] Key decisions are captured
- [ ] Relevant commands/errors are known (if troubleshooting)
- [ ] Main files/components touched are identified (if code/config work)

## External Context Collection
Request links when relevant:
- [ ] GitHub issue/PR/Action logs
- [ ] Jira issue/work item
- [ ] Mattermost or chat thread
- [ ] Other incident/runbook documents

For each external source:
- [ ] Retrieval attempted via tool/integration
- [ ] Access failures reported explicitly
- [ ] Missing sources requested as pasted text
- [ ] First-level referenced links inspected for recursive acquisition
- [ ] Recursive expansion constrained by focus directive and max depth

## Artifact Packaging Rules
- [ ] Place external documents in `context/`
- [ ] Place raw diagnostics in `logs/`
- [ ] Place meaningful code excerpts in `code-snippets/`
- [ ] Ensure markdown context files include a high-signal `## Summary` section
- [ ] Ensure `retro-summary.md` references context files by relative path
- [ ] Include `Discovered From` trace for recursively gathered sources
- [ ] Artifact assets `context, logs, code-snippets` must be numerically sorted to be easier to follow for humans

## Downstream Signal Heuristics
Set `okb_worthy: true` when at least one applies:
- [ ] Reusable troubleshooting pattern discovered
- [ ] New SOP-level operational sequence identified
- [ ] Repeated pitfall now has a clear prevention pattern

Set `context_asset_improvement_needed: true` when at least one applies:
- [ ] Agent behavior failed without clear user-side ambiguity
- [ ] Existing skills/instructions lacked critical routing guidance
- [ ] Significant prompt/tool orchestration friction was observed
