import json

import pytest


def test_login(client):
    response = client.post(
        '/auth/login',
        data=json.dumps({'username': 'test', 'password': 'test'}),
        headers={
            'Content-Type': 'application/json'
        }
    )

    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    assert 'username' in json_content
    assert json_content['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', 'incorrect username'),
    ('test', 'a', 'incorrect password'),
))
def test_login_validate_input(client, username, password, message):
    response = client.post(
        '/auth/login',
        data=json.dumps({'username': username, 'password': password}),
        headers={
            'Content-Type': 'application/json'
        },
    )

    assert response.status_code == 200
    content = response.data.decode('utf-8')
    json_content = json.loads(content)
    assert 'error' in json_content
    assert json_content['error'] == message
