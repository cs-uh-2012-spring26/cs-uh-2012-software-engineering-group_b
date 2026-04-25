import bcrypt

from app.db.users import (
    PASSWORD_HASH,
    build_user_document,
    create_user,
    get_user_by_email,
    get_user_by_phone,
    update_user_notification_preferences,
)
from app.exceptions import DomainError, NotFoundError, ValidationError


class AuthService:
    """Business logic for user registration."""

    @staticmethod
    def register_user(data: dict, role: str) -> dict:
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")

        if not name or not email or not password:
            raise ValidationError("name, email, and password are required")

        if get_user_by_email(email) is not None:
            raise DomainError("Email already registered")

        if phone and get_user_by_phone(phone) is not None:
            raise DomainError("Phone already registered")

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user_doc = build_user_document(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            phone=phone,
            birth_date=data.get("birth_date"),
            notification_preferences=data.get("notification_preferences"),
            telegram_chat_id=data.get("telegram_chat_id"),
        )
        return create_user(user_doc)

    @staticmethod
    def login_user(data: dict) -> dict:
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise ValidationError("email is required")
        if data.get("phone"):
            raise ValidationError("phone login is not supported; use email")
        if not password:
            raise ValidationError("password is required")

        user = get_user_by_email(email)
        if user is None:
            raise NotFoundError("User not found!")

        password_hash = user.get(PASSWORD_HASH)
        if not password_hash or not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
            raise ValidationError("Login credentials and password do not match")

        return user

    @staticmethod
    def update_notification_preferences(user_email: str, data: dict) -> dict:
        user = get_user_by_email(user_email)
        if user is None:
            raise NotFoundError("User not found!")

        preferences = data.get("notification_preferences")
        if not isinstance(preferences, dict):
            raise ValidationError("notification_preferences must be an object")

        allowed_keys = {"email", "telegram"}
        unknown_keys = set(preferences.keys()) - allowed_keys
        if unknown_keys:
            raise ValidationError(f"Unsupported notification preference(s): {sorted(unknown_keys)}")

        if "email" in preferences and not isinstance(preferences["email"], bool):
            raise ValidationError("notification_preferences.email must be a boolean")
        if "telegram" in preferences and not isinstance(preferences["telegram"], bool):
            raise ValidationError("notification_preferences.telegram must be a boolean")

        normalized_preferences = {
            "email": bool(preferences.get("email", True)),
            "telegram": bool(preferences.get("telegram", False)),
        }

        telegram_chat_id = data.get("telegram_chat_id")
        if telegram_chat_id is not None and not isinstance(telegram_chat_id, str):
            raise ValidationError("telegram_chat_id must be a string")

        if normalized_preferences["telegram"] and not (
            (isinstance(telegram_chat_id, str) and telegram_chat_id.strip())
            or (isinstance(user.get("telegram_chat_id"), str) and user.get("telegram_chat_id").strip())
        ):
            raise ValidationError("telegram_chat_id is required when telegram notifications are enabled")

        updated_user = update_user_notification_preferences(
            user_email=user_email,
            notification_preferences=normalized_preferences,
            telegram_chat_id=telegram_chat_id,
        )
        if updated_user is None:
            raise NotFoundError("User not found!")
        return updated_user
