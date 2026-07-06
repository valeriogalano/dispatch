#!/usr/bin/env python3
"""Generate Telegram and blog recaps from a digest file using Gemini."""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from google import genai

MODEL = "gemini-3-flash-preview"

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
Se il periodo è stato quieto o dopo l'esclusione non rimane nulla di significativo, può essere l'occasione per una riflessione più ampia.

{digest}
"""


def call_gemini(client: genai.Client, system: str, user: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=user,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.8,
        ),
    )
    return response.text.strip()


def find_latest_digest(output_dir: Path) -> Path | None:
    candidates = sorted(output_dir.glob("digest-*.md"), reverse=True)
    return candidates[0] if candidates else None


def extract_date_from_path(path: Path) -> str:
    stem = path.stem
    if stem.startswith("digest-"):
        return stem[len("digest-"):]
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def generate_recap(client: genai.Client, digest_path: Path, out_dir: Path, formats: list[str], blog_url: str = "") -> None:
    digest_text = digest_path.read_text(encoding="utf-8")
    date_str = extract_date_from_path(digest_path)

    print(f"Generating recaps from {digest_path}…", file=sys.stderr)

    header = f"_Questo testo è stato generato con {MODEL}_\n\n"

    if "telegram" in formats:
        print("  → Telegram recap…", file=sys.stderr)
        blog_instruction = (
            f'Al termine del post aggiungi: "📖 Articolo completo: {blog_url}" seguito dal tag #recap'
            if blog_url else "Chiudi con il tag #recap"
        )
        telegram_text = call_gemini(
            client, TELEGRAM_SYSTEM,
            TELEGRAM_USER.format(digest=digest_text, blog_instruction=blog_instruction),
        )
        telegram_path = out_dir / f"recap-telegram-{date_str}.md"
        telegram_path.write_text(header + telegram_text, encoding="utf-8")
        print(f"[saved] {telegram_path}", file=sys.stderr)
        print(f"\n=== {date_str} — TELEGRAM ===\n{telegram_text}")

    if "blog" in formats:
        title = f"Recap automatizzato del {date_str}"

        print("  → Blog recap…", file=sys.stderr)
        blog_text = call_gemini(client, BLOG_SYSTEM, BLOG_USER.format(digest=digest_text))
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

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[error] GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

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

    client = genai.Client(api_key=api_key)

    for digest_path in digest_paths:
        generate_recap(client, digest_path, out_dir, formats, blog_url=args.blog_url or "")


if __name__ == "__main__":
    main()
