from uuid import uuid4

import pytest

from app.exceptions import DomainError, NotFoundError, ValidationError
from app.services.auth_service import AuthService


def test_register_user_success():
    unique = str(uuid4())[:8]
    created = AuthService.register_user(
        {
            "name": "Service User",
            "email": f"service_{unique}@example.com",
            "phone": f"+1-555-000-{unique}",
            "birth_date": "1995-01-01",
            "password": "secure_pwd",
        },
        "member",
    )

    assert created["email"].startswith("service_")
    assert created["role"] == "member"
    assert created["password_hash"] != "secure_pwd"


def test_register_user_missing_required_fields():
    with pytest.raises(ValidationError):
        AuthService.register_user({"email": "missing@example.com"}, "member")


def test_register_user_duplicate_email():
    unique = str(uuid4())[:8]
    email = f"duplicate_{unique}@example.com"

    AuthService.register_user(
        {
            "name": "User One",
            "email": email,
            "phone": f"+1-555-111-{unique}",
            "password": "pwd1",
        },
        "member",
    )

    with pytest.raises(DomainError) as exc:
        AuthService.register_user(
            {
                "name": "User Two",
                "email": email,
                "phone": f"+1-555-222-{unique}",
                "password": "pwd2",
            },
            "member",
        )

    assert "Email already registered" in str(exc.value)


def test_login_user_success():
    unique = str(uuid4())[:8]
    email = f"login_{unique}@example.com"
    password = "secure_pwd"

    created = AuthService.register_user(
        {
            "name": "Login User",
            "email": email,
            "phone": f"+1-555-333-{unique}",
            "password": password,
        },
        "member",
    )

    logged_in = AuthService.login_user({"email": email, "password": password})
    assert logged_in["user_id"] == created["user_id"]


def test_login_user_validation_errors():
    with pytest.raises(ValidationError):
        AuthService.login_user({"password": "secure_pwd"})

    with pytest.raises(ValidationError):
        AuthService.login_user({"email": "person@example.com"})

    with pytest.raises(ValidationError):
        AuthService.login_user({"email": "person@example.com", "password": "secure_pwd", "phone": "+1"})


def test_login_user_not_found_and_wrong_password():
    with pytest.raises(NotFoundError):
        AuthService.login_user({"email": "missing_user@example.com", "password": "secure_pwd"})

    unique = str(uuid4())[:8]
    email = f"wrongpwd_{unique}@example.com"
    AuthService.register_user(
        {
            "name": "Wrong Password User",
            "email": email,
            "phone": f"+1-555-444-{unique}",
            "password": "actual_pwd",
        },
        "member",
    )

    with pytest.raises(ValidationError):
        AuthService.login_user({"email": email, "password": "incorrect_pwd"})
