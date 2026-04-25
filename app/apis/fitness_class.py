from http import HTTPStatus
import logging
from os import environ

from flask import request
from flask_restx import Namespace, Resource, fields
from app.apis.decorators import require_roles

from app.apis import MSG
from app.db.fitness_classes import (
    FITNESS_CLASS_COLLECTION,
    CLASS_ID,
    AVAILABLE_SPOTS,
    CAPACITY,
    DATETIME,
    TITLE,
    TRAINER_NAME,
)
from app.exceptions import AppError
from app.services.fitness_class_service import FitnessClassService

from app.db import DB
from app.db.utils import serialize_items

api = Namespace("classes", description="    Endpoint for viewing and creating classes")

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
    @api.response(HTTPStatus.BAD_REQUEST, "Invalid payload")
    def get(self):
        """
        SEE CLASS LIST: allowed for all users
        """
        collection = DB.get_collection(FITNESS_CLASS_COLLECTION)
        
        classes = list(collection.find())

        return {
            MSG: serialize_items(classes),
        }, HTTPStatus.OK

    @api.expect(create_class_model)
    @api.response(HTTPStatus.CREATED, "Class created")
    @api.response(HTTPStatus.CONFLICT, "Class already exists")
    @api.response(HTTPStatus.FORBIDDEN, "Only trainer/admin can create classes")
    @api.response(HTTPStatus.BAD_REQUEST, "Invalid fields")
    @require_roles(["trainer", "admin"])
    def post(self):
        """
        CREATE NEW CLASS: allowed for trainers/admins
        """
        _payload = request.json if isinstance(request.json, dict) else {}

        try:
            fitness_class = FitnessClassService.create_class(_payload)
        except AppError as exc:
            return {MSG: exc.message}, exc.status_code

        return {MSG: fitness_class}, HTTPStatus.CREATED


@api.route("/<string:class_id>/reminders")
@api.param("class_id", "Class identifier")
class ClassReminderResource(Resource):
    @api.response(HTTPStatus.OK, "Reminder notifications sent")
    @api.response(HTTPStatus.BAD_REQUEST, "Class already started or no attendees")
    @api.response(HTTPStatus.NOT_FOUND, "Class not found")
    @api.response(HTTPStatus.FORBIDDEN, "Only trainers can send reminders")
    @require_roles(["trainer"])
    def post(self, class_id: str):
        """
        SEND REMINDER NOTIFICATIONS: allowed for trainers only
        """
        try:
            send_result = FitnessClassService.send_reminders(
                class_id=class_id,
                sender_email=environ.get("SENDGRID_FROM_EMAIL") or "noreply@coachly.dev",
            )
        except AppError as exc:
            if exc.status_code == HTTPStatus.BAD_GATEWAY:
                logging.exception("Failed to send reminder emails for class_id=%s", class_id)
            return {MSG: exc.message}, exc.status_code

        return send_result, HTTPStatus.OK
    

