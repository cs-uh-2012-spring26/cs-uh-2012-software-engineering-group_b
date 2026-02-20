import pytest
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token

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


@pytest.fixture
def trainer_headers(app):
    with app.app_context():
        token = create_access_token(
            identity="trainer-test-user",
            additional_claims={"role": "trainer"},
        )
    return {"Authorization": f"Bearer {token}"}
