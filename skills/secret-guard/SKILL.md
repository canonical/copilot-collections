---
name: secret-guard
description: Lets an agent authenticate to APIs and MCP servers WITHOUT ever seeing secret values. Use whenever a task needs an API token, MCP token, password, or key. The agent passes a credential *reference* (a name); a trusted non-LLM broker resolves it from the OS keyring, injects it into the request, scrubs the response, and returns only scrubbed output. The secret value never enters the agent's context or the LLM.
---

# Secret Guard

## Core Principle

**You never possess a secret value. You only pass references (names).**

A secret must never enter the model's context window. Do not read secret files, do not print values, do not reconstruct them. To authenticate, you emit a credential *reference* by name and let a trusted, non-LLM broker resolve→inject→scrub. This is architectural, not advisory: the value stays inside the broker process and is never returned to you.

Secrets live in the **OS keyring** (Keychain / libsecret / Windows Credential Manager). They are stored out-of-band by a human, e.g.:

```
keyring set agent-secrets github_token
keyring set agent-secrets openai_api_key
```

You reference them by name only — e.g. `github_token`. You never see the value.

---

## Mechanism (a): Resolve-and-Inject — PRIMARY

Use this for **all API and MCP token** use. The broker resolves the named
credential, injects it into the request header, performs the call, scrubs the
response, and returns only the scrubbed body. The secret exists only inside the
broker process for the duration of one request.

```bash
python3 scripts/keyring_broker.py request \
    --name github_token \
    --url https://api.github.com/user \
    --header "Authorization: Bearer {secret}"
```

- `--name` is a **reference**, never a value.
- `{secret}` is a placeholder the broker fills internally; you never type the token.
- Output is scrubbed before you see it.

**For MCP servers:** put the credential in the **MCP server's** environment/config,
resolved by the client runtime — never in tool arguments, conversation, or files.
Prefer OAuth flows where the server holds the token and the client gets a
short-lived, scoped handle. Use `${input:...}`/env indirection so no literal
appears in committed config.

---

## Mechanism (b): Env-Injecting Exec — DISCOURAGED FALLBACK

Only when a legacy CLI can read a credential **solely** from its environment and
(a) is impossible. The broker injects the value into a **single child process's**
environment (never yours), runs one command, and scrubs its output.

```bash
python3 scripts/keyring_broker.py exec \
    --name aws_secret_access_key \
    --env-var AWS_SECRET_ACCESS_KEY \
    -- aws s3 ls
```

**Why discouraged:** the value lives in the child's `/proc/<pid>/environ` for the
process lifetime and is exposed to any subprocess it spawns and to verbose/debug
output you cannot fully control. Scope it to one invocation; never persist it;
never export it into your own shell.

---

## Never-Do (hard rules)

- ❌ Read `.env`, `.env.*`, `.netrc`, `.npmrc`, `.pypirc`, `*.pem`, `*.key`, `id_rsa`, `credentials`, `kubeconfig`, `.git-credentials`, or any `*secret*`/`*credential*`/`*password*` file to "get the token". Decline and use the broker.
- ❌ Ask the user to paste a secret into the conversation.
- ❌ Put a secret in a tool argument, URL query string, commit, log, or file.
- ❌ Echo, encode, or transform a value to move it past scrubbing.
- ❌ Export a resolved secret into your own environment or a persistent shell.

## Always-Do

- ✅ Reference credentials by **name**; let the broker resolve them.
- ✅ Prefer mechanism (a); treat (b) as a last resort scoped to one command.
- ✅ Use **short-lived, narrowly-scoped** tokens so any leak has minimal blast radius.
- ✅ Rely on the broker's scrubbing for all returned output.
- ✅ If a secret is unavoidable and no keyring entry exists, ask the user to run
     `keyring set agent-secrets <name>` themselves — never handle the value yourself.

---

## Defense in Depth (environment expectations)

These are enforced outside the model and assumed by this skill:

- The agent process runs with a **sanitized environment** (no secret env vars).
- An **egress allowlist** limits where tokens can be sent.
- Every credential **use** is audited **by name** — values are never logged.

## Reference Implementation

`scripts/keyring_broker.py` implements both mechanisms. The secret value is never
written to stdout/stderr, never logged, and never returned to the caller.
