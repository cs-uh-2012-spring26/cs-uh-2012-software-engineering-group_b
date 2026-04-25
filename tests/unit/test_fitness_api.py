"""Unit tests for the classes namespace.

Coverage focus:
- class creation validation,
- reminder endpoint behavior,
- expected success and failure responses.
"""

from http import HTTPStatus
from uuid import uuid4

from app.apis import MSG

from app.db.bookings import BookingRole, BookingUser, build_booking_document, create_booking
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
            booking_user=BookingUser(
                user_id=f"user_{uuid4()}",
                user_name="Jane Member",
                user_email="jane.member@example.com",
                phone="+1-555-555-0100",
                role=BookingRole.MEMBER,
            ),
        )
    )

    mocked_send = mocker.patch(
        "app.services.notification_service.NotificationService.send_for_bookings",
        return_value={"sent_count": 1, "recipients": ["jane.member@example.com"]},
    )

    response = client.post(f"/classes/{class_id}/reminders", headers=trainer_headers)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json()["sent_count"] == 1
    assert response.get_json()[MSG] == "Reminder notifications sent"
    mocked_send.assert_called_once()
    called_kwargs = mocked_send.call_args.kwargs
    assert called_kwargs["sender_email"] == "noreply@coachly.dev"
    assert called_kwargs["fitness_class"][CLASS_ID] == fitness_class[CLASS_ID]
    assert isinstance(called_kwargs["bookings"], list)

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

def test_generate_one_time_class():
    """One-time recurrence returns only the start date."""
    from app.db.fitness_classes import generate_recurring_instances
    
    start_dt = "2036-05-15T10:00:00Z"
    instances = generate_recurring_instances(start_dt, "one_time", None)
    
    assert len(instances) == 1
    assert instances[0] == start_dt

def test_generate_daily_class_with_end_date():
    """Daily recurrence generates instances until end date."""
    from app.db.fitness_classes import generate_recurring_instances
    
    start_dt = "2036-05-15T10:00:00Z"
    end_dt = "2036-05-17T10:00:00Z"
    instances = generate_recurring_instances(start_dt, "daily", end_dt)
    
    assert len(instances) == 3  # 15th, 16th, 17th
    assert instances[0] == "2036-05-15T10:00:00Z"
    assert instances[1] == "2036-05-16T10:00:00Z"
    assert instances[2] == "2036-05-17T10:00:00Z"

def test_generate_weekly_class_with_end_date():
    """Weekly recurrence generates instances at 7-day intervals."""
    from app.db.fitness_classes import generate_recurring_instances
    
    start_dt = "2036-05-15T10:00:00Z"
    end_dt = "2036-06-01T10:00:00Z"
    instances = generate_recurring_instances(start_dt, "weekly", end_dt)
    
    assert len(instances) == 3  # 15th, 22nd, 29th (1st is past end)
    assert instances[0] == "2036-05-15T10:00:00Z"
    assert instances[1] == "2036-05-22T10:00:00Z"
    assert instances[2] == "2036-05-29T10:00:00Z"

def test_add_fitness_class_invalid_recurrence_type(client, trainer_headers):
    """Invalid recurrence_type is rejected."""
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer",
        "recurrence_type": "invalid_type"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_add_fitness_class_invalid_end_date_format(client, trainer_headers):
    """Invalid recurrence_end_date format is rejected."""
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer",
        "recurrence_type": "daily",
        "recurrence_end_date": "not-a-date"
    }, headers=trainer_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST