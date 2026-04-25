from datetime import datetime as dt_mod, timezone

from app.db.bookings import list_bookings_by_class
from app.db.fitness_classes import (
    CAPACITY,
    DATETIME,
    TITLE,
    TRAINER_NAME,
    RECURRENCE_TYPE,
    RECURRENCE_END_DATE,
    build_fitness_class_document,
    class_exists,
    create_fitness_class,
    get_class_by_class_id,
    generate_recurring_instances
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
        recurrence_type = payload.get(RECURRENCE_TYPE, "one_time")
        recurrence_end_date = payload.get(RECURRENCE_END_DATE)

        if not title or not dt or not capacity or not trainer_name:
            raise ValidationError(f"{TITLE}, {DATETIME}, {CAPACITY}, and {TRAINER_NAME} are required")

        if not isinstance(capacity, int) or capacity <= 0:
            raise ValidationError(f"{CAPACITY} must be a positive integer")

        if not isinstance(title, str) or not isinstance(trainer_name, str) or not title.strip() or not trainer_name.strip():
            raise ValidationError(f"{TITLE} and {TRAINER_NAME} must be non-empty strings")
        
        if recurrence_type not in ["one_time", "daily", "weekly"]:
            raise ValidationError(f"{RECURRENCE_TYPE} must be 'one_time', 'daily', or 'weekly'")
        
        try:
            parsed_dt = dt_mod.fromisoformat(dt.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            raise ValidationError(f"{DATETIME} must be a valid datetime string")
    
        if recurrence_end_date:
            try:
                parsed_end_dt = dt_mod.fromisoformat(recurrence_end_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                raise ValidationError(f"{RECURRENCE_END_DATE} must be a valid datetime string")
            if parsed_end_dt <= parsed_dt:
                raise ValidationError(f"{RECURRENCE_END_DATE} must be after the start datetime")

        normalized_title = title.strip()
        normalized_trainer_name = trainer_name.strip()

        if parsed_dt <= dt_mod.now(timezone.utc):
            raise ValidationError(f"{DATETIME} must not be in the past")

        if class_exists(normalized_title, dt, normalized_trainer_name):
            raise DomainError("Class already exists")

        # Generate instances and create all
        datetimes = generate_recurring_instances(dt, recurrence_type, recurrence_end_date)
        created_instances = []
        for instance_dt in datetimes:
            if not class_exists(normalized_title, instance_dt, normalized_trainer_name):
                doc = build_fitness_class_document(
                        normalized_title, 
                        instance_dt, 
                        capacity, 
                        normalized_trainer_name,
                        recurrence_type,
                        recurrence_end_date
                    )
        created_instance = create_fitness_class(doc)
        created_instances.append(created_instance)

        return created_instances[0] if created_instances else {}    

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
