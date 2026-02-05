# The tests:
#   - test_list_students_count
#   - test_student_match_seed_data
# are sanity checks to ensure that the data is seeded correctly.
# They are not so much for testing application logic, but rather to ensure that the test setup is operating as expected.
from http import HTTPStatus
from app.apis import MSG
from app.db.students import NAME, EMAIL, SENIORITY
from tests.utils import assert_items_equal
from unittest.mock import patch


def test_list_students_count(client, students):
    """
    Test that the number of students returned by the students/ endpoint matches the seeded data.
    """
    response = client.get("/students/")
    assert response.status_code == 200

    data = response.json
    assert isinstance(data, dict)
    assert isinstance(data.get(MSG), list)
    assert len(data[MSG]) == len(students)  # Compare to students in students.yaml


def test_students_match_seed_data(client, single_student):
    """
    Test that a single seeded student is returned by the students/ endpoint and matches the seed data.
    """
    response = client.get("/students/")
    assert response.status_code == 200

    data = response.json
    assert isinstance(data, dict)
    assert isinstance(data.get(MSG), list)

    data_dict = {s["email"]: s for s in data[MSG]}
    assert (
        single_student["email"] in data_dict
    ), f"Student with email {single_student['email']} not found in response."

    retrieved_student = data_dict[single_student["email"]]
    assert (
        retrieved_student["name"] == single_student["name"]
    ), f"Mismatch in 'name' for {single_student['email']}"
    assert (
        retrieved_student["email"] == single_student["email"]
    ), f"Mismatch in 'email' for {single_student['email']}"
    assert (
        retrieved_student["seniority"] == single_student["seniority"]
    ), f"Mismatch in 'seniority' for {single_student['email']}"


def test_filter_students_by_name(client):
    response = client.get(f"students/?{NAME}=Sarah")
    assert isinstance(response.json.get(MSG), list)
    assert len(response.json.get(MSG)) > 0
    for student in response.json.get(MSG):
        assert "Sarah" in student[NAME]


def test_filter_students_by_seniority(client):
    response = client.get(f"students/?{SENIORITY}=senior")
    assert isinstance(response.json.get(MSG), list)
    assert len(response.json.get(MSG)) > 0
    for student in response.json.get(MSG):
        assert "senior" in student[SENIORITY]


def test_get_existing_student(client):
    test_email = "sarah@nyu.edu"
    response = client.get(f"students/{test_email}")
    assert response.status_code == 200
    assert_items_equal(
        response.json.get(MSG),
        {
            "name": "Sarah",
            "email": test_email,
            "seniority": "senior",
        },
    )


def test_get_non_existing_student(client):
    response = client.get("students/non_existent@nyu.edu")
    assert response.status_code == 404
    assert response.json == {MSG: "Student not found"}


def test_create_student(client):
    new_student = {NAME: "John", EMAIL: "john@nyu.edu", SENIORITY: "junior"}

    response = client.post("students/", json=new_student)
    assert response.status_code == 200
    assert "Student created with id: " in response.json.get(MSG)

    # Check that the student was actually created
    response = client.get("students/john@nyu.edu")
    assert response.status_code == 200
    assert_items_equal(response.json.get(MSG), new_student)


def test_create_student_with_no_name_fails(client):
    response = client.post(
        "/students/",
        json={
            NAME: "",
            EMAIL: "iexist@nyu.edu",
            SENIORITY: "junior",
        },
    )
    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE


def test_update_student(client):
    student_email = "sarah@nyu.edu"
    updated_student = {
        "name": "Sarah",
        "email": student_email,
        "seniority": "first-year",
    }
    response = client.put(f"students/{student_email}", json=updated_student)
    assert response.status_code == 200
    assert response.json == {MSG: "Student updated"}

    # Check that the student was actually updated
    response = client.get(f"students/{student_email}")
    assert response.status_code == 200
    assert_items_equal(response.json.get(MSG), updated_student)


def test_update_student_with_no_name_fails(client, single_student):
    response = client.put(
        f"/students/{single_student[EMAIL]}",
        json={
            NAME: "",
            EMAIL: "my_brand_new_email@nyu.edu",
            SENIORITY: "senior",
        },
    )
    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE


def test_update_non_existing_student(client):
    student_email = "nonexistent@nyu.edu"
    updated_student = {
        "name": "Nonexistent",
        "email": student_email,
        "seniority": "first-year",
    }
    response = client.put(f"students/{student_email}", json=updated_student)
    assert response.status_code == 404
    assert response.json == {MSG: "Student not found"}

    # Check that the student was not created
    response = client.get(f"students/{student_email}")
    assert response.status_code == 404


def test_exception_returns_500(client):
    """Test that in case of unexpected error, the server still returns a well formed api response"""

    # Simulate an unexpected error using mocking
    with patch("app.db.students.StudentResource.get_students") as func:
        func.side_effect = ValueError

        resp = client.get("students/")
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert isinstance(resp.json, dict)
        assert isinstance(resp.json.get(MSG), str)
