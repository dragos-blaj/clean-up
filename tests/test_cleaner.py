import json
from datetime import datetime, date

import pytest

from cleanup.booking.models import Booking
from cleanup.city.models import City
from cleanup.cleaner.models import Cleaner
from cleanup.database import db


@pytest.fixture
def cities(app):
    cities = [
        City(name='Cluj Napoca', zipcode='000123'),
        City(name='Oradea', zipcode='000123'),
        City(name='Bucuresti', zipcode='000123'),
        City(name='Iasi', zipcode='000123'),
    ]
    with app.app_context():
        db.session.add_all(cities)
        db.session.commit()
        return cities


@pytest.fixture
def cleaners(app, cities):
    with app.app_context():
        joe = Cleaner(name='Joe', email='joe@example.com', phone='123123')
        db.session.add(joe)
        joe.cities.append(cities[0])
        joe.cities.append(cities[1])

        bob = Cleaner(name='Bob', email='bob@example.com', phone='123123')
        db.session.add(bob)
        for city in cities:
            bob.cities.append(city)

        db.session.commit()
        return [joe, bob]


@pytest.fixture
def bookings(app, cleaners):
    with app.app_context():
        db.session.add_all(cleaners)

        booking = Booking(name='Joe', email='joe@example.com', phone='123123', cleaner=cleaners[0],
                          city=cleaners[0].cities[0], date=date(2020, 1, 10))
        db.session.add(booking)
        db.session.commit()


def test_available(client, bookings):
    # only Bob should be available on this date since Joe has a booking
    response1 = client.get('/available-cleaners?&date=2020-01-10&city=1')
    assert response1.status_code == 200
    content1 = response1.data.decode('utf-8')
    json_content1 = json.loads(content1)
    assert 'items' in json_content1
    items = json_content1['items']
    assert len(items) == 1
    assert_cleaner(items[0], name='Bob', id=2)

    # both cleaners are available on this date
    response2 = client.get('/available-cleaners?&date=2020-01-11&city=1')
    assert response2.status_code == 200
    content2 = response2.data.decode('utf-8')
    json_content2 = json.loads(content2)
    assert 'items' in json_content2
    items = json_content2['items']
    assert len(items) == 2
    assert_cleaner(items[0], name='Joe', id=1)
    assert_cleaner(items[1], name='Bob', id=2)


def test_post(app, client, auth, cities):
    auth.login()
    response = client.post('/cleaner', data=json.dumps({
        'name': 'My City',
        'email': 'a@a.com',
        'phone': '123123',
        'cities': [
            {'id': 1},
            {'id': 2},
        ]
    }))
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    # todo: assert content

    with app.app_context():
        cleaner = Cleaner.query.get(json_content['id'])
        # todo: assert saved information in the database


def test_update(app, client, auth, cities):
    auth.login()
    client.post('/cleaner', data=json.dumps({
        'name': 'My City',
        'email': 'a@a.com',
        'phone': '123123',
        'cities': [
            {'id': 1},
            {'id': 2},
        ]
    }))

    response = client.put('/cleaner/1', data=json.dumps({
        'name': 'My City',
        'email': 'a@a.com',
        'phone': '123123',
        'cities': [
            {'id': 1},
            {'id': 3},
            {'id': 4},
        ]
    }))
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    # todo: assert content

    with app.app_context():
        cleaner = Cleaner.query.get(json_content['id'])
        pass
        # todo: assert saved information in the database


def test_delete(client, auth):
    auth.login()
    client.post('/cleaner', data=json.dumps({
        'name': 'My City',
        'email': 'a@a.com',
        'phone': '123123',
        'cities': [
            {'id': 1},
            {'id': 2},
        ]
    }))

    response = client.delete('/cleaner/1')
    assert response.status_code == 201

    response = client.get('/cleaner/1')
    assert response.status_code == 404


def assert_cleaner(obj, name, id):
    assert 'id' in obj
    assert 'name' in obj
    assert obj['name'] == name
    assert obj['id'] == id
