from app.apis import MSG


def test_hello(client):
    response = client.get("/hello/")
    assert response.status_code == 200
    assert response.json == {MSG: "hello world!"}
