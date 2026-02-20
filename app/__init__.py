from app.apis.booking import api as booking_ns
from app.apis.fitness_class import api as fitness_class_ns
from app.apis.auth import api as auth
from app.config import Config
from app.db import DB

from http import HTTPStatus
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt = JWTManager(app)

    DB.init_app(app)

    api = Api(
<<<<<<< vl-t
        title="Fitness Class booking and management system",
        version="(Sprint 1)",
        description="endpoints for booking, creating classes, and rudimentary account management",
=======
        title="Fitness Class Management System",
        version="1.0",
        description="API for class management and booking",
        authorizations={
            "Bearer Auth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": 'Add a JWT token to the header with ** "Bearer &lt;JWT&gt;"** token to authorize',
            }
        },
        security="Bearer Auth",
>>>>>>> main
    )

    api.init_app(app)
    api.add_namespace(fitness_class_ns)
    api.add_namespace(booking_ns)
    api.add_namespace(auth)

    @api.errorhandler(Exception)
    def handle_input_validation_error(error):
        return {"message": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR

    return app
