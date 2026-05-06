from app.db import DB
from app.db.utils import serialize_item
from uuid import uuid4
from datetime import datetime
from pymongo import ReturnDocument
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
NOTIFICATION_PREFERENCES = "notification_preferences"
TELEGRAM_CHAT_ID = "telegram_chat_id"

# Roles
ROLE_GUEST = "guest"
ROLE_MEMBER = "member"
ROLE_TRAINER = "trainer"
ROLE_ADMIN = "admin"

# TODO: Add a `UserResource` when auth implementation starts.


def _collection():
	return DB.get_collection(USER_COLLECTION)


def normalize_phone(phone: str | None) -> str | None:
	"""Normalize phone numbers for matching/storage consistency."""
	if not isinstance(phone, str):
		return None
	raw = phone.strip()
	if not raw:
		return None

	has_plus = raw.startswith("+")
	digits = "".join(char for char in raw if char.isdigit())
	if not digits:
		return None

	return f"+{digits}" if has_plus else digits


def get_user_by_user_id(user_id: str) -> dict | None:
	"""Fetch one user by `user_id` from the users collection."""
	user = _collection().find_one({USER_ID: user_id})
	return serialize_item(user)

def get_user_by_email(email: str) -> dict | None:
	"""Fetch one user by 'email' from the users collection."""
	user = _collection().find_one({EMAIL: email})
	return serialize_item(user)

def get_user_by_phone(phone: str) -> dict | None:
	"""Fetch one user by phone from the users collection."""
	raw_phone = phone.strip() if isinstance(phone, str) else ""
	if not raw_phone:
		return None

	normalized_phone = normalize_phone(raw_phone)

	# Fast-path exact matches first.
	user = _collection().find_one({PHONE: raw_phone})
	if user is not None:
		return serialize_item(user)

	if normalized_phone and normalized_phone != raw_phone:
		user = _collection().find_one({PHONE: normalized_phone})
		if user is not None:
			return serialize_item(user)

	# Fallback for legacy formats already stored in DB.
	if normalized_phone:
		for candidate in _collection().find({PHONE: {"$ne": None}}):
			if normalize_phone(candidate.get(PHONE)) == normalized_phone:
				return serialize_item(candidate)

	return None

def build_user_document(
	name: str,
	email: str,
	password_hash: str,
	role: str,
	phone: str | None = None,
	birth_date: str | None = None,
	user_id: str | None = None,
	notification_preferences: dict | None = None,
	telegram_chat_id: str | None = None,
) -> dict:
	"""Build a normalized user document ready for persistence."""
	now = datetime.utcnow().isoformat()
	normalized_phone = normalize_phone(phone)
	default_preferences = {"email": True, "telegram": False}
	if isinstance(notification_preferences, dict):
		default_preferences.update({
			"email": bool(notification_preferences.get("email", default_preferences["email"])),
			"telegram": bool(notification_preferences.get("telegram", default_preferences["telegram"])),
		})

	return {
		USER_ID: user_id or str(uuid4()),
		NAME: name,
		EMAIL: email,
		PHONE: normalized_phone,
		BIRTH_DATE: birth_date,
		PASSWORD_HASH: password_hash,
		ROLE: role,
		NOTIFICATION_PREFERENCES: default_preferences,
		TELEGRAM_CHAT_ID: telegram_chat_id,
		CREATED_AT: now,
		UPDATED_AT: now,
	}


def create_user(user: dict) -> dict:
	"""Insert a user document and return the stored user (with serialized '_id')."""
	insert_result = _collection().insert_one(user)
	
	user[ID] = insert_result.inserted_id
	return serialize_item(user)


def update_user_notification_preferences(
	user_email: str,
	notification_preferences: dict,
) -> dict | None:
	"""Update one user's notification preferences and return updated document."""
	now = datetime.utcnow().isoformat()
	set_fields: dict = {
		NOTIFICATION_PREFERENCES: {
			"email": bool(notification_preferences.get("email", True)),
			"telegram": bool(notification_preferences.get("telegram", False)),
		},
		UPDATED_AT: now,
	}

	updated_user = _collection().find_one_and_update(
		{EMAIL: user_email},
		{"$set": set_fields},
		return_document=ReturnDocument.AFTER,
	)
	return serialize_item(updated_user)


def update_user_telegram_chat_id_by_user_id(user_id: str, telegram_chat_id: str) -> dict | None:
	"""Map a Telegram chat id to a user by user id."""
	if not isinstance(user_id, str) or not user_id.strip():
		return None

	chat_id = telegram_chat_id.strip() if isinstance(telegram_chat_id, str) else ""
	if not chat_id:
		return None

	now = datetime.utcnow().isoformat()
	updated_user = _collection().find_one_and_update(
		{USER_ID: user_id},
		{"$set": {TELEGRAM_CHAT_ID: chat_id, UPDATED_AT: now}},
		return_document=ReturnDocument.AFTER,
	)
	return serialize_item(updated_user)
