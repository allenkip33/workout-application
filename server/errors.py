from flask import make_response
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from models import db


def register_error_handlers(app):
    """Return every error as JSON so API clients get a consistent shape."""

    @app.errorhandler(ValidationError)
    def handle_schema_error(err):
        return make_response({"errors": err.messages}, 400)

    # Raised by the model-level @validates methods.
    @app.errorhandler(ValueError)
    def handle_model_error(err):
        db.session.rollback()
        return make_response({"errors": [str(err)]}, 400)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        db.session.rollback()
        return make_response({"errors": [str(err.orig)]}, 409)

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return make_response({"errors": [err.description]}, err.code)
