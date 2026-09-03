#!/usr/bin/env python3
"""keyring_broker.py — resolve-and-inject secret broker for agents/LLMs.

Design goal: an agent (or the LLM driving it) NEVER sees a secret value.
The agent passes a credential *reference* (a name). This trusted, non-LLM
layer resolves the value from the OS keyring, injects it into an outbound
request or a single child process, scrubs the result, and returns ONLY the
scrubbed output plus a status. The secret value is never printed, logged,
or returned.

Two mechanisms:

  (a) request   — PRIMARY. Resolve a named credential, inject it into an
                  HTTP request header, perform the request, scrub the
                  response, and return the scrubbed body. The secret exists
                  only inside this process, only for the duration of the call.

  (b) exec      — DISCOURAGED FALLBACK. For legacy CLIs that can only read a
                  secret from their environment. Inject the resolved value
                  into a SINGLE child process's environment (never the
                  agent's), run one command, scrub its output. Use only when
                  (a) is impossible. Wider exposure: the value lives in the
                  child's /proc/<pid>/environ for the process lifetime.

Secrets are stored in the OS keyring (Keychain / libsecret / Windows
Credential Manager) via the `keyring` library. Store them out-of-band, e.g.:

    keyring set agent-secrets github_token
    keyring set agent-secrets openai_api_key

The agent then references them by name only: `github_token`.

CLI:
    keyring_broker.py request --name github_token \
        --url https://api.github.com/user \
        --header "Authorization: Bearer {secret}"

    keyring_broker.py exec --name aws_secret_access_key \
        --env-var AWS_SECRET_ACCESS_KEY -- aws s3 ls

Exit code 0 on success. The secret value is never emitted on any stream.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import urllib.request

SERVICE = os.environ.get("AGENT_KEYRING_SERVICE", "agent-secrets")

# Names whose VALUES must never be printed back to the agent/LLM.
_SECRET_NAME_RE = re.compile(
    r"(?i)[\w-]*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|AUTH|PASS)$"
)
_ENV_VAR_LINE_RE = re.compile(
    r"(?i)^([\w.-]*(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API_KEY|AUTH)\s*[:=]\s*)\S+",
    re.MULTILINE,
)


def _resolve(name: str) -> str:
    """Fetch a secret value from the OS keyring by reference. Never returned to caller."""
    try:
        import keyring
    except ImportError:
        sys.exit("error: the 'keyring' package is required (pip install keyring)")
    value = keyring.get_password(SERVICE, name)
    if value is None:
        sys.exit(
            f"error: no credential named '{name}' in keyring service '{SERVICE}'. "
            f"Store it with: keyring set {SERVICE} {name}"
        )
    return value


def scrub(text: str, secret: str) -> str:
    """Remove the literal secret and secret-looking VAR=value lines from text."""
    if secret:
        text = text.replace(secret, "[REDACTED]")
        # Defeat trivial transforms that would otherwise slip a value through.
        import base64

        try:
            text = text.replace(base64.b64encode(secret.encode()).decode(), "[REDACTED]")
        except Exception:
            pass
    text = _ENV_VAR_LINE_RE.sub(r"\1[REDACTED]", text)
    return text


def cmd_request(args: argparse.Namespace) -> int:
    """(a) Resolve a named credential and inject it into an HTTP request."""
    secret = _resolve(args.name)
    headers = {}
    for raw in args.header or []:
        if ":" not in raw:
            sys.exit(f"error: malformed --header (want 'Name: value'): {raw!r}")
        key, _, val = raw.partition(":")
        headers[key.strip()] = val.strip().replace("{secret}", secret)

    data = args.data.encode() if args.data else None
    req = urllib.request.Request(
        args.url, data=data, headers=headers, method=args.method
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            body = resp.read().decode(errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        status = e.code
    except Exception as e:
        # Never let an exception echo the injected header/secret.
        sys.exit(f"error: request failed: {type(e).__name__}")

    sys.stdout.write(scrub(body, secret))
    sys.stderr.write(f"[keyring_broker] {args.method} {args.url} -> {status}\n")
    return 0 if status < 400 else 1


def cmd_exec(args: argparse.Namespace) -> int:
    """(b) DISCOURAGED: inject a named credential into one child process's env."""
    secret = _resolve(args.name)
    child_env = {
        k: v for k, v in os.environ.items() if not _SECRET_NAME_RE.search(k)
    }
    child_env[args.env_var] = secret
    try:
        proc = subprocess.run(
            args.command,
            env=child_env,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
    except Exception as e:
        sys.exit(f"error: exec failed: {type(e).__name__}")

    sys.stdout.write(scrub(proc.stdout, secret))
    sys.stderr.write(scrub(proc.stderr, secret))
    return proc.returncode


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="mode", required=True)

    r = sub.add_parser("request", help="(a) inject credential into an HTTP request")
    r.add_argument("--name", required=True, help="credential reference name")
    r.add_argument("--url", required=True)
    r.add_argument(
        "--header",
        action="append",
        help="header 'Name: value'; use {secret} placeholder for the value",
    )
    r.add_argument("--method", default="GET")
    r.add_argument("--data", help="request body (no secrets here)")
    r.add_argument("--timeout", type=float, default=30.0)
    r.set_defaults(func=cmd_request)

    e = sub.add_parser("exec", help="(b) DISCOURAGED: inject credential into a child env")
    e.add_argument("--name", required=True, help="credential reference name")
    e.add_argument("--env-var", required=True, help="env var name to expose to the child")
    e.add_argument("--timeout", type=float, default=120.0)
    e.add_argument("command", nargs=argparse.REMAINDER, help="-- command to run")
    e.set_defaults(func=cmd_exec)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "exec" and args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if args.mode == "exec" and not args.command:
        sys.exit("error: no command given after '--'")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
