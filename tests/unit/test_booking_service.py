from uuid import uuid4

import pytest

from app.db.fitness_classes import build_fitness_class_document, create_fitness_class
from app.db.users import build_user_document, create_user
from app.exceptions import DomainError, NotFoundError, ValidationError
from app.services.booking_service import BookingService


def _create_member(email: str, user_id: str):
    user = build_user_document(
        name="Member",
        email=email,
        password_hash="hashed",
        role="member",
        user_id=user_id,
    )
    return create_user(user)


def _create_class(class_id: str):
    return create_fitness_class(
        build_fitness_class_document(
            title=f"Service Class {class_id}",
            dt="2037-10-10T10:00:00Z",
            capacity=1,
            trainer_name="Trainer",
            class_id=class_id,
        )
    )


def test_book_class_success():
    suffix = str(uuid4())[:8]
    email = f"booking_{suffix}@example.com"
    class_id = f"class_service_{suffix}"

    _create_member(email=email, user_id=f"user_{suffix}")
    _create_class(class_id=class_id)

    booking = BookingService.book_class(email, class_id)

    assert booking["class_id"] == class_id
    assert booking["user_email"] == email


def test_book_class_requires_class_id():
    with pytest.raises(ValidationError):
        BookingService.book_class("member@example.com", "")


def test_book_class_not_found_user():
    with pytest.raises(NotFoundError):
        BookingService.book_class("missing-user@example.com", "class_001")


def test_book_class_duplicate_booking():
    suffix = str(uuid4())[:8]
    email = f"dup_{suffix}@example.com"
    class_id = f"class_dup_{suffix}"

    _create_member(email=email, user_id=f"user_dup_{suffix}")
    _create_class(class_id=class_id)

    BookingService.book_class(email, class_id)

    with pytest.raises(DomainError) as exc:
        BookingService.book_class(email, class_id)

    assert "Booking already exists" in str(exc.value)


def test_book_class_when_full():
    suffix = str(uuid4())[:8]
    class_id = f"class_full_{suffix}"
    _create_class(class_id=class_id)

    _create_member(email=f"full_1_{suffix}@example.com", user_id=f"user_full_1_{suffix}")
    _create_member(email=f"full_2_{suffix}@example.com", user_id=f"user_full_2_{suffix}")

    BookingService.book_class(f"full_1_{suffix}@example.com", class_id)

    with pytest.raises(DomainError) as exc:
        BookingService.book_class(f"full_2_{suffix}@example.com", class_id)

    assert "Class is full" in str(exc.value)
