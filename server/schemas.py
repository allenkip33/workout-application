from marshmallow import Schema, ValidationError, fields, validate, validates, validates_schema

from models import EXERCISE_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.OneOf(EXERCISE_CATEGORIES))
    equipment_needed = fields.Bool(load_default=False)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Name cannot be blank.")


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, strict=True, validate=validate.Range(min=1, max=600))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=1000))


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=0))
    sets = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=0))
    duration_seconds = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=0))
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates_schema
    def validate_has_measurement(self, data, **kwargs):
        # A row with no reps, sets or duration gives the trainer nothing to track.
        if not any(data.get(key) for key in ("reps", "sets", "duration_seconds")):
            raise ValidationError("Provide reps/sets or duration_seconds.")


class WorkoutDetailSchema(WorkoutSchema):
    """A workout with each of its exercises and the reps/sets/duration used."""
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)


class ExerciseDetailSchema(ExerciseSchema):
    """An exercise with every workout it has been used in."""
    workouts = fields.List(fields.Nested(WorkoutSchema), dump_only=True)


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()

workout_exercise_schema = WorkoutExerciseSchema()
