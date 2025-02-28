from main_app.models import db, User, Follow
from main_app.auth import require_api_key
from flask import Blueprint, request, jsonify

users_bp = Blueprint("users", __name__)


@users_bp.route("/api/users/me", methods=["GET"])
@require_api_key
def get_my_info(user):
    """
    Get my info
    ---
    tags:
      - Users
    description: getting information about me
    parameters:
      - name: api-key
        in: header
        type: string
        required: true
        description: The API key for authentication
    responses:
      200:
        description: user information has been successfully received
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
                user:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: Your ID
                    name:
                      type: string
                      description: Your name
                    followers:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: Followers ID
                          name:
                            type: string
                            description: Followers name
                    following:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: Following ID
                          name:
                            type: string
                            description: Following name
      500:
        description: indicates a request error
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates a request error
                error_type:
                  type: string
                  description: provides the error type
                error_message:
                  type: string
                  description: provides the error message
      401:
        description: API key is missing
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates API-key error
      403:
        description: invalid API key
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates API-key error
    """
    try:
        followers = (
            db.session.query(User)
            .join(Follow, Follow.follower_id == User.id)
            .filter(Follow.followed_id == user.id)
            .all()
        )
        followers_dict = [
            {"id": follower.id, "name": follower.name} for follower in followers
        ]
        followings = (
            db.session.query(User)
            .join(Follow, Follow.followed_id == User.id)
            .filter(Follow.follower_id == user.id)
            .all()
        )
        following_dict = [
            {"id": following.id, "name": following.name} for following in followings
        ]
        return (
            jsonify(
                {
                    "result": True,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "followers": followers_dict,
                        "following": following_dict,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify({"result": False, "error_type": type(e), "error_massage": e}),
            500,
        )


@users_bp.route("/api/users/<int:id>", methods=["GET"])
@require_api_key
def get_user_info(user, id):
    """
    Get user info by id
    ---
    tags:
      - Users
    description: getting information about me
    parameters:
      - name: api-key
        in: header
        type: string
        required: true
        description: The API key for authentication
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the user
    responses:
      200:
        description: user information has been successfully received
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
                user:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: User ID
                    name:
                      type: string
                      description: User name
                    followers:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: Followers ID
                        name:
                            type: string
                            description: Followers name
                    following:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: Following ID
                        name:
                            type: string
                            description: Following name
      500:
        description: indicates a request error
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates a request error
                error_type:
                  type: string
                  description: provides the error type
                error_message:
                  type: string
                  description: provides the error message
      401:
        description: API key is missing
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates API-key error
      403:
        description: invalid API key
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates API-key error
    """
    try:
        user = db.session.query(User).filter(User.id == id).first()
        if not user:
            return jsonify({"message": "User is missing"}), 404
        followers = (
            db.session.query(User)
            .join(Follow, Follow.follower_id == User.id)
            .filter(Follow.followed_id == id)
            .all()
        )
        followers_dict = [
            {"id": follower.id, "name": follower.name} for follower in followers
        ]
        followings = (
            db.session.query(User)
            .join(Follow, Follow.followed_id == User.id)
            .filter(Follow.follower_id == id)
            .all()
        )
        following_dict = [
            {"id": following.id, "name": following.name} for following in followings
        ]
        return (
            jsonify(
                {
                    "result": True,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "followers": followers_dict,
                        "following": following_dict,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify({"result": False, "error_type": type(e), "error_massage": e}),
            500,
        )
