---
name: documentation-verify
description: "Verifies documentation accuracy by cross-referencing claims and commands against source code in the repository."
---

# Documentation Accuracy Verification

## Scope

Accuracy verification only: cross-reference documentation claims,
commands, API names, and configuration keys against source code
in the same repository. Flag anything that cannot be verified.

## Inputs

- Changed documentation files (from `git diff`).
  If `git diff` is unavailable or empty, use files explicitly
  provided for review; otherwise, treat all documentation files
  under `docs/` as changed.
- Full codebase.
- Test files, configuration schemas.
- Documentation structure.

## Actions

### Content Completeness Check

Check that all relevant topics are covered,
especially for reference documentation:

- **CLI**: Verify command-line interface changes are reflected
  in CLI reference documentation.
- **Configuration**: Check that new configuration options
  are documented in the reference section.
- **APIs and schemas**: Validate that API and schema modifications
  are properly documented.

### Sub-stage A: Discovery Scan

1. **Identify changed documentation claims**:

   - Run `git diff` to list changed documentation files.
   - For each changed file, categorise changes:
     - **Behaviour claims**: Assertions about how the project,
       commands, or features behave.
     - **Options/defaults/constraints**: Documented flags,
       configuration keys, default values, allowed values,
       validation rules.
     - **Examples**: Code samples, command invocations,
       YAML/JSON configurations, expected outputs.
     - **CLI surface**: Command names, subcommands, flags,
       help text, output formats.
     - **API surface**: REST endpoints, request/response formats,
       client method signatures, schemas.
     - **Error messages**: Documented error text, exit codes,
       diagnostic output.
     - **Terminology/renames/deprecations**: Changed names,
       deprecated features, migration paths.
     - **Interface/component behaviour**: Connection types,
       interaction mechanics, isolation rules.

2. **Form initial hypotheses for each claim**:

   - **Supported**: Claim appears to match code structure (preliminary).
   - **Unsupported**: Claim appears inconsistent with code (preliminary).
   - **Speculative**: Claim describes future or intended behaviour
     without code backing.
   - **Ambiguous**: Unclear whether claim matches code
     (needs deeper investigation).
   - **Outdated**: Claim may describe previous code behaviour.

### Sub-stage B: Verification Pass

For every initial hypothesis, complete these verification steps.
Code is the source of truth.

1. **Locate code evidence with multiple strategies**
   (at least two distinct searches per claim):

   - **Direct identifier search**: Search for exact names, keys,
     constants, struct fields using `grep -r`, `git grep`, ripgrep,
     or language-specific tools.
   - **Entrypoint tracing**: Follow from CLI, config,
     or API entrypoint to implementation.
   - **Test evidence search**: Locate tests that exercise
     the claimed behaviour in test files.
   - **Schema/validation search**: Find parsers, validators,
     schema generators, struct tags, validation functions.

2. **Verification checklist by claim type**:

   **Behaviour claims**:

   - Locate implementation code path.
   - Verify behaviour matches documented description.
   - Check for conditional behaviour (flags, modes, edge cases).
   - Confirm error handling matches docs.

   **Options/defaults/constraints**:

   - Find struct field or config key definition.
   - Extract actual default value from code.
   - Find allowed values (enums, validation statements, regex patterns).
   - Verify constraint enforcement.

   **Examples**:

   - Confirm example syntax matches actual parser expectations.
   - If example shows command output, verify against golden test files
     or actual execution.
   - Confirm field names, indentation, and structure
     match code expectations.
   - Check that referenced flags and options exist in code.

   **CLI surface**:

   - Locate command definition in the CLI framework location.
   - Verify command name, aliases, subcommands match.
   - Check flag definitions (name, shorthand, type, default, help text).
   - Confirm help text matches command definition.
   - Verify output formatting (column headers, sorting).

   **API surface**:

   - Find route definition.
   - Verify HTTP method, path, versioning.
   - Check request/response struct definitions.
   - Confirm client method signature.
   - Verify backward compatibility.

   **Error messages**:

   - Search codebase for exact error text or pattern.
   - Verify error is returned in documented scenario.
   - Check error message format follows style guide.

   **Terminology/renames/deprecations**:

   - Search for old name to confirm it is truly deprecated or removed.
   - Find deprecation markers, aliases, or migration helpers.
   - Check changelog, release notes, or version gating logic.
   - Verify new name exists and is used consistently.

3. **Document evidence for each finding**:

   For claims supported by code:

   - Note file path, function or struct, and line range.
   - Assessment: `Supported (verified at [file:line])`.

   For claims not supported by code:

   - Document searches performed
     (at least two strategies with specific search terms).
   - Note what was expected versus what was found.
   - Assessment: `Unsupported (expected [X], found [Y] at [file:line])`.

   For inconclusive claims:

   - Document search attempts.
   - Note what evidence is missing or ambiguous.
   - Assessment: `Inconclusive (needs human review: [specific check])`.

