# internal exports
from app.db.fitness_classes import CAPACITY, DATETIME, TITLE, TRAINER_NAME
from app.db.bookings import CLASS_ID, USER_EMAIL
from app.db.users import get_user_by_user_id
from app.apis import MSG
# external import
import pytest
from http import HTTPStatus


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

# create 2 sample members specifically for testing within the booking endpoint
@pytest.fixture
def sample_member1(client):
    response = client.post("/auth/register", json ={
        "name": "sample_member1",
        "email": "member1@example.com",
        "phone": "+123-456-789-1011",
        "birth_date": "1995-01-15",
        "password": "secure_password_1"
    })
    assert response.status_code == HTTPStatus.CREATED
    return response.json["user_id"], response.json["access_token"]

@pytest.fixture
def sample_member2(client):
    response = client.post("/auth/register", json ={
        "name": "sample_member2",
        "email": "member2@example.com",
        "phone": "+123-456-789",
        "birth_date": "1995-01-15",
        "password": "secure_password_2"
    })
    assert response.status_code == HTTPStatus.CREATED
    return response.json["user_id"], response.json["access_token"]


#########################################################
# tests for POST method for 'bookings' endpoint

# correct fields
def test_make_booking_correct_fields(client, sample_class, sample_member1, sample_member2):
    
    m1_uid, m1_token = sample_member1
    m2_uid, m2_token = sample_member2
    m1_email = get_user_by_user_id(m1_uid)["email"]
    m2_email = get_user_by_user_id(m2_uid)["email"]
  
    response = client.post("/bookings/", json = {
        CLASS_ID: sample_class,
        USER_EMAIL: m1_email
    }, headers={"Authorization": f"Bearer {m1_token}"})
    assert response.status_code == HTTPStatus.CREATED