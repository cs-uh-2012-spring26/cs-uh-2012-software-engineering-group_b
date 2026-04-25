"""
Run this script alongside the Flask app for local development.
It polls Telegram for new messages and replies with the sender's chat_id.

Usage:
    python telegram_bot.py
"""
import json
import os
import time
from urllib import error, request as urllib_request

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

START_REPLY = (
    "Welcome to CoachlyyBot!\n\n"
    "Your Telegram chat ID is: {chat_id}\n\n"
    "Copy this ID and use it when registering or updating your notification "
    "preferences in the app to receive class reminders here."
)
FALLBACK_REPLY = "Send /start to get your Telegram chat ID for use with the Coachlyy app."


def _api(method: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(
        url=f"{BASE_URL}/{method}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib_request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def send_message(chat_id: int | str, text: str) -> None:
    try:
        _api("sendMessage", {"chat_id": chat_id, "text": text})
    except error.URLError as exc:
        print(f"[warn] sendMessage failed: {exc}")


def get_updates(offset: int) -> list[dict]:
    try:
        data = json.dumps({"offset": offset}).encode("utf-8")
        req = urllib_request.Request(
            url=f"{BASE_URL}/getUpdates",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib_request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("result", [])
    except error.URLError as exc:
        print(f"[warn] getUpdates failed: {exc}")
        time.sleep(2)
        return []


def handle(message: dict) -> None:
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()
    if not chat_id:
        return
    if text.startswith("/start") or text.startswith("/id"):
        send_message(chat_id, START_REPLY.format(chat_id=chat_id))
    else:
        send_message(chat_id, FALLBACK_REPLY)


def main() -> None:
    print(f"Bot polling started. Send /start to https://t.me/CoachlyyBot")
    offset = 0
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message") or update.get("edited_message")
            if message:
                handle(message)
        if not updates:
            time.sleep(1)


if __name__ == "__main__":
    main()
