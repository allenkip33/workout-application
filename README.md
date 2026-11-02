# Workout Tracking API

A REST API backend for a workout tracking application used by personal trainers, built with Flask, SQLAlchemy and Marshmallow.

Trainers can build a library of reusable **exercises** and log **workouts**. Any exercise can be added to any workout, with the sets, reps or duration done in that session. The API checks all incoming data at three levels (database constraints, model validations and schema validations), so bad data never reaches the database.

## Features

- Create, view and delete workouts
- Create, view and delete exercises
- Add an exercise to a workout with its reps, sets and/or duration
- View a workout with all its exercises and the reps, sets and duration for each
- View an exercise with every workout it has been used in
- Deleting a workout or exercise also removes its workout-exercise links
- Consistent JSON error responses (400, 404, 405, 409)

## Tech Stack

| Package | Version | Purpose |
|---|---|---|
| [Flask](https://flask.palletsprojects.com/) | 3.1.3 | Web framework and routing |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.readthedocs.io/) | 3.1.1 | Database models (ORM) |
| [Flask-Migrate](https://flask-migrate.readthedocs.io/) | 4.1.0 | `flask db` migration commands |
| [Marshmallow](https://marshmallow.readthedocs.io/) | 4.3.1 | Serialization, deserialization and validation |
| SQLAlchemy | 2.1.6 | Installed with Flask-SQLAlchemy |
| Alembic | 1.20.1 | Installed with Flask-Migrate; runs the migrations |

Database: SQLite. Python: 3.12. Dependencies are managed with Pipenv and pinned in `Pipfile.lock`.

---

## Installation

**Requirements:** Python 3.12 and [Pipenv](https://pipenv.pypa.io/) (`pip install pipenv`).

```bash
git clone <your-repo-url> workout-application
cd workout-application
pipenv install
pipenv shell
```

## Running the Application

Run these from the `server/` directory, inside `pipenv shell`:

```bash
cd server
export FLASK_APP=app.py

flask db upgrade head    # create the database tables
python seed.py           # add sample data
python app.py            # start the server
```

The API runs at **http://localhost:5555**. Check it with:

```bash
curl http://localhost:5555/workouts
```

Run `python seed.py` again at any time to reset the database to the sample data.

### Changing the models

After editing `models.py`, create and apply a migration:

```bash
flask db migrate -m "Describe your change"
flask db upgrade head
```

### Troubleshooting

- **`ModuleNotFoundError: No module named 'flask'`**: you're outside the Pipenv environment. Run `pipenv shell`, or put `pipenv run` before the command (for example `pipenv run python app.py`).
- **`pipenv install` puts packages in the wrong place**: another virtual environment is active (your editor may activate one automatically). Run `deactivate` first, then `pipenv install` again.
- **`Error: Could not locate a Flask application`**: run the command from `server/` with `FLASK_APP=app.py` set.
- **`no such table`**: run `flask db upgrade head` before `seed.py`.

---

## Project Structure

```
workout-application/
├── Pipfile              # Package list
├── Pipfile.lock         # Pinned package versions
├── README.md
└── server/
    ├── app.py           # Creates the app; wires up the database, routes and error handlers
    ├── models.py        # Models, relationships, table constraints, model validations
    ├── schemas.py       # Marshmallow schemas and schema validations
    ├── errors.py        # Turns errors into JSON responses
    ├── seed.py          # Resets and seeds the database
    ├── routes/
    │   ├── __init__.py  # Registers the blueprints
    │   ├── workouts.py  # /workouts endpoints
    │   └── exercises.py # /exercises endpoints
    └── migrations/      # Database migration history
```

The SQLite database is created at `server/instance/app.db` and is not committed to git.

---

## Data Model

```
Workout  1 ──── *  WorkoutExercise  * ──── 1  Exercise
                   (reps, sets, duration_seconds)
```

| Model | Fields |
|---|---|
| **Exercise** | `id` (integer, PK), `name` (string), `category` (string), `equipment_needed` (boolean) |
| **Workout** | `id` (integer, PK), `date` (date), `duration_minutes` (integer), `notes` (text) |
| **WorkoutExercise** | `id` (integer, PK), `workout_id` (FK), `exercise_id` (FK), `reps`, `sets`, `duration_seconds` (integers) |

### Relationships

- A WorkoutExercise **belongs to** a Workout and **belongs to** an Exercise
- A Workout **has many** WorkoutExercises
- An Exercise **has many** WorkoutExercises
- A Workout **has many** Exercises **through** WorkoutExercises (`workout.exercises`)
- An Exercise **has many** Workouts **through** WorkoutExercises (`exercise.workouts`)

The "through" relationships use SQLAlchemy's `association_proxy`. Both one-to-many relationships use `cascade="all, delete-orphan"`, so deleting a workout or exercise removes its WorkoutExercise rows.

---

## Validations

Data is checked at three levels, each catching mistakes at a different point.

### 1. Table constraints (database level, `models.py`)

The database itself rejects bad rows, even ones that bypass the API.

| Constraint | Table | Rule |
|---|---|---|
| `NOT NULL` | exercises | `name`, `category`, `equipment_needed` are required |
| `NOT NULL` | workouts | `date`, `duration_minutes` are required |
| `NOT NULL` | workout_exercises | `workout_id`, `exercise_id` are required |
| `UNIQUE` | exercises | No two exercises can share a `name` |
| `UNIQUE (workout_id, exercise_id)` | workout_exercises | An exercise appears at most once per workout |
| `CHECK` | exercises | `name` cannot be blank |
| `CHECK` | workouts | `duration_minutes > 0` |
| `CHECK` | workout_exercises | `reps`, `sets` and `duration_seconds` cannot be negative |

### 2. Model validations (SQLAlchemy `@validates`, `models.py`)

These run in Python whenever an attribute is set on a model.

- `Exercise.name`: must be a non-empty string; surrounding spaces are removed
- `Exercise.category`: must be `strength`, `cardio`, `flexibility` or `balance`
- `Workout.date`: must be a date
- `Workout.duration_minutes`: must be a positive integer
- `WorkoutExercise.reps` / `sets` / `duration_seconds`: must be non-negative integers if given

### 3. Schema validations (Marshmallow, `schemas.py`)

These check incoming request JSON before any model is created, and report every problem at once.

- Exercise `name`: required, 1–100 characters, not just spaces
- Exercise `category`: required, one of the allowed categories
- Exercise `equipment_needed`: true/false, defaults to `false`
- Workout `date`: required, format `YYYY-MM-DD`
- Workout `duration_minutes`: required whole number from 1 to 600 (text such as `"50"` is rejected)
- Workout `notes`: optional, at most 1000 characters
- WorkoutExercise `reps`, `sets`, `duration_seconds`: whole numbers of 0 or more
- WorkoutExercise: at least one of `reps`, `sets` or `duration_seconds` must be above 0
- All schemas: unknown fields (such as sending an `id`) are rejected

---

## API Reference

Base URL: `http://localhost:5555`. All requests and responses use JSON.

| Method | Endpoint | Description | Success |
|---|---|---|---|
| GET | `/workouts` | List all workouts | `200` |
| GET | `/workouts/<id>` | Get a workout with its exercises and their reps, sets and duration | `200` |
| POST | `/workouts` | Create a workout | `201` |
| DELETE | `/workouts/<id>` | Delete a workout and its WorkoutExercises | `204` |
| GET | `/exercises` | List all exercises | `200` |
| GET | `/exercises/<id>` | Get an exercise with the workouts it is used in | `200` |
| POST | `/exercises` | Create an exercise | `201` |
| DELETE | `/exercises/<id>` | Delete an exercise and its WorkoutExercises | `204` |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout | `201` |

### Workouts

#### `GET /workouts`

```json
[
  { "id": 1, "date": "2026-11-01", "duration_minutes": 45, "notes": "Upper body and core." },
  { "id": 2, "date": "2026-11-02", "duration_minutes": 60, "notes": "Leg day, heavy squats." }
]
```

#### `GET /workouts/<id>`

```json
{
  "id": 2,
  "date": "2026-11-02",
  "duration_minutes": 60,
  "notes": "Leg day, heavy squats.",
  "workout_exercises": [
    {
      "id": 3,
      "workout_id": 2,
      "exercise_id": 2,
      "sets": 5,
      "reps": 5,
      "duration_seconds": null,
      "exercise": { "id": 2, "name": "Barbell Squat", "category": "strength", "equipment_needed": true }
    }
  ]
}
```

#### `POST /workouts`

| Field | Type | Required |
|---|---|---|
| `date` | string `YYYY-MM-DD` | yes |
| `duration_minutes` | integer 1–600 | yes |
| `notes` | string (max 1000) | no |

```bash
curl -X POST http://localhost:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-11-04", "duration_minutes": 50, "notes": "Push day"}'
```

Response `201`:

```json
{ "id": 4, "date": "2026-11-04", "duration_minutes": 50, "notes": "Push day" }
```

#### `DELETE /workouts/<id>`

Returns `204 No Content` with an empty body.

### Exercises

#### `GET /exercises`

```json
[
  { "id": 1, "name": "Push Up", "category": "strength", "equipment_needed": false },
  { "id": 2, "name": "Barbell Squat", "category": "strength", "equipment_needed": true }
]
```

#### `GET /exercises/<id>`

```json
{
  "id": 5,
  "name": "Hamstring Stretch",
  "category": "flexibility",
  "equipment_needed": false,
  "workouts": [
    { "id": 2, "date": "2026-11-02", "duration_minutes": 60, "notes": "Leg day, heavy squats." },
    { "id": 3, "date": "2026-11-03", "duration_minutes": 30, "notes": "Easy cardio and mobility." }
  ]
}
```

#### `POST /exercises`

| Field | Type | Required |
|---|---|---|
| `name` | string (1–100, unique) | yes |
| `category` | `strength` / `cardio` / `flexibility` / `balance` | yes |
| `equipment_needed` | boolean | no (default `false`) |

```bash
curl -X POST http://localhost:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name": "Burpee", "category": "cardio", "equipment_needed": false}'
```

Response `201`:

```json
{ "id": 6, "name": "Burpee", "category": "cardio", "equipment_needed": false }
```

#### `DELETE /exercises/<id>`

Returns `204 No Content` with an empty body.

### Adding an exercise to a workout

#### `POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises`

| Field | Type | Required |
|---|---|---|
| `reps` | integer ≥ 0 | at least one of the three |
| `sets` | integer ≥ 0 | at least one of the three |
| `duration_seconds` | integer ≥ 0 | at least one of the three |

```bash
curl -X POST http://localhost:5555/workouts/4/exercises/6/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"sets": 3, "reps": 12}'
```

Response `201`:

```json
{
  "id": 7,
  "workout_id": 4,
  "exercise_id": 6,
  "sets": 3,
  "reps": 12,
  "duration_seconds": null,
  "exercise": { "id": 6, "name": "Burpee", "category": "cardio", "equipment_needed": false }
}
```

### Errors

Every error returns JSON with an `errors` key.

| Status | When | Example |
|---|---|---|
| `400` | Validation failed | `{"errors": {"duration_minutes": ["Missing data for required field."]}}` |
| `404` | Workout or exercise not found | `{"errors": ["Workout 99 not found."]}` |
| `405` | Method not supported (e.g. `PATCH`) | `{"errors": ["The method is not allowed for the requested URL."]}` |
| `409` | Database constraint failed (duplicate name, exercise already in workout) | `{"errors": ["UNIQUE constraint failed: exercises.name"]}` |

---

## Seed Data

`python seed.py` clears all tables and creates:

- **5 exercises**: Push Up, Barbell Squat, Treadmill Run, Plank, Hamstring Stretch
- **3 workouts**: upper body (Nov 1), leg day (Nov 2), cardio (Nov 3)
- **6 workout exercises** linking them, using a mix of sets/reps and timed durations

## Scope

As required by the spec, the API has no update (`PATCH`/`PUT`) endpoints and no way to remove a single exercise from a workout.
