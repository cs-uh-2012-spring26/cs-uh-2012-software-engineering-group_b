"""Telegram bot webhook — replies to users with their chat_id."""
import json
from http import HTTPStatus
from os import environ
from urllib import error, request as urllib_request

from flask import request
from flask_restx import Namespace, Resource

api = Namespace("telegram", description="Telegram bot webhook")

_START_REPLY = (
    "Welcome to CoachlyyBot!\n\n"
    "Your Telegram chat ID is: {chat_id}\n\n"
    "Copy this ID and use it when registering or updating your notification "
    "preferences in the app to receive class reminders here."
)

_FALLBACK_REPLY = (
    "Send /start to get your Telegram chat ID for use with the Coachlyy app."
)


def _send_message(chat_id: int | str, text: str) -> None:
    bot_token = environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        return
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib_request.Request(
        url=f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(req, timeout=10):
            pass
    except error.URLError:
        pass


@api.route("/webhook")
class TelegramWebhook(Resource):
    def post(self):
        """Receive Telegram updates and reply with the sender's chat_id."""
        data = request.get_json(silent=True, force=True) or {}
        message = data.get("message") or data.get("edited_message")
        if not message:
            return {}, HTTPStatus.OK

        chat_id = message.get("chat", {}).get("id")
        if not chat_id:
            return {}, HTTPStatus.OK

        text = (message.get("text") or "").strip()
        if text.startswith("/start") or text.startswith("/id"):
            _send_message(chat_id, _START_REPLY.format(chat_id=chat_id))
        else:
            _send_message(chat_id, _FALLBACK_REPLY)

        return {}, HTTPStatus.OK
