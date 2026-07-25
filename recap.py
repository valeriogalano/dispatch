#!/usr/bin/env python3
"""Generate Telegram and blog recaps from a digest file using AI."""

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import errors as genai_errors

GEMINI_MODEL = "gemini-3.5-flash"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

_MAX_RETRIES_PER_PROVIDER = 3

TELEGRAM_SYSTEM = """\
Sei un assistente che scrive aggiornamenti tecnici settimanali per il canale Telegram di Pensieri in codice (pensieriincodice.it).
Scrivi in italiano, in terza persona, riferendoti all'autore come "Valerio".
Il tuo stile per Telegram:
- Apri con un titolo breve con emoji che cattura il tema della settimana
- Un brevissimo cappello introduttivo (1-2 righe max), non un elenco
- Raggruppa le novità per tema o progetto correlato, non necessariamente una sezione per repository
- Ogni sezione ha un'emoji + titolo descrittivo
- Bullet point con label in **grassetto** seguita da spiegazione concisa
- Includi solo link presenti esplicitamente nel digest; non inventare, dedurre o ricostruire URL GitHub dai nomi dei progetti
- Quando citi un progetto/repository, linka la pagina GitHub del progetto, non la lista dei commit e non un singolo commit
- Se un progetto non ha link nel digest, citalo solo per nome senza URL
- Se nel digest compare un commit con "by Nome", menziona il contributo: "con il contributo di Nome"
- Tono: informativo e diretto, come una newsletter tecnica schematica
- Lunghezza totale: 200-350 parole
Ignora completamente i commit relativi alla pubblicazione di episodi del podcast (upload di mp3, aggiunta di metadati, copertine, trascrizioni, soundbite, script di episodi). Parla solo di sviluppi tecnici e nuove funzionalità.
Se dopo aver escluso questi commit non rimane nulla di significativo, scrivi un messaggio onesto che questa settimana non ci sono stati sviluppi tecnici rilevanti.
"""

TELEGRAM_USER = """\
Ecco il digest dei commit. Genera il post Telegram nel tuo stile.
Raggruppa per tema logico, non per repository. Se ci sono repository correlati, trattali insieme.
Usa solo i link già presenti nel digest. Non aggiungere URL GitHub per progetti che nel digest non hanno un link.
Quando citi un progetto/repository, usa il link alla pagina del progetto indicato nella sua sezione del digest; non usare URL /commits né link a commit specifici come link del progetto.
Ignora i commit di pubblicazione episodi (mp3, metadati episodio, copertine, trascrizioni, soundbite, script).
La sezione "## Aggiornamenti manuali" non contiene commit: sono cose fatte da Valerio fuori da git (episodi del podcast, articoli, release, altro). Trattale come il resto del materiale e non escluderle mai.
{blog_instruction}

{digest}
"""

BLOG_SYSTEM = """\
Sei un assistente che scrive post narrativi per il blog Pensieri in codice (pensieriincodice.it).
Scrivi in italiano, in terza persona, riferendoti all'autore come "Valerio". Non usare mai la prima persona.
Il tuo stile per i post del blog:
- Scrivi in prosa fluente, non usare bullet point
- Racconta cosa ha fatto Valerio come se lo stessi raccontando a un lettore curioso: non elenchi, ma storia
- Puoi partire da un'osservazione, una sensazione, un problema che ha incontrato
- Usa qualche emoji nel testo per dare vivacità, con misura (non più di una ogni due paragrafi)
- Includi solo link presenti esplicitamente nel digest; non inventare, dedurre o ricostruire URL GitHub dai nomi dei progetti
- Quando citi un progetto/repository, linka la pagina GitHub del progetto, non la lista dei commit e non un singolo commit
- Se un progetto non ha link nel digest, citalo solo per nome senza URL
- Se nel digest compare un commit con "by Nome", attribuisci quel lavoro a quella persona nel testo
- Includi una piccola riflessione finale — non necessariamente tecnica
- Non serve un frontmatter YAML: scrivi solo il corpo del post
- Lunghezza: 300-500 parole
"""

