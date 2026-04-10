"""Unit tests for the classes namespace.

Coverage focus:
- class creation validation,
- reminder endpoint behavior,
- expected success and failure responses.
"""

from http import HTTPStatus
from uuid import uuid4

from app.apis import MSG

from app.db.bookings import build_booking_document, create_booking
from app.db.fitness_classes import CAPACITY, DATETIME, TITLE, TRAINER_NAME
from app.db.fitness_classes import CLASS_ID, build_fitness_class_document, create_fitness_class

def test_add_fitness_class_correct_fields(client, trainer_headers):
    """Create class succeeds when required fields are valid."""
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.CREATED


def test_add_fitness_class_duplicate_rejected(client, trainer_headers):
    """Creating the same class twice is rejected with conflict."""
    payload = {
        TITLE: "Lunch Pilates",
        DATETIME: "2036-04-20T12:00:00Z",
        CAPACITY: 15,
        TRAINER_NAME: "Alex Trainer",
    }

    first_response = client.post("/classes/", json=payload, headers=trainer_headers)
    assert first_response.status_code == HTTPStatus.CREATED

    second_response = client.post("/classes/", json=payload, headers=trainer_headers)
    assert second_response.status_code == HTTPStatus.CONFLICT
    assert second_response.json[MSG] == "Class already exists"


def test_send_class_reminders_success(client, trainer_headers, monkeypatch, mocker):
    """Trainer can send reminders to booked attendees before class start."""
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "noreply@coachly.dev")

    class_id = f"class_{uuid4()}"
    fitness_class = create_fitness_class(
        build_fitness_class_document(
            title="Morning Yoga",
            dt="2036-02-20T09:00:00Z",
            capacity=20,
            trainer_name="Alex Trainer",
            class_id=class_id,
        )
    )

    create_booking(
        build_booking_document(
            class_id=class_id,
            user_id=f"user_{uuid4()}",
            user_name="Jane Member",
            user_email="jane.member@example.com",
            phone="+1-555-555-0100",
            role="member",
        )
    )

    mocked_send = mocker.patch(
        "app.apis.fitness_class.send_class_reminders",
        return_value={"sent_count": 1, "recipients": ["jane.member@example.com"]},
    )

    response = client.post(f"/classes/{class_id}/reminders", headers=trainer_headers)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json()["sent_count"] == 1
    assert response.get_json()[MSG] == "Reminder emails sent"
    mocked_send.assert_called_once()
    called_kwargs = mocked_send.call_args.kwargs
    assert called_kwargs["sender_email"] == "noreply@coachly.dev"
    assert called_kwargs["recipient_emails"] == ["jane.member@example.com"]
    assert called_kwargs["fitness_class"][CLASS_ID] == fitness_class[CLASS_ID]


def test_send_class_reminders_no_attendees(client, trainer_headers):
    """Reminder request fails when class has no bookings."""
    class_id = f"class_{uuid4()}"
    create_fitness_class(
        build_fitness_class_document(
            title="Core Strength",
            dt="2036-03-15T11:00:00Z",
            capacity=10,
            trainer_name="Alex Trainer",
            class_id=class_id,
        )
    )

    response = client.post(f"/classes/{class_id}/reminders", headers=trainer_headers)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json()[MSG] == "No attendees found for this class"


def test_send_class_reminders_class_not_found(client, trainer_headers):
    """Reminder request returns not found for unknown class id."""
    response = client.post(f"/classes/class_{uuid4()}/reminders", headers=trainer_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.get_json()[MSG] == "Class not found"


def test_send_class_reminders_past_class(client, trainer_headers):
    """Reminder request is rejected when class datetime is in the past."""
    class_id = f"class_{uuid4()}"
    create_fitness_class(
        build_fitness_class_document(
            title="Past Pilates",
            dt="2020-01-10T08:00:00Z",
            capacity=10,
            trainer_name="Alex Trainer",
            class_id=class_id,
        )
    )

    response = client.post(f"/classes/{class_id}/reminders", headers=trainer_headers)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json()[MSG] == "Reminders can only be sent before the class starts"

def test_add_fitness_class_missing_field(client, trainer_headers):
    """Class creation rejects missing/invalid values for required inputs."""
    # missing title
    response = client.post("/classes/", json = {
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    
    # missing datetime
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
   
    #missing capacity
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    
    #missing trainer_name
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST

# invalid required fields
    # past date
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2010-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # invalid datetime string
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "epic!",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # empty trainer name
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "      "
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # empty title 
    response = client.post("/classes/", json = {
        TITLE: "      ",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST

# empty capacity 
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: None,
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST

