import json

from flask import (
    Blueprint, request
)
from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from sqlalchemy.sql.functions import count
from werkzeug.exceptions import abort

from cleanup.database import db
from cleanup.auth.views import login_required
from .models.cleaner import Cleaner
from ..booking.models import Booking
from ..city.models import City

bp = Blueprint('cleaner', __name__)


class CleanerCitySchema(Schema):
    id = fields.Int(required=True)

    class Meta:
        unknown = EXCLUDE


class CleanerSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(equal=6))

    cities = fields.List(fields.Nested(CleanerCitySchema))


class AvailableCleanersSchema(Schema):
    date = fields.Date(required=True)
    city = fields.Int(required=True)


@bp.route('/cleaners', methods=('GET', ))
@login_required
def list():
    cleaners = Cleaner.query.all()
    return {
        'items': [cleaner_to_response(cleaner) for cleaner in cleaners]
    }


@bp.route('/available-cleaners', methods=('GET', ))
def list_available():
    try:
        result = AvailableCleanersSchema().load(request.args)
    except ValidationError as error:
        return {'errors': error.messages}, 400

    date = result['date']
    city_id = result['city']

    city = City.query.get(city_id)
    if city is None:
        abort(404)

    cleaners = query_available_cleaners(city, date)
    return {
        'items': [cleaner_to_response(cleaner) for cleaner in cleaners]
    }


def query_available_cleaners(city: City, date):
    # subquery to count the number of bookings of a cleaner in the provided city and date
    stmt = db.session.query(count(Booking.id).label('bookings_count')) \
        .filter_by(cleaner_id=Cleaner.id, city=city, date=date).as_scalar()
    # all cleaners which have 0 bookings in the provided city and date
    return db.session.query(Cleaner).filter(stmt == 0).all()


@bp.route('/cleaner/<int:id>', methods=('GET', ))
@login_required
def get(id):
    return get_item(id)


@bp.route('/cleaner', methods=('POST', ))
@login_required
def create():
    raw_content = request.data.decode('utf-8')
    data = json.loads(raw_content)

    try:
        result = CleanerSchema().load(data)
    except ValidationError as error:
        # format errors
        return {'errors': error.messages}, 400

    # find every city
    cities_ids = [x['id'] for x in data['cities']]
    from cleanup.city.models import City
    cities_found = City.query.filter(City.id.in_(cities_ids)).all()

    # todo: assert we found all cities

    cleaner = Cleaner(name=result['name'], email=result['email'], phone=result['phone'])
    db.session.add(cleaner)

    for city in cities_found:
        cleaner.cities.append(city)

    db.session.commit()

    return cleaner_to_response(cleaner)


@bp.route('/cleaner/<int:id>', methods=('PUT', ))
@login_required
def update(id):
    cleaner = get_item(id)
    raw_content = request.data.decode('utf-8')
    data = json.loads(raw_content)

    try:
        result = CleanerSchema().load(data)
    except ValidationError as error:
        # format errors
        return {'errors': error.messages}, 400

    # find every city
    cities_ids = [x['id'] for x in data['cities']]
    from cleanup.city.models import City
    cities_found = City.query.filter(City.id.in_(cities_ids)).all()

    # todo: assert we found all cities

    cleaner_cities = cleaner.cities
    cleaner_cities_ids = [city.id for city in cleaner_cities]

    for city in cleaner_cities:
        if city.id not in cities_ids:
            cleaner.cities.remove(city)

    for city in cities_found:
        if city.id not in cleaner_cities_ids:
            cleaner.cities.append(city)

    db.session.commit()

    return cleaner_to_response(cleaner)


@bp.route('/cleaner/<int:id>', methods=('DELETE',))
@login_required
def delete(id):
    item = get_item(id)
    db.session.delete(item)
    db.session.commit()
    return '', 201


def cleaner_to_response(cleaner):
    return {
        'id': cleaner.id,
        'name': cleaner.name,
        'email': cleaner.email,
        'phone': cleaner.phone,
        'cities': [{
            'id': city.id,
            'name': city.name,
            'zipcode': city.zipcode,
        } for city in cleaner.cities]
    }


def get_item(id):
    item = Cleaner.query.get(id)
    if item is None:
        abort(404)
    return item