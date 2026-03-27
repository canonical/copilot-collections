# Parse and Query Patterns

Use these patterns to answer retrospective queries precisely.

## Query Type A: Session Summary
Intent examples:
- "Summarize retro from last Wednesday"
- "What happened in the incident retro?"

Steps:
1. Locate target folder(s) in `.retrospectives/`.
2. Read `retro-summary.md`.
3. Return concise summary: catalyst, investigation, resolution, status.

## Query Type B: Extract Evidence
Intent examples:
- "Show the exact error logs used in this retro"
- "Get the before/after snippet"

Steps:
1. Read `retro-summary.md` evidence references.
2. Open only cited files under `logs/`, `context/`, or `code-snippets/`.
3. Return requested excerpt and file path.

## Query Type C: OKB Candidate Discovery
Intent examples:
- "Find retros worth converting to OKB"
- "List sessions with reusable learnings"

Steps:
1. Scan retros for `downstream_signals.okb_worthy: true`.
2. Return shortlist with path, date, session_type, core concept.
3. Include one-line rationale per candidate.

## Query Type D: Context Asset Follow-up Discovery
Intent examples:
- "Find retros requiring context asset improvements"

Steps:
1. Scan for `downstream_signals.context_asset_improvement_needed: true`.
2. Extract context asset recommendation subsection.
3. Return grouped by recurring improvement theme.

## Output Discipline
- Return only requested fields.
- Prefer bullet summaries over full markdown dumps.
- Include caveats when evidence is absent or inaccessible.
