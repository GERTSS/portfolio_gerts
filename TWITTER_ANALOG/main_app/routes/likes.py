from main_app.auth import require_api_key
from flask import Blueprint, request, jsonify
from main_app.models import db, Like, Twit

likes_bp = Blueprint("likes", __name__)


@likes_bp.route("/api/tweets/<int:id>/likes", methods=["POST"])
@require_api_key
def like_twit(user, id):
    """
    Add like
    ---
    tags:
      - Likes
    description: creating a like on twit
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
        description: The ID of the twit to like
    responses:
      200:
        description: like added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
      404:
        description: Twit is missing
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: string
                  description: indicates a twit search error
      400:
        description: the like already exists
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: string
                  description: indicates an existing like
    """
    twit = Twit.query.get(id)
    if not twit:
        return jsonify({"message": "Tweet is missing"}), 404
    existing_like = Like.query.filter_by(user_id=user.id, twit_id=id).first()
    if existing_like:
        return jsonify({"message": "You have already liked this tweet"}), 400
    new_like = Like(user_id=user.id, twit_id=id)
    db.session.add(new_like)
    db.session.commit()
    return jsonify({"result": True}), 200


@likes_bp.route("/api/tweets/<int:id>/likes", methods=["DELETE"])
@require_api_key
def delete_like(user, id):
    """
    Delete like
    ---
    tags:
      - Likes
    description: Deleting a like
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
        description: The ID of the twit to like
    responses:
      200:
        description: like added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
      404:
        description: Twit is missing
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates a twit search error
      400:
        description: there is no like
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates that there is no like
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
    twit = Twit.query.get(id)
    if not twit:
        return jsonify({"message": "Tweet is missing"}), 404
    existing_like = Like.query.filter_by(user_id=user.id, twit_id=id).first()
    if not existing_like:
        return jsonify({"message": "You have not liked this tweet"}), 400
    db.session.delete(existing_like)
    db.session.commit()
    return jsonify({"result": True}), 200
