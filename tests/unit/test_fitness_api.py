from http import HTTPStatus

from app.apis import MSG


def test_list_classes_template_endpoint(client):
    response = client.get("/classes/")
    assert response.status_code == HTTPStatus.NOT_IMPLEMENTED
    assert response.json == {MSG: "TODO: implement class listing with filters"}


def test_book_class_template_endpoint(client):
    response = client.post("/bookings/", json={"class_id": "class_001"})
    assert response.status_code == HTTPStatus.NOT_IMPLEMENTED
    assert response.json == {MSG: "TODO: implement class booking"}
