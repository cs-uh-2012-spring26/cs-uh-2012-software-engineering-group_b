from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields

from app.apis import MSG
from app.db.bookings import (
    BOOKING_ID,
    BOOKED_AT,
    CLASS_ID,
    CREATED_AT,
    PHONE,
    ROLE,
    STATUS,
    USER_EMAIL,
    USER_ID,
    USER_NAME,
)

api = Namespace("bookings", description="Booking endpoints")

_EXAMPLE_BOOKING = {
    BOOKING_ID: "booking_001",
    CLASS_ID: "class_001",
    USER_ID: "user_001",
    USER_NAME: "Jane Member",
    USER_EMAIL: "jane.member@example.com",
    PHONE: "+971-504-555-0101",
    ROLE: "member",
    STATUS: "confirmed",
    BOOKED_AT: "2026-02-15T20:30:00Z",
    CREATED_AT: "2026-02-15T20:30:00Z",
}

booking_model = api.model(
    "Booking",
    {
        BOOKING_ID: fields.String(example=_EXAMPLE_BOOKING[BOOKING_ID]),
        CLASS_ID: fields.String(example=_EXAMPLE_BOOKING[CLASS_ID]),
        USER_ID: fields.String(example=_EXAMPLE_BOOKING[USER_ID]),
        USER_NAME: fields.String(example=_EXAMPLE_BOOKING[USER_NAME]),
        USER_EMAIL: fields.String(example=_EXAMPLE_BOOKING[USER_EMAIL]),
        PHONE: fields.String(example=_EXAMPLE_BOOKING[PHONE]),
        ROLE: fields.String(example=_EXAMPLE_BOOKING[ROLE], enum=["guest", "member"]),
        STATUS: fields.String(example=_EXAMPLE_BOOKING[STATUS], enum=["confirmed", "cancelled"]),
        BOOKED_AT: fields.String(example=_EXAMPLE_BOOKING[BOOKED_AT]),
        CREATED_AT: fields.String(example=_EXAMPLE_BOOKING[CREATED_AT]),
    },
)

create_booking_model = api.model(
    "CreateBookingRequest",
    {
        CLASS_ID: fields.String(example=_EXAMPLE_BOOKING[CLASS_ID]),
        USER_ID: fields.String(example=_EXAMPLE_BOOKING[USER_ID]),
        PHONE: fields.String(example=_EXAMPLE_BOOKING[PHONE]),
    },
)


@api.route("/")
class BookingResource(Resource):
    @api.expect(create_booking_model)
    @api.response(HTTPStatus.CREATED, "Booking created")
    @api.response(HTTPStatus.CONFLICT, "Class full or duplicate booking")
    def post(self):
        """
        Book class (member only in current SRS).

        TODO:
        - Validate authenticated user is a member.
        - Check class availability.
        - Prevent duplicate booking and save booking.
        """
        _payload = request.json if isinstance(request.json, dict) else {}

        return {MSG: "TODO: implement class booking"}, HTTPStatus.NOT_IMPLEMENTED


@api.route("/class/<string:class_id>")
@api.param("class_id", "Class identifier")
class BookingListByClassResource(Resource):
    @api.response(
        HTTPStatus.OK,
        "Booking list fetched",
        api.model("BookingListResponse", {MSG: fields.List(fields.Nested(booking_model))}),
    )
    @api.response(HTTPStatus.FORBIDDEN, "Only trainer/admin can view booking list")
    def get(self, class_id: str):
        """
        View booking list for a class (trainer/admin).

        TODO:
        - Validate caller role.
        - Verify class exists.
        - Fetch and return booking list by class.
        """
        _ = class_id
        return {
            MSG: "TODO: implement booking list retrieval by class",
        }, HTTPStatus.NOT_IMPLEMENTED
