from app.db import DB
from app.db.utils import serialize_item
from uuid import uuid4
from datetime import datetime
from app.db.constants import ID

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
ROLE_USER = "user"
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

def get_user_by_email(email: str) -> dict | None:
	"""Fetch one user by 'email' from the users collection."""
	user = _collection().find_one({EMAIL: email})
	return serialize_item(user)

def get_user_by_phone(phone: str) -> dict | None:
	"""Fetch one user by 'phone' from the users collection"""
	user = _collection().find_one({PHONE: phone})
	return serialize_item(user)

def build_user_document(
	name: str,
	email: str,
	password_hash: str,
	role: str,
	phone: str | None = None,
	birth_date: str | None = None,
	user_id: str | None = None
) -> dict:
	"""Build a normalized user document ready for persistence."""
	now = datetime.utcnow().isoformat()
	return {
		USER_ID: user_id or str(uuid4()),
		NAME: name,
		EMAIL: email,
		PHONE: phone,
		BIRTH_DATE: birth_date,
		PASSWORD_HASH: password_hash,
		ROLE: role,
		CREATED_AT: now,
		UPDATED_AT: now,
	}


def create_user(user: dict) -> dict:
	"""Insert a user document and return the stored user (with serialized '_id')."""
	insert_result = _collection().insert_one(user)
	
	user[ID] = insert_result.inserted_id
	return serialize_item(user)
