import logging
from os import environ

from dotenv import load_dotenv


def get_required_environ(name: str) -> str:
    load_dotenv()
    try:
        value = environ[name]
    except KeyError as e:
        logging.fatal(f"Environment variable {e} is required.")
        raise KeyError

    if len(value.strip()) == 0:
        raise ValueError(f"Required environment variable {name} cannot be empty")
    return value


class Config(object):
    MONGO_URI = get_required_environ("MONGO_URI")
    DB_NAME = get_required_environ("DB_NAME")
    MOCK_DB = get_required_environ("MOCK_DB").lower() == "true"
    DEBUG = get_required_environ("DEBUG").lower() == "true"

