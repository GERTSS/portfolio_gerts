from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)
    db.init_app(app)

    with app.app_context():
        from . import models
        from . import routes

        db.create_all()
        app.register_blueprint(routes.main)
        return app
