# Spread Task Matrix Hierarchy & Selector Guide

Spread organizes execution environments and task suites into a multi-dimensional matrix. This guide teaches agents how to inspect `spread.yaml` using `yq` and `find` to discover available **Backends**, **Systems**, and **Suites**, how tasks and variants are structured, and how to select them using Spread's selector syntax.

---

## 1. Inspecting `spread.yaml` with `yq` & `find`

Rather than parsing large `spread.yaml` files manually, agents should use the following commands to inspect matrix components.

### Discover Backends

List all virtualization/cloud backends defined in the repository:

```bash
yq '.backends | keys | .[]' spread.yaml
```

*Example Output:*

```text
openstack
multipass
lxd
```

---

### Discover Systems

#### 1. List systems configured for a specific backend

```bash
# Replace <backend> with the target backend (e.g. openstack, multipass, lxd)
yq '.backends.<backend>.systems[] | (keys | .[0]) // .' spread.yaml
```

*Example Output:*

```text
ubuntu-20.04-64
ubuntu-22.04-64
ubuntu-24.04-64
```

#### 2. List all unique systems across all backends

```bash
yq '[.backends.[].systems[] | (keys | .[0]) // .] | unique | .[]' spread.yaml
```

---

### Discover Suites

#### 1. List all suites in the project

```bash
yq '.suites | keys | .[]' spread.yaml
```

*Example Output:*

```text
tests/spread/commands/
tests/spread/dependencies/
tests/spread/smoketests/
```

> [!NOTE]
> Suite names in `spread.yaml` and selectors must end with a trailing slash (`/`).

#### 2. List suites along with their summaries

```bash
yq '.suites | to_entries | .[] | .key + "\t(" + (.value.summary // "no summary") + ")"' spread.yaml
```

#### 3. List manual suites (suites excluded from default matrix runs)

```bash
yq '.suites | to_entries | .[] | select(.value.manual == true) | .key' spread.yaml
```

#### 4. Check system constraints for a specific suite

```bash
yq '.suites."tests/spread/dependencies/".systems[]' spread.yaml
```

---

### Discover Tasks and Variants

- **Tasks**: Use `find` with `-printf '%h\n'` to print the directory paths containing `task.yaml` without invoking subprocesses:

  ```bash
  # List all task directories inside a suite
  find tests/spread/commands/ -name "task.yaml" -printf '%h\n'

  # Or list all task directories in the entire repository
  find . -name "task.yaml" -printf '%h\n'
  ```

- **Manual Tasks**: Tasks can have `manual: true` in their `task.yaml`. Check if a task is marked manual:

  ```bash
  yq '.manual // false' tests/spread/commands/version/task.yaml
  ```

- **Variants**: Read the task's `task.yaml` file to extract variants defined under `environment:` or `variants:`:

  ```bash
  # Find variants defined via environment keys containing '/'
  yq '.environment | keys | .[] | select(. == "*/*")' tests/spread/commands/init-extensions/task.yaml

  # Or find variants defined explicitly in a variants block
  yq '.variants | keys | .[]' tests/spread/commands/init-extensions/task.yaml
  ```
  
  > [!TIP]
  > Tasks may use either format. If one `yq` command returns empty, try the other to ensure no variants are missed.

---

### Manual Suites & Tasks (`manual: true`)

Spread supports marking both entire suites and individual tasks as **manual**:

1. **Manual Suites (`suites.<suite>.manual: true` in `spread.yaml`)**:
   - **Behavior**: Excluded from default runs (e.g. running `spread -list` with no arguments or running broad wildcard selectors).
   - **Execution**: To run tasks in a manual suite, the suite (or task within it) **must be explicitly specified** by name:
     ```bash
     spread -list docs/howto/code/
     spread docs/howto/code/
     ```

2. **Manual Tasks (`manual: true` in `task.yaml`)**:
   - **Behavior**: Excluded when running the parent suite (e.g. `spread tests/spread/commands/` will skip any task inside `commands/` that has `manual: true`).
   - **Execution**: To run a manual task, you **must target the specific task explicitly**:
     ```bash
     spread -list tests/spread/commands/expensive-task
     spread tests/spread/commands/expensive-task
     ```

---

### System & Backend Constraints

Suites and tasks can restrict which systems and backends they run on using `systems:` and `backends:` lists:

- **Inclusion list**: Only matching systems/backends will execute (e.g. `systems: [ubuntu-22.04-64, ubuntu-24.04-64]`).
- **Exclusion syntax (`-` prefix)**: Specific systems can be excluded from the matrix (e.g. `systems: [-ubuntu-18.04-64]`).

#### 1. Checking Suite Constraints

```bash
# Check if a suite restricts systems
yq '.suites."tests/spread/dependencies/".systems // []' spread.yaml

# Check if a suite restricts backends
yq '.suites."tests/spread/dependencies/".backends // []' spread.yaml
```

