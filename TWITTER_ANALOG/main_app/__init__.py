from flask import Flask, render_template, send_from_directory
from main_app.config import Config
from main_app.models import db
from main_app.routes import register_blueprint
from main_app.utils import (
    create_db_if_not_exist,
    create_default_user,
    create_additional_user,
)
from flasgger import Swagger


def create_app(test=False):
    app = Flask(
        __name__,
        template_folder=Config.template_folder,
        static_folder=Config.static_folder,
    )
    app.config.from_object(Config)
    register_blueprint(app)
    with app.app_context():
        if test is False:
            create_db_if_not_exist()
            db.init_app(app)
            db.create_all()
            create_default_user()
            create_additional_user()
    swagger = Swagger(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/<path:path>")
    def send_static(path):
        return send_from_directory(Config.static_folder, path)

    return app
