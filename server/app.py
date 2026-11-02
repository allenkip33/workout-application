from flask import Flask
from flask_migrate import Migrate

from models import db
from routes import register_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Allow /workouts and /workouts/ to hit the same route.
app.url_map.strict_slashes = False

migrate = Migrate(app, db)

db.init_app(app)

register_routes(app)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
