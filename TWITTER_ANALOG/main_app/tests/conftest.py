import pytest
from main_app import create_app
from main_app.models import db as _db, User, Twit, Follow, Like


@pytest.fixture
def app():
    _app = create_app(True)
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with _app.app_context():
        _db.init_app(_app)
        _db.create_all()
        user = User(name="Jhon", api_key="12345")
        user_2 = User(name="Jhon2", api_key="67890")
        twit = Twit(content="Some text", user_id=1)
        like = Like(user_id=1, twit_id=1)
        follow = Follow(follower_id=1, followed_id=2)
        _db.session.add(user)
        _db.session.add(user_2)
        _db.session.add(twit)
        _db.session.add(like)
        _db.session.add(follow)
        yield _app
        _db.session.close()
        _db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
