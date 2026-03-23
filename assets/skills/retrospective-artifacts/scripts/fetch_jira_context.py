#!/usr/bin/env python3
"""Fetch Jira issue context from an issue URL with strict prerequisite checks."""

import argparse
import datetime as dt
import os
import re
import sys
from typing import Any, Dict, List
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print(
        "ERROR: Missing Python dependency 'requests'. Install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(2)


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _render_marks(text: str, marks: List[Dict[str, Any]]) -> str:
    out = text
    for mark in marks or []:
        mtype = mark.get("type")
        if mtype == "code":
            out = f"`{out}`"
        elif mtype == "link":
            href = (mark.get("attrs") or {}).get("href", "").strip()
            if href:
                out = f"[{out}]({href})"
    return out


def _render_adf_inline(node: Dict[str, Any]) -> str:
    ntype = node.get("type")
    if ntype == "text":
        return _render_marks(node.get("text", ""), node.get("marks", []))
    if ntype == "hardBreak":
        return "\n"
    if ntype == "inlineCard":
        url = (node.get("attrs") or {}).get("url", "").strip()
        return url if url else ""
    if ntype == "emoji":
        return (node.get("attrs") or {}).get("text", "")
    return ""


def _render_adf_block(node: Dict[str, Any], depth: int = 0) -> str:
    ntype = node.get("type")
    content = node.get("content", []) or []

    if ntype == "paragraph":
        text = "".join(_render_adf_inline(c) for c in content).strip()
        return text + "\n\n" if text else "\n"

    if ntype == "heading":
        level = int((node.get("attrs") or {}).get("level", 2))
        level = max(1, min(level, 6))
        text = "".join(_render_adf_inline(c) for c in content).strip()
        return f"{'#' * level} {text}\n\n" if text else ""

    if ntype == "codeBlock":
        code = "".join((c.get("text", "") if isinstance(c, dict) else "") for c in content)
        return f"```\n{code.rstrip()}\n```\n\n"

    if ntype == "bulletList":
        lines: List[str] = []
        for item in content:
            if item.get("type") != "listItem":
                continue
            item_text = _render_adf_block(item, depth + 1).strip()
            if item_text:
                indent = "  " * depth
                lines.append(f"{indent}- {item_text}")
        return "\n".join(lines) + ("\n\n" if lines else "")

    if ntype == "orderedList":
        lines = []
        idx = 1
        for item in content:
            if item.get("type") != "listItem":
                continue
            item_text = _render_adf_block(item, depth + 1).strip()
            if item_text:
                indent = "  " * depth
                lines.append(f"{indent}{idx}. {item_text}")
                idx += 1
        return "\n".join(lines) + ("\n\n" if lines else "")

    if ntype == "listItem":
        parts = []
        for c in content:
            parts.append(_render_adf_block(c, depth))
        joined = " ".join(p.strip() for p in parts if p.strip()).strip()
        return joined

    if ntype == "doc":
        return "".join(_render_adf_block(c, depth) for c in content)

    return ""


def render_jira_description(description: Any) -> str:
    if isinstance(description, str):
        return description.strip()
    if isinstance(description, dict):
        rendered = _render_adf_block(description).strip()
        return rendered if rendered else str(description)
    return ""


def parse_issue_key(url: str) -> str:
    parsed = urlparse(url)
    m = re.search(r"/browse/([A-Z][A-Z0-9]+-\d+)", parsed.path)
    if not m:
        fail("Unsupported Jira URL format. Expected: https://<domain>.atlassian.net/browse/PROJ-123")
    return m.group(1)


def make_headers() -> dict:
    jira_user = os.environ.get("JIRA_USERNAME", "").strip()
    jira_read = os.environ.get("JIRA_READ_TOKEN", "").strip()
    jira_full = os.environ.get("JIRA_FULL_ACCESS_TOKEN", "").strip()

    if jira_full:
        if jira_full.startswith("ATAT"):
            if not jira_user:
                fail("JIRA_FULL_ACCESS_TOKEN looks like API token; set JIRA_USERNAME as account email.")
            import base64

            b64 = base64.b64encode(f"{jira_user}:{jira_full}".encode()).decode()
            return {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Basic {b64}",
            }
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jira_full}",
        }

    if jira_user and jira_read:
        import base64

        b64 = base64.b64encode(f"{jira_user}:{jira_read}".encode()).decode()
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {b64}",
        }

    fail(
        "Missing Jira auth. Set either JIRA_FULL_ACCESS_TOKEN, or JIRA_USERNAME + JIRA_READ_TOKEN."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Jira issue context")
    parser.add_argument("--url", required=True, help="Jira issue URL")
    parser.add_argument("--output", required=True, help="Output markdown file")
    parser.add_argument(
        "--raw-description",
        action="store_true",
        help="Write Jira description as raw JSON/string instead of rendered text",
    )
    args = parser.parse_args()

    jira_url = os.environ.get("JIRA_URL", "").strip()
    if not jira_url:
        fail("Missing JIRA_URL. Example: export JIRA_URL='https://your-domain.atlassian.net'")

    key = parse_issue_key(args.url)
    headers = make_headers()

    issue_endpoint = jira_url.rstrip("/") + f"/rest/api/3/issue/{key}"
    params = {
        "fields": "summary,status,description,issuetype,priority,assignee,reporter,created,updated,resolutiondate,labels"
    }

    resp = requests.get(issue_endpoint, headers=headers, params=params, timeout=30)

    if resp.status_code == 401:
        fail("Jira authentication failed (401). Check token/username configuration.")
    if resp.status_code == 403:
        fail("Jira access forbidden (403). Verify project permissions and token scopes.")
    if resp.status_code == 404:
        fail("Jira issue not found (404). Verify issue URL/key and visibility.")
    if resp.status_code != 200:
        fail(f"Jira API error {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    fields = data.get("fields", {})

    summary = fields.get("summary", "(no summary)")
    status = (fields.get("status") or {}).get("name", "unknown")
    issue_type = (fields.get("issuetype") or {}).get("name", "unknown")
    priority = (fields.get("priority") or {}).get("name", "unknown")
    assignee = ((fields.get("assignee") or {}).get("displayName") or "unassigned")
    reporter = ((fields.get("reporter") or {}).get("displayName") or "unknown")

    description = fields.get("description")
    if args.raw_description:
        if isinstance(description, str):
            description_text = description
        else:
            import json

            description_text = json.dumps(description, ensure_ascii=False, indent=2)
    else:
        description_text = render_jira_description(description)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("# Jira Context\n\n")
        f.write(f"- Source URL: {args.url}\n")
        f.write(f"- Retrieved At (UTC): {dt.datetime.now(dt.timezone.utc).isoformat()}\n")
        f.write(f"- Issue Key: {key}\n\n")
        f.write("## Metadata\n")
        f.write(f"- Summary: {summary}\n")
        f.write(f"- Status: {status}\n")
        f.write(f"- Type: {issue_type}\n")
        f.write(f"- Priority: {priority}\n")
        f.write(f"- Assignee: {assignee}\n")
        f.write(f"- Reporter: {reporter}\n")
        f.write(f"- Created: {fields.get('created', '')}\n")
        f.write(f"- Updated: {fields.get('updated', '')}\n")
        f.write(f"- Resolution Date: {fields.get('resolutiondate', '')}\n")
        f.write(f"- Labels: {', '.join(fields.get('labels') or [])}\n\n")
        if args.raw_description:
            f.write("## Description (raw)\n")
        else:
            f.write("## Description\n")
        f.write(description_text.strip() + "\n")

    print(f"OK: Jira context written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
