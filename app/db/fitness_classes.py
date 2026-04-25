from app.db import DB
from app.db.utils import serialize_item
from pymongo import ReturnDocument

from app.db.constants import ID
from datetime import datetime, timedelta

# Collection name
FITNESS_CLASS_COLLECTION = "fitness_classes"

# Field names
CLASS_ID = "class_id"
TITLE = "title"
DATETIME = "datetime"
CAPACITY = "capacity"
AVAILABLE_SPOTS = "available_spots"
TRAINER_NAME = "trainer_name"
RECURRENCE_TYPE = "recurrence_type"  # "one_time", "daily", or "weekly"
RECURRENCE_END_DATE = "recurrence_end_date" 

COUNTERS_COLLECTION = "counters"
FITNESS_CLASS_ID_COUNTER_KEY = "fitness_class_id"

def _collection():
	return DB.get_collection(FITNESS_CLASS_COLLECTION)

def _counters_collection():
	return DB.get_collection(COUNTERS_COLLECTION)

def _next_fitness_class_sequence() -> int:
	"""Increment and return the next fitness class sequence number."""
	doc = _counters_collection().find_one_and_update(
		{"_id": FITNESS_CLASS_ID_COUNTER_KEY},
		{"$inc": {"seq": 1}},
		upsert=True,
		return_document=ReturnDocument.AFTER,
	)
	return int(doc.get("seq", 1))

def generate_fitness_class_id() -> str:
	"""Return next human-friendly class id like 'class_001'."""
	seq = _next_fitness_class_sequence()
	return f"class_{seq:03d}"

def get_class_by_class_id(class_id: str) -> dict | None:
	"""Fetch one class by `class_id`."""
	fitness_class = _collection().find_one({CLASS_ID: class_id})
	return serialize_item(fitness_class)

def generate_recurring_instances(start_dt: str, recurrence_type: str, end_dt: str | None) -> list[str]:
    """Return list of datetime strings for all recurrences."""
    
    instances = [start_dt]
    if recurrence_type == "one_time":
        return instances
    
    current = datetime.fromisoformat(start_dt.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_dt.replace("Z", "+00:00")) if end_dt else None
    delta = timedelta(days=1) if recurrence_type == "daily" else timedelta(weeks=1)
    
    while True:
        current += delta
        if end and current > end:
            break
        instances.append(current.isoformat().replace("+00:00", "Z"))
    
    return instances

def class_exists(title: str, dt: str, trainer_name: str) -> bool:
	"""Return True when a class with the same title, datetime, and trainer already exists."""
	fitness_class = _collection().find_one(
		{
			TITLE: title,
			DATETIME: dt,
			TRAINER_NAME: trainer_name,
		}
	)
	return fitness_class is not None

def decrement_available_spot(class_id: str) -> bool:
	"""Decrement `available_spots` by 1 only when spots are still available."""
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
	class_id: str | None = None,
	recurrence_type: str = "one_time",
    recurrence_end_date: str | None = None
) -> dict: 
	"""Build a normalized fitness class document ready for persistence."""
	doc = {
		CLASS_ID: class_id or generate_fitness_class_id(),
		TITLE: title,
		DATETIME: dt,
		CAPACITY: capacity,
		AVAILABLE_SPOTS: capacity,
		TRAINER_NAME: trainer_name,
		RECURRENCE_TYPE: recurrence_type
	}
	if recurrence_end_date:
		doc[RECURRENCE_END_DATE] = recurrence_end_date
	return doc

#
def create_fitness_class(fitness_class: dict) -> dict:
	"""Insert a fitness class document and return the stored fitness class (with serialized '_id')"""
	insert_result = _collection().insert_one(fitness_class)

	fitness_class[ID] = insert_result.inserted_id # We are adding the _id to the collection ("_id": ObjectId("XXXX")
	return serialize_item(fitness_class)


