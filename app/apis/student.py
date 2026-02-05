from flask_restx import Namespace, Resource, fields
from app.apis import MSG
from app.db.students import StudentResource
from app.db.students import NAME, EMAIL, SENIORITY
from http import HTTPStatus
from flask import request

api = Namespace("students", description="Endpoint for students")

_EXAMPLE_STUDENT_1 = {
    NAME: "Jane Doe",
    EMAIL: "jane.doe@software.io",
    SENIORITY: "sophomore",
}

_EXAMPLE_STUDENT_2 = {
    NAME: "John Doe",
    EMAIL: "john.doe@software.io",
    SENIORITY: "first-year",
}

STUDENT_CREATE_FLDS = api.model(
    "NewStudentEntry",
    {
        NAME: fields.String(example=_EXAMPLE_STUDENT_1[NAME]),
        EMAIL: fields.String(example=_EXAMPLE_STUDENT_1[EMAIL]),
        SENIORITY: fields.String(enum=["first-year", "sophomore", "junior", "senior"]),
    },
)


@api.route("/")
class StudentList(Resource):
    @api.doc(
        params={
            "name": "Filter student list by student name (partial matches allowed)",
            "seniority": "Filter student list by student seniority (Exact seniority match)",
        }
    )
    @api.response(
        HTTPStatus.OK,
        "Success",
        api.model(
            "All Students",
            {
                MSG: fields.List(
                    fields.Nested(STUDENT_CREATE_FLDS),
                    example=[_EXAMPLE_STUDENT_1, _EXAMPLE_STUDENT_2],
                )
            },
        ),
    )
    def get(self):
        name = request.args.get("name")
        seniority = request.args.get("seniority")
        student_resource = StudentResource()
        student_list = student_resource.get_students(name, seniority)
        return {MSG: student_list}, HTTPStatus.OK

    @api.expect(STUDENT_CREATE_FLDS)
    @api.response(
        HTTPStatus.OK,
        "Success",
        api.model(
            "Create Student",
            {MSG: fields.String("Student created with id: XXXXXXXXXXXXXXXXXXXXXXXX")},
        ),
    )
    @api.response(
        HTTPStatus.NOT_ACCEPTABLE,
        "Invalid Request",
        api.model(
            "Create Student: Bad Request",
            {MSG: fields.String("Invalid value provided for one of the fields")},
        ),
    )
    def post(self):
        assert isinstance(request.json, dict)
        name = request.json.get(NAME)
        email = request.json.get(EMAIL)
        seniority = request.json.get(SENIORITY)
        if not (
            isinstance(name, str)
            and len(name) > 0
            and isinstance(email, str)
            and len(email) > 0
            and isinstance(seniority, str)
            and seniority.lower() in ["first-year", "sophomore", "junior", "senior"]
        ):
            return {
                MSG: "Invalid value provided for one of the fields"
            }, HTTPStatus.NOT_ACCEPTABLE
        student_resource = StudentResource()
        student_id = student_resource.create_student(name, email, seniority)
        return {MSG: f"Student created with id: {student_id}"}, HTTPStatus.OK


@api.route("/<email>")
@api.param("email", "Student email to use for lookup")
@api.response(
    HTTPStatus.NOT_FOUND,
    "Student Not Found",
    api.model("Student: Not Found", {MSG: fields.String("Student not found")}),
)
class Student(Resource):
    @api.doc("Get a specific student, identified by email")
    @api.response(HTTPStatus.OK, "Success", STUDENT_CREATE_FLDS)
    def get(self, email):
        student_resource = StudentResource()
        student = student_resource.get_student_by_email(email)

        if student is None:
            return {MSG: "Student not found"}, HTTPStatus.NOT_FOUND

        return {MSG: student}, HTTPStatus.OK

    @api.expect(STUDENT_CREATE_FLDS)
    @api.doc("Update a specific student, identified by email")
    @api.response(
        HTTPStatus.OK,
        "Success",
        api.model("Update Student", {MSG: fields.String("Student updated")}),
    )
    @api.response(
        HTTPStatus.NOT_ACCEPTABLE,
        "Student Update Information Not Acceptable",
        api.model(
            "Update Student: Not Acceptable",
            {MSG: fields.String("Invalid value provided for one of the fields")},
        ),
    )
    def put(self, email):
        assert isinstance(request.json, dict)
        name = request.json.get(NAME)
        seniority = request.json.get(SENIORITY)
        new_email = request.json.get(EMAIL)
        if not (
            isinstance(name, str)
            and len(name) > 0
            and isinstance(new_email, str)
            and len(new_email) > 0
            and isinstance(seniority, str)
            and seniority.lower() in ["first-year", "sophomore", "junior", "senior"]
        ):
            return {
                MSG: "Invalid value provided for one of the fields"
            }, HTTPStatus.NOT_ACCEPTABLE

        student_resource = StudentResource()
        updated_student = student_resource.update_student(
            email, name, new_email, seniority
        )

        if updated_student is None:
            return {MSG: "Student not found"}, HTTPStatus.NOT_FOUND

        return {MSG: "Student updated"}, HTTPStatus.OK
