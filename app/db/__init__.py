from mongomock import MongoClient as mongomockClient
from pymongo import MongoClient as pyMongoClient
from pymongo.database import Collection, Database


class DB:
    _db: None | Database = None

    @classmethod
    def init_app(cls, app):
        '''
        # Initialize the database client based on the environment configuration
        # If USE_MOCK is enabled, then we will use mongomock (in-memory mock DB)
        '''
        create_db = mongomockClient if app.config["MOCK_DB"] else pyMongoClient
        client = create_db(app.config["MONGO_URI"])

        # check if the database is connected. Else fail.
        client.server_info()
        cls._db = client[app.config["DB_NAME"]]

    @classmethod
    def _get(cls) -> Database:
        assert cls._db is not None
        return cls._db

    @classmethod
    def get_collection(cls, collection_name) -> Collection:
        return cls._get()[collection_name]
