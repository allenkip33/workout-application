#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print("Seeding exercises...")
    push_up = Exercise(name="Push Up", category="strength", equipment_needed=False)
    squat = Exercise(name="Barbell Squat", category="strength", equipment_needed=True)
    run = Exercise(name="Treadmill Run", category="cardio", equipment_needed=True)
    plank = Exercise(name="Plank", category="balance", equipment_needed=False)
    stretch = Exercise(name="Hamstring Stretch", category="flexibility", equipment_needed=False)
    db.session.add_all([push_up, squat, run, plank, stretch])

    print("Seeding workouts...")
    upper = Workout(date=date(2026, 11, 1), duration_minutes=45, notes="Upper body and core.")
    legs = Workout(date=date(2026, 11, 2), duration_minutes=60, notes="Leg day, heavy squats.")
    cardio = Workout(date=date(2026, 11, 3), duration_minutes=30, notes="Easy cardio and mobility.")
    db.session.add_all([upper, legs, cardio])

    print("Seeding workout exercises...")
    db.session.add_all([
        WorkoutExercise(workout=upper, exercise=push_up, sets=4, reps=15),
        WorkoutExercise(workout=upper, exercise=plank, sets=3, duration_seconds=60),
        WorkoutExercise(workout=legs, exercise=squat, sets=5, reps=5),
        WorkoutExercise(workout=legs, exercise=stretch, duration_seconds=120),
        WorkoutExercise(workout=cardio, exercise=run, duration_seconds=1200),
        WorkoutExercise(workout=cardio, exercise=stretch, duration_seconds=90),
    ])

    db.session.commit()
    print("Done seeding!")
