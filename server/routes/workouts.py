from flask import Blueprint, make_response

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")


@workouts_bp.get("")
def list_workouts():
    return make_response({"message": "Not implemented"}, 501)


@workouts_bp.get("/<int:id>")
def get_workout(id):
    return make_response({"message": "Not implemented"}, 501)


@workouts_bp.post("")
def create_workout():
    return make_response({"message": "Not implemented"}, 501)


@workouts_bp.delete("/<int:id>")
def delete_workout(id):
    return make_response({"message": "Not implemented"}, 501)


@workouts_bp.post("/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    return make_response({"message": "Not implemented"}, 501)
