import pytest
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token

from app import create_app


@pytest.fixture(scope="session", autouse=True)
def app():
    load_dotenv()
    app = create_app({
        "MOCK_DB": True 
    })
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
            identity="trainer@example.com",
            additional_claims={"role": "trainer", "user_id": "trainer-test-user"},
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def member_headers(app):
    with app.app_context():
        token = create_access_token(
            identity="member@example.com",
            additional_claims={"role": "member", "user_id": "member-test-user"}
        )
    return {"Authorization": f"Bearer {token}"}
