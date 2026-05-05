from uuid import uuid4

from app.db.users import build_user_document, create_user, get_user_by_user_id
from app.services.telegram_link_service import TelegramLinkService


def _token_from_link(deep_link: str) -> str:
    return deep_link.split("?start=", maxsplit=1)[1]


def test_telegram_deep_link_can_be_consumed_once():
    suffix = str(uuid4())[:8]
    user_id = f"user_telegram_{suffix}"
    user_email = f"telegram_link_{suffix}@example.com"
    chat_id = "99887766"

    create_user(
        build_user_document(
            name="Telegram Link User",
            email=user_email,
            password_hash="hashed",
            role="member",
            user_id=user_id,
            phone="+971-504-555-0100",
        )
    )

    created = TelegramLinkService.create_deep_link_for_email(user_email)
    token = _token_from_link(created["deep_link"])

    first_link = TelegramLinkService.consume_start_payload_and_link_chat(token, chat_id)
    assert first_link is not None
    assert first_link["telegram_chat_id"] == chat_id

    second_link = TelegramLinkService.consume_start_payload_and_link_chat(token, chat_id)
    assert second_link is None

    persisted = get_user_by_user_id(user_id)
    assert persisted["telegram_chat_id"] == chat_id

