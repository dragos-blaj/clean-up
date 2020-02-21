from cleanup.database import db
from cleanup.city.models import City
from cleanup.cleaner.models.cleaner import Cleaner


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)

    city_id = db.Column(db.ForeignKey(City.id), nullable=False)
    city = db.relationship(City, lazy="joined", backref="bookings")

    cleaner_id = db.Column(db.ForeignKey(Cleaner.id), nullable=False)
    cleaner = db.relationship(Cleaner, lazy="joined", backref="bookings")

    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)

    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )
