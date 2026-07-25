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
from pathlib import Path


_LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a Markdown recap to Telegram.")
    parser.add_argument("file", help="Path to the recap file")
    args = parser.parse_args()

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[error] TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set", file=sys.stderr)
        return 1

    source = Path(args.file).read_text(encoding="utf-8")

    response = send_message(token, chat_id, markdown_to_telegram_html(source), parse_mode="HTML")
    if response.get("ok"):
        print("[sent] Telegram message sent with HTML formatting")
        return 0

    print(f"[warn] Telegram HTML send failed: {response}", file=sys.stderr)
    if should_retry_plain(response):
        fallback = send_message(token, chat_id, markdown_to_plain_text(source))
        if fallback.get("ok"):
            print("[sent] Telegram message sent as plain text after parse fallback")
            return 0
        print(f"[error] Telegram plain-text fallback failed: {fallback}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
