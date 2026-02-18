import pytest
from dotenv import load_dotenv

from app import create_app


@pytest.fixture(scope="session", autouse=True)
def app():
    load_dotenv()
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()
