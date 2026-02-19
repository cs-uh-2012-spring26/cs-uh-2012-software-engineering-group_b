from app.db import DB
from app.db.utils import serialize_item
from uuid import uuid4

from app.db.constants import ID

# Collection name
FITNESS_CLASS_COLLECTION = "fitness_classes"

# Field names
CLASS_ID = "class_id"
TITLE = "title"
DATETIME = "datetime"
CAPACITY = "capacity"
AVAILABLE_SPOTS = "available_spots"
TRAINER_NAME = "trainer_name"


def _collection():
	return DB.get_collection(FITNESS_CLASS_COLLECTION)


def get_class_by_class_id(class_id: str) -> dict | None:
	"""Fetch one class by `class_id`."""
	fitness_class = _collection().find_one({CLASS_ID: class_id})
	return serialize_item(fitness_class)


def decrement_available_spot(class_id: str) -> bool:
	"""Atomically decrement `available_spots` by 1 only when spots are still available."""
	update_result = _collection().update_one(
		{CLASS_ID: class_id, AVAILABLE_SPOTS: {"$gt": 0}},
		{"$inc": {AVAILABLE_SPOTS: -1}},
	)
	return update_result.modified_count == 1

#
def build_fitness_class_document(
	title: str, 
	dt: str, 
	capacity: int,
	trainer_name: str,
	class_id: str | None = None
) -> dict: 
	"""Build a normalized fitness class document ready for persistence."""
	return {
		CLASS_ID: class_id or str(uuid4()),
		TITLE: title,
		DATETIME: dt,
		CAPACITY: capacity,
		AVAILABLE_SPOTS: capacity,
		TRAINER_NAME: trainer_name
	}

#
def create_fitness_class(fitness_class: dict) -> dict:
	"""Insert a fitness class document and return the stored fitness class (with serialized '_id')"""
	insert_result = _collection().insert_one(fitness_class)

	fitness_class[ID] = insert_result.inserted_id # We are adding the _id to the collection ("_id": ObjectId("XXXX")
	return serialize_item(fitness_class)


