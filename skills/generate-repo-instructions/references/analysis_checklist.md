# Repository Analysis Checklist

This checklist guides comprehensive repository discovery for generating high-quality instructions. **Adapt based on repository type** (code, docs, data, or mixed).

---

## Phase 0: Repository Type Detection

**Determine the primary repository type to guide analysis:**

- [ ] **Check directory structure and file types:**
  - **Code repo indicators:** src/, lib/, app/, test/, code files (.py, .js, .go, etc.)
  - **Docs repo indicators:** docs/ with many .md/.rst files, documentation generator configs
  - **Data repo indicators:** data/, schemas/, pipelines/, .sql files, data processing scripts
  - **Mixed repo:** Combination of above

- [ ] **Check for documentation generators:**
  - MkDocs (mkdocs.yml), Sphinx (conf.py), Docusaurus (docusaurus.config.js)
  - Hugo (config.toml), Jekyll (_config.yml), GitBook (book.json)
  - **If present:** Likely a docs repo or has significant docs component

- [ ] **Check for data infrastructure:**
  - dbt (dbt_project.yml), Airflow (dags/), SQL migration tools
  - Schema files (.sql, .prisma, .proto), data dictionaries
  - **If present:** Likely a data repo or has data management component

**Proceed with relevant phases based on detected type.**

---

## Phase 1: Documentation Discovery

### Primary Documentation
Read and synthesize these files (if they exist):

- [ ] **README.md** / README.rst / README.txt
  - Extract: Project overview, elevator pitch, key features
  - Look for: "What does this do?", "Why does this exist?"
  
- [ ] **CONTRIBUTING.md** / .github/CONTRIBUTING.md
  - Extract: Development workflow, coding standards, pull request process
  - Look for: Formatting rules, testing requirements, code review guidelines

