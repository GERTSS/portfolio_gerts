from main_app.models import db, User, Follow
from main_app.auth import require_api_key
from flask import Blueprint, request, jsonify

follows_bp = Blueprint("follows", __name__)


@follows_bp.route("/api/users/<int:id>/follow", methods=["POST"])
@require_api_key
def add_follow(user, id):
    """
    Add follow
    ---
    tags:
      - Follows
    description: creating a subscription for a user
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
        description: The ID of the user to subscribe to
    responses:
      200:
        description: subscription added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
      404:
        description: User is missing
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: string
                  description: indicates a user search error
      400:
        description: the subscription already exists
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: string
                  description: indicates an existing subscription
    """
    user_followed = User.query.get(id)
    if not user_followed:
        return jsonify({"message": "User is missing"}), 404
    existing_follow = Follow.query.filter_by(
        follower_id=user.id, followed_id=id
    ).first()
    if existing_follow:
        return jsonify({"message": "You have already followed this user"}), 400
    new_follow = Follow(follower_id=user.id, followed_id=id)
    db.session.add(new_follow)
    db.session.commit()
    return jsonify({"result": True}), 200


@follows_bp.route("/api/users/<int:id>/follow", methods=["DELETE"])
@require_api_key
def delete_follow(user, id):
    """
    Delete follow
    ---
    tags:
      - Follows
    description: deleting a subscription
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
        description: The ID of the user to subscribe to
    responses:
      200:
        description: subscription added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
      404:
        description: User is missing
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates a user search error
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
      400:
        description: there is no subscription
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates that there is no subscription
    """
    user_followed = User.query.get(id)
    if not user_followed:
        return jsonify({"message": "User is missing"}), 404
    existing_follow = Follow.query.filter_by(
        follower_id=user.id, followed_id=id
    ).first()
    if not existing_follow:
        return jsonify({"message": "You have dont followed this user"}), 400
    db.session.delete(existing_follow)
    db.session.commit()
    return jsonify({"result": True}), 200
