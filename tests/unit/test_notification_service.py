from uuid import uuid4

import pytest

from app.db.bookings import BookingRole, BookingUser, build_booking_document
from app.db.users import build_user_document, create_user
from app.services.notification_service import NotificationService, EmailNotificationChannel, TelegramNotificationChannel


class _FakeEmailChannel:
    def send(self, user: dict, fitness_class: dict, sender_email: str) -> str:
        return f"email:{user['email']}"


class _FakeTelegramChannel:
    def send(self, user: dict, fitness_class: dict, sender_email: str) -> str:
        return f"telegram:{user['telegram_chat_id']}"
    


def test_notification_service_respects_preferences():
    suffix = str(uuid4())[:8]
    user_email = f"notify_{suffix}@example.com"
    user_id = f"user_notify_{suffix}"

    create_user(
        build_user_document(
            name="Notify User",
            email=user_email,
            password_hash="hashed",
            role="member",
            user_id=user_id,
            notification_preferences={"email": True, "telegram": True},
            telegram_chat_id="987654321",
        )
    )

    booking = build_booking_document(
        class_id=f"class_{suffix}",
        booking_user=BookingUser(
            user_id=user_id,
            user_name="Notify User",
            user_email=user_email,
            role=BookingRole.MEMBER,
        ),
    )

    service = NotificationService()
    service._channels = {
        "email": _FakeEmailChannel(),
        "telegram": _FakeTelegramChannel(),
    }

    result = service.send_for_bookings(
        bookings=[booking],
        fitness_class={"title": "Yoga", "datetime": "2036-01-01T10:00:00Z", "trainer_name": "Alex"},
        sender_email="noreply@example.com",
    )

    assert result["sent_count"] == 2
    assert "email:notify_" in result["recipients"][0]
    assert "telegram:987654321" in result["recipients"][1]


def test_notification_service_defaults_to_email_when_preferences_missing():
    suffix = str(uuid4())[:8]
    user_email = f"notify_default_{suffix}@example.com"
    user_id = f"user_notify_default_{suffix}"

    create_user(
        build_user_document(
            name="Default Notify",
            email=user_email,
            password_hash="hashed",
            role="member",
            user_id=user_id,
            notification_preferences=None,
        )
    )

    booking = build_booking_document(
        class_id=f"class_default_{suffix}",
        booking_user=BookingUser(
            user_id=user_id,
            user_name="Default Notify",
            user_email=user_email,
            role=BookingRole.MEMBER,
        ),
    )

    service = NotificationService()
    service._channels = {"email": _FakeEmailChannel(), "telegram": _FakeTelegramChannel()}

    result = service.send_for_bookings(
        bookings=[booking],
        fitness_class={"title": "Pilates", "datetime": "2036-01-01T10:00:00Z", "trainer_name": "Alex"},
        sender_email="noreply@example.com",
    )

    assert result["sent_count"] == 1
    assert result["recipients"] == [f"email:{user_email}"]

def test_resolve_user_email_fallback(mocker):
    """_resolve_user falls back to email when user_id not found"""
    suffix = str(uuid4())[:8]
    user_email = f"fallback_{suffix}@example.com"
    user_id = f"user_fallback_{suffix}"
    
    create_user(
        build_user_document(
            name="Fallback User",
            email=user_email,
            password_hash="hashed",
            role="member",
            user_id=user_id,
        )
    )
    
    booking = build_booking_document(
        class_id=f"class_{suffix}",
        booking_user=BookingUser(
            user_id="nonexistent_user_id",
            user_name="Fallback User",
            user_email=user_email,
            role=BookingRole.MEMBER,
        ),
    )
    
    service = NotificationService()
    user = service._resolve_user(booking)
    
    assert user is not None
    assert user["email"] == user_email

def test_email_channel_send_missing_email():
    """EmailNotificationChannel raises error when email is missing."""
    user = {}
    fitness_class = {"title": "Yoga"}
    channel = EmailNotificationChannel()
    
    with pytest.raises(RuntimeError, match="User email is missing"):
        channel.send(user, fitness_class, "noreply@example.com")

def test_email_channel_send_success(mocker):
    """EmailNotificationChannel calls send_single_class_reminder and returns target."""
    mocked_send = mocker.patch(
        "app.services.notification_service.send_single_class_reminder",
        return_value="email:user@example.com"
    )
    
    user = {"email": "user@example.com"}
    fitness_class = {"title": "Yoga"}
    channel = EmailNotificationChannel()
    
    result = channel.send(user, fitness_class, "noreply@example.com")
    
    assert result == "email:user@example.com"
    mocked_send.assert_called_once()

def test_telegram_channel_missing_chat_id():
    """TelegramNotificationChannel raises error when chat_id is missing."""
    user = {}
    fitness_class = {"title": "Yoga"}
    channel = TelegramNotificationChannel()
    
    with pytest.raises(RuntimeError, match="Telegram chat_id is missing"):
        channel.send(user, fitness_class, "noreply@example.com")

def test_telegram_channel_send_missing_bot_token(monkeypatch):
    """TelegramNotificationChannel raises when TELEGRAM_BOT_TOKEN is missing."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    
    user = {"telegram_chat_id": "12345"}
    fitness_class = {"title": "Yoga"}
    channel = TelegramNotificationChannel()
    
    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN is required"):
        channel.send(user, fitness_class, "noreply@example.com")

def test_telegram_channel_send_success(monkeypatch, mocker):
    """TelegramNotificationChannel sends message and returns target."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    
    mocked_urlopen = mocker.patch("app.services.notification_service.request.urlopen")
    mocked_response = mocker.MagicMock()
    mocked_response.status = 200
    mocked_urlopen.return_value.__enter__.return_value = mocked_response
    
    user = {"telegram_chat_id": "12345"}
    fitness_class = {"title": "Yoga", "datetime": "2036-01-01T10:00:00Z", "trainer_name": "Alex"}
    channel = TelegramNotificationChannel()
    
    result = channel.send(user, fitness_class, "noreply@example.com")
    
    assert result == "telegram:12345"
    mocked_urlopen.assert_called_once()

def test_telegram_channel_send_bad_status(monkeypatch, mocker):
    """TelegramNotificationChannel raises when API returns non-2xx status."""
    from urllib.error import URLError
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    
    mocked_urlopen = mocker.patch("app.services.notification_service.request.urlopen")
    mocked_response = mocker.MagicMock()
    mocked_response.status = 500
    mocked_urlopen.return_value.__enter__.return_value = mocked_response
    
    user = {"telegram_chat_id": "12345"}
    fitness_class = {"title": "Yoga"}
    channel = TelegramNotificationChannel()
    
    with pytest.raises(RuntimeError, match="Telegram API rejected message with status 500"):
        channel.send(user, fitness_class, "noreply@example.com")

def test_telegram_channel_url_error(monkeypatch, mocker):
    """TelegramNotificationChannel raises on URLError"""
    from urllib import error
    
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    mocker.patch(
        "app.services.notification_service.request.urlopen",
        side_effect=error.URLError("timeout")
    )
    
    channel = TelegramNotificationChannel()
    user = {"telegram_chat_id": "12345"}
    fitness_class = {"title": "Yoga"}
    
    with pytest.raises(RuntimeError, match="Telegram API call failed"):
        channel.send(user, fitness_class, "noreply@example.com")


