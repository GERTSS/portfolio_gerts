from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    api_key = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )


class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), nullable=False)
    filetype = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(280), nullable=False)


class Twit(db.Model):
    __tablename__ = "twits"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    files = db.relationship(
        "File", secondary="twits_files", backref=db.backref("twits", lazy="dynamic")
    )
    likes = db.relationship(
        "Like", backref="tweet", cascade="all, delete-orphan", lazy="dynamic"
    )


class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    twit_id = db.Column(db.Integer, db.ForeignKey("twits.id"), nullable=False)


class Follow(db.Model):
    __tablename__ = "follows"
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )  # Подписчик
    followed_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )  # Тот на кого подписались


twits_files = db.Table(
    "twits_files",
    db.Column("twit_id", db.Integer, db.ForeignKey("twits.id"), primary_key=True),
    db.Column("file_id", db.Integer, db.ForeignKey("files.id"), primary_key=True),
)
