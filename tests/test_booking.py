import json

import pytest

from cleanup.database import db
from cleanup.city.models import City
from cleanup.cleaner.models import Cleaner


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


def test_post(app, client, cleaners):
    response = client.post('/booking', data=json.dumps({
        'name': 'My City',
        'email': 'a@a.com',
        'phone': '123123',
        'city': {'id': 1},
        'cleaner': {'id': 1},
        'date': '2020-03-20',
    }))
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    # todo: assert content

