from routes.exercises import exercises_bp
from routes.workouts import workouts_bp


def register_routes(app):
    app.register_blueprint(workouts_bp)
    app.register_blueprint(exercises_bp)
