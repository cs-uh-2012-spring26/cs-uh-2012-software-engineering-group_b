import pytest
from dotenv import load_dotenv
import yaml

from app import create_app
from app.db import DB
from app.db.students import StudentResource


@pytest.fixture(scope="session", autouse=True)
def app():
    load_dotenv()
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()


def load_students():
    """
    Load student data from the YAML fixture file.
    """
    with open("tests/unit/fixtures/students.yaml", "r") as file:
        students = yaml.safe_load(file)

    return students


@pytest.fixture(scope="session")
def students():
    return load_students()


@pytest.fixture(scope="function", autouse=True)
def seeded_students_db(students):
    """
    Preload the mock 'students' collection with data from the YAML fixture.
    """
    student_resource = StudentResource()
    student_resource.delete_all_students()  # Clear existing data
    student_resource.add_multiple_students(students)


@pytest.fixture(scope="function", params=load_students())
def single_student(request):
    return request.param
