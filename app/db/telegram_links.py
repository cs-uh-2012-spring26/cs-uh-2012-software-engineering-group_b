from datetime import datetime

from pymongo import ReturnDocument

from app.db import DB
from app.db.utils import serialize_item

TELEGRAM_LINK_COLLECTION = "telegram_links"

TOKEN_HASH = "token_hash"
USER_ID = "user_id"
CREATED_AT = "created_at"
EXPIRES_AT = "expires_at"
USED_AT = "used_at"


def _collection():
    return DB.get_collection(TELEGRAM_LINK_COLLECTION)


def create_telegram_link_token(token_hash: str, user_id: str, expires_at: int) -> dict:
    now = datetime.utcnow().isoformat()
    document = {
        TOKEN_HASH: token_hash,
        USER_ID: user_id,
        CREATED_AT: now,
        EXPIRES_AT: int(expires_at),
        USED_AT: None,
    }
    _collection().insert_one(document)
    return serialize_item(document)


def consume_valid_telegram_link_token(token_hash: str, now_epoch: int) -> dict | None:
    consumed = _collection().find_one_and_update(
        {
            TOKEN_HASH: token_hash,
            USED_AT: None,
            EXPIRES_AT: {"$gt": int(now_epoch)},
        },
        {"$set": {USED_AT: datetime.utcnow().isoformat()}},
        return_document=ReturnDocument.BEFORE,
    )
    return serialize_item(consumed)
