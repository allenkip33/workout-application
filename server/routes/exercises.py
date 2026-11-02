from flask import Blueprint, make_response

exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercises_bp.get("")
def list_exercises():
    return make_response({"message": "Not implemented"}, 501)


@exercises_bp.get("/<int:id>")
def get_exercise(id):
    return make_response({"message": "Not implemented"}, 501)


@exercises_bp.post("")
def create_exercise():
    return make_response({"message": "Not implemented"}, 501)


@exercises_bp.delete("/<int:id>")
def delete_exercise(id):
    return make_response({"message": "Not implemented"}, 501)
