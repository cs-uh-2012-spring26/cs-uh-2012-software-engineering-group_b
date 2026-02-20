from http import HTTPStatus

from app.apis import MSG

from app.db.fitness_classes import CAPACITY, DATETIME, TITLE, TRAINER_NAME

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

