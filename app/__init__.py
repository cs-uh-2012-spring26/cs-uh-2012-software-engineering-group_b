from app.apis.booking import api as booking_ns
from app.apis.fitness_class import api as fitness_class_ns
from app.apis.auth import api as auth
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
        title="Fitness Class Management System",
        version="1.0",
        description="API for class management and booking",
    )

    api.init_app(app)
    api.add_namespace(fitness_class_ns)
    api.add_namespace(booking_ns)
    api.add_namespace(auth)

    @api.errorhandler(Exception)
    def handle_input_validation_error(error):
        return {"message": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR

    return app
