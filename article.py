#!/usr/bin/env python3
"""Adapt the script of a podcast episode into a blog article, written by Engram.

The text is written in a Claude Code session: `--export-prompt` hands it the messages,
`--import-text` checks and saves what it wrote."""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from recap import drop_invented_links, engram_system, strip_trailer

SYSTEM = engram_system("articolo-episodio")

USER = """\
Ecco lo script dell'episodio {number} di Pensieri in codice, «{title}». Adattalo in un articolo per il blog, seguendo le regole del ruolo.

Fonti dell'episodio, le sole che puoi linkare:
{sources}

Script:

{script}
"""

# measured on the script without its listening-only sections (see `without_listening_sections`):
# the articles of 148, 149 and 151 come out at 0.94, 0.99 and 1.00 of it
MIN_RATIO, MAX_RATIO = 0.8, 1.1

# sections that exist only for the ear: greetings, podcast news, farewells and supporters
_LISTENING_SECTION = re.compile(r"^## (introduzione|conclusione|.*novit)", re.IGNORECASE)

# decades and centuries are capitalised in Italian without being names, and the
# script often writes them as digits: "anni '60" becomes "anni Sessanta"
_NOT_NAMES = {
    "Venti", "Trenta", "Quaranta", "Cinquanta", "Sessanta", "Settanta", "Ottanta", "Novanta",
    "Duecento", "Trecento", "Quattrocento", "Cinquecento", "Seicento", "Settecento",
    "Ottocento", "Novecento", "Duemila",
}

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


def without_listening_sections(script: str) -> str:
    """The script the article is measured against: the role drops these sections
    whole, so counting them would make a faithful article look short."""
    out, skip = [], False
    for line in script.splitlines():
        if line.startswith("## "):
            skip = bool(_LISTENING_SECTION.match(line))
        if not skip:
            out.append(line)
    return "\n".join(out)


def read_episode(website: Path, number: int) -> dict:
    """Frontmatter of the episode page. BaseLoader keeps every value a string, so
    the date is copied to the article exactly as the episode carries it."""
    text = (website / "content" / "podcast" / f"{number}.md").read_text(encoding="utf-8")
    return yaml.load(text.split("---\n", 2)[1], Loader=yaml.BaseLoader)


def check(article: str, script: str, allowed: str) -> list[str]:
    """Reasons to hold the article back. Any one is enough: an article that
    misquotes an episode under Valerio's name is worse than no article."""
    problems = []
    ratio = len(article.split()) / max(len(without_listening_sections(script).split()), 1)
    if not MIN_RATIO <= ratio <= MAX_RATIO:
        problems.append(f"length is {ratio:.2f} of the script, expected {MIN_RATIO}-{MAX_RATIO}")
    # ponytail: a proper noun is a capitalised word right after a lowercase word;
    # sentence openers are skipped, and so are names glued to an apostrophe
    names = set(re.findall(r"(?<=[a-zà-ù,;] )([A-ZÀ-Ý][\w’'-]*\w)", article))
    if missing := sorted(n for n in names - _NOT_NAMES if n.lower() not in allowed.lower()):
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


def prepare(website: Path, number: int) -> tuple[dict, str, str, str]:
    """Episode, cleaned script, text links may come from, and the user message."""
    episode = read_episode(website, number)
    script = clean_script(read_script(website / "data" / "scripts" / f"PIC{number}.yml"))
    sources = episode.get("sources") or []
    allowed = "\n".join([script, episode["title"]] + [f"{s.get('title', '')} {s['url']}" for s in sources])
    user = USER.format(
        number=number,
        title=episode["title"],
        sources="\n".join(f"- {s.get('title', s['url'])}: {s['url']}" for s in sources) or "(nessuna)",
        script=script,
    )
    return episode, script, allowed, user


def save_article(out_dir: Path, number: int, episode: dict, script: str, allowed: str,
                 model: str, text: str, problems: list[str] = ()) -> bool:
    """Write output/article-NNN.md, or output/article-NNN.rejected.md with the
    reasons when a check fails. Either file means the text was already paid for."""
    body = drop_invented_links(strip_trailer(text), allowed)

    if problems := list(problems) + check(body, script, allowed):
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


def export_prompt(website: Path, number: int, out: Path) -> None:
    """The system and user messages for a session to write the article from,
    brought back with import_text."""
    _, _, _, user = prepare(website, number)
    out.mkdir(parents=True, exist_ok=True)
    (out / "system.md").write_text(SYSTEM, encoding="utf-8")
    (out / "user.md").write_text(user, encoding="utf-8")
    print(f"[exported] {out}/system.md, {out}/user.md", file=sys.stderr)


def import_text(website: Path, number: int, text_path: Path, model: str, out_dir: Path) -> bool:
    """Clean, check and save a text written in a session."""
    if (out_dir / f"article-{number}.md").exists():
        print(f"[skip] article-{number}.md already exists", file=sys.stderr)
        return True
    episode, script, allowed, _ = prepare(website, number)
    return save_article(out_dir, number, episode, script, allowed, model,
                        text_path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Adapt podcast episode scripts into blog articles.")
    parser.add_argument("--website", required=True, help="Checkout of pensieriincodice-website")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    parser.add_argument("--export-prompt", type=int, metavar="N",
                        help="Write the system and user messages for episode N to --out, call no model")
    parser.add_argument("--out", help="With --export-prompt, the directory for system.md and user.md")
    parser.add_argument("--import-text", type=int, metavar="N",
                        help="Check and save a text written elsewhere for episode N, call no model")
    parser.add_argument("--text", help="With --import-text, the file holding the article body")
    parser.add_argument("--model", help="With --import-text, the model that wrote it (generated_with)")
    args = parser.parse_args()

    website, out_dir = Path(args.website), Path(args.output_dir)

    if args.export_prompt is not None:
        if not args.out:
            parser.error("--export-prompt needs --out")
        export_prompt(website, args.export_prompt, Path(args.out))
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    if args.import_text is not None:
        if not (args.text and args.model):
            parser.error("--import-text needs --text and --model")
        sys.exit(0 if import_text(website, args.import_text, Path(args.text), args.model, out_dir) else 1)

    parser.error("nothing to do: use --export-prompt or --import-text")


if __name__ == "__main__":
    main()