#### 2. Checking Task Constraints

```bash
# Check if a specific task restricts systems
yq '.systems // []' tests/spread/commands/version/task.yaml

# Check if a specific task restricts backends
yq '.backends // []' tests/spread/commands/version/task.yaml
```

> [!NOTE]
> If `spread -list <selector>` returns `error: nothing matches provider filter`, check whether suite or task constraints excluded your target system or backend.

---

## 2. The Matrix Hierarchy Summary

```text
Backend (e.g., lxd, openstack, multipass)
└── System (e.g., ubuntu-24.04-64, ubuntu-22.04)
    └── Suite (e.g., tests/spread/commands/)
        └── Task (e.g., tests/spread/commands/version)
            └── Variant (e.g., flask, django)
```

| Dimension | Description | Defined In | How to Select |
|---|---|---|---|
| **Backend** | Virtualization / cloud infrastructure provider. | `backends:` in `spread.yaml` | `<backend>:` (e.g. `openstack:`) |
| **System** | Target OS image or machine spec. | `backends.<backend>.systems` | `:<system>:` or `ubuntu-24.04-64:` |
| **Suite** | Group of tasks with shared lifecycle hooks (`prepare`, `restore`, etc.). | `suites:` in `spread.yaml` (**must end in `/`**) | `<suite>/` or `<suite>/...` |
| **Task** | Executable task containing `task.yaml`. | Directory containing `task.yaml` | `<suite>/<task>` (no trailing slash) |
| **Variant** | Parameter variation of a task. | `environment: KEY/variant: val` in `task.yaml` | `:<variant>` or `<task>:<variant>` |

---

## 3. Selector Syntax & Grammar

The complete selector syntax is:

```text
[<backend>]:[<system>]:[<task-or-suite-path>][:<variant>]
```

### Syntax Rules

1. **Colons (`:`)**: Delimit matrix dimensions (`backend:system:task-path:variant`).
2. **No Consecutive Colons (`::`)**: Consecutive colons (like `::`) are invalid in Spread. To omit intermediate dimensions, use shorthand names or wildcard `...` syntax.
3. **Paths Use Forward Slashes (`/`)**: Paths are filesystem directory paths relative to the project root.
4. **Suites vs. Tasks**:
   - `tests/spread/commands/` → Targets the entire suite (must end with `/` or `...`).
   - `tests/spread/commands/version` → Targets the specific task.

---

## 4. Selector Matching Examples (using `spread -list`)

```text
<backend>:<system>:<task-path>[:<variant>]
```

> [!NOTE]
> If `spread -list` returns successfully but produces **zero lines of output**, it means your selector matched tasks, but all matched tasks were marked `manual: true`. You must target them explicitly by name.

### Examples

#### Selecting by Backend

```bash
# Preview all jobs configured on OpenStack
spread -list openstack:

# Preview all jobs configured on Multipass
spread -list multipass:
```

#### Selecting by System

```bash
# Preview all jobs on Ubuntu 24.04 across all backends
spread -list :ubuntu-24.04-64:
# Or shorthand:
spread -list ubuntu-24.04-64:

# Preview all jobs on Ubuntu 24.04 on OpenStack only
spread -list openstack:ubuntu-24.04-64:
```

#### Selecting by Suite (Must End with `/`)

```bash
# Preview an entire suite across all backends & systems (trailing '/' is required)
spread -list tests/spread/commands/
# Or with wildcard:
spread -list tests/spread/commands/...

# Preview a suite on a specific backend and system
spread -list openstack:ubuntu-24.04-64:tests/spread/commands/
```

#### Selecting by Task

```bash
# Preview a single task across all backends and systems
spread -list tests/spread/commands/version

# Preview a single task on a specific backend and system
spread -list openstack:ubuntu-24.04-64:tests/spread/commands/version
```

#### Selecting by Variant

```bash
# Preview a specific variant of a task
spread -list tests/spread/commands/init-extensions:flask

# Preview a specific variant on a specific backend and system
spread -list openstack:ubuntu-22.04-64:tests/spread/commands/init-extensions:flask

# Preview all tasks that define the 'flask' variant across the project
spread -list :flask
```

#### Wildcard Matching (`...`)

```bash
# Match all Ubuntu systems on OpenStack
spread -list openstack:ubuntu-...:

# Match all tasks containing 'smoke' in any suite
spread -list ...smoke...

# Match all tasks under a directory structure
spread -list openstack:...:tests/spread/...
```

#### Multiple Selectors (Union)

```bash
# Select a single task and an entire separate suite together
spread -list tests/spread/commands/version tests/spread/smoketests/

# Select two systems
spread -list :ubuntu-22.04-64: :ubuntu-24.04-64:
```
