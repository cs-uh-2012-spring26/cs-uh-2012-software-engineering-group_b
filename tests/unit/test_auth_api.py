"""Unit tests for authentication and authorization flows.

This module covers:
- register/login/validate-token endpoint behavior,
- permission enforcement through role-based decorators.
"""

# internal imports
from app.db.users import get_user_by_user_id, get_user_by_email
from app.apis import MSG
from app.db.fitness_classes import CAPACITY, DATETIME, TITLE, TRAINER_NAME
# external imports
import pytest
from http import HTTPStatus
from flask_jwt_extended import create_access_token


# create a sample member specifically for testing within the auth endpoint
@pytest.fixture()
def sample_member_auth(client):
    """Return a reusable member tuple (user_id, known_password)."""
    sample_member_exists = (get_user_by_email("auth_member@example.com") is not None)
    
    response = client.post("/auth/register", json ={
        "name": "auth_member",
        "email": "auth_member@example.com",
        "phone": "+123-123-123-1234",
        "birth_date": "1995-01-25",
        "password": "secure_pwd"
    })

    if(sample_member_exists):
        assert response.status_code == HTTPStatus.CONFLICT
        return get_user_by_email("auth_member@example.com")["user_id"], "secure_pwd"
    else:
        assert response.status_code == HTTPStatus.CREATED
        return response.json["user_id"], "secure_pwd"
    

#########################################################
# tests for POST method for 'auth' endpoints

def test_register_wrong_fields(client, sample_member_auth):
    """Register endpoint rejects duplicate email and duplicate phone."""
    
    sample_member_auth
    
    # register existing user (same email)
    response = client.post("/auth/register", json = {
        "name": "auth_member",
        "email": "auth_member@example.com",
        "phone": "+123-123-123-1234",
        "birth_date": "1995-01-25",
        "password": "secure_pwd"
    })
    assert response.status_code == HTTPStatus.CONFLICT and response.json[MSG] == "Email already registered"

    # register existing user (same phone number)
    response = client.post("/auth/register", json = {
        "name": "auth_member",
        "email": "auth_member_f@example.com",
        "phone": "+123-123-123-1234",
        "birth_date": "1995-01-25",
        "password": "secure_pwd"
    })
    assert response.status_code == HTTPStatus.CONFLICT and response.json[MSG] == "Phone already registered"

def test_login_correct_fields(client, sample_member_auth):
    """Login succeeds with correct credentials for existing user."""
    
    m_uid, m_pwd = sample_member_auth
    m_email = get_user_by_user_id(m_uid)["email"]
    
    response = client.post("/auth/login", json = {
        "email": m_email,
        "password": m_pwd
    })
    assert response.status_code == HTTPStatus.OK

def test_login_wrong_fields(client, sample_member_auth):
    """Login endpoint returns errors for missing/wrong credentials."""
    
    m_uid, m_pwd = sample_member_auth
    m_email = get_user_by_user_id(m_uid)["email"]

    # no email
    response = client.post("/auth/login", json = {
        "password": m_pwd
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # no password
    response = client.post("/auth/login", json = {
        "email": m_email
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # wrong password
    response = client.post("/auth/login", json = {
        "email": m_email,
        "password": "wrong password"
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST and response.json[MSG] == "Login credentials and password do not match"

def test_validate_token_correct_fields(client):
    """Validate-token endpoint returns success for known valid token."""

    response = client.post("/auth/validate-token", json = {
        "token": "trainer-secret-123"
    })
    assert response.status_code == HTTPStatus.OK and response.json["valid"] == True

def test_validate_token_wrong_fields(client):
    """Validate-token endpoint rejects unknown tokens."""

    response = client.post("/auth/validate-token", json = {
        "token": "fake token"
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_add_fitness_class_wrong_credentials(client, sample_member_auth, app):
    """Class creation endpoint denies missing, invalid, and unauthorized JWTs."""

    m_uid, m_pwd = sample_member_auth

    # no credentials
    response = client.post("/classes/", json = {
        TITLE: "Swimming",
        DATETIME: "2046-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    })
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR and response.json[MSG] == "Missing or invalid authorization header"

    # invalid credentials
    response = client.post("/classes/", json = {
        TITLE: "Swimming",
        DATETIME: "2046-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers = {"Authorization": "Bearer fake-token"})
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR and response.json[MSG] == "Missing or invalid authorization header"

    # wrong credentials
    with app.app_context():
        auth_member_token = create_access_token(
            identity="auth_member@example.com",
            additional_claims={"role": "member", "user_id": m_uid}
    )
    response = client.post("/classes/", json = {
        TITLE: "Swimming",
        DATETIME: "2046-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers = {"Authorization": f"Bearer {auth_member_token}"})
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR and response.json[MSG] == "role 'member' has insufficient permissions. require to be: ['admin', 'trainer']"