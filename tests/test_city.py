import json

import pytest

from cleanup.database import db
from cleanup.city.models import City


@pytest.fixture
def cities(app):
    with app.app_context():
        db.session.add_all(
            (
                City(name='Cluj Napoca', zipcode='000123'),
                City(name='Oradea', zipcode='000123'),
            )
        )
        db.session.commit()


def test_list(client, auth, cities):
    auth.login()
    response = client.get('/cities')
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    assert 'items' in json_content
    assert len(json_content['items']) == 2
    assert_city(json_content['items'][0], 'Cluj Napoca', '000123', 1)
    assert_city(json_content['items'][1], 'Oradea', '000123', 2)


def test_list_auth(client, auth, cities):
    response = client.get('/cities')
    assert response.status_code == 401


def assert_city(obj, name, zipcode, id):
    assert 'id' in obj
    assert 'name' in obj
    assert 'zipcode' in obj
    assert obj['name'] == name
    assert obj['zipcode'] == zipcode
    assert obj['id'] == id


def test_get(client, auth, cities):
    auth.login()
    response = client.get('/city/2')
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    assert_city(json_content, 'Oradea', '000123', 2)


def test_get_auth(client, auth, cities):
    response = client.get('/city/2')
    assert response.status_code == 401


def test_post(client, auth):
    auth.login()
    response = client.post('/city', data=json.dumps({
        'name': 'My City',
        'zipcode': '123123',
    }))
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    assert_city(json_content, 'My City', '123123', 1)


@pytest.mark.parametrize(('name', 'zipcode', 'expected_errors'), (
    ('', '', {'name': ["Length must be between 3 and 100."], 'zipcode':["Length must be 6."]}),
))
def test_post_validation(client, auth, name, zipcode, expected_errors):
    auth.login()
    response = client.post('/city', data=json.dumps({
        'name': name,
        'zipcode': zipcode,
    }))

    assert response.status_code == 400
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    assert 'errors' in json_content
    errors = json_content['errors']
    assert errors.keys() == expected_errors.keys()

    for key, val in expected_errors.items():
        assert errors[key] == val


def test_update(client, auth):
    auth.login()
    response = client.post('/city', data=json.dumps({
        'name': 'My City',
        'zipcode': '123123',
    }))

    response = client.put('/city/1', data=json.dumps({
        'name': 'My City #2',
        'zipcode': '321312',
    }))
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    assert_city(json_content, 'My City #2', '321312', 1)


def test_delete(client, auth):
    auth.login()
    client.post('/city', data=json.dumps({
        'name': 'My City',
        'zipcode': '123123',
    }))

    response = client.delete('/city/1')
    assert response.status_code == 201

    response = client.get('/city/1')
    assert response.status_code == 404
