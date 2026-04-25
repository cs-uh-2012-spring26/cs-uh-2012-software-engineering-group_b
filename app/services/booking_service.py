from app.db.bookings import BookingRole, BookingUser, booking_exists_for_user, build_booking_document, create_booking
from app.db.fitness_classes import decrement_available_spot, get_class_by_class_id
from app.db.users import (
    EMAIL as USER_EMAIL_FIELD,
    NAME as USER_NAME_FIELD,
    PHONE as USER_PHONE_FIELD,
    ROLE as USER_ROLE_FIELD,
    ROLE_MEMBER,
    USER_ID as USER_ID_FIELD,
    get_user_by_email,
)
from app.exceptions import DomainError, NotFoundError, ValidationError


class BookingService:
    """Business logic for class bookings."""

    @staticmethod
    def book_class(user_email: str, class_id: str) -> dict:
        if not user_email or not class_id:
            raise ValidationError("class_id is required")

        user = get_user_by_email(user_email)
        if user is None:
            raise NotFoundError("User not found")

        user_id = user.get(USER_ID_FIELD)
        if not user_id:
            raise NotFoundError("User not found")

        if booking_exists_for_user(user_id, class_id):
            raise DomainError("Booking already exists")

        fitness_class = get_class_by_class_id(class_id)
        if fitness_class is None:
            raise NotFoundError("Class not found")

        if user.get(USER_ROLE_FIELD) != ROLE_MEMBER:
            raise DomainError("Only members can book classes")

        role_value = user.get(USER_ROLE_FIELD, ROLE_MEMBER)
        booking_user = BookingUser(
            user_id=user_id,
            user_name=user.get(USER_NAME_FIELD, ""),
            user_email=user.get(USER_EMAIL_FIELD, ""),
            phone=user.get(USER_PHONE_FIELD),
            role=BookingRole(role_value),
        )

        booking_doc = build_booking_document(class_id=class_id, booking_user=booking_user)

        if not decrement_available_spot(class_id):
            raise DomainError("Class is full")

        return create_booking(booking_doc)
