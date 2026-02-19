from http import HTTPStatus

from app.apis import MSG

from app.db.fitness_classes import CAPACITY, DATETIME, TITLE, TRAINER_NAME

# tests for POST method

# valid object passed
def test_add_fitness_class_correct_fields(client):
    response = client.post("/classes/", json = {
        TITLE: "Morning Yoga",
        DATETIME: "2036-02-20T09:00:00Z",
        CAPACITY: 20,
        TRAINER_NAME: "Alex Trainer"
    })
    assert response.status_code == HTTPStatus.CREATED





