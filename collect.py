#!/usr/bin/env python3
"""Collect GitHub commit digests and save to file."""

import argparse
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

GITHUB_API = "https://api.github.com"

CATEGORY_MAP = {
    "feat": "Added",
    "fix": "Fixed",
    "breaking": "Breaking",
}


def load_config(path: str) -> list[dict]:
    repos = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                print(f"[warn] skipping malformed line: {line!r}", file=sys.stderr)
                continue
            slug = parts[0]
            name = parts[1]
            tags = [t.strip() for t in parts[2].split(",")] if len(parts) > 2 else []
            repos.append({"slug": slug, "name": name, "tags": tags})
    return repos


def github_get(url: str, token: str, params: dict = None) -> list | dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    results = []
    page = 1
    while True:
        p = {"per_page": 100, "page": page, **(params or {})}
        resp = requests.get(url, headers=headers, params=p, timeout=30)
        if resp.status_code == 403:
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(1, reset - int(time.time()))
            print(f"[rate-limit] sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            results.extend(data)
            if len(data) < 100:
                break
            page += 1
        else:
            return data
    return results


def categorize(message: str) -> str:
    lower = message.lower()
    if "breaking change" in lower or "!" in message.split(":")[0]:
        return "Breaking"
    prefix = message.split(":")[0].split("(")[0].lower()
    return CATEGORY_MAP.get(prefix, "Changed")


def fetch_commits(slug: str, since: datetime, token: str) -> list[dict]:
    url = f"{GITHUB_API}/repos/{slug}/commits"
    raw = github_get(url, token, params={"since": since.isoformat()})
    commits = []
    for item in raw:
        full_msg = item.get("commit", {}).get("message", "")
        subject = full_msg.splitlines()[0]
        body = full_msg[len(subject):].strip()
        sha = item.get("sha", "")[:7]
        html_url = item.get("html_url", "")
        commits.append({"sha": sha, "subject": subject, "body": body, "url": html_url, "category": categorize(subject)})
    return commits


def build_digest(repos: list[dict], days: int, token: str) -> str:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# Dev Updates — {today}", f"_Last {days} days_", ""]

    any_content = False
    for repo in repos:
        commits = fetch_commits(repo["slug"], since, token)
        if not commits:
            continue
        any_content = True
        tags = f" `{'` `'.join(repo['tags'])}`" if repo["tags"] else ""
        lines.append(f"## {repo['name']}{tags}")
        lines.append(f"<https://github.com/{repo['slug']}/commits>")
        lines.append("")

        categorized: dict[str, list] = {}
        for c in commits:
            categorized.setdefault(c["category"], []).append(c)

        for cat in ("Breaking", "Added", "Fixed", "Changed"):
            if cat not in categorized:
                continue
            lines.append(f"### {cat}")
            for c in categorized[cat]:
                lines.append(f"- [`{c['sha']}`]({c['url']}) {c['subject']}")
                if c["body"]:
                    for body_line in c["body"].splitlines():
                        lines.append(f"  {body_line}")
            lines.append("")

    if not any_content:
        lines.append("_No commits found in this period._")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Collect GitHub digest and save to file.")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    parser.add_argument("--config", default="config.txt", help="Path to config file (default: config.txt)")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    args = parser.parse_args()

    gh_token = os.environ.get("GH_TOKEN")
    if not gh_token:
        print("[error] GH_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    repos = load_config(args.config)
    if not repos:
        print("[warn] no repos configured, exiting", file=sys.stderr)
        sys.exit(0)

    print(f"Collecting commits from {len(repos)} repo(s) over the last {args.days} day(s)…", file=sys.stderr)
    digest = build_digest(repos, args.days, gh_token)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = out_dir / f"digest-{today}.md"
    out_path.write_text(digest, encoding="utf-8")
    print(f"[saved] {out_path}", file=sys.stderr)

    print(digest)


if __name__ == "__main__":
    main()