BLOG_USER = """\
Ecco il digest dei commit. Scrivi un post narrativo per il blog Pensieri in codice.
Non elencare i commit uno per uno: sintetizza, racconta, dai senso al lavoro fatto.
Usa solo i link già presenti nel digest. Non aggiungere URL GitHub per progetti che nel digest non hanno un link.
Quando citi un progetto/repository, usa il link alla pagina del progetto indicato nella sua sezione del digest; non usare URL /commits né link a commit specifici come link del progetto.
Ignora i commit di pubblicazione episodi (mp3, metadati episodio, copertine, trascrizioni, soundbite, script).
La sezione "## Aggiornamenti manuali" non contiene commit: sono cose fatte da Valerio fuori da git (episodi del podcast, articoli, release, altro). Trattale come il resto del materiale e non escluderle mai.
Se il periodo è stato quieto o dopo l'esclusione non rimane nulla di significativo, può essere l'occasione per una riflessione più ampia.

{digest}
"""


def _call_gemini(api_key: str, system: str, user: str) -> str:
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


def call_ai(system: str, user: str) -> str:
    providers = _get_providers()
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

    for provider in providers:
        print(f"  → using provider: {provider}", file=sys.stderr)
        for attempt in range(1, _MAX_RETRIES_PER_PROVIDER + 1):
            try:
                if provider in {"google", "gemini"}:
                    if not gemini_key:
                        raise RuntimeError("GEMINI_API_KEY not set")
                    result = _call_gemini(gemini_key, system, user)
                    return GEMINI_MODEL, result
                elif provider in {"anthropic", "claude"}:
                    if not anthropic_key:
                        raise RuntimeError("ANTHROPIC_API_KEY not set")
                    result = _call_claude(anthropic_key, system, user)
                    return CLAUDE_MODEL, result
                else:
                    raise RuntimeError(f"unknown provider: {provider}")
            except genai_errors.ServerError as e:
                print(f"  → Gemini error (attempt {attempt}/{_MAX_RETRIES_PER_PROVIDER}): {e}", file=sys.stderr)
                if attempt < _MAX_RETRIES_PER_PROVIDER:
                    time.sleep(60)
                else:
                    print(f"  → provider {provider} exhausted, trying next...", file=sys.stderr)
            except Exception as e:
                print(f"  → error with {provider} (attempt {attempt}/{_MAX_RETRIES_PER_PROVIDER}): {e}", file=sys.stderr)
                if attempt < _MAX_RETRIES_PER_PROVIDER:
                    time.sleep(30)
                else:
                    print(f"  → provider {provider} exhausted, trying next...", file=sys.stderr)

    raise RuntimeError(f"all providers exhausted: {', '.join(providers)}")


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
            TELEGRAM_SYSTEM,
            TELEGRAM_USER.format(digest=digest_text, blog_instruction=blog_instruction),
        )
        header = f"_Questo testo è stato generato con {model}_\n\n"
        telegram_path = out_dir / f"recap-telegram-{date_str}.md"
        telegram_path.write_text(header + telegram_text, encoding="utf-8")
        print(f"[saved] {telegram_path}", file=sys.stderr)
        print(f"\n=== {date_str} — TELEGRAM ===\n{telegram_text}")

    if "blog" in formats:
        title = f"Recap automatizzato del {date_str}"

        print("  → Blog recap…", file=sys.stderr)
        model, blog_text = call_ai(BLOG_SYSTEM, BLOG_USER.format(digest=digest_text))
        header = f"_Questo testo è stato generato con {model}_\n\n"
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
            f"author: Valerio Galano\n"
            f"---\n\n"
        )
        blog_path.write_text(frontmatter + header + blog_text, encoding="utf-8")
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
