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
            repos.append({"slug": slug, "name": name})
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


def extract_author(item: dict) -> str:
    """Return display name for external human contributors; empty string otherwise."""
    author_info = item.get("author") or {}
    login = author_info.get("login", "")
    if (
        not login
        or author_info.get("type") != "User"
        or login.endswith("[bot]")
        or login.lower() == "valeriogalano"
    ):
        return ""
    name = item.get("commit", {}).get("author", {}).get("name", "").strip()
    return name or login


def fetch_commits(slug: str, since: datetime, token: str, until: datetime = None) -> list[dict]:
    url = f"{GITHUB_API}/repos/{slug}/commits"
    params = {"since": since.isoformat()}
    if until:
        params["until"] = until.isoformat()
    raw = github_get(url, token, params=params)
    commits = []
    for item in raw:
        full_msg = item.get("commit", {}).get("message", "")
        subject = full_msg.splitlines()[0]
        body = full_msg[len(subject):].strip()
        sha = item.get("sha", "")[:7]
        html_url = item.get("html_url", "")
        commits.append({
            "sha": sha,
            "subject": subject,
            "body": body,
            "url": html_url,
            "category": categorize(subject),
            "author": extract_author(item),
        })
    return commits


def build_digest(repos: list[dict], token: str, since: datetime, until: datetime, append: bool = False) -> str:
    lines = []

    if not append:
        label = until.strftime("%Y-%m-%d")
        delta_days = (until - since).days
        lines += [f"# Dev Updates — {label}", f"_Last {delta_days} days_", ""]

    any_content = False
    for repo in repos:
        commits = fetch_commits(repo["slug"], since, token, until=until)
        if not commits:
            continue
        any_content = True
        lines.append(f"## {repo['name']}")
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
                attribution = f" — by {c['author']}" if c.get("author") else ""
                lines.append(f"- [`{c['sha']}`]({c['url']}) {c['subject']}{attribution}")
                if c["body"]:
                    for body_line in c["body"].splitlines():
                        lines.append(f"  {body_line}")
            lines.append("")

    if not any_content and not append:
        lines.append("_No commits found in this period._")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Collect GitHub digest and save to file.")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    parser.add_argument("--since", help="Start date YYYY-MM-DD (overrides --days)")
    parser.add_argument("--until", help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--append", action="store_true", help="Append repo sections to existing digest file")
    parser.add_argument("--config", default="config.txt", help="Path to config file (default: config.txt)")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    args = parser.parse_args()

    gh_token = os.environ.get("GH_TOKEN")
    if not gh_token:
        print("[error] GH_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc)
    until_dt = datetime.fromisoformat(args.until).replace(tzinfo=timezone.utc) if args.until else now
    if args.since:
        since_dt = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
    else:
        since_dt = until_dt - timedelta(days=args.days)

    repos = load_config(args.config)
    if not repos:
        print("[warn] no repos configured, exiting", file=sys.stderr)
        sys.exit(0)

    print(f"Collecting commits from {len(repos)} repo(s) between {since_dt.date()} and {until_dt.date()}…", file=sys.stderr)
    digest = build_digest(repos, gh_token, since=since_dt, until=until_dt, append=args.append)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"digest-{until_dt.strftime('%Y-%m-%d')}.md"

    if args.append and out_path.exists():
        existing = out_path.read_text(encoding="utf-8")
        out_path.write_text(existing.rstrip("\n") + "\n\n" + digest, encoding="utf-8")
        print(f"[appended] {out_path}", file=sys.stderr)
    else:
        out_path.write_text(digest, encoding="utf-8")
        print(f"[saved] {out_path}", file=sys.stderr)

    print(digest)


if __name__ == "__main__":
    main()
