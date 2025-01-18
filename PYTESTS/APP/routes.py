from flask import Blueprint, jsonify, request
from datetime import datetime
from models import Client, Parking, ClientParking

from . import db

main = Blueprint("main", __name__)


@main.route("/clients", methods=["GET"])
def all_clients():
    clients = Client.query.all()
    result = [{"client": repr(client)} for client in clients]
    return jsonify(result), 200


@main.route("/clients/<int:id>", methods=["GET"])
def client_by_id():
    client = Client.query.get_or_404(id)
    result = {
        "id": client.id,
        "name": client.name,
        "surname": client.surname,
        "credit_card": client.credit_card,
        "car_number": client.car_number,
    }
    return jsonify(result), 200


@main.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json()
    new_client = Client(
        name=data["name"],
        surname=data["surname"],
        credit_card=data["credit_card"],
        car_number=data["car_number"],
    )
    db.session.add(new_client)
    db.session.commit()
    return {"message": "Add new client"}, 200


@main.route("/parkings", methods=["POST"])
def add_parking():
    data = request.get_json()
    new_parking = Parking(
        address=data["address"],
        opened=data["opened"],
        count_places=data["count_places"],
        count_available_places=data["count_available_places"],
    )
    db.session.add(new_parking)
    db.session.commit()
    return {"message": "Add new parking"}, 200


@main.route("/client_parkings", methods=["POST"])
def add_booking():
    data = request.get_json()
    client_id = data["client_id"]
    parking_id = data["parking_id"]
    parking = Parking.query.get(parking_id)
    if not parking or parking.count_available_places <= 0:
        return {"message": "available places is missing"}
    client = Client.query.get(client_id)
    if not client or not client.credit_card:
        return {"message": "card number is missing"}
    new_booking = ClientParking(
        client_id=client_id, parking_id=parking_id, time_in=datetime.now()
    )
    db.session.add(new_booking)
    parking.count_available_places -= 1
    db.session.commit()
    return {"message": "booking is successful"}, 200


@main.route("/client_parkings", methods=["DELETE"])
def delete_booking():
    data = request.get_json()
    client_id = data["client_id"]
    parking_id = data["parking_id"]
    booking = ClientParking.query.filter_by(
        client_id=client_id, parking_id=parking_id
    ).first()
    db.session.delete(booking)
    parking = Parking.query.get(parking_id)
    parking.count_available_places += 1
    db.session.commit()
    return {"message": "booking deleted"}, 200
