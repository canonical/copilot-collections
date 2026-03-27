#!/usr/bin/env python3
"""Fetch GitHub context for a PR/issue URL with strict validation and clear errors."""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print(
        "ERROR: Missing Python dependency 'requests'. Install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(2)

GITHUB_API = "https://api.github.com"


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def parse_github_url(url: str):
    parsed = urlparse(url)
    if parsed.netloc not in {"github.com", "www.github.com"}:
        fail("Unsupported GitHub host. Use a github.com issue/PR URL.")

    path = parsed.path.strip("/")
    m = re.match(r"^([^/]+)/([^/]+)/(pull|issues)/(\d+)$", path)
    if not m:
        fail(
            "Unsupported GitHub URL format. Expected: https://github.com/<owner>/<repo>/(pull|issues)/<number>"
        )

    owner, repo, kind, number = m.group(1), m.group(2), m.group(3), int(m.group(4))
    return owner, repo, kind, number


def pick_token() -> str:
    for var in ("GITHUB_READ_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        v = os.environ.get(var, "").strip()
        if v:
            return v
    fail(
        "Missing GitHub token. Set one of: GITHUB_READ_TOKEN, GITHUB_TOKEN, or GH_TOKEN."
    )


def gh_api_fallback(endpoint: str):
    if shutil.which("gh") is None:
        return None, "GitHub CLI ('gh') not installed."

    cmd = ["gh", "api", endpoint]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "unknown gh error").strip()
        return None, f"gh api failed: {err}"
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError:
        return None, "gh api returned non-JSON output."


def fetch_endpoint(
    endpoint: str,
    headers: Dict[str, str],
    *,
    required: bool = False,
    prefer_gh: bool = False,
) -> Tuple[Optional[Any], bool]:
    ep = endpoint.lstrip("/")

    if prefer_gh:
        gh_data, gh_err = gh_api_fallback(ep)
        if gh_data is not None:
            return gh_data, True
        if required:
            fail(f"GitHub data fetch failed via gh api for '{ep}': {gh_err}")
        return None, True

    resp = requests.get(f"{GITHUB_API}/{ep}", headers=headers, timeout=30)
    if resp.status_code == 200:
        return resp.json(), False
    if resp.status_code == 401 and required:
        fail("GitHub authentication failed (401). Check your token validity.")
    if resp.status_code == 403 and required:
        fail("GitHub access denied or rate-limited (403). Verify token scopes and API limits.")
    if resp.status_code == 404:
        gh_data, gh_err = gh_api_fallback(ep)
        if gh_data is not None:
            return gh_data, True
        if required:
            fail(
                "GitHub resource not found (404) with token auth. "
                "This often means missing private-repo visibility or org SSO authorization. "
                f"Also attempted gh fallback: {gh_err}"
            )
        return None, False
    if required:
        fail(f"GitHub API error {resp.status_code} for '{ep}': {resp.text[:300]}")
    return None, False


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch GitHub PR/issue context")
    parser.add_argument("--url", required=True, help="GitHub PR/issue URL")
    parser.add_argument("--output", required=True, help="Output markdown file")
    args = parser.parse_args()

    token = pick_token()

    owner, repo, kind, number = parse_github_url(args.url)

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
    }

    if kind == "pull":
        endpoint = f"repos/{owner}/{repo}/pulls/{number}"
        issue_endpoint = f"repos/{owner}/{repo}/issues/{number}"
        comments_endpoint = f"repos/{owner}/{repo}/issues/{number}/comments"
        files_endpoint = f"repos/{owner}/{repo}/pulls/{number}/files"
    else:
        endpoint = f"repos/{owner}/{repo}/issues/{number}"
        issue_endpoint = endpoint
        comments_endpoint = f"repos/{owner}/{repo}/issues/{number}/comments"
        files_endpoint = None

    data, used_gh = fetch_endpoint(endpoint, headers, required=True)
    issue_data, _ = fetch_endpoint(issue_endpoint, headers, required=False, prefer_gh=used_gh)
    comments_data, _ = fetch_endpoint(
        comments_endpoint, headers, required=False, prefer_gh=used_gh
    )
    files_data = None
    if files_endpoint:
        files_data, _ = fetch_endpoint(files_endpoint, headers, required=False, prefer_gh=used_gh)

    title = data.get("title", "(no title)")
    state = data.get("state", "unknown")
    author = (data.get("user") or {}).get("login", "unknown")
    created_at = data.get("created_at", "")
    updated_at = data.get("updated_at", "")
    body = data.get("body") or ((issue_data or {}).get("body") if isinstance(issue_data, dict) else "") or ""
    labels = []
    if isinstance(issue_data, dict):
        labels = [x.get("name", "") for x in (issue_data.get("labels") or []) if isinstance(x, dict)]
    elif isinstance(data, dict):
        labels = [x.get("name", "") for x in (data.get("labels") or []) if isinstance(x, dict)]

    requested_reviewers = [x.get("login", "") for x in (data.get("requested_reviewers") or []) if isinstance(x, dict)]
    assignees = [x.get("login", "") for x in (data.get("assignees") or []) if isinstance(x, dict)]

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"# GitHub Context\n\n")
        f.write(f"- Source URL: {args.url}\n")
        f.write(f"- Retrieved At (UTC): {dt.datetime.now(dt.timezone.utc).isoformat()}\n")
        f.write(f"- Repository: {owner}/{repo}\n")
        f.write(f"- Kind: {kind}\n")
        f.write(f"- Number: {number}\n\n")
        f.write(f"## Metadata\n")
        f.write(f"- Title: {title}\n")
        f.write(f"- State: {state}\n")
        f.write(f"- Author: {author}\n")
        f.write(f"- Created: {created_at}\n")
        f.write(f"- Updated: {updated_at}\n\n")
        f.write(f"- Labels: {', '.join([x for x in labels if x])}\n")
        f.write(f"- Assignees: {', '.join([x for x in assignees if x])}\n")
        if kind == "pull":
            f.write(f"- Requested Reviewers: {', '.join([x for x in requested_reviewers if x])}\n")
        f.write("\n")
        f.write("## Body\n")
        if body.strip():
            f.write(body.strip() + "\n")
        else:
            f.write("_No body text provided on this PR/issue._\n")

        if isinstance(files_data, list):
            f.write("\n## Changed Files\n")
            f.write(f"- Count: {len(files_data)}\n")
            for item in files_data[:50]:
                filename = item.get("filename", "")
                status = item.get("status", "")
                additions = item.get("additions", 0)
                deletions = item.get("deletions", 0)
                f.write(f"- `{filename}` ({status}, +{additions}/-{deletions})\n")

        if isinstance(comments_data, list) and comments_data:
            f.write("\n## Issue Comments\n")
            f.write(f"- Count: {len(comments_data)}\n")
            for c in comments_data[:10]:
                user = (c.get("user") or {}).get("login", "unknown")
                created = c.get("created_at", "")
                text = (c.get("body") or "").strip().replace("\n", " ")
                if len(text) > 300:
                    text = text[:300] + "..."
                f.write(f"- {user} ({created}): {text}\n")

    print(f"OK: GitHub context written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
