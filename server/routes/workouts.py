from flask import Blueprint, make_response, request

from models import Exercise, Workout, WorkoutExercise, db
from schemas import (
    workout_detail_schema,
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")


@workouts_bp.get("")
def list_workouts():
    workouts = Workout.query.order_by(Workout.date, Workout.id).all()
    return make_response(workouts_schema.dump(workouts), 200)


@workouts_bp.get("/<int:id>")
def get_workout(id):
    workout = db.get_or_404(Workout, id, description=f"Workout {id} not found.")
    return make_response(workout_detail_schema.dump(workout), 200)


@workouts_bp.post("")
def create_workout():
    data = workout_schema.load(request.get_json(silent=True) or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return make_response(workout_schema.dump(workout), 201)


@workouts_bp.delete("/<int:id>")
def delete_workout(id):
    workout = db.get_or_404(Workout, id, description=f"Workout {id} not found.")
    # Cascade on Workout.workout_exercises removes the related join rows.
    db.session.delete(workout)
    db.session.commit()
    return make_response("", 204)


@workouts_bp.post("/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.get_or_404(Workout, workout_id, description=f"Workout {workout_id} not found.")
    exercise = db.get_or_404(Exercise, exercise_id, description=f"Exercise {exercise_id} not found.")

    data = workout_exercise_schema.load(request.get_json(silent=True) or {})
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return make_response(workout_exercise_schema.dump(workout_exercise), 201)
