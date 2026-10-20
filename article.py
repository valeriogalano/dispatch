#!/usr/bin/env python3
"""Adapt the script of a podcast episode into a blog article, written by Engram."""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from recap import Truncated, call_ai, drop_invented_links, engram_system, strip_trailer

SYSTEM = engram_system("articolo-episodio")

USER = """\
Ecco lo script dell'episodio {number} di Pensieri in codice, «{title}». Adattalo in un articolo per il blog, seguendo le regole del ruolo.

Fonti dell'episodio, le sole che puoi linkare:
{sources}

Script:

{script}
"""

# the first episode after the pipeline went live: the 82 older ones are a backfill
# run by hand, not something the nightly job should work through
FIRST_NEW_EPISODE = 151

# ponytail: bounds picked by eye on the scripts, tune them on the first articles
MIN_RATIO, MAX_RATIO = 0.6, 0.85  # the role asks for 60-80% of the script

_SPOKEN_ONLY = re.compile(r"^(sigla|buon ascolto)[.!]?$", re.IGNORECASE)
_SPEAKER = re.compile(r"^#{6}\s+(.+?)\s*$")


def read_script(path: Path) -> str:
    """The script files are a single double-quoted YAML scalar. A YAML parser folds
    its lines and glues each `###### Name` header to the paragraph after it, so the
    file is read as text: `\\"` is the only escape the scripts use."""
    raw = path.read_text(encoding="utf-8").strip()
    assert raw.startswith('text: "') and raw.endswith('"'), path
    return raw[len('text: "'):-1].replace('\\"', '"')


def clean_script(text: str) -> str:
    """Drop the cues that exist only for the ear and turn speaker headers into the
    interview format the role asks for: `**Name:**` opening each turn."""
    out, speaker = [], None
    for line in text.splitlines():
        line = line.strip()
        if _SPOKEN_ONLY.match(line):
            continue
        if m := _SPEAKER.match(line):
            speaker = m.group(1)
            continue
        if speaker and line:
            line, speaker = f"**{speaker}:** {line}", None
        out.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def read_episode(website: Path, number: int) -> dict:
    """Frontmatter of the episode page. BaseLoader keeps every value a string, so
    the date is copied to the article exactly as the episode carries it."""
    text = (website / "content" / "podcast" / f"{number}.md").read_text(encoding="utf-8")
    return yaml.load(text.split("---\n", 2)[1], Loader=yaml.BaseLoader)


def check(article: str, script: str, allowed: str) -> list[str]:
    """Reasons to hold the article back. Any one is enough: an article that
    misquotes an episode under Valerio's name is worse than no article."""
    problems = []
    ratio = len(article.split()) / max(len(script.split()), 1)
    if not MIN_RATIO <= ratio <= MAX_RATIO:
        problems.append(f"length is {ratio:.2f} of the script, expected {MIN_RATIO}-{MAX_RATIO}")
    # ponytail: a proper noun is a capitalised word right after a lowercase word;
    # sentence openers are skipped, and so are names glued to an apostrophe
    names = set(re.findall(r"(?<=[a-zà-ù,;] )([A-ZÀ-Ý][\w’'-]*\w)", article))
    if missing := sorted(n for n in names if n.lower() not in allowed.lower()):
        problems.append(f"names not in the script: {', '.join(missing)}")
    urls = set(re.findall(r"https?://[^\s)>\]\"]+", article))
    if invented := sorted(u for u in urls if u not in allowed):
        problems.append(f"URLs not in the sources: {', '.join(invented)}")
    return problems


def frontmatter(episode: dict, number: int, model: str) -> str:
    # json.dumps gives valid YAML double-quoted strings and flow lists
    return (
        f"---\n"
        f"title: {json.dumps(episode['title'], ensure_ascii=False)}\n"
        f"date: {episode['date']}\n"
        f"tags: {json.dumps(episode.get('tags') or [], ensure_ascii=False)}\n"
        f"type: blog\n"
        f"author: Valerio Galano\n"
        f"episode: {number}\n"
        f"curated_by: Engram\n"
        f"generated_with: {model}\n"
        f"---\n\n"
    )


def generate_article(website: Path, number: int, out_dir: Path) -> bool:
    """Write output/article-NNN.md, or output/article-NNN.rejected.md with the
    reasons when a check fails. Either file means the AI was already paid for."""
    episode = read_episode(website, number)
    script = clean_script(read_script(website / "data" / "scripts" / f"PIC{number}.yml"))
    sources = episode.get("sources") or []
    allowed = "\n".join([script, episode["title"]] + [f"{s.get('title', '')} {s['url']}" for s in sources])

    print(f"Episode {number}: {episode['title']}", file=sys.stderr)
    try:
        model, text = call_ai(SYSTEM, USER.format(
            number=number,
            title=episode["title"],
            sources="\n".join(f"- {s.get('title', s['url'])}: {s['url']}" for s in sources) or "(nessuna)",
            script=script,
        ))
        cut = []
    except Truncated as e:
        # 2026-10-20: the 149 article ended mid-word and still passed the length check
        model, text, cut = e.model, e.text, [str(e)]
    body = drop_invented_links(strip_trailer(text), allowed)

    if problems := cut + check(body, script, allowed):
        path = out_dir / f"article-{number}.rejected.md"
        path.write_text("\n".join(f"<!-- {p} -->" for p in problems) + f"\n\n{body}\n", encoding="utf-8")
        print(f"[rejected] {path}: " + "; ".join(problems), file=sys.stderr)
        return False

    path = out_dir / f"article-{number}.md"
    # no link to the episode in the body: the site's disclosure under the title
    # carries it, read from `episode` in the frontmatter
    path.write_text(frontmatter(episode, number, model) + body + "\n", encoding="utf-8")
    print(f"[saved] {path}", file=sys.stderr)
    return True


def missing_episodes(website: Path, out_dir: Path, since: int = FIRST_NEW_EPISODE) -> list[int]:
    """Episodes with a script and a page but no article yet, rejected ones included,
    newest first: the episode that just came out matters more than the backlog.
    The older scripts are .json transcripts without punctuation: only .yml count."""
    numbers = sorted((int(p.stem[3:]) for p in (website / "data" / "scripts").glob("PIC*.yml")), reverse=True)
    return [n for n in numbers
            if n >= since
            and (website / "content" / "podcast" / f"{n}.md").exists()
            and not list(out_dir.glob(f"article-{n}.*md"))]


def main():
    parser = argparse.ArgumentParser(description="Adapt podcast episode scripts into blog articles.")
    parser.add_argument("episodes", nargs="*", type=int, help="Episode numbers (default: --missing)")
    parser.add_argument("--website", required=True, help="Checkout of pensieriincodice-website")
    parser.add_argument("--missing", action="store_true", help="Every episode with a script and no article")
    parser.add_argument("--limit", type=int, default=0, help="With --missing, at most this many (0: no limit)")
    parser.add_argument("--since", type=int, default=FIRST_NEW_EPISODE,
                        help=f"With --missing, only episodes from this number on (default: {FIRST_NEW_EPISODE})")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    args = parser.parse_args()

    website, out_dir = Path(args.website), Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    episodes = args.episodes
    if args.missing or not episodes:
        episodes = missing_episodes(website, out_dir, args.since)[:args.limit or None]

    ok = True
    for number in episodes:
        if (out_dir / f"article-{number}.md").exists():
            print(f"[skip] article-{number}.md already generated", file=sys.stderr)
            continue
        ok = generate_article(website, number, out_dir) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
