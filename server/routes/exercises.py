from flask import Blueprint, make_response, request

from models import Exercise, db
from schemas import exercise_detail_schema, exercise_schema, exercises_schema

exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercises_bp.get("")
def list_exercises():
    exercises = Exercise.query.order_by(Exercise.id).all()
    return make_response(exercises_schema.dump(exercises), 200)


@exercises_bp.get("/<int:id>")
def get_exercise(id):
    exercise = db.get_or_404(Exercise, id, description=f"Exercise {id} not found.")
    return make_response(exercise_detail_schema.dump(exercise), 200)


@exercises_bp.post("")
def create_exercise():
    data = exercise_schema.load(request.get_json(silent=True) or {})
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return make_response(exercise_schema.dump(exercise), 201)


@exercises_bp.delete("/<int:id>")
def delete_exercise(id):
    exercise = db.get_or_404(Exercise, id, description=f"Exercise {id} not found.")
    # Cascade on Exercise.workout_exercises removes the related join rows.
    db.session.delete(exercise)
    db.session.commit()
    return make_response("", 204)
