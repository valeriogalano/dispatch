#!/usr/bin/env python3
"""Collect GitHub commit digests and save to file."""

import argparse
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# ponytail: Codeberg (Forgejo) API is GitHub-compatible for the endpoints we use;
# tokens are only sent to GitHub, Codeberg repos must be public.
HOSTS = {
    "github": {"api": "https://api.github.com", "web": "https://github.com", "page_size": 100},
    "codeberg": {"api": "https://codeberg.org/api/v1", "web": "https://codeberg.org", "page_size": 50},
}

NO_COMMITS_MARKER = "_No commits found in this period._"
MANUAL_HEADING = "## Manual updates"

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
            host = "github"
            if ":" in slug:
                host, slug = slug.split(":", 1)
                if host not in HOSTS:
                    print(f"[warn] skipping unknown host in line: {line!r}", file=sys.stderr)
                    continue
            name = parts[1]
            link = parts[2] if len(parts) >= 3 else None
            repos.append({"slug": slug, "name": name, "link": link, "host": host})
    return repos


def api_get(url: str, token: str | None, params: dict = None, page_size: int = 100) -> list | dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    results = []
    page = 1
    while True:
        # per_page is GitHub's param, limit is Forgejo's; each API ignores the other
        p = {"per_page": page_size, "limit": page_size, "page": page, **(params or {})}
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
            if len(data) < page_size:
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


def repo_host(repo: dict) -> dict:
    return HOSTS[repo.get("host", "github")]


def repo_token(repo: dict, token: str) -> str | None:
    return token if repo.get("host", "github") == "github" else None


def is_repo_public(repo: dict, token: str) -> bool:
    host = repo_host(repo)
    url = f"{host['api']}/repos/{repo['slug']}"
    data = api_get(url, repo_token(repo, token), page_size=host["page_size"])
    if isinstance(data, dict):
        return not data.get("private", True)
    return False


def fetch_commits(repo: dict, since: datetime, token: str, until: datetime = None) -> list[dict]:
    host = repo_host(repo)
    url = f"{host['api']}/repos/{repo['slug']}/commits"
    params = {"since": since.isoformat()}
    if until:
        params["until"] = until.isoformat()
    raw = api_get(url, repo_token(repo, token), params=params, page_size=host["page_size"])
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


def repo_url(repo: dict) -> str:
    return f"{repo_host(repo)['web']}/{repo['slug']}"


def load_manual_entries(manual_dir: str, since: datetime, until: datetime) -> list[str]:
    """Read manual notes for things done outside git, one file per day: manual/YYYY-MM-DD.md."""
    entries = []
    for path in sorted(Path(manual_dir).glob("[0-9]*.md")):
        try:
            entry_date = datetime.fromisoformat(path.stem).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"[warn] skipping manual note with unparsable date: {path}", file=sys.stderr)
            continue
        if since.date() <= entry_date.date() <= until.date():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                entries.append(text)
    return entries


def build_digest(
    repos: list[dict],
    token: str,
    since: datetime,
    until: datetime,
    append: bool = False,
    manual_dir: str = "manual",
) -> str:
    lines = []

    if not append:
        label = until.strftime("%Y-%m-%d")
        delta_days = (until - since).days
        lines += [f"# Dev Updates — {label}", f"_Last {delta_days} days_", ""]

    any_content = False
    for repo in repos:
        commits = fetch_commits(repo, since, token, until=until)
        if not commits:
            continue
        any_content = True
        repo_public = is_repo_public(repo, token)
        lines.append(f"## {repo['name']}")
        if repo.get("link"):
            lines.append(f"<{repo['link']}>")
        elif repo_public:
            lines.append(f"<{repo_url(repo)}>")
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
                commit_ref = f"[`{c['sha']}`]({c['url']})" if repo_public else f"`{c['sha']}`"
                lines.append(f"- {commit_ref} {c['subject']}{attribution}")
                if c["body"]:
                    for body_line in c["body"].splitlines():
                        lines.append(f"  {body_line}")
            lines.append("")

    manual_entries = load_manual_entries(manual_dir, since, until)
    if manual_entries:
        any_content = True
        lines.append(MANUAL_HEADING)
        lines.append("")
        for entry in manual_entries:
            lines.append(entry)
            lines.append("")

    if not any_content and not append:
        lines.append(NO_COMMITS_MARKER)
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
    parser.add_argument("--manual-dir", default="manual", help="Directory of manual notes (default: manual)")
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
    digest = build_digest(
        repos, gh_token, since=since_dt, until=until_dt, append=args.append, manual_dir=args.manual_dir
    )

    # nothing happened in this window: write no file, so the workflows downstream
    # find nothing to publish and stop the chain without failing
    if NO_COMMITS_MARKER in digest:
        print("[skip] no commits in this period, no digest written", file=sys.stderr)
        return

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
