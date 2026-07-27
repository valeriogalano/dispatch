#!/usr/bin/env python3
"""Send a recap to Telegram with safe formatting and a plain-text fallback."""

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


_LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")

# Telegram rejects a sendMessage over 4096 characters with a 400 that the plain-text
# fallback cannot rescue; leave room for the HTML tags added on conversion
TELEGRAM_LIMIT = 3500


def split_message(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    """Split the Markdown source on blank lines, then on newlines if a block is still too long."""
    chunks: list[str] = []
    current = ""
    for block in text.split("\n\n"):
        candidate = f"{current}\n\n{block}" if current else block
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = block
        while len(current) > limit:
            cut = current.rfind("\n", 0, limit)
            if cut <= 0:
                cut = current.rfind(" ", 0, limit)
            if cut <= 0:
                cut = limit
            chunks.append(current[:cut].rstrip())
            current = current[cut:].lstrip("\n ")
    if current:
        chunks.append(current)
    return chunks or [""]


def markdown_to_telegram_html(text: str) -> str:
    escaped = html.escape(text, quote=False)
    # links first: the other rules would happily match inside an URL
    escaped = _LINK_RE.sub(lambda m: f'<a href="{m.group(2).replace(chr(34), "&quot;")}">{m.group(1)}</a>', escaped)
    escaped = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*\n]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?m)^_([^_\n]+)_$", r"<i>\1</i>", escaped)
    return escaped


def markdown_to_plain_text(text: str) -> str:
    text = _LINK_RE.sub(r"\1: \2", text)
    text = text.replace("**", "")
    text = text.replace("`", "")
    text = re.sub(r"(?m)^_([^_\n]+)_$", r"\1", text)
    return text


def send_message(token: str, chat_id: str, text: str, parse_mode: str | None = None) -> dict:
    data = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }
    if parse_mode:
        data["parse_mode"] = parse_mode

    body = urllib.parse.urlencode(data).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    request = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return {"ok": False, "error_code": error.code, "description": payload}


def should_retry_plain(response: dict) -> bool:
    description = response.get("description", "").lower()
    return response.get("error_code") == 400 and "can't parse entities" in description


def marker_path(recap_file: str, marker_dir: str) -> Path:
    return Path(marker_dir) / f"{Path(recap_file).stem}.sent"


def write_marker(marker: Path) -> None:
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a Markdown recap to Telegram.")
    parser.add_argument("file", help="Path to the recap file")
    parser.add_argument(
        "--marker-dir",
        default="output/sent",
        help="Directory holding the already-sent markers (default: output/sent)",
    )
    args = parser.parse_args()

    # a message cannot be unsent: never send the same recap twice, so the whole
    # chain can be re-run to recover from a failure
    marker = marker_path(args.file, args.marker_dir)
    if marker.exists():
        print(f"[skip] {args.file} already sent ({marker})")
        return 0

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[error] TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set", file=sys.stderr)
        return 1

    source = Path(args.file).read_text(encoding="utf-8")

    # ponytail: on a partial failure the earlier parts stay sent and no marker is
    # written, so a re-run duplicates them. Recaps are one chunk in practice.
    chunks = split_message(source)
    if len(chunks) > 1:
        print(f"[info] recap too long for one message, splitting into {len(chunks)} parts")

    for index, chunk in enumerate(chunks, start=1):
        if not send_chunk(token, chat_id, chunk, index, len(chunks)):
            return 1

    write_marker(marker)
    return 0


def send_chunk(token: str, chat_id: str, chunk: str, index: int, total: int) -> bool:
    label = f"part {index}/{total}" if total > 1 else "message"

    response = send_message(token, chat_id, markdown_to_telegram_html(chunk), parse_mode="HTML")
    if response.get("ok"):
        print(f"[sent] Telegram {label} sent with HTML formatting")
        return True

    print(f"[warn] Telegram HTML send failed ({label}): {response}", file=sys.stderr)
    if should_retry_plain(response):
        fallback = send_message(token, chat_id, markdown_to_plain_text(chunk))
        if fallback.get("ok"):
            print(f"[sent] Telegram {label} sent as plain text after parse fallback")
            return True
        print(f"[error] Telegram plain-text fallback failed ({label}): {fallback}", file=sys.stderr)

    return False


if __name__ == "__main__":
    raise SystemExit(main())
