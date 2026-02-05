from app.apis.student import api as student_ns
from app.apis.hello import api as hello_ns
from app.config import Config
from app.db import DB

from http import HTTPStatus
from flask import Flask
from flask_restx import Api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    DB.init_app(app)

    api = Api(
        title="Students",
        version="1.0",
        description="A simple student record keeping API",
    )

    api.init_app(app)
    api.add_namespace(student_ns)
    api.add_namespace(hello_ns)

    @api.errorhandler(Exception)
    def handle_input_validation_error(error):
        return {"message": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR

    return app
