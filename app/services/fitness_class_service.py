from datetime import datetime as dt_mod, timezone

from app.db.bookings import list_bookings_by_class
from app.db.fitness_classes import (
    CAPACITY,
    DATETIME,
    TITLE,
    TRAINER_NAME,
    build_fitness_class_document,
    class_exists,
    create_fitness_class,
    get_class_by_class_id,
)
from app.exceptions import DomainError, InfrastructureError, NotFoundError, ValidationError
from app.services.notification_service import NotificationService


class FitnessClassService:
    """Business logic for class lifecycle and reminders."""

    @staticmethod
    def create_class(payload: dict) -> dict:
        title = payload.get(TITLE)
        dt = payload.get(DATETIME)
        capacity = payload.get(CAPACITY)
        trainer_name = payload.get(TRAINER_NAME)

        if not title or not dt or not capacity or not trainer_name:
            raise ValidationError(f"{TITLE}, {DATETIME}, {CAPACITY}, and {TRAINER_NAME} are required")

        if not isinstance(capacity, int) or capacity <= 0:
            raise ValidationError(f"{CAPACITY} must be a positive integer")

        if not isinstance(title, str) or not isinstance(trainer_name, str) or not title.strip() or not trainer_name.strip():
            raise ValidationError(f"{TITLE} and {TRAINER_NAME} must be non-empty strings")

        try:
            parsed_dt = dt_mod.fromisoformat(dt.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            raise ValidationError(f"{DATETIME} must be a valid datetime string")

        normalized_title = title.strip()
        normalized_trainer_name = trainer_name.strip()

        if parsed_dt <= dt_mod.now(timezone.utc):
            raise ValidationError(f"{DATETIME} must not be in the past")

        if class_exists(normalized_title, dt, normalized_trainer_name):
            raise DomainError("Class already exists")

        doc = build_fitness_class_document(normalized_title, dt, capacity, normalized_trainer_name)
        return create_fitness_class(doc)

    @staticmethod
    def send_reminders(class_id: str, sender_email: str) -> dict:
        fitness_class = get_class_by_class_id(class_id)
        if fitness_class is None:
            raise NotFoundError("Class not found")

        class_dt_raw = fitness_class.get(DATETIME)
        try:
            class_dt = dt_mod.fromisoformat(str(class_dt_raw).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            raise ValidationError(f"{DATETIME} is invalid for this class")

        if class_dt <= dt_mod.now(timezone.utc):
            raise ValidationError("Reminders can only be sent before the class starts")

        bookings = list_bookings_by_class(class_id)
        if not bookings:
            raise ValidationError("No attendees found for this class")

        try:
            send_result = NotificationService().send_for_bookings(
                bookings=bookings,
                fitness_class=fitness_class,
                sender_email=sender_email,
            )
        except Exception as exc:
            raise InfrastructureError(f"Failed to send reminder notifications: {exc}") from exc

        if send_result.get("sent_count", 0) == 0:
            raise ValidationError("No notification channels configured for attendees")

        return {
            "message": "Reminder notifications sent",
            "class_id": class_id,
            "sent_count": send_result.get("sent_count", 0),
            "recipients": send_result.get("recipients", []),
        }
