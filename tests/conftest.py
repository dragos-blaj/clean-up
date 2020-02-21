import json
import os
import tempfile

import pytest
from werkzeug.security import generate_password_hash

from cleanup import create_app
from cleanup.auth.models import User
from cleanup.database import init_db, db

_user1_pass = generate_password_hash("test")
_user2_pass = generate_password_hash("other")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    with app.app_context():
        init_db()
        db.session.add_all(
            (
                User(username="test", _password=_user1_pass),
                User(username="other", _password=_user2_pass),
            )
        )
        db.session.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data=json.dumps({'username': username, 'password': password}),
            headers={
                'Content-Type': 'application/json'
            },
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
