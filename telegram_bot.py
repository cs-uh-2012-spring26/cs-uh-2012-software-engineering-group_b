"""
Run this script alongside the Flask app for local development.
It polls Telegram for new messages and links Telegram chat_id via one-time deep-links.

Usage:
    python telegram_bot.py
"""
import json
import os
import time
from urllib import error, request as urllib_request

from dotenv import load_dotenv

from app import create_app
from app.exceptions import ValidationError
from app.services.telegram_link_service import TelegramLinkService

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

START_REPLY = (
    "Welcome to CoachlyyBot!\n\n"
    "To link reminders to your account, open Telegram using the "
    "'Connect Telegram' button from the app."
)
LINKED_REPLY = (
    "Great, your Telegram account is now linked.\n"
    "If Telegram reminders are enabled in the app, future class reminders will be sent here."
)
INVALID_LINK_REPLY = (
    "This link is invalid or expired.\n"
    "Please generate a new Telegram connect link in the app and try again."
)
FALLBACK_REPLY = "Use the app's 'Connect Telegram' button, then return to this chat."


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


def send_message(chat_id: int | str, text: str, reply_markup: dict | None = None) -> None:
    try:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        _api("sendMessage", payload)
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


def _extract_start_payload(text: str) -> str | None:
    if not text.startswith("/start"):
        return None
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    payload = parts[1].strip()
    return payload or None


def handle(message: dict) -> None:
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()
    if not chat_id:
        return

    start_payload = _extract_start_payload(text)
    if start_payload:
        try:
            linked_user = TelegramLinkService.consume_start_payload_and_link_chat(
                start_payload=start_payload,
                chat_id=str(chat_id),
            )
        except ValidationError:
            linked_user = None

        if linked_user is not None:
            send_message(chat_id, LINKED_REPLY)
            print(f"[info] linked chat_id={chat_id} to user_id={linked_user.get('user_id')}")
        else:
            send_message(chat_id, INVALID_LINK_REPLY)
            print(f"[warn] invalid/expired telegram link, chat_id={chat_id}")
        return

    if text.startswith("/start"):
        send_message(chat_id, START_REPLY)
        return

    send_message(chat_id, FALLBACK_REPLY)


def _kill_existing_instances() -> None:
    import os
    import signal
    current_pid = os.getpid()
    try:
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "telegram_bot.py"],
            capture_output=True, text=True
        )
        for pid_str in result.stdout.strip().splitlines():
            pid = int(pid_str)
            if pid != current_pid:
                os.kill(pid, signal.SIGTERM)
    except Exception:
        pass


def main() -> None:
    # Initializes DB connection through Flask app config.
    create_app()
    _kill_existing_instances()
    print("Bot polling started. Send /start to https://t.me/CoachlyyBot")
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
