import pytest

from app.db.fitness_classes import CAPACITY, DATETIME, TITLE, TRAINER_NAME
from app.db.bookings import CLASS_ID, USER_EMAIL

from http import HTTPStatus

from app.apis import MSG

# create a sample class specifically for testing within the booking endpoint
@pytest.fixture
def sample_class(client, trainer_headers):
    response = client.post("/classes/", json = {
        TITLE: "Water Kickboxing",
        DATETIME: "2037-02-20T09:00:00Z",
        CAPACITY: 3,
        TRAINER_NAME: "Alex Bob"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.CREATED
    return response.json[MSG]["class_id"]


# tests for POST method for 'bookings' endpoint

# incorrect user provided
def test_make_booking_correct_fields(client, sample_class, member_headers):
    response = client.post("/bookings/", json = {
        CLASS_ID: sample_class,
        USER_EMAIL: "member@example.com"
    }, headers=member_headers)
    assert response.status_code == HTTPStatus.NOT_FOUND