- [ ] **docs/** or **doc/** directory
  - Scan for: Architecture docs, design decisions, API documentation
  - Prioritize: Files named ARCHITECTURE.md, DESIGN.md, CONVENTIONS.md

- [ ] **ARCHITECTURE.md** / DESIGN.md
  - Extract: System structure, design patterns, architectural decisions
  - Look for: Component relationships, data flow, key abstractions

### Secondary Documentation
Check for these additional sources:

- [ ] **LICENSE** - Note the license type
- [ ] **CHANGELOG.md** - Recent changes and versioning approach
- [ ] **.github/PULL_REQUEST_TEMPLATE.md** - PR requirements
- [ ] **CODE_OF_CONDUCT.md** - Community standards

---

## Phase 2: Tech Stack Detection

### Language Detection
Inspect these dependency/configuration files:

#### JavaScript/TypeScript
- [ ] **package.json**
  - Check `dependencies` and `devDependencies` for frameworks
  - Frameworks to detect: React, Vue, Angular, Express, Next.js, Nest.js
  - Check for `typescript` dependency
  
#### Python
- [ ] **requirements.txt** / **pyproject.toml** / **setup.py** / **Pipfile**
  - Look for: Django, Flask, FastAPI, pytest, black, mypy
  - Note package manager: pip, poetry, pipenv

#### Go
- [ ] **go.mod**
  - Check imports for common frameworks
  - Note Go version

#### Rust
- [ ] **Cargo.toml**
  - Check dependencies section
  - Note Rust edition

#### Java/JVM
- [ ] **pom.xml** (Maven) / **build.gradle** (Gradle)
  - Detect: Spring Boot, Spring MVC, Jakarta EE
  - Note build tool

#### Ruby
- [ ] **Gemfile**
  - Look for: Rails, Sinatra, RSpec

#### PHP
- [ ] **composer.json**
  - Look for: Laravel, Symfony, WordPress

### Framework-Specific Files
- [ ] **.babelrc** / **babel.config.js** - Babel configuration
- [ ] **tsconfig.json** - TypeScript configuration
- [ ] **next.config.js** - Next.js project
- [ ] **vue.config.js** - Vue project
- [ ] **angular.json** - Angular project

---

## Phase 3: Build System Discovery

### Build Tools
Check for these build configuration files:

- [ ] **Makefile**
  - Read targets: `build`, `test`, `lint`, `clean`, `install`
  - Note primary commands

- [ ] **package.json** → `scripts` section
  - Look for: `build`, `test`, `lint`, `dev`, `start`
  - Note script commands

- [ ] **.github/workflows/*.yml** (GitHub Actions)
  - Extract CI/CD commands
  - Identify primary workflow (usually on push/PR)

- [ ] **justfile** / **Taskfile.yml** - Modern task runners
  - Note available tasks

- [ ] **docker-compose.yml** - Docker-based development
  - Note services and startup commands

### Test Frameworks
- [ ] **pytest.ini** / **tox.ini** - Python testing
- [ ] **jest.config.js** - Jest (JavaScript)
- [ ] **phpunit.xml** - PHPUnit (PHP)
- [ ] **Rakefile** - Ruby testing

---

## Phase 4: Code Pattern Analysis

### Indentation & Formatting
Sample 3-5 source files from `src/` or `lib/`:

- [ ] **Indentation style**
  - Detect: Tabs vs spaces, 2-space vs 4-space
  - Look for `.editorconfig` or `.prettierrc` for config

- [ ] **Formatter usage**
  - Check for: Prettier, Black, rustfmt, gofmt
  - Look in devDependencies or pre-commit hooks

### Code Style
- [ ] **Linter configuration**
  - `.eslintrc.js`, `pylint.rc`, `.rubocop.yml`
  - Extract key rules

- [ ] **Async patterns** (JavaScript/TypeScript)
  - Sample code for: callbacks, Promises, async/await
  - Determine dominant pattern

- [ ] **Error handling patterns**
  - Exceptions vs Result types vs error codes
  - Try/catch usage

- [ ] **Import organization**
  - Relative vs absolute imports
  - Module aliasing (@/ syntax)

---

## Phase 5: Project Structure Mapping

List top-level directories and infer their purpose:

### Common Patterns
Map these directories if they exist:

- [ ] `src/` or `lib/` → Source code
- [ ] `tests/` or `test/` → Test files
- [ ] `docs/` or `doc/` → Documentation
- [ ] `scripts/` → Utility scripts
- [ ] `examples/` → Example code
- [ ] `public/` or `static/` → Public assets (web projects)
- [ ] `dist/` or `build/` → Build output (should be gitignored)
- [ ] `bin/` → Compiled binaries or executable scripts

### Language-Specific Patterns

**Go:**
- [ ] `cmd/` → Command-line entry points
- [ ] `pkg/` → Public packages
- [ ] `internal/` → Private packages

**Rust:**
- [ ] `src/bin/` → Binary targets
- [ ] `benches/` → Benchmarks

**Python:**
- [ ] Package name directory (project root)
- [ ] `migrations/` → Database migrations (Django)

---

## Phase 6: Configuration Files

### Development Environment
- [ ] **.env.example** - Environment variable template
- [ ] **.nvmrc** / **.node-version** - Node version
- [ ] **.python-version** - Python version
- [ ] **.ruby-version** - Ruby version

### Git Configuration
- [ ] **.gitignore** - What's excluded from version control
- [ ] **.gitattributes** - Line ending normalization

### Editor Configuration
- [ ] **.editorconfig** - Cross-editor formatting
- [ ] **.vscode/** - VS Code settings

---

## Phase 7: Security & Quality

### Security Checks
- [ ] Scan for hardcoded secrets in docs/code (report if found)
- [ ] Check for `.env.example` vs `.env` (latter should be gitignored)
- [ ] Note if security scanning tools are configured (Dependabot, Snyk)

### Quality Tools
- [ ] **Pre-commit hooks** (`.pre-commit-config.yaml`, `husky`)
- [ ] **Code coverage** (`.coveragerc`, `jest.config.js` coverage settings)
- [ ] **Type checking** (TypeScript, mypy, flow)

---

## Phase 8: Documentation Repository Specific

**Skip this phase if not a docs repo. Execute if documentation generator detected in Phase 0.**

### Documentation Generator Detection
- [ ] **MkDocs** (mkdocs.yml)
  - Extract: site_name, theme, plugins, nav structure
  - Note: Material theme extensions, search config
  
- [ ] **Sphinx** (conf.py, docs/source/)
  - Extract: project name, extensions, theme
  - Note: autodoc settings, intersphinx mappings
  
- [ ] **Docusaurus** (docusaurus.config.js)
  - Extract: title, theme config, sidebar structure
  - Note: Plugins, navbar items
  
- [ ] **Hugo** (config.toml/yaml)
  - Extract: baseURL, title, theme
  - Note: Content organization, taxonomies
  
- [ ] **Jekyll** (_config.yml)
  - Extract: title, theme, collections
  - Note: Front matter defaults
  
- [ ] **GitBook** (book.json, SUMMARY.md)
  - Extract: title, structure
  - Note: Plugin configuration

### Writing Style Analysis
- [ ] **Sample 3-5 documentation files** from different sections
  - Analyze: Voice (formal/casual), person (1st/2nd/3rd)
  - Note: Heading styles (ATX vs Setext), code fence language tags
  - Check: Admonition usage (!!! note, > **Warning:**)
  
- [ ] **STYLE_GUIDE.md** or **WRITING_GUIDE.md**
  - Extract: Explicit style rules, preferred terminology
  - Note: Formatting conventions, tone guidelines

### Content Structure Discovery
- [ ] **Navigation structure** (SUMMARY.md, nav in config)
  - Map: Content hierarchy, main sections
  - Note: Logical organization pattern
  
- [ ] **Template discovery** (if present)
  - Check: docs/templates/, .github/ISSUE_TEMPLATE/
  - Note: Standard doc formats (ADR, API reference, tutorial)
  
- [ ] **Cross-reference patterns**
  - Analyze: How docs link to each other
  - Note: Relative vs absolute links, anchor usage

### Documentation Build System
- [ ] **Build commands** (from Makefile, package.json, or README)
  - Extract: Build, serve/preview, deploy commands
  - Example: `mkdocs build`, `hugo server`, `npm run build`
  
- [ ] **CI/CD for docs** (.github/workflows/)
  - Note: Auto-deploy on merge, preview for PRs
  - Extract: Deployment target (GitHub Pages, Netlify, etc.)

### Quality Standards
- [ ] **Link checking** (broken-link-checker, linkchecker)
- [ ] **Spell checking** (aspell, cSpell configuration)
- [ ] **Linting** (markdownlint config, vale rules)

---

## Phase 9: Data Repository Specific

**Skip this phase if not a data repo. Execute if data infrastructure detected in Phase 0.**

### Schema Discovery
- [ ] **Database schemas** (.sql files, migrations/)
  - Extract: Table definitions, relationships
  - Note: Naming conventions, data types
  
- [ ] **Schema definition files**
  - **Prisma** (schema.prisma) - models, relations
  - **Protobuf** (.proto files) - message definitions
  - **Avro** (.avsc files) - schema specifications
  - **JSON Schema** (.schema.json) - validation rules
  
- [ ] **Data dictionary** (DATA_DICTIONARY.md, metadata/)
  - Extract: Column descriptions, business rules
  - Note: Data lineage, ownership

### Data Pipeline Discovery
- [ ] **dbt** (dbt_project.yml, models/)
  - Extract: Model structure, macros, tests
  - Note: Materialization strategies, documentation
  
- [ ] **Airflow** (dags/, airflow.cfg)
  - Extract: DAG structure, task dependencies
  - Note: Scheduling patterns, connections
  
- [ ] **ETL scripts** (scripts/, pipelines/)
  - Identify: Extract, transform, load patterns
  - Note: Error handling, logging approaches

### Data Quality Standards
- [ ] **Validation rules** (great_expectations/, data_tests/)
  - Extract: Quality expectations, thresholds
  - Note: Test coverage, validation frequency
  
- [ ] **Quality documentation** (QUALITY_STANDARDS.md)
  - Extract: Completeness requirements, accuracy standards
  - Note: SLA definitions, monitoring approach

### Data Governance
- [ ] **Access control** (RBAC configs, policies/)
  - Note: Permission patterns, security requirements
  
- [ ] **Retention policies** (documented or configured)
  - Extract: Data lifecycle, archival rules
  
- [ ] **Privacy compliance** (PII handling, GDPR notes)
  - Note: Anonymization patterns, consent tracking

---

## What to Do with Findings

### Synthesize Information
After completing the checklist:

**For Code Repositories:**
1. **Elevator Pitch**: Combine README overview + project goals
2. **Tech Stack Summary**: List languages + frameworks + build tools
3. **Constitutional Rules**: Extract from CONTRIBUTING + code samples
4. **Build Commands**: Primary commands for build/test/lint
5. **Structure Map**: Directory purposes (src, tests, docs)

**For Documentation Repositories:**
1. **Elevator Pitch**: What does this documentation cover + audience
2. **Doc System Summary**: Generator + theme + build commands
3. **Writing Guidelines**: Voice, tone, style conventions extracted
4. **Build Commands**: How to preview, build, deploy docs
5. **Structure Map**: Content organization (guides, reference, tutorials)

**For Data Repositories:**
1. **Elevator Pitch**: What data + purpose + consumers
2. **Data Stack Summary**: Databases + pipelines + quality tools
3. **Governance Rules**: Quality standards + access patterns + compliance
4. **Pipeline Commands**: How to run ETL, tests, validations
5. **Structure Map**: Schemas, transformations, quality tests

### Handle Missing Information
If key information is missing:

- **Elevator pitch**: Use generic placeholder or ask user
- **Formatting rules**: Use "Follow existing code style" if inconsistent
- **Build commands**: Omit section if none found
- **Test directory**: Check both `tests/` and `test/` before giving up

### Apply Context Economics
Before generating final instructions:

- Keep under 1000 lines total
- Move framework-specific rules to path instructions
- Use positive constraints (see `positive_constraints_patterns.md`)
- No hardcoded secrets or credentials

---

## Output Format

Use the template from `references/instruction_template.md` and populate all {{placeholders}} with discovered values.

**If a value cannot be determined:** Use "Not specified" or "Follow existing code patterns" rather than leaving placeholder text.
