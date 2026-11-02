# Workout Tracking API

A Flask backend API for a workout tracking application used by personal trainers. It tracks workouts and the exercises in them. Each workout can include several exercises, and each one records sets, reps or duration. Exercises are reusable, so a trainer can add the same exercise to many workouts.

Built with **Flask**, **SQLAlchemy** and **Marshmallow**. It uses validations at three levels: table constraints, model validations and schema validations.

---

## Tech Stack & Packages

| Package | Purpose |
|---|---|
| `flask` | Web framework / routing |
| `flask-sqlalchemy` | ORM integration with Flask |
| `flask-migrate` | Database migrations (Alembic) |
| `marshmallow` | Serialization, deserialization and schema validation |
| `sqlalchemy` | Installed with flask-sqlalchemy; used for `validates` and constraints |
| `alembic` | Installed with flask-migrate |

Python version: **3.8+** (managed with `pipenv`)

### Pipfile

```toml
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
flask = "*"
flask-sqlalchemy = "*"
flask-migrate = "*"
marshmallow = "*"

[dev-packages]

[requires]
python_version = "3.8"
```

### Install the packages

```bash
pipenv install flask flask-sqlalchemy flask-migrate marshmallow
pipenv shell
```

---

## Project Structure

```
workout-application/
├── Pipfile
├── Pipfile.lock
├── README.md
├── .gitignore          # Python template
└── server/
    ├── app.py          # Flask app, config, routes
    ├── models.py       # SQLAlchemy models, constraints, validations
    ├── schemas.py      # Marshmallow schemas (optional: can live in models.py)
    ├── seed.py         # Resets and seeds the database
    ├── app.db          # SQLite database (generated)
    └── migrations/     # Flask-Migrate files (generated)
```

---

## Setup & Running

```bash
# 1. Install dependencies
pipenv install
pipenv shell

# 2. Move into the server directory
cd server

# 3. Initialize and run migrations
export FLASK_APP=app.py
flask db init
flask db migrate -m "create exercises, workouts, workout_exercises tables"
flask db upgrade head

# 4. Seed the database
python seed.py

# 5. Run the server (http://localhost:5555)
python app.py
```

To check relationships and validations by hand:

```bash
flask shell
```

---

## Data Models

### Exercise
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String | Required, unique |
| category | String | Required |
| equipment_needed | Boolean | Required, default `False` |

### Workout
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| date | Date | Required |
| duration_minutes | Integer | Required, > 0 |
| notes | Text | Optional |

### WorkoutExercise (join table)
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| workout_id | Integer | FK → `workouts.id` |
| exercise_id | Integer | FK → `exercises.id` |
| reps | Integer | Optional, ≥ 0 |
| sets | Integer | Optional, ≥ 0 |
| duration_seconds | Integer | Optional, ≥ 0 |

### Relationships
- A `WorkoutExercise` **belongs to** a `Workout`
- A `WorkoutExercise` **belongs to** an `Exercise`
- A `Workout` **has many** `WorkoutExercises`
- An `Exercise` **has many** `WorkoutExercises`
- A `Workout` **has many** `Exercises` **through** `WorkoutExercises`
- An `Exercise` **has many** `Workouts` **through** `WorkoutExercises`

Use `cascade="all, delete-orphan"` on the `workout_exercises` relationships so that deleting a workout or exercise also deletes its join rows (stretch goal).

---

## Validations

You need **at least 2 of each** type.

### Table constraints (`models.py`, `__table_args__` / column args)
- [ ] `nullable=False` on required columns (`Exercise.name`, `Exercise.category`, `Workout.date`, `Workout.duration_minutes`)
- [ ] `unique=True` on `Exercise.name`
- [ ] `CheckConstraint('duration_minutes > 0')` on `Workout`
- [ ] `CheckConstraint('reps >= 0')`, `CheckConstraint('sets >= 0')`, `CheckConstraint('duration_seconds >= 0')` on `WorkoutExercise`

### Model validations (`@validates` in `models.py`)
- [ ] `Exercise.name` must be a non-empty string
- [ ] `Exercise.category` must be in an allowed list (e.g. `strength`, `cardio`, `flexibility`, `balance`)
- [ ] `Workout.duration_minutes` must be a positive integer
- [ ] `WorkoutExercise` reps, sets and duration_seconds must not be negative

### Schema validations (Marshmallow, `schemas.py`)
- [ ] `fields.String(required=True, validate=validate.Length(min=1))` for `name`
- [ ] `validate.OneOf([...])` for `category`
- [ ] `fields.Integer(required=True, validate=validate.Range(min=1))` for `duration_minutes`
- [ ] `validate.Range(min=0)` for reps, sets and duration_seconds
- [ ] `@validates_schema`: a WorkoutExercise must have either reps/sets **or** duration_seconds

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show one workout with its exercises (stretch goal: include reps/sets/duration) |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/<id>` | Delete a workout (stretch goal: delete its WorkoutExercises) |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show one exercise with its workouts |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise (stretch goal: delete its WorkoutExercises) |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with reps/sets/duration |

> No update (PATCH/PUT) endpoints are required, and removing an exercise from a workout is not required.

### Example requests

**POST /exercises**
```json
{ "name": "Push Up", "category": "strength", "equipment_needed": false }
```

**POST /workouts**
```json
{ "date": "2026-11-03", "duration_minutes": 45, "notes": "Upper body day" }
```

**POST /workouts/1/exercises/2/workout_exercises**
```json
{ "reps": 12, "sets": 3, "duration_seconds": 0 }
```

### Response codes
- `200` OK for successful GET
- `201` Created for successful POST
- `204` No Content (or `200` with a message) for successful DELETE
- `400` / `422` for validation errors (return the Marshmallow error messages)
- `404` when a workout or exercise is not found

---

## Starter Code

**server/app.py**
```python
from flask import Flask, make_response
from flask_migrate import Migrate

from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

# Define Routes here

if __name__ == '__main__':
    app.run(port=5555, debug=True)
```

**server/models.py**
```python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
db = SQLAlchemy()

# Define Models here
```

**server/seed.py**
```python
#!/usr/bin/env python3

from app import app
from models import *

with app.app_context():

    # reset data and add new example data, committing to db
```

---

## Work Plan & Commit Checklist

Commit after each step with a clear message.

- [ ] **Step 1: Setup.** Create the GitHub repo with README and Python `.gitignore`, add the Pipfile, install packages, and create `server/app.py`, `models.py` and `seed.py`.
  *Commit: "Set up project structure and dependencies"*
- [ ] **Step 2: Models.** Add `Exercise`, `Workout` and `WorkoutExercise`, committing after each model.
- [ ] **Step 3: Relationships.** Add the belongs-to, has-many and has-many-through relationships (`relationship`, `back_populates`, `association_proxy`).
- [ ] **Step 4: Constraints & model validations.** Add at least 2 table constraints and at least 2 `@validates`.
- [ ] **Step 5: Migrate.** Run `flask db init`, then `flask db migrate -m "..."`, then `flask db upgrade head`.
- [ ] **Step 6: Seed.** Clear the tables, add a few records to each table, run `seed.py`, and check the data in `flask shell`.
- [ ] **Step 7: Scaffold endpoints.** Add a stub for every route.
- [ ] **Step 8: Schemas.** Add a Marshmallow schema for each model (with nested relationships).
- [ ] **Step 9: Schema validations.** Add at least 2.
- [ ] **Step 10: Finish the endpoints.** Use the schemas to serialize and deserialize in every route, committing after each endpoint.
