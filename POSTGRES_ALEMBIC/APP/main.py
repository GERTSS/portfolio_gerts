import random

import requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import time
from sqlalchemy.exc import OperationalError
import logging
from sqlalchemy import text
from flask_migrate import Migrate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://admin:admin@db:5432/skillbox_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)


class Coffee(db.Model):
    tablename = "coffee"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    origin = db.Column(db.String(200))
    intensifier = db.Column(db.String(100))
    notes = db.Column(db.ARRAY(db.String))

    def repr(self):
        return (
            f"<Coffee(id={self.id}, title={self.title}, origin={self.origin}, "
            f"intensifier={self.intensifier}, notes={self.notes})>"
        )


class User(db.Model):
    tablename = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50))
    patronomic = db.Column(db.String(50))
    # has_sale = db.Column(db.Boolean)
    address = db.Column(db.JSON)
    coffee_id = db.Column(db.Integer, db.ForeignKey("coffee.id"))
    coffee = db.relationship("Coffee", backref=db.backref("users", lazy=True))

    def repr(self):
        return (
            f"<User(id={self.id}, name={self.name}, has_sale={self.has_sale}, address={self.address}, "
            f"coffee_id={self.coffee_id})>"
        )


def wait_for_db(engine):
    retries = 5
    while retries > 0:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError:
            retries -= 1
            logger.info("База данных не готова")
            time.sleep(5)
    raise Exception("База данных не справилась")


@app.route("/hello")
def hello():
    return "hello"


def create_tables():
    db.create_all()
    if not Coffee.query.first():
        for _ in range(10):
            time.sleep(3)
            coffee_data = requests.get(
                "https://random-data-api.com/api/coffee/random_coffee"
            ).json()
            coffee = Coffee(
                title=coffee_data["blend_name"],
                origin=coffee_data["origin"],
                intensifier=coffee_data["intensifier"],
                notes=coffee_data["notes"].split(", "),
            )
            db.session.add(coffee)

        db.session.commit()

    if not User.query.first():
        for _ in range(10):
            time.sleep(3)
            user_data = requests.get(
                "https://random-data-api.com/api/address/random_address"
            ).json()
            list_id = db.session.query(Coffee.id).all()
            ids = [id[0] for id in list_id]
            user = User(
                name=f"User_{random.randint(1, 1000)}",
                has_sale=random.choice([True, False]),
                address=user_data,
                coffee_id=random.choice(ids),
            )
            db.session.add(user)

        db.session.commit()


@app.route("/add_user")
def add_user():
    data = request.get_json()
    name = data.get("name")
    has_sale = data.get("has_sale")
    address = data.get("address")
    coffee_id = data.get("coffee_id")
    coffee = Coffee.query.get(coffee_id)
    if coffee is None:
        return jsonify({"error": "Coffee ID not found"})
    new_user = User(name=name, has_sale=has_sale, address=address, coffee_id=coffee_id)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(
        {"message": "User added", "user": repr(new_user), "coffee": repr(coffee)}
    )


@app.route("/search_coffee")
def search_coffee():
    title = request.args.get("title")
    coffees = Coffee.query.filter(Coffee.title.ilike(f"%{title}%")).all()
    result = [repr(coffee) for coffee in coffees]
    return jsonify({"coffees": result})


@app.route("/get_notes")
def get_notes():
    all_notes = Coffee.query.with_entities(Coffee.notes).all()
    list_notes = [note for notes in all_notes for note in notes[0]]
    result = list(set(list_notes))
    return jsonify({"result": result})


@app.route("/users_from_country")
def users_from_country():
    country = request.args.get("country")
    users = User.query.filter(User.address["country"] == country).all()
    result = [repr(user) for user in users]
    return jsonify({"users": result})


if __name__ == "__main__":
    logger.info("start")
    with app.app_context():
        logger.info("start work")
        wait_for_db(db.engine)
        logger.info("Создание таблиц")
        create_tables()
    app.run()
