import pytest
from datetime import datetime

from app import create_app, db as _db
from app.models import Client, Parking, ClientParking


@pytest.fixture
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with _app.app_context():
        _db.create_all()
        client = Client(
            name="Jhon",
            surname="Jhonson",
            credit_card="5676768546746758674",
            car_number="3ABC56",
        )
        parking = Parking(
            address="hwuejhfwfj",
            opened=True,
            count_places=100,
            count_available_places=100,
        )
        booking = ClientParking(
            client_id=1, parking_id=1, time_in=datetime.now(), time_out=datetime.now()
        )
        _db.session.add(client)
        _db.session.add(parking)
        _db.session.add(booking)
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
