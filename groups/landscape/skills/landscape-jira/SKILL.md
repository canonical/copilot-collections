---
name: landscape-jira
description: Creates well-formed Jira stories in the LNDENG project (warthogs.atlassian.net) with correct field mappings, sprint assignment, and acceptance criteria.
---

## Cloud ID

Always pass `warthogs.atlassian.net` as `cloudId` to every Atlassian MCP tool call.

## Key Field IDs (LNDENG Stories)

| Field | Field ID | Notes |
|-------|----------|---------|
| Summary | `summary` | Required |
| Description | `description` | ADF format for API v3 |
| Acceptance Criteria | `customfield_10614` | **ADF format** — NOT a plain string. See format below. |
| Story Points | `customfield_10024` | Number. Do NOT use `customfield_10016` (legacy read-only) |
| Sprint | `customfield_10020` | Numeric sprint ID — plain integer, not an object |
| Assignee | `assignee` | `{"accountId": "..."}` |
| Parent (Epic or Objective) | `parent` | `{"key": "LNDENG-XXXX"}` — can be any parent issue type |
| Issue Type | `issuetype` | `{"id": "10002"}` for Story |
| Labels | `labels` | Array of strings |

## Finding the Current Sprint ID

Never hardcode sprint IDs — they change every two weeks. Always look up the active sprint at call time:

```
project = LNDENG AND sprint in openSprints() ORDER BY created DESC
```

Read `customfield_10020[0].id` from any result. That integer is the sprint ID to pass.

For the next/upcoming sprint use `sprint in futureSprints()` instead.

## Acceptance Criteria — ADF Format

`customfield_10614` requires Atlassian Document Format (ADF), **not a plain string**. A plain string will error: `"Operation value must be an Atlassian Document"`.

Bullet list template:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Criterion one"}]}]
        },
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Criterion two"}]}]
        }
      ]
    }
  ]
}
```

Each bullet is a separate `listItem`. Do not use `\n` in text nodes — use multiple `listItem` or `paragraph` nodes instead. Literal `\n` characters render as the string `\n` in Jira, not a line break.

## Sprint Field Format

Sprint must be a **plain integer**, not an object:

```json
"customfield_10020": 30952
```

`{"id": 30952}` will error: `"Number value expected as the Sprint id."`

## Description Field

Plain strings work via the MCP wrapper. For multi-paragraph content, use ADF — multiple `paragraph` nodes, never `\n` literals inside text nodes.

## Useful JQL Patterns

Find open stories assigned to you in the current sprint:

```
project = LNDENG AND sprint in openSprints() AND assignee = currentUser() AND resolution = Unresolved
```

Find child stories under a parent:

```
project = LNDENG AND parent = LNDENG-XXXX ORDER BY created ASC
```

Find stories created by you recently:

```
project = LNDENG AND reporter = currentUser() AND created >= -7d ORDER BY created DESC
```

## Writing Good Acceptance Criteria

AC is about **building the right product**. DoD is about building it right. Don't conflate them.

AC are required for Epics and Objectives, recommended for Stories.

### Three types of AC

- **User-centered** — does it meet user needs? Functionality, experience, edge cases. Written from the user's perspective.
- **Operational** — does it meet internal standards? Security, scalability, compliance, maintainability. Unlike DoD (task-level quality), these are deployment-readiness criteria tied to operational use cases.
- **System-centric** — does it work in the broader ecosystem? APIs, shared services, downstream dependencies, indirect users.

### Qualities of good AC

- **Testable** — can you verify it against a proposed implementation or in QA?
- **Result-oriented** — focus on outcomes for the user, not the implementation. "Latency < 250ms" not "written in Go".
- **Unambiguous** — understood the same way by PM, engineering, and design.
- **Concise** — enough detail to make the right implementation choices, not a full spec.

### What AC is not

- Not a description of the UI or solution — describe what the user can *do*, not how it's built.
- Not a DoD checklist (unit tests, docs, CI passing) — those belong in the PR template or DoD.
- Not an exhaustive list — if you're writing many ACs for one story, break the story up.

### Format tips

- Use plain declarative statements: "User can X", "System must Y", "Returns Z on error"
- Group by type when there are many: user-centered first, then operational, then system
- State inputs, outputs, states, error conditions, and edge cases where relevant
- Leave implementation choices open — describe the outcome, not the mechanism

## Gotchas

1. **AC is ADF, not a string** — wrap in `doc > bulletList > listItem > paragraph > text`. Most common failure.
2. **Sprint is a plain integer** — not `{"id": ...}`.
3. **Story Points** — `customfield_10024`. The field `customfield_10016` is read-only legacy, don't write to it.
4. **Parent field** — use `parent: {"key": "LNDENG-XXXX"}`. Works for epics and objectives. `customfield_10014` is the read-only epic link.
5. **No `\n` in text nodes** — use separate ADF nodes for line breaks; `\n` renders as a literal backslash-n.
6. **AC vs description** — AC belongs in `customfield_10614` only. Description = context/approach. Never duplicate AC into the description.
7. **New issues land in "Untriaged"** — transition them explicitly if a different status is needed.
