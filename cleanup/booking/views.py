import json

from flask import (
    Blueprint, request
)
from marshmallow import Schema, fields, EXCLUDE, ValidationError

from cleanup.database import db
from cleanup.auth.views import login_required
from cleanup.booking.models import Booking
from cleanup.city.models import City
from cleanup.cleaner.models import Cleaner

bp = Blueprint('booking', __name__)


class ObjectSchema(Schema):
    id = fields.Int(required=True)

    class Meta:
        unknown = EXCLUDE


class BookingSchema(Schema):
    cleaner = fields.Nested(ObjectSchema)
    city = fields.Nested(ObjectSchema)
    date = fields.Date(required=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    phone = fields.Str(required=True)


@bp.route('/bookings', methods=('GET', ))
@login_required
def items():
    bookings = Booking.query.all()

    return {
        'items': [booking_to_response(booking) for booking in bookings]
    }


@bp.route('/booking', methods=('POST', ))
def create():
    raw_content = request.data.decode('utf-8')
    data = json.loads(raw_content)

    try:
        result = BookingSchema().load(data)
    except ValidationError as error:
        # format errors
        return {'errors': error.messages}, 400

    cleaner = Cleaner.query.get(result['cleaner']['id'])
    city = City.query.get(result['cleaner']['id'])

    booking = Booking(name=result['name'], email=result['email'], phone=result['phone'], cleaner=cleaner, city=city,
                      date=result['date'])
    db.session.add(booking)
    db.session.commit()

    return booking_to_response(booking)


def booking_to_response(booking):
    return {
        'id': booking.id,
    }
