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
Sei Valerio Galano, il creatore del podcast Pensieri in codice (pensieriincodice.it).
Scrivi in italiano, in prima persona, con un tono personale, diretto e appassionato.
Rivolgiti al lettore usando il "tu".
Il tuo stile per Telegram:
- Apri con un titolo breve con emoji che cattura il tema della settimana
- Scrivi un breve paragrafo introduttivo narrativo (2-3 righe), non un elenco
- Raggruppa le novità per tema o progetto correlato, non necessariamente una sezione per repository
- Ogni sezione ha un'emoji + titolo descrittivo
- Bullet point con label in **grassetto** seguita da spiegazione concisa
- Includi i link GitHub dove rilevante (formato: https://github.com/valeriogalano/nome-repo)
- Chiudi con una nota personale breve e il tag #recap
- Tono: entusiasta ma concreto, come se lo raccontassi a un amico tecnico nel canale Telegram
- Lunghezza totale: 300-500 parole
Ignora completamente i commit relativi alla pubblicazione di episodi del podcast (upload di mp3, aggiunta di metadati, copertine, trascrizioni, soundbite, script di episodi). Parla solo di sviluppi tecnici e nuove funzionalità.
Se dopo aver escluso questi commit non rimane nulla di significativo, scrivi un messaggio onesto che questa settimana non ci sono stati sviluppi tecnici rilevanti.
"""

TELEGRAM_USER = """\
Ecco il digest dei commit. Genera il post Telegram nel tuo stile.
Raggruppa per tema logico, non per repository. Se ci sono repository correlati, trattali insieme.
Ignora i commit di pubblicazione episodi (mp3, metadati episodio, copertine, trascrizioni, soundbite, script).

{digest}
"""

BLOG_SYSTEM = """\
Sei Valerio Galano, il creatore del podcast Pensieri in codice (pensieriincodice.it).
Scrivi in italiano, in prima persona, con un tono narrativo, curioso e personale.
Il tuo stile per i post del blog:
- Scrivi in prosa fluente, non usare bullet point
- Rivolgiti al lettore con il "tu"
- Racconta cosa hai fatto come se lo stessi raccontando a un amico: non elenchi, ma storia
- Puoi partire da un'osservazione, una sensazione, un problema che hai incontrato
- Usa qualche emoji nel testo per dare vivacità, con misura (non più di una ogni due paragrafi)
- Per ogni progetto citato includi il link GitHub nella forma https://github.com/valeriogalano/nome-repo
- Includi una piccola riflessione finale — non necessariamente tecnica
- Tono: come i tuoi post tipo "Hello World: l'origine dell'esempio per eccellenza"
- Non serve un frontmatter YAML: scrivi solo il corpo del post
- Lunghezza: 300-500 parole
"""

BLOG_USER = """\
Ecco il digest dei commit. Scrivi un post narrativo per il blog Pensieri in codice.
Non elencare i commit uno per uno: sintetizza, racconta, dai senso al lavoro fatto.
Ignora i commit di pubblicazione episodi (mp3, metadati episodio, copertine, trascrizioni, soundbite, script).
Se il periodo è stato quieto o dopo l'esclusione non rimane nulla di significativo, può essere l'occasione per una riflessione più ampia.

{digest}
"""

TITLE_SYSTEM = """\
Sei Valerio Galano, il creatore del podcast Pensieri in codice.
Genera un titolo breve e accattivante in italiano per un post blog di tipo recap settimanale degli aggiornamenti tecnici.
Rispondi con il solo titolo, senza virgolette, senza prefissi, senza spiegazioni.
"""

TITLE_USER = """\
Ecco il digest dei commit della settimana. Genera il titolo del post.

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


def generate_recap(client: genai.Client, digest_path: Path, out_dir: Path, formats: list[str]) -> None:
    digest_text = digest_path.read_text(encoding="utf-8")
    date_str = extract_date_from_path(digest_path)

    print(f"Generating recaps from {digest_path}…", file=sys.stderr)

    header = f"_Questo testo è stato generato con {MODEL}_\n\n"

    if "telegram" in formats:
        print("  → Telegram recap…", file=sys.stderr)
        telegram_text = call_gemini(client, TELEGRAM_SYSTEM, TELEGRAM_USER.format(digest=digest_text))
        telegram_path = out_dir / f"recap-telegram-{date_str}.md"
        telegram_path.write_text(header + telegram_text, encoding="utf-8")
        print(f"[saved] {telegram_path}", file=sys.stderr)
        print(f"\n=== {date_str} — TELEGRAM ===\n{telegram_text}")

    if "blog" in formats:
        print("  → Titolo post blog…", file=sys.stderr)
        title = call_gemini(client, TITLE_SYSTEM, TITLE_USER.format(digest=digest_text))

        print("  → Blog recap…", file=sys.stderr)
        blog_text = call_gemini(client, BLOG_SYSTEM, BLOG_USER.format(digest=digest_text))
        blog_path = out_dir / f"{date_str}-recap.md"
        frontmatter = (
            f"---\n"
            f"title: \"{title}\"\n"
            f"date: {date_str}T10:00:00+02:00\n"
            f"featureImage: https://pensieriincodice.it/images/blog/recap.png\n"
            f"image: https://pensieriincodice.it/images/blog/recap.png\n"
            f"tags:\n"
            f"- Dev\n"
            f"- Recap\n"
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
            print("[error] no digest file found in output/", file=sys.stderr)
            sys.exit(1)
        digest_paths = [latest]

    formats = args.formats or ["telegram", "blog"]

    client = genai.Client(api_key=api_key)

    for digest_path in digest_paths:
        generate_recap(client, digest_path, out_dir, formats)


if __name__ == "__main__":
    main()
