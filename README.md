# Workout Tracking API

A Flask REST API for a workout tracking application used by personal trainers. Trainers can create workouts and a library of reusable exercises, then add exercises to workouts with the sets, reps or duration for each one.

Built with **Flask**, **Flask-SQLAlchemy**, **Flask-Migrate** and **Marshmallow**. Data is validated at three levels: database table constraints, SQLAlchemy model validations and Marshmallow schema validations.

---

## Packages

| Package | Version | Purpose |
|---|---|---|
| `flask` | 3.1 | Web framework and routing |
| `flask-sqlalchemy` | 3.1 | SQLAlchemy ORM integration |
| `flask-migrate` | 4.1 | Database migrations (Alembic) |
| `marshmallow` | 4.3 | Serialization, deserialization and schema validation |
| `sqlalchemy` | 2.1 | Installed with flask-sqlalchemy |
| `alembic` | 1.20 | Installed with flask-migrate |

Requires **Python 3.12** and **pipenv**. Exact versions are pinned in `Pipfile.lock`.

---

## Installation

```bash
git clone <your-repo-url>
cd workout-application

pipenv install      # installs the packages from Pipfile.lock
pipenv shell        # activates the virtual environment
```

## Running the app

All commands run from the `server/` directory:

```bash
cd server
export FLASK_APP=app.py

flask db upgrade head   # create the tables in server/instance/app.db
python seed.py          # reset the tables and add sample data
python app.py           # start the API at http://localhost:5555
```

Run `python seed.py` again at any time to reset the data. To explore the models interactively, use `flask shell`.

If you change a model, create and apply a new migration:

```bash
flask db migrate -m "describe the change"
flask db upgrade head
```

---

## Project Structure

```
workout-application/
├── Pipfile / Pipfile.lock
├── README.md
└── server/
    ├── app.py              # App setup: config, database, routes and error handlers
    ├── models.py           # Models, relationships, table constraints, model validations
    ├── schemas.py          # Marshmallow schemas and schema validations
    ├── errors.py           # JSON error handlers (400 / 404 / 409)
    ├── seed.py             # Resets the database and adds sample data
    ├── routes/
    │   ├── __init__.py     # Registers the blueprints
    │   ├── workouts.py     # /workouts endpoints
    │   └── exercises.py    # /exercises endpoints
    └── migrations/         # Alembic migration files
```

---

## Data Models

**Exercise**: `id`, `name` (string), `category` (string), `equipment_needed` (boolean)

**Workout**: `id`, `date` (date), `duration_minutes` (integer), `notes` (text)

**WorkoutExercise** (join table): `id`, `workout_id` → workouts, `exercise_id` → exercises, `reps`, `sets`, `duration_seconds` (integers)

### Relationships
- A WorkoutExercise belongs to a Workout and to an Exercise.
- A Workout has many WorkoutExercises, and has many Exercises through them (`workout.exercises`).
- An Exercise has many WorkoutExercises, and has many Workouts through them (`exercise.workouts`).
- Deleting a Workout or an Exercise also deletes its WorkoutExercise rows (`cascade="all, delete-orphan"`).

---

## Validations

### Table constraints (`models.py`)
- `NOT NULL` on `Exercise.name`, `Exercise.category`, `Exercise.equipment_needed`, `Workout.date`, `Workout.duration_minutes` and both foreign keys
- `UNIQUE` on `Exercise.name`
- `UNIQUE (workout_id, exercise_id)`: an exercise appears at most once per workout
- `CHECK` that the exercise name is not blank
- `CHECK duration_minutes > 0`
- `CHECK` that `reps`, `sets` and `duration_seconds` are not negative

### Model validations (`@validates` in `models.py`)
- `Exercise.name` must be a non-empty string (surrounding spaces are removed)
- `Exercise.category` must be one of `strength`, `cardio`, `flexibility`, `balance`
- `Workout.date` must be a `date` object
- `Workout.duration_minutes` must be a positive integer
- `WorkoutExercise` reps, sets and duration_seconds must be non-negative integers

### Schema validations (`schemas.py`)
- Exercise `name`: required, 1–100 characters, not only spaces
- Exercise `category`: required, must be one of the allowed categories
- Workout `date`: required, valid `YYYY-MM-DD` date
- Workout `duration_minutes`: required integer between 1 and 600
- Workout `notes`: at most 1000 characters
- WorkoutExercise `reps`, `sets`, `duration_seconds`: integers ≥ 0
- WorkoutExercise: must include at least one of reps, sets or duration_seconds

---

## API Endpoints

| Method | Route | Description | Success |
|---|---|---|---|
| GET | `/workouts` | List all workouts | 200 |
| GET | `/workouts/<id>` | One workout with its exercises and their reps/sets/duration | 200 |
| POST | `/workouts` | Create a workout | 201 |
| DELETE | `/workouts/<id>` | Delete a workout and its WorkoutExercises | 204 |
| GET | `/exercises` | List all exercises | 200 |
| GET | `/exercises/<id>` | One exercise with the workouts it is used in | 200 |
| POST | `/exercises` | Create an exercise | 201 |
| DELETE | `/exercises/<id>` | Delete an exercise and its WorkoutExercises | 204 |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout | 201 |

### Errors
All errors are returned as JSON with an `errors` key:
- **400**: schema or model validation failed, for example `{"errors": {"duration_minutes": ["Must be greater than or equal to 1 and less than or equal to 600."]}}`
- **404**: the workout or exercise does not exist
- **409**: a database constraint failed, such as a duplicate exercise name or adding the same exercise to a workout twice

### Example requests

```bash
# Create an exercise
curl -X POST localhost:5555/exercises -H "Content-Type: application/json" \
  -d '{"name": "Burpee", "category": "cardio", "equipment_needed": false}'

# Create a workout
curl -X POST localhost:5555/workouts -H "Content-Type: application/json" \
  -d '{"date": "2026-11-04", "duration_minutes": 50, "notes": "Push day"}'

# Add the exercise to the workout
curl -X POST localhost:5555/workouts/4/exercises/6/workout_exercises \
  -H "Content-Type: application/json" -d '{"sets": 3, "reps": 12}'

# View the workout with its exercises
curl localhost:5555/workouts/4
```

Example response from `GET /workouts/1`:

```json
{
  "id": 1,
  "date": "2026-11-01",
  "duration_minutes": 45,
  "notes": "Upper body and core.",
  "workout_exercises": [
    {
      "id": 1, "workout_id": 1, "exercise_id": 1,
      "sets": 4, "reps": 15, "duration_seconds": null,
      "exercise": {"id": 1, "name": "Push Up", "category": "strength", "equipment_needed": false}
    }
  ]
}
```
