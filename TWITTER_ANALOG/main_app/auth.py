from flask import jsonify, request
from main_app.models import User
from functools import wraps


def require_api_key(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("api_key")
        if not api_key:
            return jsonify({"message": "API key is missing"}), 401
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({"message": "Invalid API key"}), 403
        return function(user, *args, **kwargs)

    return decorated_function
