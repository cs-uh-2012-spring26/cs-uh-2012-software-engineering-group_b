"""Unit tests for booking endpoints.

This module validates booking creation and booking-list retrieval,
including important error paths around user/class validation.
"""

# internal exports
from app.db.fitness_classes import CAPACITY, DATETIME, TITLE, TRAINER_NAME
from app.db.bookings import CLASS_ID
from app.db.users import get_user_by_email
from app.apis import MSG
# external import
import pytest
from http import HTTPStatus
from uuid import uuid4
from flask_jwt_extended import create_access_token


# create a sample class specifically for testing within the booking endpoint
@pytest.fixture
def sample_class(client, trainer_headers):
    """Create and return a future class id used by booking tests."""
    unique_suffix = str(uuid4())[:8]

    response = client.post("/classes/", json = {
        TITLE: f"Water Kickboxing {unique_suffix}",
        DATETIME: "2037-02-20T09:00:00Z",
        CAPACITY: 10,
        TRAINER_NAME: f"Alex Bob {unique_suffix}"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.CREATED
    return response.json[MSG]["class_id"]

# create 2 sample members specifically for testing within the booking endpoint
@pytest.fixture
def sample_member1(client, app):
    """Return member1 tuple (user_id, token), creating user if needed."""
    sample_member1_exists = (get_user_by_email("member1@example.com") is not None)

    response = client.post("/auth/register", json ={
        "name": "sample_member1",
        "email": "member1@example.com",
        "phone": "+123-456-789-1011",
        "birth_date": "1995-01-15",
        "password": "secure_password_1"
    })
    if not sample_member1_exists:
        assert response.status_code == HTTPStatus.CREATED
        return response.json["user_id"], response.json["access_token"]
    else:
        assert response.status_code == HTTPStatus.CONFLICT
        with app.app_context():
            sample_member1_token = create_access_token (
                identity="member1@example.com",
                additional_claims={"role": "member", "user_id": get_user_by_email("member1@example.com")["user_id"]}
            )
        return get_user_by_email("member1@example.com")["user_id"], sample_member1_token

@pytest.fixture
def sample_member2(client, app):
    """Return member2 tuple (user_id, token), creating user if needed."""
    sample_member2_exists = (get_user_by_email("member2@example.com") is not None)

    response = client.post("/auth/register", json ={
        "name": "sample_member2",
        "email": "member2@example.com",
        "phone": "+123-456-789-1012",
        "birth_date": "2995-01-15",
        "password": "secure_password_2"
    })
    if not sample_member2_exists:
        assert response.status_code == HTTPStatus.CREATED
        return response.json["user_id"], response.json["access_token"]
    else:
        assert response.status_code == HTTPStatus.CONFLICT
        with app.app_context():
            sample_member2_token = create_access_token (
                identity="member2@example.com",
                additional_claims={"role": "member", "user_id": get_user_by_email("member2@example.com")["user_id"]}
            )
        return get_user_by_email("member2@example.com")["user_id"], sample_member2_token


#########################################################
# tests for POST method for 'bookings' endpoint

def test_make_booking_correct_fields(client, sample_class, sample_member1):
    """Booking succeeds for an authenticated member and valid class."""
    
    _, m1_token = sample_member1
  
    response = client.post("/bookings/", json = {
        CLASS_ID: sample_class
    }, headers={"Authorization": f"Bearer {m1_token}"})
    assert response.status_code == HTTPStatus.CREATED

def test_make_booking_incorrect_fields(client, sample_class, sample_member1, app):
    """Booking endpoint returns expected errors for invalid scenarios."""

    _, m1_token = sample_member1

    # missing class id
    response = client.post("/bookings/", json = {
    }, headers={"Authorization": f"Bearer {m1_token}"})
    assert response.status_code == HTTPStatus.BAD_REQUEST and response.json[MSG] == "class_id is required"

    # fake member token
    with app.app_context():
        fake_member_token = create_access_token (
            identity="fake_member@example.com",
            additional_claims={"role": "member", "user_id": "fake_user_id"}
        )
    # non-existent user (email)
    response = client.post("/bookings/", json = {
        CLASS_ID: sample_class
    }, headers={"Authorization": f"Bearer {fake_member_token}"})
    assert response.status_code == HTTPStatus.NOT_FOUND and response.json[MSG] == "User not found"

    # non-existent class
    response = client.post("/bookings/", json = {
        CLASS_ID: "fake class id"
    }, headers={"Authorization": f"Bearer {m1_token}"})
    assert response.status_code == HTTPStatus.NOT_FOUND and response.json[MSG] == "Class not found"

def test_view_booking_list_correct_fields(client, sample_class, trainer_headers):
    """Trainer can retrieve booking list for a valid class id."""
    
    response = client.get(f"/bookings/class/{sample_class}", headers=trainer_headers)
    assert response.status_code == HTTPStatus.OK