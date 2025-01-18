from . import db


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))

    def repr(self):
        return f"Client('{self.name}', '{self.surname}')"


class Parking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    def repr(self):
        return f"Parking('{self.address}', Opened: {self.opened})"


class ClientParking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    parking_id = db.Column(db.Integer, db.ForeignKey("parking.id"))
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)

    table_args = (
        db.UniqueConstraint("client_id", "parking_id", name="unique_client_parking"),
    )

    def repr(self):
        return (
            f"ClientParking(Client ID: {self.client_id}, Parking ID: {self.parking_id})"
        )
