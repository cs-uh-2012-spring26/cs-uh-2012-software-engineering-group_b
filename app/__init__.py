from app.apis.booking import api as booking_ns
from app.apis.fitness_class import api as fitness_class_ns
from app.apis.auth import api as auth
from app.apis.telegram import api as telegram_ns
from app.config import Config
from app.db import DB

from http import HTTPStatus
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException

from app.apis import MSG
from app.exceptions import AppError


def create_app(test_config = None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if(test_config):
        app.config.update(test_config)

    jwt = JWTManager(app)

    DB.init_app(app)

    api = Api(
        title="Fitness Class booking and management system",
        version="(Sprint 1)",
        description=(
            "endpoints for booking, creating classes, and rudimentary account management\n\n"
            "Telegram setup for reminders: open https://t.me/CoachlyyBot, send /start, "
            "copy the chat ID the bot replies with, then save it with POST /auth/notification-preferences."
        ),
        authorizations={
            "Bearer Auth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": (
                    'Add a JWT token to the header with ** "Bearer &lt;JWT&gt;"** token to authorize. '
                    "For Telegram reminders, start the bot at https://t.me/CoachlyyBot"
                ),
            }
        },
        security="Bearer Auth",
    )

    api.init_app(app)
    api.add_namespace(fitness_class_ns)
    api.add_namespace(booking_ns)
    api.add_namespace(auth)
    api.add_namespace(telegram_ns)

    @api.errorhandler(AppError)
    def handle_application_error(error):
        return {MSG: error.message}, error.status_code

    @api.errorhandler(HTTPException)
    def handle_http_error(error):
        return {MSG: error.description}, error.code or HTTPStatus.BAD_REQUEST

    @api.errorhandler(Exception)
    def handle_unexpected_error(_error):
        return {MSG: "Internal server error"}, HTTPStatus.INTERNAL_SERVER_ERROR

    return app
