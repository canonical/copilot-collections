#!/usr/bin/env python3
"""Fetch Mattermost thread context with strict prerequisite checks."""

import argparse
import datetime as dt
import os
import re
import sys
from typing import Dict, List
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


def parse_thread_id(thread: str) -> str:
    m = re.search(r"/pl/([a-z0-9]+)", thread)
    if m:
        return m.group(1)
    if re.fullmatch(r"[a-z0-9]+", thread):
        return thread
    fail(
        "Invalid Mattermost thread input. Use a thread URL containing /pl/<id> or a raw post/thread id."
    )


def api_get(mm_url: str, token: str, endpoint: str) -> Dict:
    url = f"{mm_url.rstrip('/')}/api/v4/{endpoint.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 401:
        fail("Mattermost authentication failed (401). Check MM_TOKEN validity.")
    if resp.status_code == 403:
        fail("Mattermost access forbidden (403). Verify MM_TOKEN permissions.")
    if resp.status_code == 404:
        fail(f"Mattermost endpoint not found (404): {endpoint}")
    if resp.status_code != 200:
        fail(f"Mattermost API error {resp.status_code} for '{endpoint}': {resp.text[:300]}")
    return resp.json()


def ensure_mm_url_matches(thread: str, mm_url: str) -> None:
    if not thread.startswith("http"):
        return
    parsed_thread = urlparse(thread)
    parsed_mm = urlparse(mm_url)
    if parsed_thread.netloc and parsed_mm.netloc and parsed_thread.netloc != parsed_mm.netloc:
        fail(
            f"Thread host '{parsed_thread.netloc}' does not match MM_URL host '{parsed_mm.netloc}'. "
            "Set MM_URL to the correct Mattermost host."
        )


def format_timestamp(ms: int) -> str:
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def extract_text(value: str) -> str:
    return value.strip() if isinstance(value, str) else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Mattermost thread context")
    parser.add_argument("--thread", required=True, help="Mattermost thread URL or id")
    parser.add_argument("--output", required=True, help="Output markdown file")
    args = parser.parse_args()

    mm_url = os.environ.get("MM_URL", "").strip()
    mm_token = os.environ.get("MM_TOKEN", "").strip()

    if not mm_url:
        fail("Missing MM_URL. Example: export MM_URL='https://chat.canonical.com'")
    if not mm_token:
        fail("Missing MM_TOKEN. Example: export MM_TOKEN='<personal-access-token>'")

    ensure_mm_url_matches(args.thread, mm_url)
    thread_id = parse_thread_id(args.thread)

    post_json = api_get(mm_url, mm_token, f"posts/{thread_id}")
    root_id = post_json.get("root_id") or thread_id
    channel_id = post_json.get("channel_id")
    if not channel_id:
        fail("Mattermost response missing channel_id; cannot resolve channel metadata.")

    channel_json = api_get(mm_url, mm_token, f"channels/{channel_id}")
    channel_name = channel_json.get("display_name") or channel_json.get("name") or "unknown-channel"

    thread_json = api_get(mm_url, mm_token, f"posts/{root_id}/thread")
    posts_map = thread_json.get("posts") or {}
    order: List[str] = thread_json.get("order") or []
    if not order:
        fail("Mattermost thread response returned no posts in 'order'.")

    user_cache: Dict[str, str] = {}

    def username_for(user_id: str) -> str:
        if user_id in user_cache:
            return user_cache[user_id]
        user_json = api_get(mm_url, mm_token, f"users/{user_id}")
        username = user_json.get("username") or user_id
        user_cache[user_id] = username
        return username

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("# Mattermost Context\n\n")
        f.write(f"- Source Thread: {args.thread}\n")
        f.write(f"- Retrieved At (UTC): {dt.datetime.now(dt.timezone.utc).isoformat()}\n")
        f.write(f"- Channel: {channel_name}\n")
        f.write(f"- Thread Link: {mm_url.rstrip('/')}/_redirect/pl/{root_id}\n\n")
        f.write("---\n\n")

        for post_id in order:
            post = posts_map.get(post_id)
            if not post:
                continue

            user_id = str(post.get("user_id") or "").strip()
            if not user_id:
                continue

            username = username_for(user_id)
            created = post.get("create_at")
            if not isinstance(created, int):
                continue

            text = extract_text(post.get("message", ""))
            if not text:
                continue

            f.write(f"### {username} — {format_timestamp(created)}\n\n")
            f.write(text + "\n\n")

    print(f"OK: Mattermost context written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
