# pylint: disable=too-many-arguments
from datetime import datetime, timezone
from uuid import uuid4

from app.db import DB
from app.db.constants import ID
from app.db.utils import serialize_item, serialize_items

# Collection name
BOOKING_COLLECTION = "bookings"

# Field names
BOOKING_ID = "booking_id"
CLASS_ID = "class_id"
USER_ID = "user_id"
USER_NAME = "user_name"
USER_EMAIL = "user_email"
PHONE = "phone"
ROLE = "role"
STATUS = "status"
BOOKED_AT = "booked_at"

# Booking status values
STATUS_CONFIRMED = "confirmed"
STATUS_CANCELLED = "cancelled"


def _collection():
	return DB.get_collection(BOOKING_COLLECTION)


def utc_now_iso() -> str:
	"""Return current UTC timestamp as ISO-8601 string ending with 'Z'."""
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_booking_document(
	class_id: str,
	user_id: str,
	user_name: str,
	user_email: str,
	phone: str | None,
	role: str,
	*,
	booking_id: str | None = None,
	status: str = STATUS_CONFIRMED,
	booked_at: str | None = None,
) -> dict:
	"""Build a normalized booking document ready for persistence."""
	booked_ts = booked_at or utc_now_iso()

	return {
		BOOKING_ID: booking_id or str(uuid4()),
		CLASS_ID: class_id,
		USER_ID: user_id,
		USER_NAME: user_name,
		USER_EMAIL: user_email,
		PHONE: phone,
		ROLE: role,
		STATUS: status,
		BOOKED_AT: booked_ts,
	}


def create_booking(booking: dict) -> dict:
	"""Insert a booking and return the stored booking (with serialized `_id`)."""
	insert_result = _collection().insert_one(booking)
	
	booking[ID] = insert_result.inserted_id # We are adding the _id to the collection ("_id": ObjectId("XXXX"),)
	return serialize_item(booking)


def get_booking_by_user_and_class(user_id: str, class_id: str) -> dict | None:
	"""Return a single booking for a user in a class, if present."""
	booking = _collection().find_one({USER_ID: user_id, CLASS_ID: class_id})
	return serialize_item(booking)


def booking_exists_for_user(user_id: str, class_id: str) -> bool:
	"""Return True if user already has a booking for the class."""
	return get_booking_by_user_and_class(user_id, class_id) is not None


def list_bookings_by_class(class_id: str) -> list[dict]:
	"""Return all bookings for a class."""
	bookings = list(_collection().find({CLASS_ID: class_id}))
	return serialize_items(bookings)
