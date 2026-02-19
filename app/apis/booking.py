from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields

from app.apis import MSG
from app.db.bookings import (
    booking_exists_for_user,
    build_booking_document,
    create_booking,
    list_bookings_by_class,
)
from app.db.bookings import (
    BOOKING_ID,
    BOOKED_AT,
    CLASS_ID,
    PHONE,
    ROLE,
    STATUS,
    USER_EMAIL,
    USER_ID,
    USER_NAME,
)
from app.db.users import (
    EMAIL as USER_EMAIL_FIELD,
    NAME as USER_NAME_FIELD,
    ROLE as USER_ROLE_FIELD,
    ROLE_MEMBER,
    get_user_by_user_id,
)
from app.db.fitness_classes import decrement_available_spot, get_class_by_class_id

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
    @api.response(HTTPStatus.NOT_FOUND, "User not found")
    @api.response(HTTPStatus.NOT_FOUND, "Class not found")
    @api.response(HTTPStatus.FORBIDDEN, "Only members can book classes")
    def post(self):
        """
        Book class (member only in current SRS).

        TODO:
        - Validate authenticated user is a member. [ X ]
        - Check class availability. [ X ]
        - Prevent duplicate booking and save booking. [ X ]
        """
        _payload = request.json if isinstance(request.json, dict) else {}

        user_id = _payload.get(USER_ID)
        class_id = _payload.get(CLASS_ID)
        phone = _payload.get(PHONE)

        if not user_id or not class_id or not phone:
            return {
                MSG: f"{USER_ID}, {CLASS_ID}, and {PHONE} are required",
            }, HTTPStatus.BAD_REQUEST

        if booking_exists_for_user(user_id, class_id):
            return {MSG: "Booking already exists"}, HTTPStatus.CONFLICT

        fitness_class = get_class_by_class_id(class_id)
        if fitness_class is None:
            return {MSG: "Class not found"}, HTTPStatus.NOT_FOUND

        user = get_user_by_user_id(user_id)
        if user is None:
            return {MSG: "User not found"}, HTTPStatus.NOT_FOUND

        if user.get(USER_ROLE_FIELD) != ROLE_MEMBER:
            return {MSG: "Only members can book classes"}, HTTPStatus.FORBIDDEN

        booking_doc = build_booking_document(
            class_id=class_id,
            user_id=user_id,
            user_name=user.get(USER_NAME_FIELD, ""),
            user_email=user.get(USER_EMAIL_FIELD, ""),
            phone=phone,
            role=user.get(USER_ROLE_FIELD, ROLE_MEMBER),
        )

        if not decrement_available_spot(class_id):
            return {MSG: "Class is full"}, HTTPStatus.CONFLICT

        booking = create_booking(booking_doc)

        return {MSG: booking}, HTTPStatus.CREATED


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
        - Validate caller role. [ ]
        - Verify class exists. [ X ]
        - Fetch and return booking list by class. [ X ]
        """
        bookings = list_bookings_by_class(class_id)

        return {
            MSG: bookings,
        }, HTTPStatus.OK
