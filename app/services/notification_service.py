import json
from abc import ABC, abstractmethod
from os import environ
from urllib import error, request

from app.db.bookings import USER_EMAIL, USER_ID
from app.db.users import (
    EMAIL,
    NOTIFICATION_PREFERENCES,
    TELEGRAM_CHAT_ID,
    get_user_by_email,
    get_user_by_user_id,
)
from app.services.email_reminders import send_single_class_reminder

DEFAULT_NOTIFICATION_PREFERENCES = {"email": True, "telegram": False}


class NotificationChannel(ABC):
    """Strategy interface for notification channels."""

    channel_name: str

    @abstractmethod
    def send(self, user: dict, fitness_class: dict, sender_email: str) -> str:
        """Send a notification and return a target label."""


class EmailNotificationChannel(NotificationChannel):
    channel_name = "email"

    def send(self, user: dict, fitness_class: dict, sender_email: str) -> str:
        email = str(user.get(EMAIL, "")).strip()
        if not email:
            raise RuntimeError("User email is missing")
        return send_single_class_reminder(
            recipient_email=email,
            fitness_class=fitness_class,
            sender_email=sender_email,
        )


class TelegramNotificationChannel(NotificationChannel):
    channel_name = "telegram"

    def send(self, user: dict, fitness_class: dict, sender_email: str) -> str:
        chat_id = str(user.get(TELEGRAM_CHAT_ID, "")).strip()
        if not chat_id:
            raise RuntimeError("Telegram chat_id is missing")

        bot_token = str(environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
        if not bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

        title = str(fitness_class.get("title", "your upcoming class"))
        class_datetime = str(fitness_class.get("datetime", "soon"))
        trainer_name = str(fitness_class.get("trainer_name", "your trainer"))
        text = (
            f"Reminder: {title} starts soon\n"
            f"Date & time: {class_datetime}\n"
            f"Trainer: {trainer_name}"
        )

        payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
        req = request.Request(
            url=f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=10) as response:
                status_code = getattr(response, "status", None)
                if status_code not in (200, 202):
                    raise RuntimeError(f"Telegram API rejected message with status {status_code}")
        except error.URLError as exc:
            raise RuntimeError(f"Telegram API call failed: {exc}") from exc

        return f"telegram:{chat_id}"


class NotificationService:
    """Dispatch reminders through channel strategies based on user preferences."""

    def __init__(self):
        self._channels: dict[str, NotificationChannel] = {
            "email": EmailNotificationChannel(),
            "telegram": TelegramNotificationChannel(),
        }

    @staticmethod
    def _normalized_preferences(user: dict) -> dict[str, bool]:
        prefs = user.get(NOTIFICATION_PREFERENCES)
        if not isinstance(prefs, dict):
            prefs = {}

        normalized = dict(DEFAULT_NOTIFICATION_PREFERENCES)
        for key in normalized:
            if key in prefs:
                normalized[key] = bool(prefs[key])
        return normalized

    @staticmethod
    def _resolve_user(booking: dict) -> dict | None:
        user_id = str(booking.get(USER_ID, "")).strip()
        if user_id:
            user = get_user_by_user_id(user_id)
            if user is not None:
                return user

        email = str(booking.get(USER_EMAIL, "")).strip()
        if email:
            return get_user_by_email(email)
        return None

    def send_for_bookings(self, bookings: list[dict], fitness_class: dict, sender_email: str) -> dict:
        sent_count = 0
        recipients: list[str] = []

        for booking in bookings:
            user = self._resolve_user(booking)
            if user is None:
                continue

            preferences = self._normalized_preferences(user)
            for channel_name, enabled in preferences.items():
                if not enabled:
                    continue

                channel = self._channels.get(channel_name)
                if channel is None:
                    continue

                target = channel.send(user=user, fitness_class=fitness_class, sender_email=sender_email)
                sent_count += 1
                recipients.append(target)

        return {"sent_count": sent_count, "recipients": recipients}
