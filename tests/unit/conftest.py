"""Shared pytest fixtures for unit tests.

This module provides:
- a Flask app configured to use the mock database,
- a test client for HTTP requests,
- reusable auth headers for trainer-only endpoints.
"""

import pytest
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token

from app import create_app


@pytest.fixture(scope="session", autouse=True)
def app():
    """Create one Flask app for the full test session using MOCK_DB."""
    load_dotenv()
    app = create_app({
        "MOCK_DB": True 
    })
    yield app


@pytest.fixture
def client(app):
    """Return Flask test client bound to the shared app fixture."""
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    """Return Flask CLI runner for command-level tests."""
    return app.test_cli_runner()


@pytest.fixture
def trainer_headers(app):
    """Build a valid JWT Authorization header for a trainer role user."""
    with app.app_context():
        token = create_access_token(
            identity="trainer@example.com",
            additional_claims={"role": "trainer", "user_id": "trainer-test-user"},
        )
    return {"Authorization": f"Bearer {token}"}