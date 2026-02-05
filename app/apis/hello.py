from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from app.apis import MSG

api = Namespace(
    "hello", description="Simple hello world endpoint for making sure app works"
)

hello_model = api.model("HelloWorld", {MSG: fields.String(example="hello world!")})


@api.route("/")
@api.response(HTTPStatus.OK, "HelloWorld: Success", hello_model)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """

    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {MSG: "hello world!"}, HTTPStatus.OK

