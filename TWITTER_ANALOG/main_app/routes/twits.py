from werkzeug.utils import secure_filename
from main_app.auth import require_api_key
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from main_app.models import db, User, Twit, File, Like, Follow, twits_files
import os
from sqlalchemy.orm import aliased
import logging
from main_app.config import Config

logging.basicConfig(level=logging.DEBUG)
allowed_extensions = {"png", "jpeg", "jpg", "mp4", "mov"}
upload_folder = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "static", "uploads"
)
twits_bp = Blueprint("twits", __name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@twits_bp.route("/api/get_file/<filename>")
def get_file(filename):
    return send_from_directory(upload_folder, filename)


@twits_bp.route("/api/medias", methods=["POST"])
@require_api_key
def upload(user):
    """
    Upload files
    ---
    tags:
      - Twits
    description: Upload files for twit
    parameters:
      - name: api-key
        in: header
        type: string
        required: true
        description: The API key for authentication
      - name: file
        in: formData
        required: true
        schema:
          type: file
        description: the photo or video
    responses:
      201:
        description: file or files added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
                media_id:
                  type: array
                  items:
                    type: integer
                    description: file ID
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
        description: Invalid file type
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates a file type error
                  example: Invalid file type
    """
    files_list = []
    files = request.files.getlist("file")
    logging.debug(f"{files}")
    for file in files:
        if not file or not allowed_file(file.filename):
            return jsonify({"message": "Invalid file type"}), 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, f"{uuid.uuid4()}_{filename}")
        file.save(filepath)
        filetype = filename.rsplit(".", 1)[1].lower()
        filename = os.path.basename(filepath)
        new_file = File(
            filetype=filetype, filename=filename, url=f"/api/get_file/{filename}"
        )
        db.session.add(new_file)
        db.session.commit()
        files_list.append(new_file)
    return jsonify({"result": True, "media_id": [file.id for file in files_list]}), 201


@twits_bp.route("/api/tweets", methods=["POST"])
@require_api_key
def add_twit(user):
    """
    Create twit
    ---
    tags:
      - Twits
    description: Create twit
    parameters:
      - name: api-key
        in: header
        type: string
        required: true
        description: The API key for authentication
      - name: tweet_data
        in: body
        required: true
        type: string
        description: the tex content of the twit
      - name: tweet_media_ids
        in: body
        required: false
        schema:
          type: array
          items:
            type: integer
          description: File ID
    responses:
      201:
        description: file or files added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
                  example: True
                tweet_id:
                  type: integer
                  description: twit ID
                  example: 1
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
        description: Invalid file ID
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates a file ID error
    """
    files = []
    data = request.json
    content = data.get("tweet_data")
    files_ids = data.get("tweet_media_ids")
    logging.debug(f"{files_ids}")
    if files_ids:
        for file_id in files_ids:
            logging.debug(f"{Config.static_folder} number")
            file = File.query.get(file_id)
            if not file:
                return jsonify({"message": "Invalid file ID"}), 400
            files.append(file)
    new_twit = Twit(content=content, user_id=user.id)
    db.session.add(new_twit)
    db.session.commit()
    for file in files:
        new_twit.files.append(file)
    db.session.commit()
    return jsonify({"result": True, "tweet_id": new_twit.id}), 201


@twits_bp.route("/api/tweets/<int:id>", methods=["DELETE"])
@require_api_key
def delete_twit(user, id):
    """
    Delete twit
    ---
    tags:
      - Twits
    description: Delete twit by id
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
        description: The ID of the twit to delete
    responses:
      200:
        description: file or files added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: boolean
                  description: indicates the success of the request
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
      422:
        description: Permission has been denied
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: indicates permission denied
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
    """
    twit = Twit.query.get(id)
    if not twit:
        return jsonify({"message": "Tweet is missing"}), 404
    if twit.user_id != user.id:
        return jsonify({"message": "Permission denied"}), 403
    db.session.delete(twit)
    db.session.commit()
    return jsonify({"result": True}), 200


@twits_bp.route("/api/tweets", methods=["GET"])
@require_api_key
def get_tweets(user):
    """
    Getting tweets
    ---
    tags:
      - Twits
    description: Getting all tweets
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
                tweets:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: Tweet ID
                    content:
                      type: string
                      description: The text content of the tweet
                    attachments:
                      type: array
                      items:
                        link:
                          type: string
                          description: File link
                    author:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: Author ID
                          name:
                            type: string
                            description: Author name
                    likes:
                      type: array
                      description: list of likes
                      items:
                        type: object
                        properties:
                          user_id:
                            type: integer
                            description: ID of the user who liked it
                          name:
                            type: string
                            description: Name of the user who liked it
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
    """
    try:
        followed_users = (
            db.session.query(Follow.followed_id)
            .filter(Follow.follower_id == user.id)
            .subquery()
        )
        twit_alias = aliased(Twit)
        twit_likes = (
            db.session.query(twit_alias.id, db.func.count(Like.id).label("like_count"))
            .outerjoin(Like, Like.twit_id == twit_alias.id)
            .group_by(twit_alias.id)
            .subquery()
        )
        twits = (
            db.session.query(
                Twit.id,
                Twit.content,
                Twit.user_id,
                User.name,
                twit_likes.c.like_count,
                db.func.sum(
                    db.case((Like.user_id.in_(followed_users), 1), else_=0)
                ).label("followed_user_likes"),
            )
            .join(User, User.id == Twit.user_id)
            .outerjoin(twits_files, twits_files.c.twit_id == Twit.id)
            .outerjoin(Like, Like.twit_id == Twit.id)
            .outerjoin(twit_likes, twit_likes.c.id == Twit.id)
            .group_by(Twit.id, User.name, twit_likes.c.like_count)
            .order_by(db.desc("followed_user_likes"), db.desc(twit_likes.c.like_count))
            .all()
        )
        twit_list = []
        for twit in twits:
            files_for_twit = (
                (
                    db.session.query(File.url).join(
                        twits_files, twits_files.c.file_id == File.id
                    )
                )
                .filter(twits_files.c.twit_id == twit.id)
                .all()
            )
            files = [{"url": file.url} for file in files_for_twit]
            likes_for_twit = (
                db.session.query(Like.user_id, User.name)
                .join(User, User.id == Like.user_id)
                .filter(Like.twit_id == twit.id)
                .all()
            )
            likes = [
                {"user_id": like.user_id, "name": like.name} for like in likes_for_twit
            ]
            twit_list.append(
                {
                    "id": twit.id,
                    "content": twit.content,
                    "attachments": [file["url"] for file in files],
                    "author": {"id": twit.user_id, "name": twit.name},
                    "likes": [data_like for data_like in likes],
                }
            )
        return jsonify({"result": True, "tweets": twit_list}), 200
    except Exception as e:
        return (
            jsonify({"result": False, "error_type": type(e), "error_massage": e}),
            500,
        )
