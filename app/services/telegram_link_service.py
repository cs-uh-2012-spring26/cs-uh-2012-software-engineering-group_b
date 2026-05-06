import hashlib
import secrets
import time

from app.db.telegram_links import (
    USER_ID,
    create_telegram_link_token,
    consume_valid_telegram_link_token,
)
from app.db.users import (
    get_user_by_email,
    update_user_telegram_chat_id_by_user_id,
)
from app.exceptions import NotFoundError, ValidationError

DEFAULT_LINK_TTL_SECONDS = 600
BOT_USERNAME = "CoachlyyBot"


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class TelegramLinkService:
    @staticmethod
    def create_deep_link_for_email(user_email: str) -> dict:
        user = get_user_by_email(user_email)
        if user is None:
            raise NotFoundError("User not found!")

        raw_token = secrets.token_urlsafe(32)
        expires_at = int(time.time()) + DEFAULT_LINK_TTL_SECONDS
        create_telegram_link_token(
            token_hash=_hash_token(raw_token),
            user_id=user["user_id"],
            expires_at=expires_at,
        )
        return {
            "deep_link": f"https://t.me/{BOT_USERNAME}?start={raw_token}",
            "expires_at": expires_at,
        }

    @staticmethod
    def consume_start_payload_and_link_chat(start_payload: str, chat_id: str) -> dict | None:
        token = start_payload.strip() if isinstance(start_payload, str) else ""
        normalized_chat_id = chat_id.strip() if isinstance(chat_id, str) else ""

        if not token or not normalized_chat_id:
            raise ValidationError("Invalid Telegram linking payload")

        token_doc = consume_valid_telegram_link_token(
            token_hash=_hash_token(token),
            now_epoch=int(time.time()),
        )
        if token_doc is None:
            return None

        user_id = token_doc.get(USER_ID)
        if not isinstance(user_id, str) or not user_id.strip():
            return None

        return update_user_telegram_chat_id_by_user_id(user_id, normalized_chat_id)
