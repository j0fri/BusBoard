import os
from flask import Flask
#from BusBoard.models import db, migrate
from BusBoard.controllers import register_controllers


def create_app():
    app = Flask(__name__)

    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    register_controllers(app)

    if __name__ == "__main__":
        app.run()

    return app
