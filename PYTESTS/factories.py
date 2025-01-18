import factory
from app.models import Client, Parking
from faker import Faker
from app import db

fake = Faker()


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.Faker("credit_card_number")
    car_number = factory.Faker("license_plate")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address")
    opened = factory.Faker("boolean")
    count_places = factory.Faker("random_int", min=10, max=100)
    count_available_places = factory.LazyAttribute(
        lambda o: o.count_places - fake.random_int(min=0, max=o.count_places)
    )