4. **Reclassify each hypothesis** based on verification evidence:

   | Original Hypothesis | Verification Outcome | Final Classification |
   |---|---|---|
   | Unsupported | Found matching code | Retract claim (docs are correct) |
   | Unsupported | Found code with different default | Docs outdated (needs value update) |
   | Unsupported | No code evidence after thorough search | Confirmed unsupported (docs ahead of code) |
   | Supported | Code contradicts doc claim | Docs incorrect (needs correction) |
   | Ambiguous | Tests confirm behaviour | Supported (test-backed) |
   | Ambiguous | Cannot locate relevant code | Inconclusive (flag for human review) |

5. **Apply false-positive prevention rules**:

   - Do not claim "unsupported" without documented code search evidence
     (at least two strategies with explicit search terms).
   - Prefer "inconclusive" over "unsupported"
     when code is complex or evidence is indirect.
   - Prefer "outdated" over "unsupported"
     when code exists but with different behaviour or values.
   - Prefer "imprecise" over "incorrect"
     when docs are vague but not technically wrong.
   - Retract claim entirely if verification confirms docs are accurate.

6. **Cross-check documentation coverage**:

   - Before claiming "unsupported",
     verify the entity is not documented elsewhere.
   - Search `docs/` for related terms, alternative phrasings, synonyms.
   - If claim is supported elsewhere,
     classify as "present but undiscoverable" instead.

### Sub-stage C: Refined Final Report

1. **Group findings by classification**:

   - **Confirmed unsupported**: Docs describe behaviour or options
     not present in code.
   - **Docs outdated**: Code exists but with different values
     or behaviour than documented.
   - **Docs incorrect**: Code contradicts doc claim.
   - **Docs imprecise**: Code behaviour more nuanced than docs suggest.
   - **Docs speculative**: Describes intended future behaviour
     (not yet implemented).
   - **Inconclusive**: Cannot verify (requires human review).
   - **No issues found**: All doc claims backed by code
     (state this explicitly).

2. **Format each verified finding**:

   For each issue, include:

   ````markdown
   **Doc Claim**: [File path:line] "[Quoted claim from docs]"

   **Verification Checklist**:
   - [ ] Search strategies used: [list at least two strategies]
   - [ ] Code location(s) checked: [file paths]
   - [ ] Test evidence: [test file/function or "Not found"]
   - [ ] Schema/validation: [struct/parser location or "Not found"]

   **Code Evidence**:
   - **Expected**: [What docs claim should exist]
   - **Found**: [What code actually shows, with file:line references]
   - **Assessment**: [Supported | Unsupported | Outdated | Incorrect | Imprecise | Inconclusive]

   **Issue**: [Classification from list above]
   - [Brief description of mismatch]

   **Recommended Action**:
   - [File path]: [Specific minimal edit to restore correctness]
   - Rationale: [Why this edit aligns docs with code]
   - Alternative: [If docs are ahead of code, suggest opening an issue or reverting speculative claim]
   ````

3. **Conservative change suggestions**:

   - For "docs outdated": Update specific values or behaviour
     descriptions to match current code.
   - For "docs incorrect": Correct the claim
     with precise wording from code.
   - For "docs imprecise": Add qualifiers, conditions,
     or edge-case notes.
   - For "confirmed unsupported": Revert or remove unsupported claim.
     Alternative: if claim represents intended behaviour,
     change to future tense and add note.
   - For "docs speculative": Mark as future or intended,
     not current behaviour.
   - For "inconclusive": Provide specific human review action.

4. **Link to code artefacts**: Reference specific files, functions,
   structs, constants with line numbers. Reference test files.
   Include search commands used for verification.

### Report Integration

- Prioritise code backing findings appropriately
  (blocking issues for incorrect or unsupported claims).
- Cross-reference with Diataxis compliance findings
  to identify if inaccuracies stem from category misalignment.
- Prepare evidence-based recommendations with code references.

## Constraints

- Complete the verification pass (Sub-stage B)
  before reporting any documentation claims.
- Provide code evidence for all documentation consistency claims.
- Code is the source of truth:
  flag documentation that contradicts code behaviour,
  not vice versa.
- Do not claim documentation is "unsupported by code"
  without verification evidence
  (at least two search strategies with explicit code search
  and no-match confirmation).
- Do not report false positives.
- Do not prefer "unsupported" when docs are vague or imprecise;
  use accurate classifications.
- Do not recommend changing code to match docs as the primary action;
  only documentation should be adjusted to match code reality.

## Output

Only verified findings with evidence make it to the final report.
Do not include intermediate hypotheses or reasoning.
