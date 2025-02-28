from main_app.routes.twits import twits_bp
from main_app.routes.likes import likes_bp
from main_app.routes.follows import follows_bp
from main_app.routes.users import users_bp


def register_blueprint(app):
    app.register_blueprint(twits_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(follows_bp)
    app.register_blueprint(users_bp)
