from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields

from app.apis import MSG
from app.db.fitness_classes import FITNESS_CLASS_COLLECTION, CLASS_ID, AVAILABLE_SPOTS, CAPACITY, DATETIME, TITLE, TRAINER_NAME
from app.db import DB
from app.db.utils import serialize_items

api = Namespace("classes", description="Fitness class endpoints")

_EXAMPLE_CLASS = {
    CLASS_ID: "class_001",
    TITLE: "Morning Yoga",
    DATETIME: "2026-02-20T09:00:00Z",
    CAPACITY: 20,
    AVAILABLE_SPOTS: 20,
    TRAINER_NAME: "Alex Trainer",
}

class_model = api.model(
    "FitnessClass",
    {
        CLASS_ID: fields.String(example=_EXAMPLE_CLASS[CLASS_ID]),
        TITLE: fields.String(example=_EXAMPLE_CLASS[TITLE]),
        DATETIME: fields.String(example=_EXAMPLE_CLASS[DATETIME]),
        CAPACITY: fields.Integer(example=_EXAMPLE_CLASS[CAPACITY]),
        AVAILABLE_SPOTS: fields.Integer(example=_EXAMPLE_CLASS[AVAILABLE_SPOTS]),
        TRAINER_NAME: fields.String(example=_EXAMPLE_CLASS[TRAINER_NAME]),
    },
)

create_class_model = api.model(
    "CreateClassRequest",
    {
        TITLE: fields.String(example=_EXAMPLE_CLASS[TITLE]),
        DATETIME: fields.String(example=_EXAMPLE_CLASS[DATETIME]),
        CAPACITY: fields.Integer(example=_EXAMPLE_CLASS[CAPACITY]),
        TRAINER_NAME: fields.String(example=_EXAMPLE_CLASS[TRAINER_NAME]),
    },
)


@api.route("/")
class ClassListResource(Resource):
    @api.response(
        HTTPStatus.OK,
        "Class list fetched",
        api.model(MSG, {MSG: fields.List(fields.Nested(class_model))}),
    )
    def get(self):
        """
        View class list.

        TODO:
        - Fetch upcoming classes from storage.
        """
        collection = DB.get_collection(FITNESS_CLASS_COLLECTION)
        
        classes = list(collection.find())

        return {
            MSG: serialize_items(classes),
        }, HTTPStatus.OK

    @api.expect(create_class_model)
    @api.response(HTTPStatus.CREATED, "Class created")
    @api.response(HTTPStatus.FORBIDDEN, "Only trainer/admin can create classes")
    def post(self):
        """
        Create class (trainer/admin).

        TODO:
        - Validate trainer/admin permissions.
        - Validate payload fields.
        - Save class in database.
        """
        _payload = request.json if isinstance(request.json, dict) else {}

        return {
            MSG: "TODO: implement class creation",
        }, HTTPStatus.NOT_IMPLEMENTED
