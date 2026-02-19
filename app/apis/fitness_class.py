from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields

from datetime import datetime as dt_mod, timezone

from app.apis import MSG
from app.db.fitness_classes import CLASS_ID, AVAILABLE_SPOTS, CAPACITY, DATETIME, TITLE, TRAINER_NAME
from app.db.fitness_classes import build_fitness_class_document, create_fitness_class

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
    @api.doc(params={"trainer": "Optional trainer filter"})
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
        - Apply optional trainer filter.
        """
        _trainer_filter = request.args.get("trainer")
        _ = _trainer_filter

        return {
            MSG: "TODO: implement class listing with filters",
        }, HTTPStatus.NOT_IMPLEMENTED

    @api.expect(create_class_model)
    @api.response(HTTPStatus.CREATED, "Class created")
    @api.response(HTTPStatus.FORBIDDEN, "Only trainer/admin can create classes")
    def post(self):
        """
        Create class (trainer/admin).

        TODO:
        - Validate trainer/admin permissions.
        - Validate payload fields. [ X ]
        - Save class in database. [ X ]
        """
        _payload = request.json if isinstance(request.json, dict) else {}

        # extract fields
        title = _payload.get(TITLE)
        dt = _payload.get(DATETIME)
        capacity = _payload.get(CAPACITY)
        trainer_name = _payload.get(TRAINER_NAME)

        # validate payload fields
        if not title or not dt or not capacity or not trainer_name:
            return {
                MSG: f"{TITLE}, {DATETIME}, {CAPACITY}, and {TRAINER_NAME} are required"
            }, HTTPStatus.BAD_REQUEST
        
        # format checks
        if not isinstance(capacity, int) or capacity <= 0:
            return {
                MSG: f"{CAPACITY} must be a positive integer"
            }, HTTPStatus.BAD_REQUEST
        try:
            parsed_dt = dt_mod.fromisoformat(dt.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return {
                MSG: f"{DATETIME} must be a valid datetime string"
            }, HTTPStatus.BAD_REQUEST
        if not isinstance(title, str) or not isinstance(trainer_name, str) or not title.strip() or not trainer_name.strip():
            return {
                MSG: f"{TITLE} and {TRAINER_NAME} must be non-empty strings"
            }, HTTPStatus.BAD_REQUEST
        
        # logic checks
        if parsed_dt <= dt_mod.now(timezone.utc):
            return {
                MSG: f"{DATETIME} must not be in the past"
            }, HTTPStatus.BAD_REQUEST

        # HERE WE WILL VALIDATE PERMISSIONS 
        
        
        # build and insert
        doc = build_fitness_class_document(title, dt, capacity, trainer_name)
        fitness_class = create_fitness_class(doc)

        return {MSG: fitness_class}, HTTPStatus.CREATED
    

