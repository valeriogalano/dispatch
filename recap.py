#!/usr/bin/env python3
"""Generate Telegram and blog recaps from a digest file using AI."""

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

GEMINI_MODEL = "gemini-3.5-flash"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

_MAX_RETRIES_PER_PROVIDER = 3

_SKILL = Path(__file__).parent / "skills" / "engram" / "references"


def engram_system(role: str) -> str:
    """Engram's voice lives in the skill, not in a copy kept here.

    Identity and prose apply to everything Engram writes; the role file adds the
    task at hand. Editing the prompt means editing those files.
    """
    parts = ("engram-identita.md", "engram-prosa.md", f"roles/{role}.md")
    return "\n\n---\n\n".join((_SKILL / p).read_text(encoding="utf-8") for p in parts)


SYSTEM = engram_system("recap-settimanale")

TELEGRAM_USER = """\
Ecco il digest del periodo. Scrivi il post per il canale Telegram, seguendo le regole del formato Telegram.
{blog_instruction}

{digest}
"""

BLOG_USER = """\
Ecco il digest del periodo. Scrivi il post per il blog, seguendo le regole del formato blog.

{digest}
"""


def _call_gemini(api_key: str, system: str, user: str) -> str:
    # imported lazily so that running with AI_PROVIDER=anthropic needs no google-genai
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.8,
        ),
    )
    return response.text.strip()


def _call_claude(api_key: str, system: str, user: str) -> str:
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text.strip()


def _get_providers() -> list[str]:
    raw = os.environ.get("AI_PROVIDER", "google,anthropic")
    providers = [p.strip().lower() for p in raw.split(",") if p.strip()]
    return providers or ["google", "anthropic"]


_PROVIDERS = {
    "google": ("GEMINI_API_KEY", GEMINI_MODEL, _call_gemini),
    "gemini": ("GEMINI_API_KEY", GEMINI_MODEL, _call_gemini),
    "anthropic": ("ANTHROPIC_API_KEY", CLAUDE_MODEL, _call_claude),
    "claude": ("ANTHROPIC_API_KEY", CLAUDE_MODEL, _call_claude),
}


def call_ai(system: str, user: str) -> tuple[str, str]:
    """Return (model, text) from the first provider that answers."""
    providers = _get_providers()

    for provider in providers:
        if provider not in _PROVIDERS:
            print(f"  → unknown provider: {provider}, skipping", file=sys.stderr)
            continue
        env_var, model, call = _PROVIDERS[provider]
        # a missing key will not appear on the third attempt: fail over now
        key = os.environ.get(env_var, "")
        if not key:
            print(f"  → {provider}: {env_var} not set, skipping", file=sys.stderr)
            continue

        print(f"  → using provider: {provider}", file=sys.stderr)
        for attempt in range(1, _MAX_RETRIES_PER_PROVIDER + 1):
            try:
                return model, call(key, system, user)
            except Exception as e:
                print(f"  → error with {provider} (attempt {attempt}/{_MAX_RETRIES_PER_PROVIDER}): {e}", file=sys.stderr)
                if attempt < _MAX_RETRIES_PER_PROVIDER:
                    time.sleep(30)
                else:
                    print(f"  → provider {provider} exhausted, trying next...", file=sys.stderr)

    raise RuntimeError(f"all providers exhausted: {', '.join(providers)}")


def disclosure(model: str) -> str:
    """The disclosure travels with every recap, signed or not."""
    return f"\n\n_Questo testo è stato generato con {model}_\n"


def signature(model: str) -> str:
    """Engram signs the blog post; on Telegram the channel already shows the sender."""
    return f"\n\n— Engram" + disclosure(model)


def find_latest_digest(output_dir: Path) -> Path | None:
    candidates = sorted(output_dir.glob("digest-*.md"), reverse=True)
    return candidates[0] if candidates else None


def extract_date_from_path(path: Path) -> str:
    stem = path.stem
    if stem.startswith("digest-"):
        return stem[len("digest-"):]
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def generate_recap(digest_path: Path, out_dir: Path, formats: list[str], blog_url: str = "") -> None:
    digest_text = digest_path.read_text(encoding="utf-8")
    date_str = extract_date_from_path(digest_path)

    print(f"Generating recaps from {digest_path}…", file=sys.stderr)

    if "telegram" in formats:
        print("  → Telegram recap…", file=sys.stderr)
        blog_instruction = (
            f'Al termine del post aggiungi: "📖 Articolo completo: {blog_url}" seguito dal tag #recap'
            if blog_url else "Chiudi con il tag #recap"
        )
        model, telegram_text = call_ai(
            SYSTEM,
            TELEGRAM_USER.format(digest=digest_text, blog_instruction=blog_instruction),
        )
        telegram_path = out_dir / f"recap-telegram-{date_str}.md"
        telegram_path.write_text(telegram_text + disclosure(model), encoding="utf-8")
        print(f"[saved] {telegram_path}", file=sys.stderr)
        print(f"\n=== {date_str} — TELEGRAM ===\n{telegram_text}")

    if "blog" in formats:
        title = f"Recap automatizzato del {date_str}"

        print("  → Blog recap…", file=sys.stderr)
        model, blog_text = call_ai(SYSTEM, BLOG_USER.format(digest=digest_text))
        blog_path = out_dir / f"recap-blog-{date_str}.md"
        frontmatter = (
            f"---\n"
            f"title: \"{title}\"\n"
            f"date: {date_str}T10:00:00+02:00\n"
            f"featureImage: https://pensieriincodice.it/images/blog/recap.png\n"
            f"image: https://pensieriincodice.it/images/blog/recap.png\n"
            f"tags:\n"
            f"- Dev\n"
            f"- Recap\n"
            f"- Generato\n"
            f"categories:\n"
            f"- News\n"
            f"type: blog\n"
            f"author: Engram\n"
            f"---\n\n"
        )
        blog_path.write_text(frontmatter + blog_text + signature(model), encoding="utf-8")
        print(f"[saved] {blog_path}", file=sys.stderr)
        print(f"\n=== {date_str} — BLOG (titolo: {title}) ===\n{blog_text}")


def main():
    parser = argparse.ArgumentParser(description="Generate Telegram and/or blog recaps from one or more digests.")
    parser.add_argument("--digest", action="append", metavar="FILE",
                        help="Path to a digest .md file (repeatable; default: latest in output/)")
    parser.add_argument("--format", action="append", dest="formats", choices=["telegram", "blog"],
                        metavar="FORMAT", help="Format to generate: telegram, blog (repeatable; default: both)")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    parser.add_argument("--blog-url", default="", help="URL of the blog post to include in the Telegram recap")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.digest:
        digest_paths = [Path(p) for p in args.digest]
    else:
        latest = find_latest_digest(out_dir)
        if not latest:
            print(f"[error] no digest file found in {out_dir}/", file=sys.stderr)
            sys.exit(1)
        digest_paths = [latest]

    formats = args.formats or ["telegram", "blog"]

    for digest_path in digest_paths:
        generate_recap(digest_path, out_dir, formats, blog_url=args.blog_url or "")


if __name__ == "__main__":
    main()
