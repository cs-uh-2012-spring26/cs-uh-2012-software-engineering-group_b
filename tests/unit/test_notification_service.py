from uuid import uuid4

from app.db.bookings import BookingRole, BookingUser, build_booking_document
from app.db.users import build_user_document, create_user
from app.services.notification_service import NotificationService


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
