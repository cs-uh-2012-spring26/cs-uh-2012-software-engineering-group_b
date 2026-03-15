from http import HTTPStatus
from uuid import uuid4

from app.apis import MSG

from app.db.bookings import build_booking_document, create_booking
from app.db.fitness_classes import CAPACITY, DATETIME, TITLE, TRAINER_NAME
from app.db.fitness_classes import CLASS_ID, build_fitness_class_document, create_fitness_class

# tests for POST method for 'classes' endpoint

# valid object passed
def test_add_fitness_class_correct_fields(client, trainer_headers):
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.CREATED


def test_send_class_reminders_success(client, trainer_headers, monkeypatch):
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

    called = {}

    def _fake_send_class_reminders(recipient_emails, fitness_class, sender_email):
        called["recipient_emails"] = recipient_emails
        called["fitness_class"] = fitness_class
        called["sender_email"] = sender_email
        return {"sent_count": len(recipient_emails), "recipients": recipient_emails}

    monkeypatch.setattr("app.apis.fitness_class.send_class_reminders", _fake_send_class_reminders)

    response = client.post(f"/classes/{class_id}/reminders", headers=trainer_headers)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json()["sent_count"] == 1
    assert response.get_json()[MSG] == "Reminder emails sent"
    assert called["sender_email"] == "noreply@coachly.dev"
    assert called["recipient_emails"] == ["jane.member@example.com"]
    assert called["fitness_class"][CLASS_ID] == fitness_class[CLASS_ID]


def test_send_class_reminders_no_attendees(client, trainer_headers):
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
    response = client.post(f"/classes/class_{uuid4()}/reminders", headers=trainer_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.get_json()[MSG] == "Class not found"


def test_send_class_reminders_past_class(client, trainer_headers):
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

# missing required field
def test_add_fitness_class_missing_field(client, trainer_headers):
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

