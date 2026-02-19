from app.db import DB
from app.db.utils import serialize_item

# Collection name
USER_COLLECTION = "users"

# Field names
USER_ID = "user_id"
NAME = "name"
EMAIL = "email"
PHONE = "phone"
BIRTH_DATE = "birth_date"
PASSWORD_HASH = "password_hash"
ROLE = "role"
CREATED_AT = "created_at"
UPDATED_AT = "updated_at"

# Roles
ROLE_GUEST = "guest"
ROLE_MEMBER = "member"
ROLE_TRAINER = "trainer"
ROLE_ADMIN = "admin"

# TODO: Add a `UserResource` when auth implementation starts.


def _collection():
	return DB.get_collection(USER_COLLECTION)


def get_user_by_user_id(user_id: str) -> dict | None:
	"""Fetch one user by `user_id` from the users collection."""
	user = _collection().find_one({USER_ID: user_id})
	return serialize_item(user)
