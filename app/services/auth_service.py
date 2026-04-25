import bcrypt

from app.db.users import PASSWORD_HASH, build_user_document, create_user, get_user_by_email, get_user_by_phone
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
