import json

from flask import (
    Blueprint, request
)
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.exceptions import abort

from cleanup.database import db
from cleanup.auth.views import login_required
from .models import City


class CitySchema(Schema):
    name = fields.Str(validate=validate.Length(min=3, max=100), required=True)
    zipcode = fields.Str(validate=validate.Length(equal=6), required=True)


bp = Blueprint('city', __name__)


@bp.route('/cities', methods=('GET', ))
@login_required
def items():
    cities = City.query.all()

    return {
        'items': [city_to_response(city) for city in cities]
    }


@bp.route('/city/<int:id>', methods=('GET',))
@login_required
def get(id):
    city = get_item(id)  # type: City
    return city_to_response(city)


@bp.route('/city', methods=('POST', ))
@login_required
def create():
    raw_content = request.data.decode('utf-8')
    data = json.loads(raw_content)

    try:
        result = CitySchema().load(data)
    except ValidationError as error:
        # format errors
        return {'errors': error.messages}, 400

    city = City(name=result['name'], zipcode=result['zipcode'])
    db.session.add(city)
    db.session.commit()

    return city_to_response(city)


@bp.route('/city/<int:id>', methods=('PUT',))
@login_required
def update(id):
    city = get_item(id)

    raw_content = request.data.decode('utf-8')
    data = json.loads(raw_content)

    try:
        result = CitySchema().load(data)
    except ValidationError as error:
        # format errors
        return {'errors': error.messages}, 400

    city.name = result['name']
    city.zipcode = result['zipcode']
    db.session.add(city)
    db.session.commit()

    return city_to_response(city)


@bp.route('/city/<int:id>', methods=('DELETE',))
@login_required
def delete(id):
    city = get_item(id)
    db.session.delete(city)
    db.session.commit()
    return '', 201


def city_to_response(city):
    return {
        'id': city.id,
        'name': city.name,
        'zipcode': city.zipcode,
        'created': city.created,
    }


def get_item(id):
    item = City.query.get(id)
    if item is None:
        abort(404)
    return item
